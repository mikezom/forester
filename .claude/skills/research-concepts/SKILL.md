---
name: research-concepts
description: Run the concept definition research pipeline, which iterates through a document's concept registry and uses Claude subagents to research and write .tree definition files for each concept. Use this skill when the user wants to run Step 3 of the pipeline, research all concept definitions, generate tree files from the registry, or says things like "research definitions", "generate tree files", "run research_concepts", or "define all concepts". Triggers after Step 2 (concept-registry) is complete.
disable-model-invocation: true
---

# Research Concepts

## Overview

This skill runs `research_concepts.py` (located at `.claude/skills/research-concepts/research_concepts.py`) to iterate through the concept registry produced by Step 2 and research a definition for each concept. It spawns a Claude subagent per concept using the `/concept-definition-researcher` slash command.

## Required Input

The user must provide the **document name** -- the folder name under `intermediate/`. For example: `attention-is-all-you-need` or `手把手教你读财报`.

If the user doesn't specify a document name, list the available documents by checking which folders exist under `intermediate/` and ask them to pick one.

## Process

### Step 1: Verify Prerequisites

Before running the script, confirm that the document has completed Steps 1 and 2:

1. Check that `intermediate/<document>/ingestion/meta.json` exists and has a `prefix` field
2. Check that `intermediate/<document>/structural-analysis/<prefix>_master_registry.json` exists

If either is missing, tell the user which step needs to run first.

### Step 2: Dry Run

Always do a dry run first so the user can see what will be processed:

```bash
python .claude/skills/research-concepts/research_concepts.py <document-name> --dry-run
```

Show the user the output (total concepts, how many already have .tree files, how many will be processed) and confirm they want to proceed.

### Step 3: Run the Script

Run the script with appropriate arguments:

```bash
python .claude/skills/research-concepts/research_concepts.py <document-name>
```

The script runs sequentially with a 2-second delay between calls by default. If the user wants a different delay:

```bash
python .claude/skills/research-concepts/research_concepts.py <document-name> --delay <seconds>
```

### Step 4: Report Results

After the script finishes, report:
- How many concepts succeeded
- How many failed (and which ones)
- How many were skipped (already had .tree files)

If there are failures, the user can re-run the script -- it will skip already-completed concepts and retry the failed ones.

## Pipeline Continuation

This is **Step 3.1** of the Forester pipeline. After concept research completes, the next steps are:

**Step 3.2: Find Relations** -- Use `/find-relations` (or `python .claude/skills/find-relations/find_relations.py <document>`) to discover semantic relations between concepts using tag-based filtering.

**Step 3.3: Generate Chapter Indices** -- Use `/generate-chapter-index` per chapter to create chapter-level index files.

Steps 3.2 and 3.3 are independent of each other (both depend on 3.1 but not on each other). Recommended order: 3.2 first, then 3.3. Do NOT skip ahead to Step 3.4 (paper index) or Step 4 (validation) -- they require outputs from 3.2 and 3.3.
