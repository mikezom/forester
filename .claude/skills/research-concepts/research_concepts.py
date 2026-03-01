#!/usr/bin/env python3
"""
Iterate through the concept registry and research definitions using Claude Agent SDK.

For each concept in the master registry, this script uses the Claude Agent SDK
to spawn an agent with the concept-definition-researcher instructions. The agent
searches the ingestion files for a definition and writes a .tree file.

Usage:
    python research_concepts.py <document-name>
    python research_concepts.py <document-name> --delay 5
    python research_concepts.py <document-name> --dry-run

Examples:
    python research_concepts.py attention-is-all-you-need

Requires:
    pip install claude-agent-sdk
"""

import argparse
import json
import os
import sys
from pathlib import Path

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKError,
    ProcessError,
    TextBlock,
    query,
)


def load_meta(ingestion_path: Path) -> dict:
    """Load meta.json from the ingestion directory."""
    meta_path = ingestion_path / "meta.json"
    if not meta_path.exists():
        print(f"Error: meta.json not found at {meta_path}")
        sys.exit(1)
    with open(meta_path, encoding="utf-8") as f:
        return json.load(f)


def derive_author_id(authors: list[str]) -> str:
    """Derive author-id from the authors list.

    Single author: full name slug (e.g., "tang-chao")
    Multiple authors: first author's last name + "-et-al" (e.g., "vaswani-et-al")
    """
    if len(authors) == 1:
        return authors[0].lower().replace(" ", "-")
    first_author_last = authors[0].split()[-1].lower()
    return f"{first_author_last}-et-al"


def load_master_registry(structural_analysis_path: Path, prefix: str) -> dict:
    """Load the master registry JSON file."""
    registry_path = structural_analysis_path / f"{prefix}_master_registry.json"
    if not registry_path.exists():
        print(f"Error: Master registry not found at {registry_path}")
        sys.exit(1)
    with open(registry_path, encoding="utf-8") as f:
        return json.load(f)


def get_all_concepts(master_registry: dict) -> list[tuple[str, str, str]]:
    """Extract a deduplicated flat list of (concept_name, tree_id, category)
    from the categorized master registry."""
    concepts = []
    seen_ids = set()
    for category, cat_concepts in master_registry["concepts"].items():
        for name, tree_id in cat_concepts.items():
            if tree_id not in seen_ids:
                concepts.append((name, tree_id, category))
                seen_ids.add(tree_id)
    return concepts


def find_tree_file(trees_path: Path, tree_id: str) -> bool:
    """Check if a .tree file already exists for this concept.

    Searches both flat in trees/ and in any subdirectory.
    """
    if (trees_path / f"{tree_id}.tree").exists():
        return True
    for _ in trees_path.rglob(f"{tree_id}.tree"):
        return True
    return False


def load_skill_instructions(skill_name: str) -> str:
    """Load the SKILL.md instructions for a sibling skill."""
    skill_path = Path(__file__).resolve().parent.parent / skill_name / "SKILL.md"
    if not skill_path.exists():
        print(f"Error: Skill instructions not found at {skill_path}")
        sys.exit(1)
    return skill_path.read_text(encoding="utf-8")


async def research_concept(
    concept_name: str,
    document_name: str,
    prefix: str,
    author_id: str,
    ingestion_path: str,
    project_root: Path,
    skill_instructions: str,
) -> None:
    """Use Claude Agent SDK to research a single concept definition."""
    prompt = (
        f'Research the following concept and generate a .tree definition file.\n\n'
        f'concept="{concept_name}"\n'
        f'document="{document_name}"\n'
        f'prefix="{prefix}"\n'
        f'author-id="{author_id}"\n'
        f'ingestion-path="{ingestion_path}"'
    )

    options = ClaudeAgentOptions(
        system_prompt=skill_instructions,
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "WebSearch"],
        permission_mode="acceptEdits",
        cwd=str(project_root),
        max_turns=30,
    )

    # Remove CLAUDECODE env var to allow nested claude invocations
    old_val = os.environ.pop("CLAUDECODE", None)
    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        # Print agent progress (trimmed)
                        preview = block.text.strip()[:200]
                        print(f"    {preview}")
    finally:
        if old_val is not None:
            os.environ["CLAUDECODE"] = old_val


async def async_main():
    parser = argparse.ArgumentParser(
        description="Research concept definitions using Claude Agent SDK.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "This script reads the master registry from Step 2 (concept-registry)\n"
            "and uses Claude Agent SDK with concept-definition-researcher instructions\n"
            "for each concept that doesn't already have a .tree file."
        ),
    )
    parser.add_argument(
        "document",
        help="Document name (folder name under intermediate/)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2,
        help="Seconds to wait between API calls to avoid rate limits (default: 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List concepts that would be processed without calling Claude",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    intermediate_path = project_root / "intermediate" / args.document
    ingestion_path = intermediate_path / "ingestion"
    structural_analysis_path = intermediate_path / "structural-analysis"
    trees_path = intermediate_path / "trees"

    # --- Validate paths ---
    if not ingestion_path.exists():
        print(f"Error: Ingestion path not found: {ingestion_path}")
        sys.exit(1)
    if not structural_analysis_path.exists():
        print(f"Error: Structural analysis path not found: {structural_analysis_path}")
        sys.exit(1)

    # --- Load skill instructions ---
    skill_instructions = load_skill_instructions("concept-definition-researcher")

    # --- Load metadata ---
    meta = load_meta(ingestion_path)
    prefix = meta.get("prefix")
    if not prefix:
        print("Error: meta.json is missing the 'prefix' field.")
        sys.exit(1)

    author_id = derive_author_id(meta["authors"])

    # --- Load registry ---
    registry = load_master_registry(structural_analysis_path, prefix)
    concepts = get_all_concepts(registry)

    print(f"Document:  {meta['title']}")
    print(f"Prefix:    {prefix}")
    print(f"Author ID: {author_id}")
    print(f"Concepts in registry: {len(concepts)}")
    print()

    # --- Ensure trees directory exists ---
    trees_path.mkdir(parents=True, exist_ok=True)

    # --- Filter out concepts that already have .tree files ---
    to_process = []
    skipped = []
    for name, tree_id, category in concepts:
        if find_tree_file(trees_path, tree_id):
            skipped.append((name, tree_id))
        else:
            to_process.append((name, tree_id, category))

    print(f"Already have .tree files: {len(skipped)}")
    print(f"To process: {len(to_process)}")
    print()

    if not to_process:
        print("Nothing to do.")
        return

    # --- Dry run ---
    if args.dry_run:
        print("=== DRY RUN (no Claude calls) ===")
        for i, (name, tree_id, category) in enumerate(to_process, 1):
            print(f"  {i}. [{category}] {name} -> {tree_id}.tree")
        return

    # --- Process each concept sequentially ---
    succeeded = 0
    failed = 0
    failed_concepts = []

    for i, (name, tree_id, category) in enumerate(to_process, 1):
        print(f"[{i}/{len(to_process)}] [{category}] {name}")

        try:
            await research_concept(
                concept_name=name,
                document_name=args.document,
                prefix=prefix,
                author_id=author_id,
                ingestion_path=str(ingestion_path),
                project_root=project_root,
                skill_instructions=skill_instructions,
            )

            if find_tree_file(trees_path, tree_id):
                print(f"  -> Done")
                succeeded += 1
            else:
                print(f"  -> Warning: agent finished but {tree_id}.tree not found")
                failed += 1
                failed_concepts.append(name)

        except ProcessError as e:
            print(f"  -> Failed (process error): {e}")
            failed += 1
            failed_concepts.append(name)
        except ClaudeSDKError as e:
            print(f"  -> Failed (SDK error): {e}")
            failed += 1
            failed_concepts.append(name)
        except Exception as e:
            print(f"  -> Error: {e}")
            failed += 1
            failed_concepts.append(name)

        # Delay between calls to avoid rate limits
        if i < len(to_process):
            await anyio.sleep(args.delay)

    # --- Summary ---
    print()
    print("=" * 40)
    print(f"Succeeded:  {succeeded}")
    print(f"Failed:     {failed}")
    print(f"Skipped:    {len(skipped)}")
    print(f"Total:      {len(concepts)}")

    if failed_concepts:
        print()
        print("Failed concepts:")
        for name in failed_concepts:
            print(f"  - {name}")


def main():
    anyio.run(async_main)


if __name__ == "__main__":
    main()
