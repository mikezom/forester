---
name: concept-definition-researcher
description: Use when given a concept name to find its definition in intermediate ingestion markdown files and generate a Forester .tree definition file. Triggers include single-concept lookup, definition tree generation, and Step 3.1 of the forester pipeline.
---

# Concept Definition Researcher

## Overview

Given a concept name, search the document's intermediate ingestion files for its definition, then produce a single Forester `.tree` file with `\taxon{Definition}`. If ingestion files lack a clear definition, search the Internet and cite the source.

## Slash Command Usage

This skill can be invoked as `/concept-definition-researcher` with arguments:

```
/concept-definition-researcher concept="Self-Attention" document="attention-is-all-you-need" prefix="006" author-id="vaswani-et-al" ingestion-path="intermediate/attention-is-all-you-need/ingestion/"
```

All arguments are key="value" pairs. When invoked this way, use the provided values directly instead of asking the user.

## Required Input

| Argument | Example | Source |
|----------|---------|--------|
| **concept** | `Nash Equilibrium` | User-provided |
| **document** | `attention-is-all-you-need` | Folder name under `intermediate/` |
| **prefix** | `006` | From `meta.json` or user-provided |
| **author-id** | `vaswani-et-al` | From existing `.tree` files or user-provided |
| **ingestion-path** | `intermediate/attention-is-all-you-need/ingestion/` | Path to the ingestion folder containing markdown files and meta.json |

## Process

### Step 1: Load Document Context

Read `<ingestion-path>/meta.json` (or `intermediate/<document>/ingestion/meta.json` if ingestion-path is not provided) to get paper title, authors, year, and prefix (if present). If `meta.json` lacks a `prefix` field, the user must provide it.

Derive `author-id` from the authors field (lowercase, hyphenated). For multiple authors, use `<first-author-last-name>-et-al`. For a single author, use their name slug. If `author-id` is already provided as an argument, use it directly.

### Step 2: Search Ingestion Files for the Concept

Search ALL `.md` files in the ingestion directory for the concept name (case-insensitive).

Read each matching file. Look for:
- Explicit definitions ("X is...", "X is defined as...", "X refers to...")
- Explanatory descriptions of what the concept means
- Mathematical formulations or formal definitions
- Key properties that constitute a definition

**If the concept appears but is only mentioned in passing** (not defined or explained), treat it as "not found."

### Step 3: Internet Fallback (if not found)

If no clear definition exists in ingestion files:

1. Search the Internet: query `"<concept name>" definition <field/domain>`
2. Prefer authoritative sources: textbooks, encyclopedias, Wikipedia, academic papers
3. Extract a concise, rigorous definition
4. Record the source URL and description

### Step 4: Generate `.tree` File

**Output path:** `intermediate/<document>/trees/<prefix>-<concept-slug>.tree`

**Concept slug:** lowercase, words separated by hyphens (e.g., `nash-equilibrium`, `self-attention`)

Use this structure:

```
\title{<Concept Title>}
\taxon{Definition}
\date{<YYYY-MM-DD>}
\author{<author-id>}
\import{base-macros}
\meta{tags}{tag1, tag2, tag3}

\p{
  <Core definition. Use \strong{key terms} on first appearance.>
}

\p{
  <Additional detail, formula, or elaboration. Optional.>
}

\p{
  \mark{<Key insight or important property. Optional.>}
}
```

### Tags

Every `.tree` file must include `\meta{tags}{...}` with a comma-separated list of category tags describing what domains or topics this concept relates to. Tags help downstream relation-finding steps pair related concepts efficiently.

Choose tags from the concept's domain. For a machine learning paper, tags might include: `architecture`, `attention`, `training`, `optimization`, `evaluation`, `embedding`, `regularization`, `baseline`. For a finance book: `balance-sheet`, `income-statement`, `cash-flow`, `valuation`, `risk`, `accounting-policy`.

Use 2-5 tags per concept. Tags should be lowercase, hyphenated if multi-word.

If the definition came from an Internet search (Step 3), append a source paragraph:

```
\p{
  \em{(Standard definition provided for context. Source: <source description>, <URL>)}
}
```

### Step 5: Confirm Output

Print the full content of the generated `.tree` file and its path.

## .tree Syntax Quick Reference

| Element | Syntax | Notes |
|---------|--------|-------|
| Title | `\title{Title Text}` | Required, top of file |
| Taxon | `\taxon{Definition}` | Always capitalize: `Definition` |
| Date | `\date{YYYY-MM-DD}` | Required |
| Author | `\author{author-id}` | Required |
| Import | `\import{base-macros}` | Always include |
| Tags | `\meta{tags}{tag1, tag2}` | Required, 2-5 tags |
| Paragraph | `\p{ content }` | Wrap all body text |
| Bold | `\strong{text}` | NOT `**text**` |
| Emphasis | `\em{text}` | NOT `*text*` |
| Inline math | `#{formula}` | NOT `$formula$` |
| Block math | `##{formula}` | NOT `$$formula$$` |
| Highlight | `\mark{text}` | For key insights |
| Unordered list | `\ul{ \li{item1} \li{item2} }` | |
| Ordered list | `\ol{ \li{item1} \li{item2} }` | |
| Table | `\table{ \tr{ \th{h} } \tr{ \td{d} } }` | NOT LaTeX arrays |
| Link | `[text](tree-id)` | |
| Escape percent | `\%` | NEVER bare `%` |
| Code | `\code{code}` | |

## Critical Syntax Rules

1. **No Markdown formatting.** Use `\strong{}` not `**bold**`. Use `\em{}` not `*italic*`.
2. **No LaTeX math delimiters.** Use `#{x}` not `$x$`. Use `##{...}` not `$$...$$`.
3. **Escape percent signs.** Write `50\%` not `50%`.
4. **Capitalize taxon values.** `\taxon{Definition}` not `\taxon{definition}`.
5. **No LaTeX table environments.** Use `\table{}` with `\tr{}`, `\th{}`, `\td{}`.
6. **All body text inside `\p{}`**. Never write bare text outside a `\p{}` block.
7. **Always include `\import{base-macros}`** after the metadata block.

## Example

**Input:** concept=`Self-Attention`, document=`attention-is-all-you-need`

**Step 1:** meta.json gives authors=`Vaswani et al.`, year=`2017`. Prefix=`006`, author-id=`vaswani-et-al`.

**Step 2:** Grep finds in `02_background.md`:
> **Self-attention** (sometimes called **intra-attention**) is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence.

Definition found. No Internet search needed.

**Step 4:** Write `intermediate/attention-is-all-you-need/trees/006-self-attention.tree`:

```
\title{Self-Attention}
\taxon{Definition}
\date{2026-02-14}
\author{vaswani-et-al}
\import{base-macros}
\meta{tags}{attention, architecture, sequence-modeling}

\p{
  \strong{Self-attention} (sometimes called \strong{intra-attention}) is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence.
}

\p{
  In self-attention, the queries, keys, and values all come from the same sequence:
  ##{
    \text{SelfAttention}(X) = \text{Attention}(XW^Q, XW^K, XW^V)
  }
}

\p{
  \mark{The Transformer is the first transduction model relying entirely on self-attention} to compute representations of its input and output without using sequence-aligned RNNs or convolution.
}
```

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `$x^2$` for math | `#{x^2}` |
| `**bold text**` | `\strong{bold text}` |
| `\taxon{definition}` | `\taxon{Definition}` |
| Bare `%` in text | `\%` |
| `\begin{array}...` | `\table{ \tr{ \td{} } }` |
| Text outside `\p{}` | Wrap in `\p{ ... }` |
| Missing `\import{base-macros}` | Add after `\author{}` line |
| Vague "see above" content | Self-contained definition |
