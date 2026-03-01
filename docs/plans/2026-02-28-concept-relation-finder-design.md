# Concept Relation Finder -- Design

## Problem

After Step 2 (concept registry) and Step 3.1 (concept definition research), we have a set of defined concepts but no semantic relations between them. Step 3.2 of the pipeline requires a `{prefix}-relations.tree` file capturing all meaningful connections.

The challenge is discovering relations comprehensively -- both those explicitly stated in the source document and those logically inferable from concept definitions.

## Decisions

- **Comprehensive coverage with provenance**: Capture all plausible relations. Each relation carries a boolean indicating whether it is explicitly mentioned in the source document or inferred.
- **Pairwise concept reasoning**: For each concept, reason about its relationships to other concepts using the full concept list and ingestion text as evidence.
- **Tag-based filtering**: Each concept's `.tree` file includes tags (added by an updated concept-definition-researcher). Only concept pairs sharing at least one tag are considered, reducing the search space significantly.
- **Python orchestrator + subagents**: A Python script handles tag matching and pair computation; Claude subagents do the reasoning per concept.
- **Extended `\relation` macro**: The existing 3-arg macro becomes 4-arg to carry the `mentioned` boolean. Existing relation files are migrated.

## Architecture

### Components

1. **`find_relations.py`** -- Python script at project root
   - Reads all `.tree` concept files to extract tags
   - Reads the master registry for the full concept list and tree IDs
   - Computes concept pairs that share at least one tag
   - For each concept, sends its tag-matched candidates + ingestion context to a Claude subagent via `claude -p`
   - Collects JSON relation outputs from subagents
   - Deduplicates (if both A->B and B->A runs produce the same relation, keep one)
   - Merges into a single `intermediate/{document}/trees/{prefix}-relations.tree`

2. **`/find-concept-relations`** -- slash command skill in `.claude/skills/`
   - Input: one focus concept, its tags, a list of candidate related concepts with their tags and tree IDs, the document name, and ingestion path
   - Process: for each candidate, determine if a relation exists, what kind, and whether the source document explicitly states it
   - Output: structured JSON to stdout (not a .tree file -- the Python script handles assembly)

3. **`\relation` macro update** -- `trees/utils/base-macros.tree`
   - Extended from 3 args to 4: `\relation{source}{type}{target}{mentioned}`
   - `{true}` = relation is explicitly stated or clearly implied in the source text
   - `{false}` = relation is inferred from concept definitions or domain knowledge
   - All existing relation files migrated (existing relations get `{true}`)

### Data Flow

```
concept .tree files (with tags) ──┐
                                  ├──> find_relations.py
ingestion/*.md                   ──┤       │
master_registry.json             ──┘       │
                                           ├── for each concept:
                                           │     claude -p "/find-concept-relations ..."
                                           │     └── returns JSON relations
                                           │
                                           └── merge & deduplicate
                                                     │
                                                     ▼
                                        {prefix}-relations.tree
```

### Subagent Interface

The Python script sends per concept:

```
/find-concept-relations
focus-concept="Multi-Head Attention"
focus-tree-id="006-multi-head-attention"
focus-tags=["attention", "architecture"]
candidates=[{"name": "Scaled Dot-Product Attention", "tree_id": "006-scaled-dot-product-attention", "tags": ["attention", "computation"]}, ...]
document="attention-is-all-you-need"
ingestion-path="intermediate/attention-is-all-you-need/ingestion/"
prefix="006"
```

The subagent returns JSON:

```json
[
  {"source": "006-multi-head-attention", "relation": "is-composed-of", "target": "006-attention-head", "mentioned": true},
  {"source": "006-multi-head-attention", "relation": "uses", "target": "006-linear-projection", "mentioned": true},
  {"source": "006-multi-head-attention", "relation": "enables", "target": "006-parallelization", "mentioned": false}
]
```

### Relation Types

Reuse the existing relation vocabulary from the project:

- Compositional: `is-composed-of`, `contains`, `is-component-of`
- Hierarchical: `is-a`, `is-specialized-by`, `generalizes`
- Causal: `enables`, `requires`, `is-consequence-of`
- Similarity: `is-also-known-as`, `defines`, `implements`, `uses`
- Contrast: `contrasts-with`, `is-different-from`
- Extension: `extends`, `is-derived-from`, `improves`
- Domain-specific types are allowed when standard ones don't fit

### Migration

A script updates all existing `\relation{a}{b}{c}` calls to `\relation{a}{b}{c}{true}` since all existing relations were derived from source documents.

The `\relation` macro in `base-macros.tree` changes from:

```
\def\relation[source][desc][target]{
  \<html:span>[data-source]{\source}[data-relation]{\desc}[data-target]{\target}[class]{semantic-relation}
}
```

To:

```
\def\relation[source][desc][target][mentioned]{
  \<html:span>[data-source]{\source}[data-relation]{\desc}[data-target]{\target}[data-mentioned]{\mentioned}[class]{semantic-relation}
}
```

## Prerequisites

- Concept `.tree` files must include tags (requires updating the concept-definition-researcher skill)
- The tag format in `.tree` files needs to be defined (e.g., `\meta{tags}{attention, architecture}` or `\tag{attention}`)

## Output Example

```
\title{Relations: Attention Is All You Need}
\taxon{Metadata}
\date{2026-02-28}
\author{vaswani-et-al}
\import{base-macros}

% Core Architecture
\relation{006-transformer}{is-composed-of}{006-encoder}{true}
\relation{006-transformer}{is-composed-of}{006-decoder}{true}
\relation{006-encoder}{contains}{006-encoder-self-attention}{true}

% Inferred Relations
\relation{006-multi-head-attention}{enables}{006-parallelization}{false}
```
