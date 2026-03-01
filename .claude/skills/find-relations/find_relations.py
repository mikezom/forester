#!/usr/bin/env python3
"""
Find semantic relations between concepts using Claude Agent SDK.

Reads concept .tree files for tags, computes candidate pairs via tag overlap,
dispatches per-concept reasoning to Claude agents, and merges results into
a single {prefix}-relations.tree file.

Usage:
    python find_relations.py <document-name>
    python find_relations.py <document-name> --dry-run
    python find_relations.py <document-name> --delay 5

Examples:
    python find_relations.py attention-is-all-you-need
    python find_relations.py attention-is-all-you-need --dry-run

Requires:
    pip install claude-agent-sdk
"""

import argparse
import json
import os
import re
import sys
from datetime import date
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
    meta_path = ingestion_path / "meta.json"
    if not meta_path.exists():
        print(f"Error: meta.json not found at {meta_path}")
        sys.exit(1)
    with open(meta_path, encoding="utf-8") as f:
        return json.load(f)


def derive_author_id(authors: list[str]) -> str:
    if len(authors) == 1:
        return authors[0].lower().replace(" ", "-")
    first_author_last = authors[0].split()[-1].lower()
    return f"{first_author_last}-et-al"


def load_master_registry(structural_analysis_path: Path, prefix: str) -> dict:
    registry_path = structural_analysis_path / f"{prefix}_master_registry.json"
    if not registry_path.exists():
        print(f"Error: Master registry not found at {registry_path}")
        sys.exit(1)
    with open(registry_path, encoding="utf-8") as f:
        return json.load(f)


def get_all_concepts(master_registry: dict) -> dict[str, str]:
    """Return {concept_name: tree_id} deduplicated."""
    concepts = {}
    seen_ids = set()
    for category, cat_concepts in master_registry["concepts"].items():
        for name, tree_id in cat_concepts.items():
            if tree_id not in seen_ids:
                concepts[name] = tree_id
                seen_ids.add(tree_id)
    return concepts


def extract_tags_from_tree(tree_path: Path) -> list[str]:
    """Extract tags from \\meta{tags}{...} in a .tree file."""
    if not tree_path.exists():
        return []
    content = tree_path.read_text(encoding="utf-8")
    match = re.search(r'\\meta\{tags\}\{([^}]+)\}', content)
    if not match:
        return []
    return [t.strip().lower() for t in match.group(1).split(",") if t.strip()]


def find_tree_file(trees_path: Path, tree_id: str) -> Path | None:
    """Find the .tree file for a given tree_id."""
    flat = trees_path / f"{tree_id}.tree"
    if flat.exists():
        return flat
    for p in trees_path.rglob(f"{tree_id}.tree"):
        return p
    return None


def build_tag_index(concepts: dict[str, str], trees_path: Path) -> dict[str, list[str]]:
    """Build {tree_id: [tags]} for all concepts."""
    tag_index = {}
    for name, tree_id in concepts.items():
        tree_file = find_tree_file(trees_path, tree_id)
        tags = extract_tags_from_tree(tree_file) if tree_file else []
        tag_index[tree_id] = tags
    return tag_index


def find_candidates(
    focus_tree_id: str,
    tag_index: dict[str, list[str]],
    concepts: dict[str, str],
) -> list[dict]:
    """Find concepts sharing at least one tag with the focus concept."""
    focus_tags = set(tag_index.get(focus_tree_id, []))
    if not focus_tags:
        return []

    id_to_name = {v: k for k, v in concepts.items()}

    candidates = []
    for tree_id, tags in tag_index.items():
        if tree_id == focus_tree_id:
            continue
        if focus_tags & set(tags):
            candidates.append({
                "name": id_to_name.get(tree_id, tree_id),
                "tree_id": tree_id,
            })
    return candidates


def load_skill_instructions(skill_name: str) -> str:
    """Load the SKILL.md instructions for a sibling skill."""
    skill_path = Path(__file__).resolve().parent.parent / skill_name / "SKILL.md"
    if not skill_path.exists():
        print(f"Error: Skill instructions not found at {skill_path}")
        sys.exit(1)
    return skill_path.read_text(encoding="utf-8")


async def call_subagent(
    focus_name: str,
    focus_tree_id: str,
    candidates: list[dict],
    document: str,
    ingestion_path: str,
    prefix: str,
    project_root: Path,
    skill_instructions: str,
) -> list[dict]:
    """Use Claude Agent SDK to find relations for one concept."""
    candidates_json = json.dumps(candidates, ensure_ascii=False)
    prompt = (
        f'Find semantic relations for the following concept.\n\n'
        f'focus-concept="{focus_name}"\n'
        f'focus-tree-id="{focus_tree_id}"\n'
        f"candidates='{candidates_json}'\n"
        f'document="{document}"\n'
        f'ingestion-path="{ingestion_path}"\n'
        f'prefix="{prefix}"'
    )

    options = ClaudeAgentOptions(
        system_prompt=skill_instructions,
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",
        cwd=str(project_root),
        max_turns=30,
    )

    # Remove CLAUDECODE env var to allow nested claude invocations
    old_val = os.environ.pop("CLAUDECODE", None)
    try:
        collected_text = ""
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        collected_text += block.text
    finally:
        if old_val is not None:
            os.environ["CLAUDECODE"] = old_val

    # Extract JSON array from collected text
    start = collected_text.find("[")
    end = collected_text.rfind("]")
    if start == -1 or end == -1:
        return []

    try:
        return json.loads(collected_text[start : end + 1])
    except json.JSONDecodeError:
        return []


def deduplicate_relations(all_relations: list[dict]) -> list[dict]:
    """Remove duplicate relations (same source, relation, target)."""
    seen = set()
    unique = []
    for rel in all_relations:
        key = (rel["source"], rel["relation"], rel["target"])
        if key not in seen:
            seen.add(key)
            unique.append(rel)
    return unique


def write_relations_tree(
    relations: list[dict],
    output_path: Path,
    title: str,
    author_id: str,
):
    """Write the merged relations to a .tree file."""
    today = date.today().isoformat()

    lines = [
        f"\\title{{Relations: {title}}}",
        "\\taxon{Metadata}",
        f"\\date{{{today}}}",
        f"\\author{{{author_id}}}",
        "\\import{base-macros}",
        "",
    ]

    # Group by source concept for readability
    by_source: dict[str, list[dict]] = {}
    for rel in relations:
        by_source.setdefault(rel["source"], []).append(rel)

    for source_id in sorted(by_source.keys()):
        source_rels = by_source[source_id]
        lines.append(f"% {source_id}")
        for rel in sorted(source_rels, key=lambda r: r["relation"]):
            mentioned = "true" if rel.get("mentioned", True) else "false"
            lines.append(
                f"\\relation{{{rel['source']}}}{{{rel['relation']}}}{{{rel['target']}}}{{{mentioned}}}"
            )
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


async def async_main():
    parser = argparse.ArgumentParser(
        description="Find semantic relations between concepts using Claude Agent SDK.",
    )
    parser.add_argument("document", help="Document name (folder under intermediate/)")
    parser.add_argument(
        "--delay", type=float, default=2,
        help="Seconds between API calls (default: 2)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show candidate pairs without calling Claude",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    intermediate_path = project_root / "intermediate" / args.document
    ingestion_path = intermediate_path / "ingestion"
    structural_analysis_path = intermediate_path / "structural-analysis"
    trees_path = intermediate_path / "trees"

    if not ingestion_path.exists():
        print(f"Error: Ingestion path not found: {ingestion_path}")
        sys.exit(1)
    if not structural_analysis_path.exists():
        print(f"Error: Structural analysis path not found: {structural_analysis_path}")
        sys.exit(1)

    # --- Load skill instructions ---
    skill_instructions = load_skill_instructions("find-concept-relations")

    meta = load_meta(ingestion_path)
    prefix = meta.get("prefix")
    if not prefix:
        print("Error: meta.json missing 'prefix' field")
        sys.exit(1)

    author_id = derive_author_id(meta["authors"])
    registry = load_master_registry(structural_analysis_path, prefix)
    concepts = get_all_concepts(registry)

    print(f"Document:  {meta['title']}")
    print(f"Prefix:    {prefix}")
    print(f"Concepts:  {len(concepts)}")
    print()

    # Build tag index
    tag_index = build_tag_index(concepts, trees_path)
    tagged = sum(1 for tags in tag_index.values() if tags)
    untagged = len(tag_index) - tagged
    print(f"Tagged:    {tagged}")
    print(f"Untagged:  {untagged} (will be skipped -- no tags to match)")
    print()

    if untagged > 0:
        id_to_name = {v: k for k, v in concepts.items()}
        print("Untagged concepts:")
        for tree_id, tags in tag_index.items():
            if not tags:
                print(f"  - {id_to_name.get(tree_id, tree_id)}")
        print()

    # Find candidates for each concept
    work_items = []
    for name, tree_id in concepts.items():
        candidates = find_candidates(tree_id, tag_index, concepts)
        if candidates:
            work_items.append((name, tree_id, candidates))

    print(f"Concepts with candidates: {len(work_items)}")
    total_pairs = sum(len(c) for _, _, c in work_items)
    print(f"Total concept pairs to evaluate: {total_pairs}")
    print()

    if args.dry_run:
        print("=== DRY RUN ===")
        for name, tree_id, candidates in work_items:
            print(f"  {name} ({len(candidates)} candidates)")
            for c in candidates[:5]:
                print(f"    - {c['name']}")
            if len(candidates) > 5:
                print(f"    ... and {len(candidates) - 5} more")
        return

    # Process each concept sequentially
    all_relations = []
    succeeded = 0
    failed = 0
    failed_concepts = []

    for i, (name, tree_id, candidates) in enumerate(work_items, 1):
        print(f"[{i}/{len(work_items)}] {name} ({len(candidates)} candidates)")

        try:
            relations = await call_subagent(
                focus_name=name,
                focus_tree_id=tree_id,
                candidates=candidates,
                document=args.document,
                ingestion_path=str(ingestion_path),
                prefix=prefix,
                project_root=project_root,
                skill_instructions=skill_instructions,
            )
            print(f"  -> {len(relations)} relations found")
            all_relations.extend(relations)
            succeeded += 1
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

        if i < len(work_items):
            await anyio.sleep(args.delay)

    # Deduplicate and write output
    unique_relations = deduplicate_relations(all_relations)
    output_path = trees_path / f"{prefix}-relations.tree"
    write_relations_tree(unique_relations, output_path, meta["title"], author_id)

    print()
    print("=" * 40)
    print(f"Succeeded:    {succeeded}/{len(work_items)} concepts")
    print(f"Failed:       {failed}")
    print(f"Relations:    {len(unique_relations)} (deduplicated from {len(all_relations)})")
    print(f"Output:       {output_path}")

    if failed_concepts:
        print()
        print("Failed concepts:")
        for name in failed_concepts:
            print(f"  - {name}")


def main():
    anyio.run(async_main)


if __name__ == "__main__":
    main()
