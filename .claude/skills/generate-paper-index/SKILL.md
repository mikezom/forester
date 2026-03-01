---
name: generate-paper-index
description: Generate the final top-level paper index .tree file that assembles all chapter indices into a single document overview. Use when generating the main paper index for Step 3.4 of the pipeline, creating the document-level tree, assembling chapters into a paper, or when the user says "generate paper index", "create main index", "build document index", or "assemble the paper".
---

# Generate Paper Index

## Overview

Generate the top-level Forester `.tree` index file for a document. This file serves as the entry point for the entire knowledge graph: it presents the abstract, provides a structural overview, and transcludes all chapter indices using `\transclude-unexpanded{}`. It may also include a lasting impact section and a reference to the semantic relations file.

## Slash Command Usage

```
/generate-paper-index document="attention-is-all-you-need" prefix="006" author-id="vaswani-et-al"
```

All arguments are key="value" pairs. When invoked this way, use the provided values directly.

## Required Input

| Argument | Description |
|----------|-------------|
| **document** | Document name (folder under `intermediate/`) |
| **prefix** | 3-digit prefix for tree IDs (e.g., `006`) |
| **author-id** | Author identifier (e.g., `vaswani-et-al`) |

## Process

### Step 1: Gather Context

Read these files:

1. **meta.json**: `intermediate/<document>/ingestion/meta.json`
   - Extract: title, authors, year, abstract, keywords

2. **Master registry**: `intermediate/<document>/structural-analysis/<prefix>_master_registry.json`
   - Extract: section list (to know all chapters and their order)

3. **Chapter index files**: Verify that each chapter's index file exists at `intermediate/<document>/trees/<chapter-folder>/<prefix>-<XX>-index.tree`
   - If any are missing, warn the user and list which chapters lack index files.

4. **Relations file** (optional): Check if `intermediate/<document>/trees/<prefix>-relations.tree` exists.

5. **Ingestion markdown files**: Skim the first and last sections to understand the document's opening motivation and conclusion.

### Step 2: Write the Paper Index

**Output path:** `intermediate/<document>/trees/<prefix>-index.tree`

The paper index follows this structure:

```
\title{<Document Title>}
\taxon{Reference}
\date{<YYYY-MM-DD>}
\author{<author-id>}
\import{base-macros}

\p{
  \strong{Abstract}
}

\p{
  <Full abstract from meta.json, with key concepts linked on first mention
  using [concept](tree-id) syntax.>
}

\p{
  <Optional second abstract paragraph if the abstract is long.>
}

\p{
  \mark{<Central insight or key contribution of the document. One or two
  sentences capturing the most important takeaway.>}
}

\p{
  \strong{Paper Structure}
}

\p{
  <Brief overview of the document's structure -- what it covers and how
  it is organized. 2-3 sentences.>
}

\p{
  <Introductory paragraph for the first chapter. Summarize what this
  chapter covers and why it matters. Link the chapter title:
  [Chapter Title](prefix-XX-index). Link key concepts on first mention.>
}

\transclude-unexpanded{<prefix>-01-index}

\p{
  <Introductory paragraph for the next chapter...>
}

\transclude-unexpanded{<prefix>-02-index}

... (continue for all chapters) ...

\p{
  \strong{Semantic Relations}
}

\p{
  The [relations file](<prefix>-relations) defines the semantic graph
  connecting all concepts in this document.
}

\p{
  \strong{Lasting Impact}
}

\p{
  <Description of how this work influenced its field, what came after,
  and why it remains relevant. Include links to downstream concepts if
  they exist in the registry.>
}
```

### Writing Guidelines

**Abstract:**
- Reproduce the abstract from meta.json faithfully, but link key concepts on first mention using `[concept name](tree-id)`.
- Split into multiple `\p{}` blocks if the abstract is long.
- Follow with a `\mark{}` block highlighting the document's central contribution.

**Paper Structure:**
- Write a brief overview (2-3 sentences) describing what the document covers.
- This is a high-level roadmap, not a detailed table of contents.

**Chapter introductions:**
- Before each `\transclude-unexpanded{}`, write one `\p{}` paragraph that:
  - Names the chapter with a bold link: `\strong{[Chapter Title](<prefix>-XX-index)}`
  - Summarizes what the chapter covers (2-3 sentences)
  - Links key concepts from that chapter on first mention
  - Explains how this chapter connects to the document's overall argument
- These paragraphs are regular narrative text, not remarks. Use `\p{}`.

**`\transclude-unexpanded{}` vs `\transclude{}`:**
- Always use `\transclude-unexpanded{}` for chapter transclusions. Chapters are long, so they should appear as collapsed references rather than expanded inline.
- The `-unexpanded` variant shows the chapter title as a clickable link without inlining all its content.

**Remarks with `\aside{}`:**
- Use `\aside{}` only for side commentary that isn't part of the main narrative: editorial observations, historical notes, or meta-commentary about the document's significance.
- Do NOT use `\aside{}` for chapter introductions or transitions. Those belong in regular `\p{}` paragraphs.

**Semantic Relations section:**
- Include only if a relations file exists (`<prefix>-relations.tree`).
- Keep it brief -- one paragraph linking to the relations file.

**Lasting Impact section:**
- For research papers: describe influence on the field, follow-up work, and lasting contributions.
- For books or other documents: describe key takeaways and practical applications.
- Link to downstream concepts if they exist in the registry (e.g., `[BERT](006-bert)`).
- If the document's impact is unclear or too recent to assess, this section can be omitted or kept brief.

**Do NOT include:**
- Author information in the body text (it's already in `\author{}`).
- A redundant title paragraph (the `\title{}` metadata handles this).
- Bare `%` signs (escape as `\%`).
- Markdown formatting (`**bold**`, `*italic*`) -- use `\strong{}` and `\em{}`.
- LaTeX math delimiters (`$...$`) -- use `#{...}` and `##{...}`.

### Step 3: Verify Output

Before finalizing, check:

1. All chapter index files referenced by `\transclude-unexpanded{}` actually exist
2. Every chapter from the master registry's section list is included
3. Chapters appear in correct order (01, 02, ..., N)
4. Key concepts are linked on first mention throughout the file
5. No concept is linked before its first textual mention
6. `\aside{}` is only used for remarks, not for chapter introductions
7. No author information in the body (only in `\author{}` metadata)
8. All `%` escaped as `\%`
9. All body text inside `\p{}`, `\aside{}`, or list/table macros

Print the full content of the generated `.tree` file and its path.

## .tree Syntax Quick Reference

| Element | Syntax | Notes |
|---------|--------|-------|
| Title | `\title{Document Title}` | From meta.json |
| Taxon | `\taxon{Reference}` | Always `Reference` for index files |
| Date | `\date{YYYY-MM-DD}` | Today's date |
| Author | `\author{author-id}` | Required, no author info in body |
| Import | `\import{base-macros}` | Always include |
| Paragraph | `\p{ content }` | All narrative text |
| Aside/Remark | `\aside{ remark }` | Side commentary only |
| Bold | `\strong{text}` | NOT `**text**` |
| Emphasis | `\em{text}` | NOT `*text*` |
| Inline math | `#{formula}` | NOT `$formula$` |
| Block math | `##{formula}` | NOT `$$formula$$` |
| Highlight | `\mark{text}` | Central insight |
| Link | `[text](tree-id)` | First mention of concepts |
| Transclude unexpanded | `\transclude-unexpanded{tree-id}` | Chapter-level references |
| Unordered list | `\ul{ \li{item} }` | |
| Ordered list | `\ol{ \li{item} }` | |
| Escape percent | `\%` | Never bare `%` |

## Example

**Input:** document=`attention-is-all-you-need`, prefix=`006`, author-id=`vaswani-et-al`

**Output:** `intermediate/attention-is-all-you-need/trees/006-index.tree`

```
\title{Attention Is All You Need}
\taxon{Reference}
\date{2026-02-28}
\author{vaswani-et-al}
\import{base-macros}

\p{
  \strong{Abstract}
}

\p{
  The dominant sequence transduction models are based on complex recurrent or
  convolutional neural networks that include an encoder and a decoder. The best
  performing models also connect the encoder and decoder through an attention
  mechanism. We propose a new simple network architecture, the
  [Transformer](006-transformer), based solely on attention mechanisms,
  dispensing with recurrence and convolutions entirely.
}

\p{
  \mark{The central innovation of the Transformer is the complete removal of
  recurrence, replaced entirely by attention mechanisms. This enables full
  parallelization of computation across sequence positions.}
}

\p{
  \strong{Paper Structure}
}

\p{
  This paper introduces the Transformer architecture and demonstrates its
  effectiveness on sequence transduction tasks, moving from motivation through
  architecture details to experimental validation.
}

\p{
  In the \strong{[Introduction](006-01-index)}, we review the limitations of
  existing recurrent approaches and motivate the need for a purely
  attention-based architecture.
}

\transclude-unexpanded{006-01-index}

\p{
  The \strong{[Background](006-02-index)} provides context by reviewing related
  work on reducing sequential computation, including convolutional sequence
  models and memory networks.
}

\transclude-unexpanded{006-02-index}

\p{
  With this foundation, we present the \strong{[Model Architecture](006-03-index)}
  in detail. The Transformer follows an [encoder-decoder](006-encoder-decoder-architecture)
  structure with stacked layers of [self-attention](006-self-attention) and
  feed-forward sub-layers.
}

\transclude-unexpanded{006-03-index}

\p{
  \strong{Semantic Relations}
}

\p{
  The [relations file](006-relations) defines the semantic graph connecting all
  concepts in this paper.
}

\p{
  \strong{Lasting Impact}
}

\p{
  The Transformer architecture has become the foundation for
  [BERT](006-bert), [GPT](006-gpt), [Vision Transformer](006-vision-transformer),
  and modern [large language models](006-large-language-model).
}
```

(Example truncated for brevity -- a full paper index would include introductory paragraphs and `\transclude-unexpanded{}` for all chapters.)

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `\transclude{prefix-01-index}` | `\transclude-unexpanded{prefix-01-index}` |
| `\aside{Introduction to chapter...}` | `\p{Introduction to chapter...}` |
| Author name in body text | Only in `\author{}` metadata |
| `\p{\strong{Document Title}}` at top | `\title{}` handles this |
| `$x^2$` for math | `#{x^2}` |
| `**bold text**` | `\strong{bold text}` |
| Bare `%` in text | `\%` |
| Missing chapters in transclusion order | Include all chapters from registry |

## Pipeline Continuation

This is **Step 3.4** of the Forester pipeline. After generating the paper index, the ONLY next step is:

**Step 4: Validate Document** -- Use `/validate-document` to create the person tree and run validation checks on all generated `.tree` files.

Do NOT consider the pipeline complete until validation passes.
