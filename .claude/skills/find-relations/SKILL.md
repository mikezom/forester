---
name: find-relations
description: Run the relation-finding pipeline, which discovers semantic relations between concepts using tag-based filtering and Claude subagents, producing a relations .tree file. Use when the user wants to run Step 3.2 of the pipeline, find relations between concepts, build the relations tree, or says things like "find relations", "discover connections", "build relation graph", or "run find_relations". Triggers after concept definition research is complete and .tree files have tags.
disable-model-invocation: true
---

# Find Relations

## Overview

This skill runs `find_relations.py` (located at `.claude/skills/find-relations/find_relations.py`) to discover semantic relations between concepts. It reads concept `.tree` files for tags, finds candidate pairs via tag overlap, and dispatches reasoning to Claude subagents.

## Required Input

The user must provide the **document name** -- the folder name under `intermediate/`. For example: `attention-is-all-you-need` or `手把手教你读财报`.

If the user doesn't specify a document name, list the available documents by checking which folders exist under `intermediate/` and ask them to pick one.

## Process

### Step 1: Verify Prerequisites

Before running the script, confirm that the document has completed prior steps:

1. `intermediate/<document>/ingestion/meta.json` exists and has a `prefix` field
2. `intermediate/<document>/structural-analysis/<prefix>_master_registry.json` exists
3. Concept `.tree` files exist in `intermediate/<document>/trees/` and have `\meta{tags}{...}`

If concept `.tree` files exist but lack tags, warn the user that untagged concepts will be skipped and suggest re-running the concept definition research with the updated skill.

### Step 2: Dry Run

Always do a dry run first so the user can see what will be processed:

```bash
python .claude/skills/find-relations/find_relations.py <document-name> --dry-run
```

Show the user the output (tagged/untagged counts, concepts with candidates, total pairs) and confirm they want to proceed.

### Step 3: Run the Script

Run the script with appropriate arguments:

```bash
python .claude/skills/find-relations/find_relations.py <document-name>
```

The script runs sequentially with a 2-second delay between calls by default. If the user wants a different delay:

```bash
python .claude/skills/find-relations/find_relations.py <document-name> --delay <seconds>
```

### Step 4: Report Results

After the script finishes, report:
- How many concepts were processed successfully
- How many relations were found (before and after deduplication)
- How many failed (and which ones)
- The output file path

If there are failures, the user can re-run the script -- but note that unlike `research_concepts.py` (`.claude/skills/research-concepts/research_concepts.py`), this script regenerates the full relations file each time (it doesn't skip previously processed concepts).

## Pipeline Continuation

This is **Step 3.2** of the Forester pipeline. After relations are found, check whether chapter indices (Step 3.3) are done:

- If chapter indices are NOT yet generated: **Step 3.3: Generate Chapter Indices** -- Use `/generate-chapter-index` per chapter.
- If chapter indices ARE already done: **Step 3.4: Generate Paper Index** -- Use `/generate-paper-index`.

Do NOT skip ahead to Step 4 (validation) until the paper index exists.
