# Graph Description: Disruption Subgraph — PO-MOTR

**File:** `dma_disruption_PO-MOTR.png`
**Scenario:** DC Motor (DMA-MTR-DC) delivery delayed 14 days — Vendor 1003 (Ade Supply Company), 100 units at $50/unit
**Graph type:** Two-layer disruption subgraph, 2-hop neighbourhood around PO-MOTR

---

## Overview

This graph shows the two-layer intelligence network centred on purchase order **PO-MOTR**, which represents the safety-stock breach scenario from `safety_stock_breach.md`. The image is divided into two horizontal bands separated by a faint boundary line. The lower band is **Layer 1 (Supply Chain Network)**, labelled in blue on the left. The upper band is **Layer 2 (Intelligence Layer)**, labelled in purple. Dashed orange and red lines crossing the boundary connect intelligence memory in Layer 2 to operational entities in Layer 1.

---

## Layer 1 — Supply Chain Network (lower half)

The supply chain portion of the graph is sparsely populated, reflecting the narrow scope of this particular disruption.

**The focal node** is **PO-MOTR**, rendered with a bright yellow border to distinguish it as the disrupted purchase order. It sits towards the centre-right of Layer 1 and is the entry point for the disruption — 100 units of DMA-MTR-DC ordered from Vendor 1003 at $50/unit, with delivery now delayed by 14 days.

Around PO-MOTR, several connected nodes are visible:

- **Vendor 1003 (Ade Supply Company)** appears as a deep blue node, connected to PO-MOTR by a `supplies` edge. It is the originating vendor for the disruption.
- **Item: DMA-MTR-DC** (DC Motor) appears as a sky-blue node, reached from PO-MOTR via a `delivers` edge. This item is the subject of the disruption.
- **Item: DMA-MTR-AC** (AC Motor, the alternate item) appears nearby, connected to DMA-MTR-DC via a `substitutes_for` edge. This is the only configured substitute.
- **Inventory nodes** appear as smaller green nodes — one for DMA-MTR-DC (30 units on-hand, 20-unit safety stock floor) and one for DMA-MTR-AC (same stock levels). These are reached from the item nodes via `stocked_at` edges.
- **Sales Order SO-MOTR** appears as a forest-green node, connected to PO-MOTR via a `pegged_to` edge annotated as a Marking relationship. This sales order belongs to customer US-001 (MegaRetail Corp, Tier 1) and requires 100 units by today+10 days.
- **Customer US-001** appears as an amber node at the far end of the chain, reached from SO-MOTR via an `allocated_to` edge.

The Layer 1 portion clearly traces the full pegging chain: **Vendor 1003 → PO-MOTR → DMA-MTR-DC → SO-MOTR → US-001**, with the on-hand inventory and alternate item branching off from the item node.

---

## Layer 2 — Intelligence Layer (upper half)

The intelligence layer is considerably denser, reflecting that PO-MOTR's vendor (1003) and item (DMA-MTR-DC) are referenced across multiple past execution episodes. The nodes here represent institutional memory accumulated from prior DMA runs.

**Episodes (burnt orange nodes)** form the backbone of Layer 2. Six episode nodes are visible, arranged across the top half of the graph. They are connected left-to-right by `NEXT` edges (orange arrows) representing the temporal sequence of disruption events — EP-001 through EP-006. EP-006 corresponds directly to the PO-MOTR disruption itself (the safety-stock breach scenario). These episodes span different items and POs but all involve Vendor 1003 as the source of the disruption.

**MitigationDecision nodes (dark red-orange)** cluster beneath the episode chain. For EP-006 specifically, four decision nodes are visible:
- DEC-006A and DEC-006B are Full mitigation decisions — AlternateVendor switches to Vendor 1002 (Lande, $52/unit, 8-day lead, rank 1) and Vendor 1001 (Acme, $55/unit, 5-day lead, rank 2) respectively.
- DEC-006C and DEC-006D are Partial decisions — UseOnHandInventory on DMA-MTR-DC and AlternateItem on DMA-MTR-AC respectively, both flagged with `inventory_breached: true` because drawing all 30 on-hand units drops below the 20-unit safety stock floor.

`DERIVED_FROM` edges (yellow) connect each decision back to its parent episode. `SCORED_AGAINST` edges (brown) link the Full decisions to the four Goal nodes (G-SLA, G-COST, G-QTY, G-INV), which encode the 25/25/25/25 weighting scheme.

**Fact nodes (bright yellow)** represent LLM-distilled atomic insights. FACT-006 ("DMA-MTR-DC has 30 units on-hand against a 20-unit safety stock floor — any standalone full draw triggers a breach") and FACT-007 ("Vendor 1003 is the disruption source across all 6 recorded episodes") are anchored here. `DERIVED_FROM` edges link them to their source episodes.

**Reflection nodes (purple)** synthesise higher-order patterns. REF-003 ("Safety-stock breach risk is concentrated in items with on-hand/floor ratios below 2×") is visible, linked to FACT-006 via `DERIVED_FROM_FACT`.

**Concept nodes (deep purple)** act as retrieval anchors — `safety_stock_erosion` and `alternate_vendor_switch` are tagged on EP-006 via `HAS_CONCEPT` edges. The same concepts are tagged on the relevant Facts via `ABOUT_CONCEPT` edges.

**Policy nodes (grey-blue)** representing POL-ONHOLD, POL-ORIGVEND, and POL-TACOST are connected from the MitigationDecision nodes via `GOVERNED_BY` edges, recording which business rules constrained each decision.

**Recommendation nodes (pink)** — REC-001 ("Qualify vendor 1001 or 1002 as alternates on all single-sourced items") and REC-002 ("Increase on-hand inventory targets for DMA-MTR-DC/AC to ≥ 40 units") — are linked to REF-001 and REF-003 respectively via `SUPPORTED_BY` edges.

---

## Cross-Layer Edges (dashed lines spanning both halves)

The dashed orange and red lines crossing the layer boundary are the defining structural feature of this graph. They represent the intelligence layer anchored to specific supply chain entities:

- **CONCERNS edges** (orange dashed): from each Episode node in Layer 2 pointing down to `vendor:1003`, `item:DMA-MTR-DC`, and `po:PO-MOTR` in Layer 1. These are the primary anchors — they mean "this episode is about these entities."
- **CHARACTERIZES edges** (orange-red dashed): from FACT-006 and FACT-007 pointing down to `item:DMA-MTR-DC` and `vendor:1003`. When a future DMA query asks about this vendor or item, these Facts are surfaced.
- **TARGETS edges** (dark red dashed): from REF-003 and REC-002 pointing down to `item:DMA-MTR-DC` and `item:DMA-MTR-AC`, marking these items as the primary subjects of the structural recommendation.
- **RESOLVED edge** (teal dashed): from DEC-006A (the rank-1 Full decision — Vendor 1002 AlternateVendor) pointing down to `po:PO-MOTR`, recording which decision was selected to resolve this disruption.

---

## Key Insight Visible in the Graph

The density of Layer 2 relative to Layer 1 is intentional and meaningful: a relatively simple Layer 1 disruption (one PO, one item, one downstream sales order) has generated rich institutional memory — 6 episodes, 13 decisions, 7 facts, 3 reflections, and 2 recommendations. This asymmetry reflects the compounding nature of the context graph: each new disruption enriches the intelligence layer, so future DMA runs on the same vendor or item arrive pre-loaded with prior context rather than starting from zero.

The yellow-bordered PO-MOTR node at the focal point of Layer 1, and the dense orange-red cluster of episodes and decisions above it, visually communicate the core idea: **the agent does not just react to the current disruption — it reasons across the full history of past disruptions involving the same entities.**
