# Forest

A personal knowledge forest built on [Forester](https://www.jonmsterling.com/jms-005P.xml) for ingesting documents (papers, books) and organizing their concepts into an interconnected, navigable knowledge graph.

## What it does

Documents go through a multi-step pipeline:

1. **Ingestion** — extract and chunk documents into markdown sections
2. **Concept registry** — identify concepts needing definitions
3. **Tree generation** — create Forester `.tree` files for definitions, relations, chapter indices, and paper indices
4. **Validation** — verify completeness and correctness of generated trees

The output is a static HTML forest with full-text search, keyboard navigation, and interactive graph visualization.

## Structure

```
trees/           # Forester tree files (concepts, indices, relations)
intermediate/    # Pipeline working directory (ingestion, analysis, generated trees)
resources/       # Source documents (PDFs, etc.)
assets/          # Static assets
theme/           # Forester base theme (git submodule)
skills/          # Claude Code skills for pipeline automation
scripts/         # Utility scripts
docs/            # Design documents and plans
```

## Setup

Requires [Forester](https://www.jonmsterling.com/jms-005P.xml) installed.

```sh
# Install theme dependencies
cd theme && npm install && cd ..

# Build the forest
forester build
```

The built site will be in `output/`.

## Documents

The forest currently includes notes on topics ranging from machine learning papers (e.g. "Attention Is All You Need") to finance books (e.g. 手把手教你读财报), with shared concept definitions and cross-document relations.
