# Porting Checklist

Use this when adapting the layout algorithm from `theme/graph.js` to another project.

## Input Schema

- Node IDs must be unique and stable strings.
- Edges use `source` / `target` (not `from` / `to`).
- Optional `weights` map for layering tiebreaks.
- Optional `relation` and `mentioned` fields on edges (domain-specific).

## Algorithm Port

Entry point shape:
```
runLayeredCrossingHcaLayout(rootId, weights, degreeMap)
  → Map<nodeId, {x, y}>
```

Include these internals in order:
1. `getWeaklyConnectedComponents()` — weakly connected component detection.
2. `assignComponentLayers()` — BFS layer assignment from root.
3. `buildProperComponentGraph()` — dummy node expansion for long edges.
4. `runCrossingReduction()` — multi-start hybrid crossing minimization.
5. `runHcaAssignment()` — Brandes-Koepf 4-biased HCA.
6. Coordinate scaling (× 210 horizontal, × 160 vertical).
7. Component packing (guillotine row layout).

## HCA Integration

The HCA function (`runHcaAssignment`) expects:
- `orders`: Map of rank → ordered array of node IDs.
- `ranks`: Map of node ID → rank integer.
- `edges`: array of `{ from, to }` on the proper (dummy-expanded) graph.

It returns: Map of node ID → x coordinate (unscaled integer).

Configuration points:
- `min_sep`: minimum separation between nodes (currently 1).
- `type2_mode`: `"ignore"` unless strict handling needed.

## Output Compatibility

- Current convention: Cytoscape.js `preset` layout with `{x, y}` per node.
- Dummy nodes rendered with CSS class `dummy` (smaller, no label).
- Dummy edges rendered with class `dummy-edge` / `dummy-terminal`.
- Polyline edges reconstructed via `getFullPolylineEdges()`.

If porting to a different renderer:
- Preserve `isDummy` flag to distinguish real vs. dummy nodes.
- Emit turning points in source→target order for polyline rendering.
- Decide coordinate convention (center vs. top-left) for your renderer.

## Quality + Regression Tests

- Crossing count improves vs. initial random order.
- Deterministic output for fixed `stableHash` seed.
- Node/edge count preserved after dummy removal.
- Same-layer edges: current impl routes them normally (no rejection).
- Components do not overlap after packing.

## Performance Notes

For ~100 nodes, the browser-tuned defaults work well:
- `multiStartRuns = 4`, `sweepRounds = 6`, `transposeRounds = 12`.

For larger graphs (500+ nodes), consider:
- Reducing multi-start runs to 2.
- Adding early-exit when crossing improvement plateaus.
- Web Worker offloading to avoid blocking the main thread.

For higher quality at the cost of speed:
- Increase to `multiStartRuns = 12`, `sweepRounds = 8`, `transposeRounds = 20`.
- Add sifting rounds (move one vertex across all positions per layer).
- Optional exact refinement with ILP solver (not implemented in JS version).
