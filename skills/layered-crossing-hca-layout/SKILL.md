---
name: layered-crossing-hca-layout
description: End-to-end workflow for layered graph layout: long-edge dummy expansion, high-quality crossing reduction (multi-start sweep + transpose + sifting, with optional exact refinement), and Brandes-Koepf horizontal coordinate assignment. Use when Codex needs to build or adapt a Sugiyama-style layout pipeline in a new project and output node coordinates plus edge turning points.
---

# Layered Crossing + HCA Layout

## Overview

Use this skill to implement a reusable layered layout pipeline in another repository.
It combines crossing reduction and Brandes-Koepf horizontal coordinate assignment into one
deterministic workflow.

## Required Input Contract

Expect graph input with:

- `nodes`: objects containing at least `id`, plus optional domain fields (`name`, `weight`, etc.).
- `edges`: objects with `from` and `to`.
- either provided `layers` or a layering rule (weight buckets or topological layering).

If long edges span multiple layers, convert them into proper segments by inserting dummy nodes.

## Workflow

1. Build initial layers and stable in-layer order.
2. Expand long edges into dummy chains (track original edge -> path mapping).
3. Run crossing reduction:
   - default: hybrid (`multi-start sweep + transpose + sifting`)
   - optional: exact per-layer refinement with solver fallback to hybrid.
4. Run Brandes-Koepf HCA on the proper layered graph.
5. Scale coordinates (`x` from HCA, `y` from layer index).
6. Merge back to original edges by turning points derived from dummy nodes.
7. Emit only real nodes in `nodes`; keep bend points in `edges[*].points`.

## Integration Notes

- Reuse the implementation blueprint in:
  - `layout_processor.py` (`WeightedLayeredLayout`)
  - `skills/brandes-koepf-hca/scripts/brandes_koepf_hca.py`
- Keep deterministic seeds for reproducible layouts.
- Preserve legacy output shapes when integrating into an existing frontend renderer.

## Validation Checklist

- Node/edge counts match original graph.
- Output nodes have numeric `x`, `y`.
- Crossing count is reduced vs. initial ordering.
- All final edge points are in source->target order.
- Running twice with same seed yields identical layout.

## References

- Implementation playbook: `references/workflow-playbook.md`
- Porting checklist + defaults: `references/porting-checklist.md`
