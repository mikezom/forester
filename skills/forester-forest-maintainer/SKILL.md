---
name: forester-forest-maintainer
description: Maintain and extend the Forester knowledge-forest project at /Users/wanyu/Sync/Study/forest. Use when tasks involve editing or generating .tree notes, updating semantic relations via \relation entries, validating transcludes/links and tree IDs, regenerating output/graph.json with aggregate_graph.py, changing theme rendering in theme/*.xsl and theme/*.js, or working with the graph visualization in graph.js.
---

# Forester Forest Maintainer

## Overview

This project is a Forester-based personal knowledge forest that transforms source documents (academic papers, books, guides) into interconnected concept graphs. Each document goes through a 7-step pipeline (orchestrated by `skills/forester-pipeline/`) that extracts concepts, defines them as `.tree` files, discovers semantic relations, and assembles chapter/paper indices. The result is a static site with an interactive Cytoscape.js graph panel showing concept relationships.

Read `references/project-map.md` at the start of non-trivial tasks for the full repository layout, pipeline flow, and conventions.

## Workflow Selection

Choose the workflow that matches the request:

1. Use **Tree Content Workflow** for `.tree` creation, edits, reorganization, and chapter/index updates.
2. Use **Relations and Graph Workflow** for `\\relation{}` maintenance and graph visualization issues.
3. Use **Theme Workflow** for XSL/CSS/JS behavior in `theme/`.
4. Run `scripts/validate_forest.py` after structural or cross-file edits.

## Tree Content Workflow

1. Locate the relevant area in `trees/` and keep the existing prefix-based ID scheme (for example, `008-*`).
2. Keep metadata blocks at the top (`\\title`, `\\date`, `\\author`; include `\\taxon` where appropriate).
3. Prefer these conventions while editing:
   - Use `\\transclude{...}` for in-flow concepts.
   - Use `\\transclude-unexpanded{...}` for large chapter blocks.
   - Use `\\aside{...}` for connective narrative text between transclusions.
   - Escape percentages as `\\%`.
   - Keep taxon values capitalized (`Definition`, `Reference`, `Metadata`, `Person`).
4. Preserve file-local style: concise paragraphs, explicit highlights with `\\mark{...}`, and links on first mention.

## Relations and Graph Workflow

1. Edit relation files (for example `*-relations.tree`) using the 4-argument form: `\\relation{source}{relation}{target}{mentioned}`.
   - Use `{true}` for the 4th arg when the relation is explicitly mentioned in the source text, `{false}` otherwise.
   - Use `scripts/migrate_relations.py` to batch-migrate any old 3-arg relations to 4-arg form.
2. Keep source and target aligned with existing tree IDs.
3. Prefer concise hyphenated relation labels (for example `is-a`, `supports`, `extends`, `is-part-of`).
4. **One relation per concept pair**: For any unordered pair {A, B}, there must be at most one relation. Avoid both:
   - Multiple relations on the same directed pair (e.g., A→"contains" + A→"depends-on" toward same B).
   - Redundant inverse pairs (e.g., A→"contains"→B and B→"is-part-of"→A).
   - `graph.js` enforces this at runtime by deduplicating edges (keeping the first encountered, logging dropped duplicates to the console), but the source `.tree` files should be kept clean.
5. After relation changes, regenerate graph data:
   - `python3 aggregate_graph.py`
6. Ensure graph consumption path stays intact:
   - Relation markup in trees -> Forester XML in `output/` -> `output/graph.json` -> `theme/graph.js` runtime fetch.

## Theme Workflow

1. Edit source files first (`theme/javascript-source/forester.js`, `theme/tree.xsl`, `theme/style.css`).
2. Rebundle JS only when needed:
   - `bash theme/bundle-js.sh`
3. Keep graph panel hooks in sync:
   - `theme/tree.xsl` script includes and `<aside id="graph-panel">`
   - `theme/graph.js` fetch path and ID extraction logic
4. Avoid duplicating script includes and remove accidental duplicates when touched.
5. When editing `theme/graph.js`, keep `output/graph.js` in sync (it is a deployed copy).

### Graph Visualization Architecture (theme/graph.js)

Key design aspects to preserve when modifying graph.js:

- **Edge deduplication** at the top of `initGraph()`: canonicalizes each {source, target} pair and keeps only the first edge per unordered pair. Logs dropped duplicates via `console.warn`.
- **Two display modes**: Layered Crossing + HCA layout (default, Sugiyama-style with dummy nodes for long-span edges) and Force-directed (CoSE). Toggled via a UI button.
- **Two page states**: State 1 (non-concept page: shows relations among transcluded concepts) and State 2 (concept page: shows the concept's direct neighbors).
- **Node weights**: PageRank + degree hybrid, or precomputed weights from `graph.json`.
- **Card stack UI**: Clicking a node fetches its tree XML and renders content in a slide-in card panel.
- **Polyline edges**: Long-span edges are split through dummy nodes; relation labels are placed on the middle segment.

## Validation and Verification

Run project validation after meaningful edits:

```bash
python3 skills/forester-forest-maintainer/scripts/validate_forest.py
```

Use `--strict` only when you explicitly want a failing exit code on unresolved errors.

For local manual preview workflows (if tools are installed):

```bash
forester build
python3 aggregate_graph.py
live-server --port=1313 --host=localhost output
```

Use `watchexec -w trees -e tree -r -- forester build` for iterative editing when requested.
