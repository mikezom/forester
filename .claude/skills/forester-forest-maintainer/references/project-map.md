# Project Map

## What This Project Is

A Forester-based personal knowledge forest that transforms source documents (academic papers, books, guides) into interconnected concept graphs. Each document goes through a 7-step pipeline (see `.claude/skills/forester-pipeline/`) that extracts concepts, defines them as `.tree` files, discovers semantic relations between them, and assembles chapter/paper indices. The result is a static site with a Cytoscape.js graph panel showing concept relationships.

## Repository Layout

```
forest/
├── forest.toml                  # Forester config (trees=["trees"], assets=["assets"])
├── aggregate_graph.py           # Aggregates relation spans from output XML into output/graph.json
├── trees/                       # Source .tree files, the heart of the forest
│   ├── index.tree               # Root: "Root of the World"
│   ├── utils/base-macros.tree   # Shared macros (\relation, \aside, \mark, tables, etc.)
│   ├── people/                  # Person trees (\taxon{Person})
│   ├── definitions/             # Standalone definition trees
│   ├── books/                   # Book study notes (b01-*, b02-*)
│   ├── 001-learning-forester/   # Forester learning notes
│   ├── 002-Stock-Trading/       # Investment strategies
│   ├── 003-Reading/             # Reading notes
│   ├── 004-Semantic-Relation-Test/
│   ├── 005-gemini-semantic-relation-homework/  # Category theory concepts
│   ├── 006-glm-attention-is-all-you-need/      # "Attention Is All You Need" paper
│   ├── 007-glm-hand-to-hand/                   # 手把手教你读财报 (v1)
│   ├── 008-glm-hand-to-hand-v2/                # 手把手教你读财报 (v2)
│   └── 009-glm-claude-skill/                   # Building Skills for Claude guide (158+ files)
├── intermediate/                # Pipeline workspace (documents in progress)
│   ├── attention-is-all-you-need/
│   ├── building-skill-for-claude/
│   ├── 手把手教你读财报/
│   └── 手把手教你读财报2021/
├── output/                      # Forester build output (XML/HTML) + graph.json
├── theme/                       # Forester theme (submodule from sr.ht/~jonsterling/forester-base-theme)
│   ├── tree.xsl                 # Page scaffold, script includes, graph panel mount
│   ├── graph.js                 # Graph visualization (Cytoscape.js): filtering, layout, card UI
│   ├── style.css                # Main stylesheet
│   ├── forester.js              # Bundled JS (from javascript-source/forester.js via bundle-js.sh)
│   ├── javascript-source/       # JS source before bundling
│   ├── bundle-js.sh             # esbuild bundler script
│   ├── fonts/                   # Inria Sans + KaTeX fonts
│   └── core.xsl, default.xsl, links.xsl, metadata.xsl  # Other XSL templates
├── resources/                   # Source documents (PDFs, etc.)
├── scripts/
│   └── migrate_relations.py     # Migrates \relation{a}{b}{c} to \relation{a}{b}{c}{true}
├── docs/plans/                  # Design documents
└── .claude/skills/              # All Claude Code skills
    ├── forester-forest-maintainer/  # Forest maintenance workflows
    ├── forester-pipeline/           # Pipeline orchestrator (7-step sequencing)
    ├── paper-ingestion/             # Step 1: PDF/text to chunked markdown
    ├── concept-registry/            # Step 2: Concept identification and cataloging
    ├── concept-definition-researcher/  # Step 3.1: Generate concept .tree files
    ├── research-concepts/              # Step 3.1 orchestrator
    ├── find-concept-relations/         # Step 3.2 helper: per-concept relation finding
    ├── find-relations/                 # Step 3.2: Orchestrate relation discovery
    ├── generate-chapter-index/         # Step 3.3: Per-chapter index .tree files
    ├── generate-paper-index/           # Step 3.4: Top-level paper index .tree
    ├── validate-document/              # Step 4: Validation + person tree
    └── layered-crossing-hca-layout/    # Graph layout algorithm reference
```

## Data and Rendering Flow

1. Author content in `trees/**/*.tree` (or run the pipeline to generate trees from documents).
2. Build with Forester (`forester build`) to produce XML/HTML in `output/`.
3. Run `python3 aggregate_graph.py` to extract `<html:span>` relation markers from output XML into `output/graph.json`.
4. `theme/tree.xsl` injects Cytoscape script tags and `<aside id="graph-panel">` into each page.
5. `theme/graph.js` fetches `graph.json` at runtime and renders an interactive concept graph.

## Pipeline Flow (Document to Forest)

```
Source document (PDF/text)
  → Step 1: paper-ingestion        → meta.json + chunked markdown in intermediate/<doc>/ingestion/
  → Step 2: concept-registry       → per-section + master registry JSONs in intermediate/<doc>/structural-analysis/
  → Step 3.1: research-concepts    → concept .tree files in intermediate/<doc>/trees/
  → Step 3.2: find-relations       → relations .tree file
  → Step 3.3: generate-chapter-index → per-chapter index .tree files
  → Step 3.4: generate-paper-index → main document index .tree
  → Step 4: validate-document      → person tree + validation report
  → Deploy: copy trees to trees/<prefix>-<doc>/, forester build, aggregate_graph.py
```

## Tree Conventions

- **Prefix-based IDs** encoded in filenames (e.g., `008-net-profit-quality-ratio.tree`).
- **File roles**:
  - Concept/definition trees (`\taxon{Definition}`)
  - Section index trees (`...-index.tree`, usually `\taxon{Reference}`)
  - Relation trees (`...-relations.tree`, usually `\taxon{Metadata}`)
  - People trees (`trees/people/*.tree`, `\taxon{Person}` + `\meta{...}`)
- **Metadata blocks** at the top: `\title`, `\date`, `\author`; `\taxon` where appropriate.
- **Transclusion**: `\transclude{tree-id}` for in-flow, `\transclude-unexpanded{tree-id}` for large blocks.
- **Shared macros** in `trees/utils/base-macros.tree`: `\relation`, `\aside`, `\mark`, table helpers.

## Relation and Graph Conventions

- Semantic edges use `\relation{source-id}{relation-label}{target-id}{mentioned}` (4-arg form).
- `aggregate_graph.py` parses `data-source`, `data-relation`, `data-target`, `data-mentioned` from output XML spans.
- `graph.json` format: `{ "nodes": { id: label }, "edges": [{ source, relation, target, mentioned }] }`.
- **Edge deduplication**: `graph.js` enforces that each unordered pair {A, B} has at most one edge. Duplicates (same-direction with different relations, or bidirectional inverse pairs like A→"contains"→B + B→"is-part-of"→A) are dropped at load time with console warnings.
- Prefer concise hyphenated relation labels (e.g., `is-a`, `supports`, `extends`, `is-part-of`).

## Graph Visualization (theme/graph.js)

- **Two display modes**: Layered Crossing + HCA (default) and Force-directed (CoSE). Toggled via UI button.
- **Two states**: State 1 (default page, shows relations among transcluded concepts) and State 2 (concept page, shows the concept's direct relations).
- **Node weights**: Computed via PageRank + degree, or precomputed from `graph.json`.
- **Card stack UI**: Clicking a node fetches the tree's XML and displays its content in a slide-in card.
- **Edge label display**: Labels shown on hover/selection; polyline edges through dummy nodes for long-span edges.

## Practical Checks

- Run `python3 .claude/skills/forester-forest-maintainer/scripts/validate_forest.py` after edits touching links/relations.
- Re-run `python3 aggregate_graph.py` after relation changes.
- Prefer editing source files and re-bundling instead of patching generated artifacts.
- For local preview: `forester build && python3 aggregate_graph.py && live-server --port=1313 --host=localhost output`.
