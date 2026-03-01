---
name: concept-registry
description: Scan ingestion markdown files to identify and catalog all concepts that need definitions, producing a structured registry of concept names and tree IDs. Use this skill when the user wants to run Step 2 of the pipeline, extract concepts from ingested text, build a concept registry, catalog definitions, or says things like "find all concepts", "what needs defining", "create the registry", or "run structural analysis". Also triggers when the user has just finished ingestion and wants to identify what concepts exist in the document.
---

# Concept Registry

## Overview

This skill is Step 2 of the Paper-to-Forester pipeline. It reads the chunked markdown files produced by Step 1 (Ingestion) and identifies every concept that needs a definition. The output is a structured registry -- a catalog of concept names mapped to tree IDs, organized by category.

This skill does NOT write definitions. It answers the question: "What concepts exist in this document and need to be defined?" A separate downstream skill handles retrieving and writing the actual definition content.

## Input

- Chunked markdown files in `intermediate/{document-name}/ingestion/`
- `meta.json` from the same directory (for prefix and metadata)

**Before starting, check that `meta.json` contains a `prefix` field.** If it doesn't, ask the user to provide one.

## Output

All output goes into `intermediate/{document-name}/structural-analysis/`:

```
intermediate/{document-name}/structural-analysis/
  {prefix}_01_{section}_registry.json
  {prefix}_02_{section}_registry.json
  ...
  {prefix}_master_registry.json
```

## Process

### Step 1: Load Context

Read `meta.json` to get the prefix, title, and other metadata. Then list all `.md` files in the ingestion directory to know which sections to process.

### Step 2: Scan Each Section

Read each ingestion markdown file and identify every concept that would need a definition. A "concept" is any term, technique, model, component, metric, or domain-specific idea that a reader would benefit from having defined.

**What counts as a concept:**
- Named architectures, models, or systems (e.g., "Transformer", "LSTM")
- Mechanisms and techniques (e.g., "Self-Attention", "Dropout")
- Components and building blocks (e.g., "Encoder", "Positional Encoding")
- Metrics and evaluation methods (e.g., "BLEU Score", "Perplexity")
- Mathematical constructs with names (e.g., "Softmax", "Cross-Entropy")
- Hyperparameters and configuration choices (e.g., "Learning Rate Schedule", "Warmup Steps")
- Domain-specific terminology that isn't everyday language

**What does NOT count:**
- Common English words or phrases that any reader would know
- Basic undergraduate-level concepts (unless the document treats them as key terms)
- Section titles or headings themselves (they organize content, they aren't concepts)
- Proper nouns that are just citations (e.g., "Bahdanau et al." is not a concept, but "Bahdanau Attention" is)

**Prerequisite concepts:** Also identify domain-specific terms the text *uses without defining*. These are concepts the reader needs to understand but the document assumes as background knowledge. Include them in the registry alongside concepts the document does define -- downstream skills will handle retrieving definitions for them.

For each concept found, assign a tree ID using the format `{prefix}-{concept-slug}`, where `concept-slug` is the concept name in lowercase with hyphens replacing spaces (e.g., `006-multi-head-attention`).

### Step 3: Write Per-Section Registry Files

For each ingestion markdown file, write a registry JSON file:

**Filename:** `{prefix}_{section-number}_{section-name}_registry.json`

Match the section number and name from the ingestion file. For example, `04_attention.md` produces `006_04_attention_registry.json`.

**Format:**

```json
{
  "prefix": "006",
  "source_file": "04_attention.md",
  "section": "Attention",
  "concepts": {
    "Scaled Dot-Product Attention": "006-scaled-dot-product-attention",
    "Query": "006-query",
    "Key": "006-key",
    "Value": "006-value",
    "Multi-Head Attention": "006-multi-head-attention"
  }
}
```

The `section` field should be the human-readable section title (from the markdown heading), not the filename.

### Step 4: Write the Master Registry

Consolidate all per-section concepts into a single master file: `{prefix}_master_registry.json`.

**Format:**

```json
{
  "prefix": "006",
  "title": "Document Title - Master Registry",
  "description": "Consolidated concept dictionary. Human checkpoint: review and remove trivial terms, rename IDs if needed.",
  "total_concepts": 96,
  "sections": {
    "01_introduction": {
      "file": "006_01_introduction_registry.json",
      "concept_count": 12
    },
    "02_background": {
      "file": "006_02_background_registry.json",
      "concept_count": 10
    }
  },
  "concepts": {
    "Category Name": {
      "Concept Name": "prefix-concept-slug",
      "Another Concept": "prefix-another-concept"
    },
    "Another Category": {
      "Yet Another Concept": "prefix-yet-another-concept"
    }
  }
}
```

The `concepts` object groups concepts by category. Categories are your judgment call based on the document's subject matter. For a machine learning paper, categories might be "Core Architecture", "Attention Mechanisms", "Training", "Evaluation". For a finance book, they might be "Financial Statements", "Valuation Methods", "Risk Indicators". Choose categories that help a reader quickly find related concepts.

**Deduplication:** A concept that appears in multiple sections should appear only once in the master registry's `concepts` object (under whichever category fits best). The per-section files may have overlapping concepts -- that's fine, they reflect what each section discusses. The master registry is the deduplicated, organized view.

### Step 5: Present for Review

After writing all files, present a summary to the user:
- Total concept count
- Category breakdown (category name and count)
- Any concepts you're uncertain about (borderline between "real concept" and "common term")

The description field in the master registry says "Human checkpoint" for a reason -- the user should review the list and remove anything trivial or rename IDs before proceeding to downstream steps. Invite them to do so.

## Judgment Calls

**Granularity:** Err on the side of including too many concepts rather than too few. It's easier for the user to remove a trivial term than to notice a missing one later. If you're unsure whether something is a "concept" or just a common term, include it and flag it in your summary.

**Concept naming:** Use the most specific common name. "Multi-Head Attention" is better than "Attention" (too vague) or "The Multi-Head Attention Mechanism Used in the Transformer" (too verbose). Match the terminology the document uses.

**Synonyms:** If the document uses two names for the same thing (e.g., "Self-Attention" and "Intra-Attention"), list both in the per-section file where they appear, but they can share the same tree ID or have separate IDs -- use your judgment. If they are truly synonymous, giving them separate IDs and noting both is fine; downstream steps will handle merging if needed.

**Prerequisites vs. in-document concepts:** Don't try to separate these into different files or mark them differently in the registry. They're all just concepts that need definitions. The distinction matters for how the definition gets written (extracted from the text vs. looked up externally), but that's not this skill's concern.

## Example

Given `intermediate/attention-is-all-you-need/ingestion/` with 11 markdown files and a `meta.json` with `"prefix": "006"`, this skill produces:

```
intermediate/attention-is-all-you-need/structural-analysis/
  006_01_introduction_registry.json
  006_02_background_registry.json
  006_03_model-architecture_registry.json
  ...
  006_11_summary_registry.json
  006_master_registry.json
```

The master registry organizes ~96 concepts into categories like "Core Architecture", "Attention Mechanisms", "Network Components", "Training", "Evaluation", etc.

## Pipeline Continuation

This is **Step 2** of the Forester pipeline. After the user reviews and approves the registry, the ONLY next step is:

**Step 3.1: Research Concepts** -- Use `/research-concepts` (or `python .claude/skills/research-concepts/research_concepts.py <document>`) to iterate through the registry and generate `.tree` definition files for each concept.

Do NOT skip ahead to relation finding, chapter indices, or the paper index. Concept definitions must exist before any of those steps can work.
