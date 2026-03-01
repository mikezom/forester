---
name: validate-document
description: Run validation checks on all generated .tree files for a document and create the person tree file. Use when completing the pipeline, validating tree files, checking for syntax errors, creating author/person trees, or when the user says "validate", "run validation", "check the trees", "create person tree", or "finish the pipeline". This is Step 4 of the pipeline, the final step before a document is considered complete.
---

# Validate Document

## Overview

This skill performs the final pipeline step: create a person tree file for the document's author(s), then validate all generated `.tree` files for correctness. It checks syntax, metadata, references, and formatting to catch issues before the document is deployed to the forest.

## Slash Command Usage

```
/validate-document document="attention-is-all-you-need" prefix="006" author-id="vaswani-et-al"
```

All arguments are key="value" pairs. When invoked this way, use the provided values directly.

## Required Input

| Argument | Description |
|----------|-------------|
| **document** | Document name (folder under `intermediate/`) |
| **prefix** | 3-digit prefix for tree IDs (e.g., `006`) |
| **author-id** | Author identifier (e.g., `vaswani-et-al`) |

## Process

### Step 1: Create Person Tree File

Read `intermediate/<document>/ingestion/meta.json` to get author information.

**Output path:** `intermediate/<document>/trees/person/<author-id>.tree`

Use this structure:

```
\title{<Author Name or Group Name>}
\taxon{Person}
\date{<YYYY-MM-DD>}
\meta{external}{<URL to paper, profile, or homepage>}
\meta{institution}{<Institution or affiliation>}
\meta{venue}{<Conference, journal, or publisher>}

\p{
  Brief description of the author(s) and their contribution to this document.
}

\p{
  \strong{Impact}
}

\p{
  Description of the impact of their work, key contributions, and influence
  on the field.
}
```

**Person tree guidelines:**
- For multi-author papers, use the group name as the title (e.g., `Vaswani et al.`).
- List individual authors in the body using `\ul{}` with `\li{}`.
- `\meta{external}{}`: Link to the paper (arXiv, DOI) or author's homepage.
- `\meta{institution}{}`: Primary affiliation at time of publication.
- `\meta{venue}{}`: Where the work was published (conference name + year, publisher, etc.).
- `\meta{orcid}{}`: Include if known (optional).
- Link to concepts from the document where relevant (e.g., `[Transformer](006-transformer)`).
- The Impact section should describe real-world influence and downstream work.

If the person tree already exists, read it and check whether it needs updating rather than overwriting.

### Step 2: Run Validation Checks

Scan all `.tree` files in `intermediate/<document>/trees/` (recursively) and check for the following issues. Report each issue with the file path and line number.

#### 2.1 Metadata Validation

Every `.tree` file must have:

| Field | Check |
|-------|-------|
| `\title{...}` | Present and non-empty |
| `\taxon{...}` | Present, capitalized (e.g., `Definition` not `definition`) |
| `\date{...}` | Present, valid format `YYYY-MM-DD` |
| `\author{...}` | Present (except person trees, which may omit it) |
| `\import{base-macros}` | Present (except person trees) |

Person trees (`\taxon{Person}`) may omit `\author{}` and `\import{base-macros}`.

#### 2.2 Syntax Validation

| Check | Description |
|-------|-------------|
| **Unescaped `%`** | Every `%` must be `\%`. Bare `%` starts a comment in Forester and silently eats content. |
| **Balanced braces** | All `\p{...}`, `\ul{...}`, `\li{...}`, `\strong{...}`, `\em{...}`, `\mark{...}`, `\aside{...}`, `\table{...}`, `\tr{...}`, `\td{...}`, `\th{...}`, `\ol{...}`, `\code{...}` must have matching opening and closing braces. |
| **Math delimiters** | `#{...}` and `##{...}` must have balanced braces. No `$...$` or `$$...$$` (LaTeX-style delimiters are not valid in Forester). |
| **No markdown formatting** | No `**bold**` or `*italic*` patterns. These should be `\strong{}` and `\em{}`. |
| **No LaTeX tables** | No `\begin{array}` or `\begin{tabular}`. Use `\table{}` with `\tr{}`, `\th{}`, `\td{}` instead. |
| **Body text in blocks** | All text content should be inside `\p{}`, `\aside{}`, `\li{}`, `\td{}`, `\th{}`, or similar block macros. Flag bare text outside any block. |

#### 2.3 Reference Validation

| Check | Description |
|-------|-------------|
| **Link targets** | Every `[text](tree-id)` where `tree-id` doesn't start with `http` should reference an existing `.tree` file. Collect all tree IDs from the document's tree files and check that link targets exist either within this document or in the broader forest (`trees/` directory). |
| **Transclusion targets** | Every `\transclude{tree-id}` and `\transclude-unexpanded{tree-id}` must reference an existing `.tree` file. |
| **Relation targets** | Every `\relation{source}{type}{target}{mentioned}` must have both `source` and `target` referencing existing tree IDs. |

#### 2.4 Structural Validation

| Check | Description |
|-------|-------------|
| **Index completeness** | The paper index (`<prefix>-index.tree`) should have a `\transclude-unexpanded{}` for every chapter index. |
| **Chapter coverage** | Every section in the master registry should have a corresponding chapter index file. |
| **Concept coverage** | Every concept in the master registry should have a corresponding `.tree` file. Report missing ones. |
| **Duplicate tree IDs** | No two `.tree` files should have the same stem (filename without extension). |
| **Relation format** | All `\relation{}` calls should have exactly 4 arguments (source, type, target, mentioned). Flag any with 3 arguments (pre-migration format). |
| **Tags presence** | Concept definition files (`\taxon{Definition}`) should have `\meta{tags}{...}`. Flag untagged definitions. |

### Step 3: Report Results

Present a structured validation report:

```
=== Validation Report: <Document Title> ===

Person tree: <created | already exists | updated>
  Path: intermediate/<document>/trees/person/<author-id>.tree

--- Errors (must fix) ---
[E001] Missing metadata: <file> -- missing \title{}
[E002] Broken reference: <file>:<line> -- [text](tree-id) target not found
[E003] Broken transclusion: <file>:<line> -- \transclude{tree-id} target not found
[E004] Duplicate tree ID: <file1> and <file2> share stem "<id>"
[E005] Old relation format: <file>:<line> -- \relation{}{}{} needs 4th arg

--- Warnings (should fix) ---
[W001] Unescaped percent: <file>:<line> -- bare % found
[W002] Lowercase taxon: <file>:<line> -- \taxon{definition} should be \taxon{Definition}
[W003] Markdown formatting: <file>:<line> -- **text** should be \strong{text}
[W004] LaTeX math: <file>:<line> -- $...$ should be #{...}
[W005] Missing tags: <file> -- Definition without \meta{tags}{...}
[W006] Missing concept: <concept-name> (tree-id) -- no .tree file found
[W007] LaTeX table: <file>:<line> -- \begin{array} should use \table{}

--- Summary ---
Files scanned:  XX
Errors:         XX
Warnings:       XX
Concepts:       XX/YY have .tree files
Chapter indices: XX/YY exist
```

**Error vs Warning distinction:**
- **Errors** break the forest build or produce incorrect output. These must be fixed.
- **Warnings** are quality issues that should be fixed but won't break the build.

### Step 4: Offer Fixes

After reporting, offer to fix automatically fixable issues:

1. **Unescaped `%`**: Replace `%` with `\%` (excluding lines that are intentional comments)
2. **Lowercase taxon**: Capitalize the first letter
3. **Old relation format**: Append `{true}` to 3-argument `\relation{}` calls
4. **Missing tags**: Cannot auto-fix, but list which files need tags added

Ask the user before applying any fixes.

## Existing Validation Script

The project includes a forest-wide validation script at `skills/forester-forest-maintainer/scripts/validate_forest.py`. After document-level validation, suggest running it for a full forest check:

```bash
python skills/forester-forest-maintainer/scripts/validate_forest.py --root .
```

This script checks duplicate IDs, missing titles, link validity, transclusion targets, and relation references across the entire forest.

## Example

**Input:** document=`attention-is-all-you-need`, prefix=`006`, author-id=`vaswani-et-al`

**Person tree created:** `intermediate/attention-is-all-you-need/trees/person/vaswani-et-al.tree`

```
\title{Vaswani et al.}
\taxon{Person}
\date{2026-02-28}
\meta{external}{https://arxiv.org/abs/1706.03762}
\meta{institution}{Google Brain}
\meta{venue}{NeurIPS 2017}

\p{
  The authors of "Attention Is All You Need" (2017), the seminal paper that
  introduced the [Transformer](006-transformer) architecture:
}

\p{
  \ul{
    \li{\strong{Ashish Vaswani}}
    \li{\strong{Noam Shazeer}}
    \li{\strong{Niki Parmar}}
    \li{\strong{Jakob Uszkoreit}}
    \li{\strong{Llion Jones}}
    \li{\strong{Aidan N. Gomez}}
    \li{\strong{Lukasz Kaiser}}
    \li{\strong{Illia Polosukhin}}
  }
}

\p{
  \strong{Impact}
}

\p{
  The Transformer architecture has become the foundation for virtually all
  modern large language models including [BERT](006-bert), [GPT](006-gpt),
  and [Vision Transformer](006-vision-transformer).
}
```

**Validation output:**

```
=== Validation Report: Attention Is All You Need ===

Person tree: already exists
  Path: intermediate/attention-is-all-you-need/trees/person/vaswani-et-al.tree

--- Errors (must fix) ---
  (none)

--- Warnings (should fix) ---
[W005] Missing tags: intermediate/.../trees/01-introduction/006-hidden-state.tree
[W005] Missing tags: intermediate/.../trees/02-background/006-bytenet.tree

--- Summary ---
Files scanned:  108
Errors:         0
Warnings:       2
Concepts:       96/96 have .tree files
Chapter indices: 11/11 exist
```

## Common Mistakes in .tree Files

These are the most frequent issues the validation step catches:

| Issue | Frequency | Fix |
|-------|-----------|-----|
| Bare `%` (silent comment) | Very common | `\%` |
| Lowercase taxon | Common | Capitalize first letter |
| Missing `\import{base-macros}` | Occasional | Add after `\author{}` |
| 3-arg `\relation{}` | Legacy files | Append `{true}` |
| `$...$` math | Common in AI-generated | Convert to `#{...}` |
| `**bold**` markdown | Common in AI-generated | Convert to `\strong{}` |
| Missing tags on definitions | After migration | Add `\meta{tags}{...}` |

## Pipeline Completion

This is **Step 4**, the final step of the Forester pipeline. After validation passes with zero errors, the document is ready for deployment:

1. **Deploy to forest**: Copy trees from `intermediate/<doc>/trees/` to `trees/<prefix>-<doc>/`
2. **Build the forest**: Run `forester build` to generate the site
3. **Review the graph**: Run `python aggregate_graph.py` to generate the relation graph JSON

The pipeline is complete. Do NOT re-run earlier steps unless the user explicitly requests changes.
