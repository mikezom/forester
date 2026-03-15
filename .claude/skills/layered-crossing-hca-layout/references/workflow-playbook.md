# Workflow Playbook

Describes the algorithm phases as implemented in `theme/graph.js`.

## 1) Component Detection

1. Build undirected adjacency from all edges.
2. BFS from each unvisited node to find weakly connected components.
3. Return `{ nodeIds, nodeSet, edges }` per component.
4. Each component is laid out independently, then packed together.

## 2) Layer Assignment (BFS from Root)

1. Pick root: the current page node if in the component, else the first node.
2. BFS outward from root:
   - outgoing edges assign `rank + 1` to target,
   - incoming edges assign `rank - 1` to source.
3. For nodes with mixed connectivity, use median of already-assigned neighbors.
4. Normalize all ranks so minimum is 0.
5. Group nodes into layers by rank index.

## 3) Dummy Expansion (Proper Graph)

For each edge spanning more than one layer:
1. Insert dummy nodes at each intermediate layer (`isDummy: true`).
2. Split into adjacent-layer segments.
3. Preserve the relation label only on the middle segment.
4. Build edge-path mapping for later polyline reconstruction.

Result: proper layered graph where every edge spans exactly one layer.

## 4) Crossing Reduction (Hybrid)

### Multi-start (4 runs)

Each run starts with a perturbed initial order:
- `stableHash`-based seed determines shuffle/reverse per layer.
- Keeps best result across all runs.

### Bidirectional Sweep (6 rounds per run)

Each round:
1. **Downward pass:** reorder each layer based on upper neighbors.
2. **Upward pass:** reorder each layer based on lower neighbors.

Sort keys for `reorderLayer()`:
- Primary: **median** index of connected nodes in the fixed layer.
- Secondary: **barycenter** (average index of connected nodes).
- Tertiary: original position (stability).

### Transpose (12 rounds per run)

1. For each layer, try swapping adjacent node pairs.
2. Accept swap only if total crossing count decreases.
3. Stop early if a full round produces no improvement.

### Selection

Keep the ordering with the lowest total crossing count across all multi-start runs.

## 5) Brandes-Koepf Horizontal Coordinate Assignment

Feed the crossing-reduced proper graph to HCA:

1. Compute 4 biased assignments (`up/down × left/right`):
   - Traverse layers in direction order.
   - Desired x = median of already-assigned neighbor x-coordinates.
   - Compact: ensure x >= previous node's x + 1 (no overlaps).
2. Align all 4 to the narrowest-width assignment (center alignment).
3. Combine per node: take median of the 4 aligned x values.

Outputs `x` for all nodes (real + dummy).

## 6) Coordinate Scaling

```
x_final = hca_x × 210    (horizontal spacing)
y_final = layer_rank × 160  (vertical spacing)
```

## 7) Component Packing

1. Sort components by: highlight priority (current page first), then root name.
2. Pack left-to-right in rows:
   - `xGap = 180` between component bounding boxes.
   - `yGap = 180` between rows.
   - `targetRowWidth = max(1000, canvasWidth × 1.8)`.
3. Center final bounding box at origin.

## 8) Polyline Reconstruction

For edges that passed through dummy nodes:
- `getFullPolylineEdges()` traverses the dummy chain.
- Collects `(x, y)` at each dummy node as turning points.
- Stores ordered points for edge rendering.

## Tuned Defaults (Browser-Optimized)

| Parameter | Value | Notes |
|-----------|-------|-------|
| `multiStartRuns` | 4 | Tuned down from 12 for browser perf |
| `sweepRounds` | 6 | Tuned down from 8 |
| `transposeRounds` | 12 | Tuned down from 20 |
| `xSpacing` | 210 | Pixels between nodes horizontally |
| `ySpacing` | 160 | Pixels between layers vertically |
| `xGap` | 180 | Pixels between packed components |
| `yGap` | 180 | Pixels between packed rows |
| `type2_mode` | ignore | Type-2 conflict handling in HCA |
