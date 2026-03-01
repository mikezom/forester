# Forest

A document-to-knowledge-graph pipeline built on [Forester](https://www.jonmsterling.com/jms-005P.xml). It ingests papers and books, extracts concepts, discovers semantic relations, and produces a static HTML forest with full-text search, keyboard navigation, and interactive graph visualization.

## Pipeline

The pipeline transforms source documents into interconnected Forester trees through a sequence of steps, each producing artifacts consumed by the next.

```
Step 1: Ingestion          → markdown chunks + meta.json
Step 2: Concept Registry   → per-section + master registry (human review checkpoint)
Step 3.1: Research Concepts → concept .tree definition files
Step 3.2: Find Relations    → semantic relations .tree file  (parallel with 3.3)
Step 3.3: Chapter Indices   → chapter index .tree files      (parallel with 3.2)
Step 3.4: Paper Index       → top-level paper index .tree
Step 4: Validation          → person tree + validation report
```

### Step 1: Ingestion

Extracts and chunks a source document (PDF, text) into numbered markdown sections with a `meta.json` metadata file. Each section targets 200-800 words and preserves the document's structure.

**Output:** `intermediate/{document}/ingestion/`

### Step 2: Concept Registry

Scans ingestion markdown to identify all domain-specific concepts (architectures, mechanisms, metrics, terminology). Produces per-section registries and a consolidated master registry. The user reviews the master registry before proceeding — this is a checkpoint to remove trivial terms before expensive downstream processing.

**Output:** `intermediate/{document}/structural-analysis/{prefix}_master_registry.json`

### Step 3.1: Research Concepts

Generates a `.tree` definition file for each concept in the master registry. Each definition includes the concept name, taxon, tags (for relation discovery), and a concise description sourced from the document or authoritative references.

```sh
python .claude/skills/research-concepts/research_concepts.py <document-name>
python .claude/skills/research-concepts/research_concepts.py <document-name> --dry-run
```

**Output:** `intermediate/{document}/trees/{prefix}-{concept}.tree`

### Step 3.2: Find Relations

Discovers semantic relations between concepts using tag-based candidate pairing and Claude reasoning. Produces a single relations file with typed, directional edges (e.g. `is-composed-of`, `enables`, `contrasts-with`).

```sh
python .claude/skills/find-relations/find_relations.py <document-name>
python .claude/skills/find-relations/find_relations.py <document-name> --dry-run
```

**Output:** `intermediate/{document}/trees/{prefix}-relations.tree`

### Step 3.3: Chapter Indices

Creates chapter index `.tree` files that weave narrative text with `\transclude{}` of concept definitions, following the source document's flow.

```
/generate-chapter-index chapter="01" chapter-title="Introduction" \
  document="<document-name>" prefix="<prefix>" author-id="<author-id>"
```

### Step 3.4: Paper Index

Assembles all chapter indices into a top-level document overview with abstract, structure summary, semantic relations, and lasting impact sections.

```
/generate-paper-index document="<document-name>" prefix="<prefix>" author-id="<author-id>"
```

### Step 4: Validation

Creates the author/person tree and validates all generated `.tree` files for metadata completeness, syntax correctness, and referential integrity.

```
/validate-document document="<document-name>" prefix="<prefix>" author-id="<author-id>"
```

### Deploying to the Forest

After validation, copy the generated trees into the main `trees/` directory and build:

```sh
cp -r intermediate/<document>/trees/* trees/<document-folder>/
forester build
```

## Project Structure

```
trees/           # Forester .tree files (deployed concepts, indices, relations)
intermediate/    # Pipeline working directory (per-document ingestion & generation)
resources/       # Source documents (PDFs, etc.)
assets/          # Static assets
theme/           # Custom Forester theme (git submodule)
skills/          # Claude Code skills for pipeline automation
scripts/         # Utility scripts (graph aggregation, validation)
```

## Setup

Requires [Forester](https://www.jonmsterling.com/jms-005P.xml) (v5.0+) and Node.js.

```sh
git clone --recurse-submodules <this-repo-url>

# Install theme dependencies and set up fonts (see theme/README.md)
cd theme && npm install && cd ..

# Build the forest
forester build
```

The built site will be in `output/`.

## Conventions

- **Prefix**: each document gets a unique 3-digit prefix (e.g. `006`) for all its tree IDs.
- **Tree ID**: `{prefix}-{concept-slug}` (e.g. `006-multi-head-attention`).
- **Author ID**: `firstname-lastname` or `lastname-et-al` for multi-author works.

## License

MIT
