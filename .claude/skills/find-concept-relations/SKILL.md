---
name: find-concept-relations
description: Given a focus concept and a list of candidate related concepts, determine semantic relations between them by reading the source document. Use when finding relations for a single concept against its tag-matched candidates. Returns JSON to stdout for the orchestrator script to merge. This skill is called by find_relations.py and should not normally be invoked manually.
---

# Find Concept Relations

## Overview

Given one focus concept and a list of candidate related concepts (pre-filtered by shared tags), determine what semantic relations exist between the focus concept and each candidate. For each relation found, indicate whether it is explicitly mentioned in the source document.

## Slash Command Usage

```
/find-concept-relations focus-concept="Multi-Head Attention" focus-tree-id="006-multi-head-attention" candidates='[{"name": "Scaled Dot-Product Attention", "tree_id": "006-scaled-dot-product-attention"}]' document="attention-is-all-you-need" ingestion-path="intermediate/attention-is-all-you-need/ingestion/" prefix="006"
```

All arguments are key="value" pairs. When invoked this way, use the provided values directly.

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

1. **Is there a meaningful semantic relation between the focus concept and this candidate?** Not every pair of concepts that share a tag are related. Only emit a relation if there is a genuine semantic connection.

2. **What is the relation type?** Use the standard vocabulary below. Pick the most specific type that fits. If no standard type captures the relationship well, use a descriptive hyphenated label (e.g., `prevents-attention-to`).

3. **Is this relation explicitly mentioned in the source text?**
   - `mentioned: true` -- the source text explicitly states or clearly implies this relationship (e.g., "Multi-Head Attention is composed of multiple attention heads")
   - `mentioned: false` -- the relation is logically true based on domain knowledge but is not stated in the source text

The focus concept is always the **source** of the relation. If the natural direction is reversed (the candidate acts on the focus), express it from the focus concept's perspective (e.g., use `requires` instead of `enables`, or use `is-component-of` instead of `contains`).

One concept pair can have multiple relations if genuinely warranted. But avoid redundant relations that are obvious consequences of others already captured.

### Step 3: Output JSON

Print ONLY a valid JSON array to stdout. No other text, no explanations, no markdown fencing, no preamble. The orchestrator script parses this directly.

```json
[
  {"source": "006-multi-head-attention", "relation": "is-composed-of", "target": "006-attention-head", "mentioned": true},
  {"source": "006-multi-head-attention", "relation": "uses", "target": "006-linear-projection", "mentioned": true},
  {"source": "006-multi-head-attention", "relation": "enables", "target": "006-parallelization", "mentioned": false}
]
```

If no relations exist for any candidate, return an empty array: `[]`

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

- Be comprehensive: if a plausible relation exists, include it
- But not trivial: skip relations that are obvious consequences of others you already listed
- `mentioned: true` means the source text explicitly states or strongly implies this connection
- `mentioned: false` means the relation is logically true from domain knowledge but not in the text
- When in doubt about `mentioned`, default to `false`
- The output MUST be valid JSON -- no trailing commas, proper quoting
- Do NOT wrap the JSON in markdown code fences or add any text before/after it
