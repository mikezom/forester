# Concept Relation Finder -- Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a relation-finding pipeline that discovers semantic relations between concepts using tag-based pair filtering and Claude subagents, outputting a `{prefix}-relations.tree` file with a `mentioned` boolean per relation.

**Architecture:** Python orchestrator (`find_relations.py`) reads concept `.tree` files for tags, computes candidate pairs via tag overlap, dispatches per-concept reasoning to Claude subagents (`/find-concept-relations` skill), then merges JSON results into a single `.tree` file. The `\relation` macro gains a 4th argument.

**Tech Stack:** Python 3 (pathlib, subprocess, json, re, argparse), Claude CLI (`claude -p`), Forester macros

---

### Task 1: Extend the `\relation` macro to 4 arguments

**Files:**
- Modify: `trees/utils/base-macros.tree:41-43`

**Step 1: Update the macro definition**

Change the existing `\relation` macro from 3 args to 4:

```
\def\relation[source][desc][target][mentioned]{
  \<html:span>[data-source]{\source}[data-relation]{\desc}[data-target]{\target}[data-mentioned]{\mentioned}[class]{semantic-relation}
}
```

**Step 2: Verify forester builds without errors**

Run: `forester build 2>&1 | head -20`
Expected: Build will show errors because existing `\relation` calls still pass 3 args. That's expected -- Task 2 fixes them.

**Step 3: Commit**

```bash
git add trees/utils/base-macros.tree
git commit -m "feat: extend \relation macro with 4th 'mentioned' argument"
```

---

### Task 2: Migrate all existing relation files to 4-arg format

**Files:**
- Modify: all 8 `.tree` files containing `\relation{` calls (508 total occurrences):
  - `trees/001-learning-forester/001-semantic-relations.tree`
  - `trees/004-Semantic-Relation-Test/004-relationship.tree`
  - `trees/005-gemini-semantic-relation-homework/005-relations.tree`
  - `trees/006-glm-attention-is-all-you-need/006-relations.tree`
  - `trees/007-glm-hand-to-hand/007-relations.tree`
  - `trees/008-glm-hand-to-hand-v2/008-relations.tree`
  - `intermediate/attention-is-all-you-need/trees/006-relations.tree`
  - `intermediate/手把手教你读财报/trees/008-relations.tree`

**Step 1: Write migration script**

Create `scripts/migrate_relations.py`:

```python
#!/usr/bin/env python3
"""Migrate all \relation{a}{b}{c} calls to \relation{a}{b}{c}{true}."""
import re
import sys
from pathlib import Path

def migrate_file(path: Path) -> int:
    content = path.read_text(encoding="utf-8")
    # Match \relation{...}{...}{...} that do NOT already have a 4th {arg}
    pattern = r'(\\relation\{[^}]+\}\{[^}]+\}\{[^}]+\})(?!\{)'
    new_content, count = re.subn(pattern, r'\1{true}', content)
    if count > 0:
        path.write_text(new_content, encoding="utf-8")
    return count

def main():
    root = Path(__file__).parent.parent
    total = 0
    for tree_file in sorted(root.rglob("*.tree")):
        count = migrate_file(tree_file)
        if count > 0:
            print(f"  {tree_file.relative_to(root)}: {count} relations migrated")
            total += count
    print(f"\nTotal: {total} relations migrated")

if __name__ == "__main__":
    main()
```

**Step 2: Run the migration**

Run: `python scripts/migrate_relations.py`
Expected: Output listing each file and count, total ~508.

**Step 3: Spot-check a migrated file**

Run: `head -15 trees/006-glm-attention-is-all-you-need/006-relations.tree`
Expected: Lines like `\relation{006-transformer}{is-composed-of}{006-encoder}{true}`

**Step 4: Verify forester builds cleanly**

Run: `forester build 2>&1 | tail -5`
Expected: Clean build, no macro argument errors.

**Step 5: Commit**

```bash
git add -A
git commit -m "chore: migrate all existing relations to 4-arg format with {true}"
```

---

### Task 3: Update `aggregate_graph.py` to handle the new `data-mentioned` attribute

**Files:**
- Modify: `aggregate_graph.py:7-9` (edge_pattern regex)
- Modify: `aggregate_graph.py:33-34` (edge tuple extraction)
- Modify: `aggregate_graph.py:44-47` (edges_list construction)

**Step 1: Update the edge regex to capture the 4th attribute**

The current regex:
```python
edge_pattern = re.compile(
    r'<html:span\s+data-source="([^"]+)"\s+data-relation="([^"]+)"\s+data-target="([^"]+)"\s+class="semantic-relation"\s*/>'
)
```

Updated regex:
```python
edge_pattern = re.compile(
    r'<html:span\s+data-source="([^"]+)"\s+data-relation="([^"]+)"\s+data-target="([^"]+)"\s+data-mentioned="([^"]+)"\s+class="semantic-relation"\s*/>'
)
```

**Step 2: Update edge tuple to include mentioned**

Change `unique_edges.add((match[0], match[1], match[2]))` to:
```python
unique_edges.add((match[0], match[1], match[2], match[3]))
```

**Step 3: Update edges_list to include mentioned**

```python
edges_list = [
    {"source": src, "relation": rel, "target": tgt, "mentioned": mentioned == "true"}
    for src, rel, tgt, mentioned in unique_edges
]
```

**Step 4: Rebuild and verify graph.json**

Run: `forester build && python aggregate_graph.py`
Expected: `graph.json` now contains `"mentioned": true` on each edge.

**Step 5: Commit**

```bash
git add aggregate_graph.py
git commit -m "feat: include 'mentioned' field in graph.json edges"
```

---

### Task 4: Define the tag format and update `concept-definition-researcher` skill

**Files:**
- Modify: `.claude/skills/concept-definition-researcher/SKILL.md`

**Step 1: Add tag instructions to the skill**

In the "Step 4: Generate `.tree` File" section, add `\meta{tags}{...}` to the file template, after `\import{base-macros}`:

```
\title{<Concept Title>}
\taxon{Definition}
\date{<YYYY-MM-DD>}
\author{<author-id>}
\import{base-macros}
\meta{tags}{tag1, tag2, tag3}
```

Add a guidance section explaining tags:

```markdown
### Tags

Add `\meta{tags}{...}` with a comma-separated list of category tags that describe what domains or topics this concept relates to. Tags help downstream relation-finding steps pair related concepts efficiently.

Choose tags from the concept's domain. For a machine learning paper, tags might include: `architecture`, `attention`, `training`, `optimization`, `evaluation`, `embedding`, `regularization`, `baseline`. For a finance book: `balance-sheet`, `income-statement`, `cash-flow`, `valuation`, `risk`, `accounting-policy`.

Use 2-5 tags per concept. Tags should be lowercase, hyphenated if multi-word.
```

**Step 2: Update the example to include tags**

Update the Self-Attention example to show:
```
\title{Self-Attention}
\taxon{Definition}
\date{2026-02-14}
\author{vaswani-et-al}
\import{base-macros}
\meta{tags}{attention, architecture, sequence-modeling}
```

**Step 3: Update the Required Input table to mention tags**

Add a note that tags are required in the output `.tree` file.

**Step 4: Commit**

```bash
git add .claude/skills/concept-definition-researcher/SKILL.md
git commit -m "feat: add tag requirement to concept-definition-researcher skill"
```

---

### Task 5: Create the `/find-concept-relations` slash command skill

**Files:**
- Create: `.claude/skills/find-concept-relations/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: find-concept-relations
description: Given a focus concept and a list of candidate related concepts, determine semantic relations between them. Use when finding relations for a single concept against its tag-matched candidates. Returns JSON to stdout for the orchestrator script to merge.
---

# Find Concept Relations

## Overview

Given one focus concept and a list of candidate related concepts (pre-filtered by shared tags), determine what semantic relations exist between the focus concept and each candidate. For each relation found, indicate whether it is explicitly mentioned in the source document.

## Slash Command Usage

/find-concept-relations focus-concept="..." focus-tree-id="..." candidates='[...]' document="..." ingestion-path="..." prefix="..."

## Required Input

| Argument | Description |
|----------|-------------|
| **focus-concept** | Name of the concept to find relations for |
| **focus-tree-id** | Tree ID of the focus concept (e.g., `006-multi-head-attention`) |
| **candidates** | JSON array of candidate concepts: `[{"name": "...", "tree_id": "..."}]` |
| **document** | Document name (folder under `intermediate/`) |
| **ingestion-path** | Path to ingestion markdown files |
| **prefix** | 3-digit prefix for tree IDs |

## Process

### Step 1: Read Ingestion Files

Read all `.md` files in the ingestion path. These provide the source text to determine whether relations are explicitly mentioned.

### Step 2: Reason About Relations

For each candidate concept, consider:
1. Is there a meaningful semantic relation between the focus concept and this candidate?
2. If yes, what is the relation type? Use the standard vocabulary (see below).
3. Is this relation explicitly stated or clearly implied in the source text (`mentioned: true`), or is it inferred from domain knowledge (`mentioned: false`)?

The focus concept is always the **source** of the relation. If the natural relation direction is reversed (the candidate acts on the focus), use a passive relation type or swap accordingly.

### Step 3: Output JSON

Print ONLY a JSON array to stdout. No other text, no explanations, no markdown formatting. The orchestrator script parses this directly.

```json
[
  {"source": "006-multi-head-attention", "relation": "is-composed-of", "target": "006-attention-head", "mentioned": true},
  {"source": "006-multi-head-attention", "relation": "uses", "target": "006-linear-projection", "mentioned": true}
]
```

If no relations are found for any candidate, return an empty array: `[]`

## Relation Type Vocabulary

Prefer these standard types. Domain-specific types are allowed when none of these fit.

| Category | Types |
|----------|-------|
| Compositional | `is-composed-of`, `contains`, `is-component-of`, `includes` |
| Hierarchical | `is-a`, `is-specialized-by`, `generalizes`, `is-generalized-by` |
| Causal | `enables`, `requires`, `is-required-for`, `is-consequence-of` |
| Usage | `uses`, `implements`, `defines`, `processes`, `generates` |
| Similarity | `is-also-known-as`, `is-an-instance-of` |
| Contrast | `contrasts-with`, `is-different-from`, `is-faster-than`, `is-advantageous-to` |
| Extension | `extends`, `is-derived-from`, `improves`, `is-replaced-by` |
| Dependency | `depends-on`, `supports` |

## Guidelines

- One concept pair can have multiple relations (e.g., A `uses` B AND A `requires` B)
- Be comprehensive but not trivial -- skip relations that are obvious consequences of other relations already captured
- `mentioned: true` means the source text explicitly states or strongly implies this relation
- `mentioned: false` means the relation is logically true based on domain knowledge but not stated in the text
- When in doubt about `mentioned`, default to `false`
```

**Step 2: Commit**

```bash
git add .claude/skills/find-concept-relations/SKILL.md
git commit -m "feat: add find-concept-relations slash command skill"
```

---

### Task 6: Write `find_relations.py` orchestrator script

**Files:**
- Create: `find_relations.py`

**Step 1: Write the script**

```python
#!/usr/bin/env python3
"""
Find semantic relations between concepts using Claude subagents.

Reads concept .tree files for tags, computes candidate pairs via tag overlap,
dispatches per-concept reasoning to Claude subagents, and merges results into
a single {prefix}-relations.tree file.

Usage:
    python find_relations.py <document-name>
    python find_relations.py <document-name> --dry-run
    python find_relations.py <document-name> --delay 5
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path


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
    for category, cat_concepts in master_registry["concepts"].items():
        for name, tree_id in cat_concepts.items():
            if tree_id not in concepts.values():
                concepts[name] = tree_id
    return concepts


def extract_tags_from_tree(tree_path: Path) -> list[str]:
    """Extract tags from \meta{tags}{...} in a .tree file."""
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

    # Reverse lookup: tree_id -> name
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


def call_subagent(
    focus_name: str,
    focus_tree_id: str,
    candidates: list[dict],
    document: str,
    ingestion_path: str,
    prefix: str,
    project_root: Path,
) -> list[dict]:
    """Call claude subagent to find relations for one concept."""
    candidates_json = json.dumps(candidates, ensure_ascii=False)
    prompt = (
        f'/find-concept-relations '
        f'focus-concept="{focus_name}" '
        f'focus-tree-id="{focus_tree_id}" '
        f"candidates='{candidates_json}' "
        f'document="{document}" '
        f'ingestion-path="{ingestion_path}" '
        f'prefix="{prefix}"'
    )

    result = subprocess.run(
        ["claude", "-p", prompt, "--verbose"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        return []

    # Extract JSON from stdout -- find the first [ and last ]
    stdout = result.stdout
    start = stdout.find("[")
    end = stdout.rfind("]")
    if start == -1 or end == -1:
        return []

    try:
        return json.loads(stdout[start : end + 1])
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
    prefix: str,
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
        # Comment with source concept name (use tree_id as fallback)
        lines.append(f"% {source_id}")
        for rel in sorted(source_rels, key=lambda r: r["relation"]):
            mentioned = "true" if rel.get("mentioned", True) else "false"
            lines.append(
                f"\\relation{{{rel['source']}}}{{{rel['relation']}}}{{{rel['target']}}}{{{mentioned}}}"
            )
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Find semantic relations between concepts using Claude subagents.",
    )
    parser.add_argument("document", help="Document name (folder under intermediate/)")
    parser.add_argument("--delay", type=float, default=2, help="Seconds between API calls (default: 2)")
    parser.add_argument("--dry-run", action="store_true", help="Show candidate pairs without calling Claude")
    args = parser.parse_args()

    project_root = Path(__file__).parent.resolve()
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
        print("Untagged concepts:")
        id_to_name = {v: k for k, v in concepts.items()}
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

    # Process each concept
    all_relations = []
    succeeded = 0
    failed = 0

    for i, (name, tree_id, candidates) in enumerate(work_items, 1):
        print(f"[{i}/{len(work_items)}] {name} ({len(candidates)} candidates)")

        try:
            relations = call_subagent(
                focus_name=name,
                focus_tree_id=tree_id,
                candidates=candidates,
                document=args.document,
                ingestion_path=str(ingestion_path),
                prefix=prefix,
                project_root=project_root,
            )
            print(f"  -> {len(relations)} relations found")
            all_relations.extend(relations)
            succeeded += 1
        except subprocess.TimeoutExpired:
            print(f"  -> Timeout")
            failed += 1
        except Exception as e:
            print(f"  -> Error: {e}")
            failed += 1

        if i < len(work_items):
            time.sleep(args.delay)

    # Deduplicate and write output
    unique_relations = deduplicate_relations(all_relations)
    output_path = trees_path / f"{prefix}-relations.tree"
    write_relations_tree(unique_relations, output_path, meta["title"], author_id, prefix)

    print()
    print("=" * 40)
    print(f"Succeeded:    {succeeded}/{len(work_items)} concepts")
    print(f"Failed:       {failed}")
    print(f"Relations:    {len(unique_relations)} (deduplicated from {len(all_relations)})")
    print(f"Output:       {output_path}")


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add find_relations.py
git commit -m "feat: add find_relations.py orchestrator for relation discovery"
```

---

### Task 7: Create the `/find-relations` runner skill

**Files:**
- Create: `.claude/skills/find-relations/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: find-relations
description: Run the relation-finding pipeline, which discovers semantic relations between concepts using tag-based filtering and Claude subagents. Use when the user wants to run Step 3.2 of the pipeline, find relations between concepts, build the relations tree, or says things like "find relations", "discover connections", "build relation graph", or "run find_relations".
disable-model-invocation: true
---

# Find Relations

## Overview

This skill runs `find_relations.py` to discover semantic relations between concepts. It reads concept `.tree` files for tags, finds candidate pairs via tag overlap, and dispatches reasoning to Claude subagents.

## Required Input

The user must provide the **document name** (folder under `intermediate/`).

If not specified, list available documents under `intermediate/` and ask.

## Process

### Step 1: Verify Prerequisites

Check that the document has completed prior steps:

1. `intermediate/<document>/ingestion/meta.json` exists with a `prefix` field
2. `intermediate/<document>/structural-analysis/<prefix>_master_registry.json` exists
3. Concept `.tree` files exist in `intermediate/<document>/trees/`

### Step 2: Dry Run

Always do a dry run first:

    python find_relations.py <document-name> --dry-run

Show the user the output and confirm they want to proceed.

### Step 3: Run the Script

    python find_relations.py <document-name>

### Step 4: Report Results

Report total relations found, any failed concepts, and the output file path.
```

**Step 2: Commit**

```bash
git add .claude/skills/find-relations/SKILL.md
git commit -m "feat: add find-relations runner skill"
```

---

### Task 8: Test the full pipeline on a small subset

**Step 1: Manually add tags to 3-5 existing concept .tree files in `intermediate/attention-is-all-you-need/trees/`**

Pick related concepts (e.g., `006-multi-head-attention.tree`, `006-scaled-dot-product-attention.tree`, `006-query.tree`, `006-key.tree`, `006-value.tree`) and add `\meta{tags}{attention, computation}` to each.

**Step 2: Run dry run**

Run: `python find_relations.py attention-is-all-you-need --dry-run`
Expected: Shows the tagged concepts and their candidate pairs.

**Step 3: Run on the small subset**

Run: `python find_relations.py attention-is-all-you-need`
Expected: Produces `intermediate/attention-is-all-you-need/trees/006-relations.tree` with relations between the tagged concepts.

**Step 4: Verify output format**

Check the output file contains valid `\relation{src}{type}{tgt}{true/false}` lines.

**Step 5: Verify forester build**

Run: `forester build 2>&1 | tail -5`
Expected: Clean build.

**Step 6: Commit test tags and results**

```bash
git add intermediate/attention-is-all-you-need/trees/
git commit -m "test: verify relation pipeline with small concept subset"
```
