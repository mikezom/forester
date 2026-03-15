---
name: layered-crossing-hca-layout
description: End-to-end workflow for layered graph layout: component detection, BFS layering, long-edge dummy expansion, hybrid crossing reduction (multi-start sweep + transpose), Brandes-Koepf horizontal coordinate assignment, and multi-component packing. Reference implementation lives in theme/graph.js and renders via Cytoscape.js.
---

# Layered Crossing + HCA Layout

## Overview

This skill documents the Sugiyama-style layered layout pipeline used in the Forester
knowledge-graph renderer. The reference implementation is a single JavaScript module
(`theme/graph.js`, function `runLayeredCrossingHcaLayout`) that runs client-side and
feeds coordinates to Cytoscape.js via `preset` layout mode.

Use this skill to understand, modify, or port the layout algorithm.

## Data Flow

```
aggregate_graph.py → output/forest/graph.json → theme/graph.js → Cytoscape.js
```

1. **aggregate_graph.py** scans Forester XML output, extracts nodes (titles) and
   edges (semantic relations), writes `graph.json`.
2. **theme/graph.js** fetches `graph.json`, runs the layout pipeline, renders via
   Cytoscape.js in the `#graph-panel` container.

## Input Contract (graph.json)

```json
{
  "nodes": { "node_id": "Node Title", ... },
  "edges": [
    { "source": "id", "target": "id", "relation": "type", "mentioned": true|false }
  ],
  "weights": { "node_id": 2.5, ... }
}
```

- `nodes`: map of ID → display title.
- `edges`: directed edges with `source`, `target`, `relation`, `mentioned`.
- `weights`: optional per-node weight used for layering tiebreaks.

## Pipeline Phases

1. **Component detection** — find weakly connected components via BFS.
2. **BFS layer assignment** — assign ranks from a component root; outgoing edges
   go down, incoming go up; fallback median rank for mixed-connectivity nodes.
3. **Dummy expansion** — insert dummy nodes for edges spanning >1 layer; split
   into adjacent-layer segments; track `isDummy` flag.
4. **Crossing reduction** — hybrid algorithm:
   - 4 multi-start runs with `stableHash`-based perturbation.
   - 6 bidirectional sweep rounds (median primary, barycenter tiebreak).
   - 12 transpose rounds (adjacent-pair swaps while crossings decrease).
   - Keep best ordering by total crossing count.
5. **Brandes-Koepf HCA** — 4 biased assignments (`up/down × left/right`), align
   to narrowest, combine by median.
6. **Coordinate scaling** — `x = hcaX × 210`, `y = layerIndex × 160`.
7. **Component packing** — guillotine row packing with `xGap=180`, `yGap=180`,
   `targetRowWidth = max(1000, canvasWidth × 1.8)`.
8. **Render** — Cytoscape.js `preset` layout with computed positions. Dummy nodes
   get CSS class `dummy`; dummy edges get `dummy-edge` / `dummy-terminal`.

## Internal Node Representations

**Real node:** `{ id, label, isDummy: false }`
**Dummy node:** `{ id: "dummy_{edgeId}_{i}", label: "", isDummy: true }`

## Rendering Modes

The graph panel supports two layout modes toggled by `isLayeredMode`:

- **Layered (default):** `runLayeredCrossingHcaLayout()` → preset positions.
- **Force-directed fallback:** Cytoscape COSE layout (`nodeRepulsion: 400000`,
  `idealEdgeLength: 150`).

## Key Functions (theme/graph.js)

| Function | Purpose |
|----------|---------|
| `runLayeredCrossingHcaLayout()` | Full pipeline entry point |
| `getWeaklyConnectedComponents()` | BFS component detection |
| `assignComponentLayers()` | BFS rank assignment |
| `buildProperComponentGraph()` | Dummy node expansion |
| `runCrossingReduction()` | Multi-start hybrid crossing minimization |
| `runHcaAssignment()` | Brandes-Koepf 4-assignment HCA |
| `getFullPolylineEdges()` | Reconstruct polylines through dummy chains |
| `computeNodeDegrees()` | In/out/total degree computation |
| `computeNodeWeights()` | Weight from graph.json or degree fallback |

## Validation Checklist

- Node/edge counts match original graph after dummy removal.
- Output nodes have numeric `x`, `y`.
- Crossing count is reduced vs. initial ordering.
- Polyline edges traverse dummy nodes in source→target order.
- Running twice with same seed yields identical layout.
- Components are non-overlapping after packing.

## References

- Reference implementation: `theme/graph.js` (lines ~1002–1736)
- Graph data generator: `aggregate_graph.py`
- Implementation playbook: `references/workflow-playbook.md`
- Porting checklist: `references/porting-checklist.md`
