# Workflow Playbook

## 1) Layering and Proper Graph Conversion

1. Choose a layer index for each real node (weight bucket or topological depth).
2. Keep stable initial order inside each layer.
3. For each edge crossing more than one layer:
   - insert dummy nodes for intermediate layers,
   - split into adjacent-layer segments,
   - save an `edge_path` mapping to reconstruct final bends.

Result: proper layered graph (every segment spans one layer).

## 2) Crossing Reduction (Quality-First)

Use hybrid crossing reduction:

1. Multi-start runs from lightly perturbed layer orders.
2. Bidirectional sweep rounds:
   - downward then upward,
   - median primary key, barycenter tie-break.
3. Iterative transpose swaps adjacent vertices while crossing count improves.
4. Sifting rounds move one vertex across all candidate positions.
5. Keep best run by total crossing count.

Optional exact refinement:

- solve one layer at a time with pairwise precedence variables and transitivity constraints,
- enforce short time limits per layer,
- fallback to hybrid when no solver is available.

## 3) Brandes-Koepf Horizontal Assignment

Feed the reduced proper graph to Brandes-Koepf HCA:

1. preprocess type-1 conflicts,
2. compute 4 biased assignments (`up/down` x `left/right`),
3. compact each assignment,
4. align to smallest width assignment,
5. combine with average median.

Outputs `x` for real + dummy nodes.

## 4) Coordinate Finalization and Merge-Back

1. Map layer index to `y`.
2. Normalize and scale `x`.
3. Real nodes:
   - write final top-left node coordinates (`x`, `y`) for renderer.
4. Original edges:
   - convert dummy nodes in `edge_path` to turning points,
   - store ordered points as `[{x, y, node_id, is_dummy}]`.

## 5) Recommended Defaults

- `crossing_method = "hybrid"`
- `multi_start_runs = 12`
- `sweep_rounds = 8`
- `transpose_max_rounds = 20`
- `sifting_rounds = 2`
- `random_seed = 42`
- `type2_mode = "ignore"` (unless strict handling required)
