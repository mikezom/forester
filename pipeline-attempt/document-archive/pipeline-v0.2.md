# Paper to Forester Pipeline

This document describes the complete pipeline for transforming unstructured text into Forester-compatible knowledge graph structures.

## Overview

The pipeline consists of 4 main steps:
1. **Ingestion** - Extract and chunk paper content into markdown
2. **Structural Analysis** - Identify and catalog all concepts
3. **Synthesis** - Generate Forester tree files (concepts, relations, indices)
4. **Validation** - Verify syntax and completeness

---

## STEP 1: Ingestion

### Input
- PDF paper file, or raw, potentially unstructured text (like video transcripts or OCR output) in `/resource` folder

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

## STEP 2: Structural Analysis (Rhetorical Units)

### STEP 2.1: Atomic Unit Extraction

#### Input
- Chunked markdown files from STEP 1

#### Output
- `intermediate/{paper-name}/structural-analysis/{prefix}_XX_{section}_units.json` - Per-section rhetorical units
- `intermediate/{paper-name}/structural-analysis/{prefix}_master_units.json` - Consolidated units with all relationships

#### Philosophy

Treat the input text as if it were a chaotic mathematical proof that needs rigorous reorganization. Every paragraph or section serves a specific functional purpose. The goal is to deconstruct text into atomic **Rhetorical Units**.

**Example transformation:**
- **Linear Text:** "We built a new transformer model because old ones are slow. Our model uses X and is 50% faster."
- **Structured Output:**
  1. **Context (Lemma):** Old transformer models have high latency.
  2. **Method (Definition):** Definition of Model X architecture.
  3. **Claim (Theorem):** Model X reduces latency by 50%.
  4. **Evidence (Proof):** Benchmarks showing the speed comparison.

#### Process

1. **Create folder structure:**
   ```
   intermediate/{paper-name}/structural-analysis/
   ```

2. **Choose a prefix:**
   - Use a 3-digit number (e.g., `006`) to uniquely identify this paper's trees
   - This prevents ID collisions when multiple papers exist in the same forest

3. **Analyze each section** to identify Atomic Units (single, self-contained ideas, arguments, or definitions).

4. **Categorize each unit** using Mathematical Taxons:

   | Taxon | Purpose | Example |
   |-------|---------|---------|
   | **Definition** | Sets boundary of a term, concept, or scope | "What is X?" |
   | **Axiom** | Fundamental assumption taken as true without proof | "We assume markets are efficient." |
   | **Theorem** | Major assertion, core argument, or key insight | "The main point the author is making." |
   | **Lemma** | Background knowledge or prerequisite context | "Required to understand the Theorem." |
   | **Proof** | Data, reasoning, citations supporting a Theorem | "Evidence for the claim." |
   | **Corollary** | Consequence, application, or prediction | "What follows from the Theorem." |
   | **Remark** | Interesting tangent, counter-example, or comparison | "Enriches but not strictly necessary." |
   | **Algorithm** | Step-by-step process or methodology | "How to do X." |

5. **Create per-section unit files:**
   ```json
   {
     "section": "Introduction",
     "units": [
       {
         "id_slug": "concept-name-slug",
         "taxon": "Definition | Axiom | Theorem | Lemma | Proof | Corollary | Remark | Algorithm",
         "title": "Short distinct title for this unit",
         "content": "The rewritten, concise content. Use $...$ for inline math, $$...$$ for block math.",
         "related_to": [
           {
             "target_slug": "id-of-another-unit",
             "relationship": "supports | contradicts | extends | defines | is_consequence_of"
           }
         ],
         "tags": ["keyword1", "keyword2"]
       }
     ]
   }
   ```

6. **Create master units file:**
   ```json
   {
     "paper_title": "Paper Title",
     "prefix": "006",
     "total_units": 96,
     "taxon_distribution": {
       "Definition": ["prefix-unit-1", "prefix-unit-2"],
       "Theorem": ["prefix-unit-3", ...],
       "Lemma": [...],
       "Proof": [...],
       ...
     },
     "units": {
       "unit-title-slug": "prefix-unit-title-slug",
       ...
     }
   }
   ```

#### Constraints & Rules

1. **Atomic Principle**: If a paragraph contains a Definition AND a Claim, split them into two separate units.
2. **Self-Contained**: Each `content` field should make sense on its own. Do not use phrases like "As mentioned above..." without context.
3. **No Fluff**: Strip out transitional phrases like "It is interesting to note that..." or "Let's dive into...". Go straight to the logic.
4. **Math Notation**: Always use `$...$` for inline math and `$$...$$` for block math.
5. **IDs**: `id_slug` must be kebab-case (e.g., `probability-mass-function`).
6. **JSON String Escaping**: When writing JSON files, escape all ASCII double quotation marks (`"`) inside string values as `\"`. For example, write `"content": "He said \"hello\" to me"` instead of `"content": "He said "hello" to me"`. Note: Chinese full-width quotation marks (`“”`) do not need escaping.

#### Example

**Input:**
> "Many people think LLMs reason like humans, but they are actually probabilistic engines. They predict the next token based on statistical likelihood. This was proven by the 'Stochastic Parrots' paper which analyzed the statistical distribution of outputs."

**Output:**
```json
{
  "units": [
    {
      "id_slug": "llm-probabilistic-nature",
      "taxon": "Definition",
      "title": "Probabilistic Nature of LLMs",
      "content": "Large Language Models (LLMs) are probabilistic engines that generate text by predicting the next token based on the conditional probability maximized over a vast corpus of training data.",
      "related_to": [],
      "tags": ["llm", "probability", "token-prediction"]
    },
    {
      "id_slug": "llm-reasoning-fallacy",
      "taxon": "Theorem",
      "title": "The Reasoning Fallacy",
      "content": "LLMs do not possess human-like reasoning capabilities; their output is strictly a function of statistical likelihood rather than semantic understanding or logic.",
      "related_to": [
        {"target_slug": "llm-probabilistic-nature", "relationship": "is_consequence_of"}
      ],
      "tags": ["reasoning", "fallacy"]
    },
    {
      "id_slug": "evidence-stochastic-parrots",
      "taxon": "Proof",
      "title": "Evidence: Stochastic Parrots",
      "content": "Bender et al. demonstrate in 'On the Dangers of Stochastic Parrots' that LLM outputs mirror the statistical distribution of their training sets, confirming the lack of internal intent or ground truth.",
      "related_to": [
        {"target_slug": "llm-reasoning-fallacy", "relationship": "supports"}
      ],
      "tags": ["evidence", "stochastic-parrots"]
    }
  ]
}
```

### STEP 2.2: Prerequisite Resolution

#### Input
- The JSON files generated in Step 2.1.

#### Output
- The updated JSON files (master and section files) containing the newly injected prerequisite units.
- An `prefix_00_prerequisites_units.json` to cleanly separate purely external, retrieved definitions.

#### Process
1. **Scan and Detect**: Review the `content` of all extracted units to identify the "Curse of Knowledge." Spot domain-specific concepts, mathematical constructs, algorithms, or named theorems that are crucial to understanding the text but are NOT defined in any existing `Definition` unit.
* *Ignore* common words or basic undergraduate-level concepts.
* *Focus* on advanced prerequisites (e.g., "Lipschitz continuity", "KL Divergence", "Ergodic theory").
2. **Retrieve Standard Definitions**: For each identified missing concept, retrieve a clear, rigorous, and standard definition (either via LLM knowledge or external search).
3. **Format New Units**: Package these new definitions into the exact same JSON object format as the Step 2.1 units.
* **Taxon**: Must be `Definition` or `Prerequisite`.
* **Content**: Be concise. Use LaTeX for math (`$...$`).
* **Source Note**: Append a brief note indicating it is external context (e.g., "*(Standard definition provided for context.)*").
4. **Merge and Update**: Inject these new supplementary units into the JSON dataset. Save them in `prefix_00_prerequisites_units.json` and update `prefix_master_units.json` so they are successfully passed downstream to the Synthesis step.

---

## STEP 3: Synthesis

### STEP 3.1: Generate Concept Tree Files

#### Input
- The consolidated and augmented JSON array of all "Atomic Units" completed at the end of Step 2.

#### Output
- `intermediate/{paper-name}/trees/XX-section/prefix-id-slug.tree` - Individual tree files

#### Process

1. **Create folder structure:**
   ```
   intermediate/{paper-name}/trees/
   ├── 01-introduction/
   ├── 02-background/
   ├── ...
   ├── 11-summary/
   └── person/
   ```

2. **For each unit, create a tree file:**
   ```tex
   \title{unit-title}
   \taxon{Definition | Axiom | Theorem | Lemma | Proof | Corollary | Remark | Algorithm}
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

#### Forester Syntax Reference

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
| Table | `\table{ \tr{ \th{header} } \tr{ \td{col1} \td{col2} } }` |
| Inline Code | `\code{code}` |
| Verbatim | `\startverb...\stopverb` |

#### Critical Syntax Rules

1. **Percentage Sign**: Always use `\%` (backslash percentage) instead of `%` in `.tree` files.
   - ❌ Wrong: `117%`
   - ✅ Correct: `117\%`

2. **Taxon Capitalization**: Use capital first letter for taxon values.
   - ❌ Wrong: `\taxon{definition}`
   - ✅ Correct: `\taxon{Definition}`
   - ❌ Wrong: `\taxon{reference}`
   - ✅ Correct: `\taxon{Reference}`

3. **Conjunctions**: Only put section-level conjunctions (connecting text between chapter/section transclusions in the main index file) within `\aside{...}`.
   - ✅ Correct (in main index file):
     ```tex
     \transclude-unexpanded{prefix-01-index}

     \aside{This leads us to the next chapter...}

     \transclude-unexpanded{prefix-02-index}
     ```
   - ❌ Wrong (in section index files): Do NOT put unit relation text in `\aside{}`:
     ```tex
     \transclude{prefix-concept}

     \aside{This leads us to the next concept...}  % WRONG in section index files

     \transclude{prefix-another-concept}
     ```
   - ✅ Correct (in section index files): Unit relation text should be plain paragraphs, not in `\aside{}`:
     ```tex
     \transclude{prefix-concept}

     \aside{Section-level conjunction only}

     \transclude{prefix-another-concept}
     ```
   - **Note**: In section index files, the text serves to indicate relations between units and should be written as regular paragraphs if needed, not wrapped in `\aside{}`.

4. **Tables**: Do NOT use LaTeX array environments (like `\begin{array}...\end{array}`) inside tex blocks. Instead, use Forester's native `\table{}` macro with `\tr{}`, `\th{}`, and `\td{}` elements.
   - ❌ Wrong:
     ```tex
     \p{
       ##{
         \begin{array}{|l|c|c|c|}
         \hline
         \text{Layer Type} & \text{Complexity} & \text{Sequential} \\
         \hline
         \text{Self-Attention} & O(n^2 \cdot d) & O(1) \\
         \hline
         \end{array}
       }
     }
     ```
   - ✅ Correct:
     ```tex
     \table{
       \tr{
         \th{Layer Type}
         \th{Complexity}
         \th{Sequential}
         \th{Path Length}
       }
       \tr{
         \td{Self-Attention}
         \td{#{O(n^2 \cdot d)}}
         \td{#{O(1)}}
         \td{#{O(1)}}
       }
       \tr{
         \td{Recurrent}
         \td{#{O(n \cdot d^2)}}
         \td{#{O(n)}}
         \td{#{O(n)}}
       }
       \tr{
         \td{Convolutional}
         \td{#{O(k \cdot n \cdot d^2)}}
         \td{#{O(1)}}
         \td{#{O(\log_k(n))}}
       }
     }
     ```
   - **Key elements**: Use `\tr{}` for each row, `\th{}` for header cells, and `\td{}` for data cells. Math formulas inside cells use `#{...}` notation.

5. **Transclude Titles**: Transcluding automatically includes the title (which is bolded). Do NOT add a separate `\p{\strong{Title}}` before transclude.
   - ❌ Wrong:
     ```tex
     \p{
       \strong{Important Concept}
     }

     \transclude{important-concept}
     ```
   - ✅ Correct:
     ```tex
     \transclude{important-concept}
     ```

6. **Author in Main Index**: Do NOT include author information in the content of the main index file. The author is already specified in the `\author{}` metadata field and will be displayed automatically.
   - ❌ Wrong:
     ```tex
     \author{author-id}

     \p{
       \strong{Author}
     }

     \p{
       Author Name
     }

     \p{
       \strong{Abstract}
     }
     ...
     ```
   - ✅ Correct:
     ```tex
     \author{author-id}

     \p{
       \strong{Abstract}
     }
     ...
     ```

#### Guidelines
- Use definitions from the paper when available
- Search the internet for standard definitions if not in paper
- Use `\strong{}` for key terminology
- Use `\mark{}` for important insights
- Keep math in proper notation: `#{d_k}` for inline, `##{...}` for block

---

### STEP 3.2: Generate Relations File

#### Input
- Registry files from STEP 2
- Concept tree files from STEP 3.1

#### Output
- `intermediate/{paper-name}/trees/prefix-relations.tree` - Single relations file

#### Process

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

#### Common Relation Types
- `is-a` - Taxonomic relationship
- `is-composed-of` - Part-whole relationship
- `is-used-in` - Usage relationship
- `is-replaced-by` - Replacement/evolution
- `enables` - Enables something
- `requires` - Dependency
- `improves` - Improvement relationship
- `is-an-instance-of` - Instance relationship

#### Guidelines
- Multi-word relationships are allowed: `is-composed-of`, `is-replaced-by`
- Create relations for ALL meaningful connections between concepts
- Aim for comprehensive semantic graph coverage

---

### STEP 3.3: Generate Chapter Index Files

#### Input
- Ingestion markdown files from STEP 1
- Concept tree files from STEP 3.1

#### Output
- `intermediate/{paper-name}/trees/XX-section/prefix-XX-index.tree` - Per-chapter indices

#### Process

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

#### Guidelines
- Match the narrative flow of the original ingestion markdown
- First mention of a concept → link to its definition: `[concept](prefix-concept)`
- If the concept IS defined in this chapter → use `\transclude{prefix-concept}`
- Use `\transclude{}` for concepts defined in the current chapter
- Use `\aside{}` for conjunctions between sections for narrative flow

---

### STEP 3.4: Generate Final Paper Index

#### Input
- Chapter index files from STEP 3.3
- meta.json from STEP 1

#### Output
- `intermediate/{paper-name}/trees/prefix-index.tree` - Main paper index

#### Process

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

#### Guidelines
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
│   ├── prefix_01_introduction_units.json
│   ├── prefix_02_background_units.json
│   └── prefix_master_units.json
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

- [ ] STEP 2: Structural Analysis (Rhetorical Units)
  - [ ] Per-section unit files created (`*_units.json`)
  - [ ] Master units file consolidated
  - [ ] All atomic units identified and categorized with Mathematical Taxons
  - [ ] Relationships between units captured (supports, contradicts, extends, etc.)
  - [ ] Content rewritten to be concise, dense, and self-contained

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
  - [ ] No redundant title paragraphs before `\transclude{}`

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
- **No title before transclude**: `\transclude{}` auto-includes the bolded title, so don't add `\p{\strong{Title}}` before it
