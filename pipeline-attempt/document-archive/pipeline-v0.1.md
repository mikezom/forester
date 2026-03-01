# Paper to Forester Pipeline

This document describes the complete pipeline for transforming academic papers into Forester-compatible knowledge graph structures.

## Overview

The pipeline consists of 4 main steps:
1. **Ingestion** - Extract and chunk paper content into markdown
2. **Structural Analysis** - Identify and catalog all concepts
3. **Synthesis** - Generate Forester tree files (concepts, relations, indices)
4. **Validation** - Verify syntax and completeness

---

## STEP 1: Ingestion

### Input
- PDF paper file in `/resource` folder

### Output
- `intermediate/{paper-name}/ingestion/meta.json` - Paper metadata
- `intermediate/{paper-name}/ingestion/01_introduction.md` through `XX_summary.md` - Chunked content

### Process

1. **Create folder structure:**
   ```
   intermediate/{paper-name}/ingestion/
   ```

2. **Create `meta.json`:**
   ```json
   {
     "title": "Paper Title",
     "authors": ["Author 1", "Author 2", ...],
     "year": 20XX,
     "venue": "Conference/Journal",
     "abstract": "Full abstract text..."
   }
   ```

3. **Create chunked markdown files:**
   - Split paper by logical sections (Introduction, Background, Methods, Results, etc.)
   - Preserve mathematical notation using LaTeX syntax: `$...$` for inline, `$$...$$` for block
   - Name files with numeric prefix for ordering: `01_introduction.md`, `02_background.md`, etc.
   - Each file should be self-contained but reference other sections naturally

### Guidelines
- Keep chunks at reasonable size (not too long, not too short)
- Preserve all equations with proper LaTeX formatting
- Maintain original section structure when possible
- Include key definitions and terminology

---

## STEP 2: Structural Analysis

### Input
- Chunked markdown files from STEP 1

### Output
- `intermediate/{paper-name}/structural-analysis/{prefix}_XX_{section}_registry.json` - Per-section registries
- `intermediate/{paper-name}/structural-analysis/{prefix}_master_registry.json` - Consolidated registry

### Process

1. **Create folder structure:**
   ```
   intermediate/{paper-name}/structural-analysis/
   ```

2. **Choose a prefix:**
   - Use a 3-digit number (e.g., `006`) to uniquely identify this paper's trees
   - This prevents ID collisions when multiple papers exist in the same forest

3. **Create per-section registries:**
   ```json
   {
     "section": "Introduction",
     "concepts": [
       {
         "name": "Concept Name",
         "tree_id": "prefix-concept-name",
         "category": "Architecture|Mechanism|Component|etc.",
         "description": "Brief description"
       }
     ]
   }
   ```

4. **Create master registry:**
   ```json
   {
     "paper_title": "Paper Title",
     "prefix": "006",
     "total_concepts": 96,
     "categories": {
       "Architecture": ["prefix-transformer", "prefix-encoder", ...],
       "Mechanism": ["prefix-attention", ...],
       ...
     },
     "concepts": {
       "Concept Name": "prefix-concept-name",
       ...
     }
   }
   ```

### Guidelines
- Identify ALL concepts: architectures, mechanisms, components, hyperparameters, equations, etc.
- Use consistent naming for tree IDs: lowercase, hyphens for spaces
- Group concepts by category for organization
- Cross-reference between sections to avoid duplicates

---

## STEP 3: Synthesis

### STEP 3.1: Generate Concept Tree Files

### Input
- Registry files from STEP 2

### Output
- `intermediate/{paper-name}/trees/XX-section/prefix-concept-name.tree` - Individual concept files

### Process

1. **Create folder structure:**
   ```
   intermediate/{paper-name}/trees/
   ├── 01-introduction/
   ├── 02-background/
   ├── ...
   ├── 11-summary/
   └── person/
   ```

2. **For each concept, create a tree file:**
   ```tex
   \title{Concept Name}
   \taxon{Definition}
   \date{YYYY-MM-DD}
   \author{author-id}
   \import{base-macros}

   \p{
     Definition and explanation of the concept...
   }

   \p{
     Additional details with \strong{key terms} highlighted.
   }

   \p{
     \mark{Key insight or important observation about this concept.}
   }
   ```

### Forester Syntax Reference

| Element | Syntax |
|---------|--------|
| Title | `\title{Title}` |
| Taxon | `\taxon{Definition}` or `\taxon{Reference}` |
| Date | `\date{YYYY-MM-DD}` |
| Author | `\author{author-id}` |
| Import | `\import{base-macros}` |
| Paragraph | `\p{ content }` |
| Strong | `\strong{text}` |
| Emphasis | `\em{text}` |
| Inline Math | `#{formula}` |
| Block Math | `##{formula}` |
| Link | `[text](tree-id)` |
| List | `\ul{ \li{item} }` or `\ol{ \li{item} }` |
| Mark/Insight | `\mark{insight text}` |
| Aside/Conjunction | `\aside{conjunction text}` |
| Table | `\table{ \tr{ \th{header} } \row{col1}{col2} }` |
| Inline Code | `\code{code}` |
| Verbatim | `\startverb...\stopverb` |

### Critical Syntax Rules

1. **Percentage Sign**: Always use `\%` (backslash percentage) instead of `%` in `.tree` files.
   - ❌ Wrong: `117%`
   - ✅ Correct: `117\%`

2. **Taxon Capitalization**: Use capital first letter for taxon values.
   - ❌ Wrong: `\taxon{definition}`
   - ✅ Correct: `\taxon{Definition}`
   - ❌ Wrong: `\taxon{reference}`
   - ✅ Correct: `\taxon{Reference}`

3. **Conjunctions**: Write conjunctions (connecting text between sections/concepts) within `\aside{...}`.
   ```tex
   \transclude{prefix-concept}

   \aside{This leads us to the next important concept...}

   \transclude{prefix-another-concept}
   ```

4. **Tables**: Do NOT use LaTeX array environments (like `\begin{array}...\end{array}`) inside tex blocks. Instead, use Forester's native `\table{}` macro with inline tex for formulas.
   - ❌ Wrong: `##{\begin{array}{cc} a & b \\ c & d \end{array}}`
   - ✅ Correct:
     ```tex
     \table{
         \tr{
             \th{Column 1}
             \th{Column 2}
         }
         \row{#{a}}{#{b}}
         \row{#{c}}{#{d}}
     }
     ```
   - For code/examples in table cells, use `\startverb...\stopverb`:
     ```tex
     \table{
         \tr{
             \th{Element}
             \th{Syntax}
         }
         \row{Bold}{\startverb\strong{bold}\stopverb}
         \row{Italic}{\startverb\em{italic}\stopverb}
     }
     ```

### Guidelines
- Use definitions from the paper when available
- Search the internet for standard definitions if not in paper
- Use `\strong{}` for key terminology
- Use `\mark{}` for important insights
- Keep math in proper notation: `#{d_k}` for inline, `##{...}` for block

---

### STEP 3.2: Generate Relations File

### Input
- Registry files from STEP 2
- Concept tree files from STEP 3.1

### Output
- `intermediate/{paper-name}/trees/prefix-relations.tree` - Single relations file

### Process

1. **Create relations file:**
   ```tex
   \title{Relations: Paper Title}
   \taxon{Metadata}
   \date{YYYY-MM-DD}
   \author{author-id}
   \import{base-macros}

   \p{
     \strong{Semantic Relations}
   }

   \relation{prefix-source}{relationship}{prefix-target}
   \relation{prefix-source}{relationship}{prefix-target}
   ...
   ```

### Common Relation Types
- `is-a` - Taxonomic relationship
- `is-composed-of` - Part-whole relationship
- `is-used-in` - Usage relationship
- `is-replaced-by` - Replacement/evolution
- `enables` - Enables something
- `requires` - Dependency
- `improves` - Improvement relationship
- `is-an-instance-of` - Instance relationship

### Guidelines
- Multi-word relationships are allowed: `is-composed-of`, `is-replaced-by`
- Create relations for ALL meaningful connections between concepts
- Aim for comprehensive semantic graph coverage

---

### STEP 3.3: Generate Chapter Index Files

### Input
- Ingestion markdown files from STEP 1
- Concept tree files from STEP 3.1

### Output
- `intermediate/{paper-name}/trees/XX-section/prefix-XX-index.tree` - Per-chapter indices

### Process

1. **For each chapter, create an index file:**
   ```tex
   \title{Chapter Title}
   \taxon{Reference}
   \date{YYYY-MM-DD}
   \author{author-id}
   \import{base-macros}

   \p{
     \strong{Section Overview}
   }

   \p{
     Introduction to the section content with [concept](prefix-concept) linked on first mention.
   }

   \transclude{prefix-concept-defined-in-this-chapter}

   \aside{Conjunction text connecting to next concept...}

   \transclude{prefix-another-concept}
   ```

### Guidelines
- Match the narrative flow of the original ingestion markdown
- First mention of a concept → link to its definition: `[concept](prefix-concept)`
- If the concept IS defined in this chapter → use `\transclude{prefix-concept}`
- Use `\transclude{}` for concepts defined in the current chapter
- Use `\aside{}` for conjunctions between sections for narrative flow

---

### STEP 3.4: Generate Final Paper Index

### Input
- Chapter index files from STEP 3.3
- meta.json from STEP 1

### Output
- `intermediate/{paper-name}/trees/prefix-index.tree` - Main paper index

### Process

1. **Create main index file:**
   ```tex
   \title{Paper Title}
   \taxon{Reference}
   \date{YYYY-MM-DD}
   \author{author-id}
   \import{base-macros}

   \p{
     \strong{Abstract}
   }

   \p{
     Full abstract text...
   }

   \p{
     \mark{Central insight or key contribution of the paper.}
   }

   \p{
     \strong{Paper Structure}
   }

   \p{
     Introduction to the paper structure...
   }

   \transclude-unexpanded{prefix-01-index}

   \aside{Conjunction text connecting to next chapter...}

   \transclude-unexpanded{prefix-02-index}

   ... (continue for all chapters)

   \p{
     \strong{Lasting Impact}
   }

   \p{
     Description of how this paper influenced the field...
   }
   ```

### Guidelines
- Use `\transclude-unexpanded` for chapter transclusions (chapters are long)
- Include abstract and paper structure overview
- Use `\aside{}` for conjunctions between chapters for smooth reading flow
- Add "Lasting Impact" section for influential papers
- Reference related work and future directions

---

## STEP 4: Validation

### Input
- All generated tree files

### Output
- Validation report (console output)
- Person tree file: `intermediate/{paper-name}/trees/person/author-id.tree`

### Process

1. **Create person tree file:**
   ```tex
   \title{Author Name / Group Name}
   \taxon{Person}
   \date{YYYY-MM-DD}
   \meta{external}{https://link-to-paper-or-profile}
   \meta{institution}{Institution Name}
   \meta{venue}{Conference/Journal Name}
   \meta{orcid}{0000-0000-0000-0000}  % if available

   \p{
     Brief description of the author(s) and their contribution...
   }

   \p{
     \strong{Impact}
   }

   \p{
     Description of the impact of their work...
   }
   ```

2. **Run validation checks:**
   - Markdown syntax validation (all `\p{}`, `\ul{}`, etc. properly closed)
   - Math delimiter validation (all `#{}` and `##{}` properly formatted)
   - Metadata validation (all files have `\title`, `\taxon`, `\date`, `\author`)
   - Reference validation (all `[text](tree-id)` and `\transclude{}` point to existing files)

### Validation Script Example
```bash
# Check for unclosed delimiters
grep -r '\\p{[^}]*$' trees/

# Check for dangling references
# Extract all tree-ids from \transclude and []() references
# Verify each referenced file exists
```

### Guidelines
- All person trees go in `trees/person/` folder
- Use `\meta{external}{}` for links to papers or profiles
- Use `\meta{institution}{}` for affiliation
- Validate before considering the pipeline complete

---

## File Structure Summary

After completing the pipeline, the folder structure will be:

```
intermediate/{paper-name}/
├── ingestion/
│   ├── meta.json
│   ├── 01_introduction.md
│   ├── 02_background.md
│   └── ... (more sections)
├── structural-analysis/
│   ├── prefix_01_introduction_registry.json
│   ├── prefix_02_background_registry.json
│   └── prefix_master_registry.json
└── trees/
    ├── prefix-index.tree          # Main paper index
    ├── prefix-relations.tree      # Semantic relations
    ├── 01-introduction/
    │   ├── prefix-01-index.tree
    │   └── prefix-*.tree          # Concept files
    ├── 02-background/
    │   ├── prefix-02-index.tree
    │   └── prefix-*.tree
    ├── ... (more section folders)
    └── person/
        └── author-id.tree
```

---

## Checklist

- [ ] STEP 1: Ingestion
  - [ ] meta.json created
  - [ ] All sections chunked into markdown
  - [ ] LaTeX math preserved

- [ ] STEP 2: Structural Analysis
  - [ ] Per-section registries created
  - [ ] Master registry consolidated
  - [ ] All concepts identified and cataloged

- [ ] STEP 3.1: Concept Trees
  - [ ] Folder structure created
  - [ ] All concept tree files generated
  - [ ] Proper Forester syntax used
  - [ ] All `%` escaped as `\%`
  - [ ] Taxon values capitalized (e.g., `Definition` not `definition`)
  - [ ] Tables use `\table{}` macro, not LaTeX array environments

- [ ] STEP 3.2: Relations
  - [ ] Relations file created
  - [ ] All semantic connections captured

- [ ] STEP 3.3: Chapter Indices
  - [ ] Per-chapter index files created
  - [ ] Narrative flow matches original
  - [ ] Links and transclusions correct
  - [ ] Conjunctions use `\aside{}`

- [ ] STEP 3.4: Main Index
  - [ ] Paper index created
  - [ ] Abstract included
  - [ ] Chapters transcluded
  - [ ] Conjunctions written with `\aside{}`

- [ ] STEP 4: Validation
  - [ ] Person tree created
  - [ ] Syntax validation passed
  - [ ] Reference validation passed
  - [ ] All metadata present

---

## Notes

- The prefix (e.g., `006`) must be unique across all papers in the forest
- Tree IDs should be lowercase with hyphens: `prefix-multi-head-attention`
- Always use `\import{base-macros}` to access standard macros
- The `\mark{}` macro is for highlighting key insights
- Use `\taxon{Definition}` for concept definitions, `\taxon{Reference}` for paper sections
- Use `\taxon{Person}` for author/group trees with `\meta{}` declarations
- **Always escape percentage signs**: use `\%` instead of `%`
- **Capitalize taxon values**: `\taxon{Definition}` not `\taxon{definition}`
- **Use `\aside{}` for conjunctions**: connecting text between transcluded content
- **Use `\table{}` for tables**: never use LaTeX array environments in tex blocks
