# Porting Checklist

## Input + Schema

- Confirm node IDs are unique and stable.
- Confirm edge endpoints reference valid nodes.
- Decide whether layers come from:
  - provided `layers`, or
  - computed rule (weight buckets / topological depth).

## Algorithm Port

- Implement/port a single layout class (example shape):
  - `layout(nodes, edges) -> (nodes_with_xy, edges_with_points)`
- Include internals:
  - layer assignment,
  - long-edge dummy expansion,
  - crossing reduction (hybrid default),
  - HCA call,
  - coordinate scaling,
  - merge-back.

## HCA Integration

- Import `assign_horizontal_coordinates(...)` from your local BK module.
- Build payload:
  - `layers`,
  - `nodes` with `is_dummy`,
  - proper adjacent-layer edges.
- Keep `min_sep` and `type2_mode` configurable.

## Output Compatibility

- Preserve expected frontend node coordinate convention (center vs. top-left).
- Emit turning points in source->target order.
- Keep point fields stable (recommended: `x`, `y`, `node_id`, `is_dummy`).

## Quality + Regression Tests

- Crossing count improves vs. initial order.
- Deterministic output for fixed seed.
- Node/edge count preservation.
- Same-layer edge policy decided explicitly:
  - reject (strict layered),
  - or route with special handling.

## Performance Notes (~100 Nodes)

- Hybrid mode is usually acceptable.
- If adding exact mode:
  - cap per-layer solve time,
  - auto-fallback to hybrid when solver unavailable.
