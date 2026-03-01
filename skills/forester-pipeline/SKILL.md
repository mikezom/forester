---
name: forester-pipeline
description: Orchestrate the Paper-to-Forester pipeline that transforms documents into knowledge graphs. Use whenever the user mentions the pipeline, wants to process a document end-to-end, asks "what's next", checks pipeline status, or references any pipeline step by number (Step 1, Step 2, etc.). Also triggers when the user wants to ingest a new paper, create a knowledge graph from a document, or says things like "run the pipeline", "process this paper", "what step am I on", or "pipeline status". This skill should be consulted before any individual pipeline skill to ensure correct ordering.
---

# Forester Pipeline Orchestrator

## Overview

This skill orchestrates the 7-step pipeline that transforms a source document into a Forester knowledge graph. It detects pipeline state from filesystem artifacts, routes to the correct next step, and prevents skipping.

<HARD-GATE>
Do NOT invoke a later pipeline step before confirming all prior steps are complete.
The pipeline is strictly sequential -- each step produces artifacts that subsequent steps require.
Skipping a step means the next step will fail or produce garbage output.
</HARD-GATE>

## Pipeline Steps

```
Step 1: paper-ingestion          → meta.json + chunked markdown
Step 2: concept-registry         → per-section + master registry JSONs
Step 3.1: research-concepts      → concept .tree definition files (with tags)
Step 3.2: find-relations         → relations .tree file
Step 3.3: generate-chapter-index → per-chapter index .tree files
Step 3.4: generate-paper-index   → main document index .tree file
Step 4: validate-document        → person tree + validation report
```

## Process

### Step 1: Identify the Document

Ask the user which document they want to work on. If they haven't named one, list available documents:

```
ls intermediate/
```

If they're starting fresh with a new document, that means Step 1 (ingestion) is next.

### Step 2: Check Pipeline State

For the identified document, check which artifacts exist to determine the current pipeline state. Run these checks in order and stop at the first incomplete step:

| Step | Artifact Check | How to Verify |
|------|---------------|---------------|
| **1** | `intermediate/<doc>/ingestion/meta.json` exists with `prefix` field | Read the file |
| **1** | At least one `.md` file in `intermediate/<doc>/ingestion/` | Glob for `*.md` |
| **2** | `intermediate/<doc>/structural-analysis/<prefix>_master_registry.json` exists | Check file existence |
| **3.1** | Concept `.tree` files exist in `intermediate/<doc>/trees/` | Count `.tree` files matching prefix, compare to registry concept count |
| **3.2** | `intermediate/<doc>/trees/<prefix>-relations.tree` exists | Check file existence |
| **3.3** | Chapter index files `<prefix>-XX-index.tree` exist for each section | Match against registry sections |
| **3.4** | `intermediate/<doc>/trees/<prefix>-index.tree` exists | Check file existence |
| **4** | Person tree exists in `intermediate/<doc>/trees/person/` | Check file existence |

### Step 3: Report Status and Route

Present the pipeline status clearly:

```
=== Pipeline Status: <Document Title> ===
  [done] Step 1:   Ingestion (meta.json + 11 markdown files)
  [done] Step 2:   Concept Registry (96 concepts in master registry)
  [done] Step 3.1: Research Concepts (94/96 .tree files)
  [    ] Step 3.2: Find Relations
  [    ] Step 3.3: Generate Chapter Indices
  [    ] Step 3.4: Generate Paper Index
  [    ] Step 4:   Validation

  Next step: Step 3.2 -- Find Relations
```

Then guide the user to the next step. Provide the exact invocation:

| Next Step | Skill to Invoke | Invocation |
|-----------|----------------|------------|
| 1 | paper-ingestion | Use the paper-ingestion skill (auto-triggered) |
| 2 | concept-registry | Use the concept-registry skill (auto-triggered) |
| 3.1 | research-concepts | `/research-concepts` or `python .claude/skills/research-concepts/research_concepts.py <doc>` |
| 3.2 | find-relations | `/find-relations` or `python .claude/skills/find-relations/find_relations.py <doc>` |
| 3.3 | generate-chapter-index | `/generate-chapter-index chapter="XX" ...` (per chapter) |
| 3.4 | generate-paper-index | `/generate-paper-index document="<doc>" prefix="<prefix>" author-id="<id>"` |
| 4 | validate-document | `/validate-document document="<doc>" prefix="<prefix>" author-id="<id>"` |

### Step 3.3 Note: Per-Chapter Invocation

Step 3.3 (generate-chapter-index) must be invoked once per chapter. List all chapters from the master registry's `sections` field and provide the full invocation for each:

```
Chapters to generate:
  /generate-chapter-index chapter="01" chapter-title="Introduction" document="<doc>" prefix="<prefix>" author-id="<id>"
  /generate-chapter-index chapter="02" chapter-title="Background" document="<doc>" prefix="<prefix>" author-id="<id>"
  ... (one per section)
```

Track which chapter indices already exist and only list the remaining ones.

### Steps 3.2 and 3.3: Parallel-Safe

Steps 3.2 (find-relations) and 3.3 (generate-chapter-index) are independent -- they both depend on Step 3.1 but not on each other. Either can run first. However, Step 3.4 (generate-paper-index) needs Step 3.3 to be complete and benefits from Step 3.2 being complete (to include the relations section).

Recommended order: 3.1 → 3.2 → 3.3 → 3.4. But 3.1 → 3.3 → 3.2 → 3.4 is also valid.

## Data Flow Between Steps

This table maps what each step produces and what subsequent steps consume. Use it to verify that preconditions are met.

| Step | Produces | Consumed By |
|------|----------|-------------|
| **1** | `meta.json` (prefix, title, authors, abstract) | 2, 3.1, 3.2, 3.3, 3.4, 4 |
| **1** | `XX_section.md` ingestion files | 2, 3.3 |
| **2** | `<prefix>_XX_section_registry.json` | 3.1, 3.3 |
| **2** | `<prefix>_master_registry.json` | 3.1, 3.2, 3.3, 3.4, 4 |
| **3.1** | `<prefix>-<concept>.tree` files (with tags) | 3.2, 3.3, 3.4, 4 |
| **3.2** | `<prefix>-relations.tree` | 3.4, 4 |
| **3.3** | `<prefix>-XX-index.tree` per chapter | 3.4, 4 |
| **3.4** | `<prefix>-index.tree` | 4 |
| **4** | `person/<author-id>.tree` + validation report | (terminal) |

## Derived Parameters

Several parameters recur across steps. Derive them once from Step 1 output and pass them forward:

| Parameter | Source | Derivation |
|-----------|--------|------------|
| `document` | User or directory name | Kebab-case folder name under `intermediate/` |
| `prefix` | `meta.json` | 3-digit number, e.g., `006` |
| `author-id` | `meta.json` authors field | Single author: `lastname`. Multiple: `firstlast-et-al` |
| `ingestion-path` | Convention | `intermediate/<document>/ingestion/` |

## Human Checkpoints

The pipeline has natural review points where the user should confirm before proceeding:

| After Step | Review | Why |
|------------|--------|-----|
| **2** | Review master registry | Remove trivial concepts, fix IDs, adjust categories before generating 96+ tree files |
| **3.1** | Spot-check a few .tree files | Verify definition quality before bulk relation finding |
| **3.3** | Review a chapter index | Check narrative flow before generating the paper index |
| **4** | Review validation report | Fix errors before deploying to the forest |

At each checkpoint, present the review items and ask the user to confirm before proceeding to the next step.

## Anti-Rationalization

| Thought | Reality |
|---------|---------|
| "The user just wants the paper index, I can skip to Step 3.4" | Step 3.4 needs chapter indices from 3.3, which need concept trees from 3.1, which need the registry from Step 2, which needs ingestion from Step 1. Every step depends on prior outputs. |
| "The concept trees already exist from a previous run" | Check the filesystem. If they exist, the status check will mark Step 3.1 as done and route to the next incomplete step. |
| "I can generate the registry and tree files in one step" | Steps 2 and 3.1 are separate for a reason: the registry is a human checkpoint where the user reviews and prunes the concept list before committing to researching 96+ definitions. |
| "Validation can happen anytime" | Validation checks references and completeness. Running it before all tree files exist will produce false errors. Run it last. |
| "I'll just do a quick ingestion without meta.json" | Every downstream step reads meta.json for prefix, title, and authors. Without it, nothing works. |
| "The user said 'just validate', so I should skip to Step 4" | Check the status first. If prior steps are incomplete, tell the user what needs to happen first. |

## Pipeline Completion

When all steps show `[done]`, congratulate the user and suggest:

1. **Deploy to forest**: Copy trees from `intermediate/<doc>/trees/` to `trees/<prefix>-<doc>/`
2. **Build the forest**: Run `forester build` to generate the site
3. **Review the graph**: Run `python aggregate_graph.py` to generate the relation graph JSON

## Example Session

```
User: "I want to process this paper about attention mechanisms"

Pipeline: Check intermediate/ → no folder exists → Step 1 is next

  === Pipeline Status: (new document) ===
    [    ] Step 1:   Ingestion
    [    ] Step 2:   Concept Registry
    [    ] Step 3.1: Research Concepts
    [    ] Step 3.2: Find Relations
    [    ] Step 3.3: Generate Chapter Indices
    [    ] Step 3.4: Generate Paper Index
    [    ] Step 4:   Validation

  Next step: Step 1 -- Ingestion
  Use the paper-ingestion skill to extract and chunk the document.

User: (completes ingestion)

Pipeline: meta.json exists, markdown files exist → Step 2 is next

  === Pipeline Status: Attention Is All You Need ===
    [done] Step 1:   Ingestion (meta.json + 11 files)
    [    ] Step 2:   Concept Registry
    ...

  Next step: Step 2 -- Concept Registry
  Use the concept-registry skill to identify all concepts.

(continues step by step...)
```
