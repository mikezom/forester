---
name: generate-chapter-index
description: Given a document chapter, generate a Forester chapter index .tree file that weaves narrative text with concept transclusions. Use when generating chapter-level index files for Step 3.3 of the pipeline, building chapter summaries, creating section overviews, or when the user says "generate chapter index", "create chapter indices", or "build section index".
---

# Generate Chapter Index

## Overview

Given a specific chapter from a document, generate a Forester `.tree` index file that retells the chapter's narrative while embedding concept definitions via `\transclude{}` and cross-referencing related concepts via links. The index follows the source text's flow, transforming it from linear prose into a structured knowledge document.

## Slash Command Usage

```
/generate-chapter-index chapter="01" chapter-title="Introduction" document="attention-is-all-you-need" prefix="006" author-id="vaswani-et-al"
```

All arguments are key="value" pairs. When invoked this way, use the provided values directly.

## Required Input

| Argument | Description |
|----------|-------------|
| **chapter** | Chapter number as 2-digit string (e.g., `01`, `02`, `10`) |
| **chapter-title** | Human-readable chapter title (e.g., `Introduction`, `Model Architecture`) |
| **document** | Document name (folder under `intermediate/`) |
| **prefix** | 3-digit prefix for tree IDs (e.g., `006`) |
| **author-id** | Author identifier (e.g., `vaswani-et-al`) |

## Process

### Step 1: Gather Context

Read these files to understand the chapter and its concepts:

1. **Ingestion markdown**: `intermediate/<document>/ingestion/<chapter>_*.md`
   - This is the source narrative. The index should follow its flow.

2. **Section registry** (if it exists): `intermediate/<document>/structural-analysis/<prefix>_<chapter>_*_registry.json`
   - Lists concepts that belong to this chapter with their tree IDs.

3. **Concept tree files**: scan `intermediate/<document>/trees/` for `.tree` files matching tree IDs from the registry
   - Check both flat (`trees/<id>.tree`) and chapter subfolder (`trees/<chapter>-<section-name>/<id>.tree`) layouts.
   - Note which concepts have existing `.tree` files (these can be transcluded).

4. **Master registry**: `intermediate/<document>/structural-analysis/<prefix>_master_registry.json`
   - For cross-referencing concepts defined in other chapters.

### Step 2: Plan the Index Structure

Before writing, plan how to organize the chapter index:

1. **Identify concepts to transclude**: Concepts from the section registry that have `.tree` files in this chapter's folder. These are the definitions that should appear inline.

2. **Identify concepts to link**: Concepts mentioned in the source text but defined in other chapters. These get `[concept name](tree-id)` links.

3. **Identify narrative segments**: The connecting prose between concept definitions that tells the chapter's story. These become `\p{}` paragraphs.

4. **Identify remarks**: Side observations, comparisons, interesting tangents, or commentary that enriches but isn't part of the main narrative. These go in `\aside{}`.

### Step 3: Write the Chapter Index

**Output path:** `intermediate/<document>/trees/<chapter>-<section-slug>/<prefix>-<chapter>-index.tree`

Where `<section-slug>` is the chapter title in kebab-case (e.g., `introduction`, `model-architecture`).

Use this structure:

```
\title{<Chapter Title>}
\taxon{Reference}
\date{<YYYY-MM-DD>}
\author{<author-id>}
\import{base-macros}

\p{
  Opening narrative from the source text, retold concisely. Link concepts
  on first mention: [concept name](tree-id). Follow the source text's
  logical flow.
}

\transclude{<prefix>-<concept-slug>}

\p{
  Continuing narrative connecting to the next concept or elaborating
  on what was just defined. This is regular prose, not a remark.
}

\aside{
  Side observation or interesting tangent that adds context but isn't
  essential to the main argument.
}

\transclude{<prefix>-<another-concept>}

\p{
  Further narrative...
}
```

### Writing Guidelines

**Narrative flow with `\p{}`:**
- Follow the source text's order and logic, but rewrite for conciseness and clarity.
- Use `\p{}` for all main narrative text: introductions, explanations, transitions between concepts, conclusions.
- Include mathematical formulas where they help explain the concepts: `#{...}` for inline, `##{...}` for block.
- Multiple `\p{}` blocks can appear consecutively to break up long passages.

**Concept transclusion with `\transclude{}`:**
- Use `\transclude{<tree-id>}` for concepts that have `.tree` files and are defined/explained in this chapter.
- Do NOT add `\p{\strong{Concept Title}}` before `\transclude{}`. The transclude macro automatically includes the title.
- Place the transclusion at the natural point in the narrative where the source text introduces or defines the concept.
- If the source text has a subsection heading like "Scaled Dot-Product Attention" followed by its explanation, use `\p{\strong{Scaled Dot-Product Attention}}` as a section header, then `\transclude{prefix-scaled-dot-product-attention}` for the definition, then continuing narrative in `\p{}`.

**Concept linking with `[name](tree-id)`:**
- Link a concept on its first mention in the chapter: `[Self-Attention](006-self-attention)`.
- After the first mention, use plain text (no repeated links).
- Link concepts defined in other chapters using their tree IDs from the master registry.

**Remarks with `\aside{}`:**
- Use `\aside{}` for side commentary, observations, or tangential information that enriches understanding but isn't part of the main argument.
- Examples of appropriate `\aside{}` content:
  - Historical context or origin of a technique
  - Comparison with alternative approaches not discussed in the main text
  - Practical implications or implementation notes
  - Caveats or limitations worth noting
- Do NOT use `\aside{}` as transition/conjunction text between concepts. Transitions belong in regular `\p{}` paragraphs.

**Lists and tables:**
- Use `\ol{}` / `\ul{}` with `\li{}` for lists.
- Use `\table{}` with `\tr{}`, `\th{}`, `\td{}` for tables. Never use LaTeX array environments.

### Step 4: Verify Output

Before finalizing, check:

1. Every concept from the section registry is either transcluded or linked
2. No `\transclude{}` references point to non-existent `.tree` files
3. All `%` signs are escaped as `\%`
4. All body text is inside `\p{}`, `\aside{}`, or list/table macros
5. No bare markdown formatting (`**bold**` or `*italic*`) -- use `\strong{}` and `\em{}`
6. No LaTeX math delimiters (`$...$`) -- use `#{...}` and `##{...}`
7. The narrative flows naturally when read top-to-bottom
8. `\aside{}` is only used for remarks, not for transitions

Print the full content of the generated `.tree` file and its path.

## .tree Syntax Quick Reference

| Element | Syntax | Notes |
|---------|--------|-------|
| Title | `\title{Title Text}` | Required |
| Taxon | `\taxon{Reference}` | Always `Reference` for index files |
| Date | `\date{YYYY-MM-DD}` | Today's date |
| Author | `\author{author-id}` | Required |
| Import | `\import{base-macros}` | Always include |
| Paragraph | `\p{ content }` | All narrative text |
| Aside/Remark | `\aside{ remark }` | Side commentary only |
| Bold | `\strong{text}` | NOT `**text**` |
| Emphasis | `\em{text}` | NOT `*text*` |
| Inline math | `#{formula}` | NOT `$formula$` |
| Block math | `##{formula}` | NOT `$$formula$$` |
| Link | `[text](tree-id)` | First mention of cross-chapter concepts |
| Transclude | `\transclude{tree-id}` | Inline concept definition |
| Unordered list | `\ul{ \li{item} }` | |
| Ordered list | `\ol{ \li{item} }` | |
| Table | `\table{ \tr{ \th{h} } \tr{ \td{d} } }` | NOT LaTeX arrays |
| Escape percent | `\%` | Never bare `%` |
| Highlight | `\mark{text}` | Key insights |

## Example

**Input:** chapter=`04`, chapter-title=`Attention`, document=`attention-is-all-you-need`, prefix=`006`

**Section registry concepts:** Scaled Dot-Product Attention, Multi-Head Attention, Additive Attention, Dot-Product Attention, Query, Key, Value, Attention Head, etc.

**Output:** `intermediate/attention-is-all-you-need/trees/04-attention/006-04-index.tree`

```
\title{Attention}
\taxon{Reference}
\date{2026-02-28}
\author{vaswani-et-al}
\import{base-macros}

\p{
  An [attention mechanism](006-attention-mechanism) can be described as mapping
  a [query](006-query) and a set of [key-value](006-key) pairs to an output,
  where the query, keys, [values](006-value), and output are all vectors. The
  output is computed as a weighted sum of the values, where the weight assigned
  to each value is computed by a compatibility function of the query with the
  corresponding key.
}

\p{
  \strong{Scaled Dot-Product Attention}
}

\transclude{006-scaled-dot-product-attention}

\p{
  In practice, we compute the attention function on a set of queries
  simultaneously, packed together into a matrix #{Q}. The keys and values
  are also packed together into matrices #{K} and #{V}:
  ##{
    \text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
  }
}

\aside{
  While [additive attention](006-additive-attention) and
  [dot-product attention](006-dot-product-attention) are similar in theoretical
  complexity, dot-product attention is faster in practice due to optimized
  matrix multiplication. The scaling factor #{\frac{1}{\sqrt{d_k}}} prevents
  large dot products from pushing [softmax](006-softmax) into regions with
  vanishing gradients.
}

\p{
  \strong{Multi-Head Attention}
}

\transclude{006-multi-head-attention}

\p{
  Multi-head attention allows the model to jointly attend to information from
  different [representation subspaces](006-representation-subspace) at
  different positions.
}

\p{
  \strong{Applications of Attention in Our Model}
}

\p{
  The Transformer uses multi-head attention in three different ways:
}

\ol{
  \li{\strong{[Encoder-decoder attention](006-encoder-decoder-attention)}:
    Queries come from the previous decoder layer, keys and values from the
    encoder output.}
  \li{\strong{[Encoder self-attention](006-encoder-self-attention)}:
    All keys, values, and queries come from the encoder's previous layer.}
  \li{\strong{[Decoder self-attention](006-decoder-self-attention)}:
    Self-attention in the decoder, with masking to prevent leftward
    information flow.}
}
```

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `\aside{Transition to next concept...}` | `\p{Transition to next concept...}` |
| `\p{\strong{Title}} \transclude{id}` | `\transclude{id}` (title is automatic) |
| `$x^2$` for math | `#{x^2}` |
| `**bold text**` | `\strong{bold text}` |
| `\taxon{reference}` | `\taxon{Reference}` |
| Bare `%` in text | `\%` |
| `\begin{array}...` | `\table{ \tr{ \td{} } }` |
| Text outside `\p{}` | Wrap in `\p{ ... }` |
| Linking every mention | Link only first mention per chapter |

Note: The one exception to "no title before transclude" is when the source text uses explicit subsection headers (like "Scaled Dot-Product Attention" as a section heading). In that case, use `\p{\strong{Subsection Title}}` as a visual section divider, followed by `\transclude{}` for the concept definition. This mirrors the source text's structure.

## Pipeline Continuation

This is **Step 3.3** of the Forester pipeline. This skill generates ONE chapter index at a time. After generating all chapter indices, check whether relations (Step 3.2) are done:

- If relations are NOT yet generated: **Step 3.2: Find Relations** -- Use `/find-relations`.
- If relations ARE already done: **Step 3.4: Generate Paper Index** -- Use `/generate-paper-index`.

Do NOT skip ahead to Step 4 (validation) until the paper index exists.
