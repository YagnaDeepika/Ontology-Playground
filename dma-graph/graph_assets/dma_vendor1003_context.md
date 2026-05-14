# Graph Description: 2-Hop Neighbourhood of Vendor 1003

**File:** `dma_vendor1003_context.png`
**Focus node:** `vendor:1003` — Ade Supply Company
**Graph type:** Mixed two-layer neighbourhood subgraph, 2-hop radius, spring layout

---

## Overview

This graph shows the complete **2-hop neighbourhood** of Vendor 1003 (Ade Supply Company) within the two-layer supply chain intelligence network. Unlike the disruption subgraphs, which separate layers into top and bottom bands, this view uses a **spring layout** — all nodes are arranged in a single oval plane by the graph's force-directed algorithm, placing Vendor 1003 at the top centre with Layer 1 and Layer 2 nodes interleaved around it. The title "2-hop neighbourhood of vendor:1003" is visible at the top.

This view is the most direct representation of the intelligence the DMA retrieves when it encounters Vendor 1003 as the failing supplier in any disruption. Every node visible here is either directly connected to Vendor 1003 (hop 1) or connected to one of those hop-1 nodes (hop 2).

---

## Focal Node: Vendor 1003 (Ade Supply Company)

**Vendor 1003** is the central highlighted node — rendered in deep blue with a bright yellow border, positioned near the top centre of the graph. Its prominent size and yellow border distinguish it visually as the focal point of the neighbourhood.

By DMA convention, Vendor 1003 is the original PO vendor on every disrupted purchase order in the test dataset. It is excluded from alternate vendor recommendations via the `IsOriginalVendor` infeasibility reason. This node carries attributes: `on_hold: False`, `general_lead_time: 0`, `region: Southeast Asia`, `tier: 2`.

---

## Hop 1 Nodes — Direct Connections to Vendor 1003

### Layer 1 (supply chain entities — blues, greens, amber)

**Purchase Order nodes (dark teal)** — All eight PO nodes are directly reachable from Vendor 1003 via `supplies` edges. They appear scattered around the right and lower portions of the graph: `_PO-BRNG`, `_PO-SEAL`, `_PO-FLTR`, `_PO-PUMP-S`, `_PO-PUMP-L`, `_PO-COUP`, `_PO-VLVE`, and `PO-MOTR`. Each represents a disruption scenario where Vendor 1003 was the failing supplier.

**Trade Agreement nodes (pale sky blue, small)** — For each item where Vendor 1003 has a price agreement, a small pale-blue TradeAgreement node appears connected via `has_trade_agreement` edges. Seven such nodes are visible (one per item with a TA). These represent `PurchasePriceAgreements` entries: price $10–$200/unit, lead time 0 days (the original vendor), fixed charges $0.

### Layer 2 (intelligence nodes — orange, yellow, purple, pink)

**Episode nodes (burnt orange)** — All six episode nodes (EP-001 through EP-006) are directly connected to Vendor 1003 via `CONCERNS` edges, since every recorded disruption episode involved Vendor 1003 as the source vendor. They appear clustered to the left and upper portions of the graph, linked to each other by a chain of `NEXT` edges (temporal succession).

**Fact node (bright yellow)** — **FACT-007** ("Vendor 1003 is the disruption source on every PO across all 6 recorded episodes") appears as a large yellow node with a direct `CHARACTERIZES` edge pointing to Vendor 1003. This is the most direct intelligence fact about this vendor, distilled from the pattern of episodes.

**Reflection node (purple)** — **REF-001** ("Vendor 1003 is a systemic disruption source — qualify additional tier-1 alternates") appears as a purple node with a `TARGETS` edge pointing to Vendor 1003.

**Recommendation node (pink)** — **REC-001** ("Qualify Vendor 1001 or Vendor 1002 as approved alternates on all single-sourced items") appears as a pink node with a `TARGETS` edge pointing to Vendor 1003, linked back to REF-001 via `SUPPORTED_BY`.

---

## Hop 2 Nodes — Connections to Hop-1 Nodes

The hop-2 layer adds significant breadth to the neighbourhood, bringing in the full downstream supply chain and the decision-level intelligence.

### From the Purchase Order nodes (hop 2)

**Item nodes (sky blue)** — Each PO's `delivers` edge leads to its corresponding item: `_DMA-BRNG-6205`, `_DMA-SEAL-NBR`, `_DMA-FLTR-HYD`, `_DMA-PUMP-CTF`, `_DMA-COUP-RGD`, `_DMA-VLVE-INT`, and `DMA-MTR-DC`. These appear on the right side of the graph as sky-blue nodes of medium size. Because `_DMA-PUMP-CTF` has two POs (`_PO-PUMP-S` and `_PO-PUMP-L`), it receives two incoming `delivers` edges.

**Sales Order nodes (forest green)** — `SO-MOTR` (100 units DMA-MTR-DC, customer US-001, Marking) and `SO-VLVE-9` (100 units _DMA-VLVE-INT, customer US-007, Marking) appear as green nodes, reached from `PO-MOTR` and `_PO-VLVE` via `pegged_to` edges. Other sales orders (`SO-000704`, `SO-000891`) also appear.

**MitigationDecision nodes (dark red-orange)** — For each episode, the winning (rank-1 Full) MitigationDecision connects back to the originating PO via a `RESOLVED` edge. All 13 decision nodes therefore appear in the hop-2 neighbourhood: DEC-001 through DEC-006D. These cluster in the lower-left and bottom portions of the oval, connected via yellow `DERIVED_FROM` edges to the episode nodes.

### From the Episode nodes (hop 2)

**Concept nodes (deep purple)** — Five concept nodes appear: `alternate_vendor_switch`, `lead_time_vs_cost_tradeoff`, `safety_stock_erosion`, `fixed_charge_cost_inversion`, and `so_deadline_drives_feasibility`. They are reached via `HAS_CONCEPT` edges from the episode nodes. These act as thematic clusters for retrieval — visible along the left edge of the oval.

**Fact nodes (bright yellow)** — FACT-001 through FACT-006 appear as yellow nodes connected from episodes via `DERIVED_FROM` edges. Together with FACT-007 (directly connected to Vendor 1003 at hop 1), the full set of seven facts is visible in this neighbourhood.

**Reflection nodes (purple)** — REF-002 ("Fixed charges can invert vendor cost rankings at low quantities") and REF-003 ("Safety-stock breach risk concentrated in items with tight on-hand/floor ratios") appear at hop 2, connected from FACT-004 and FACT-006 respectively via `DERIVED_FROM_FACT` edges.

**Policy nodes (grey-blue)** — POL-ONHOLD, POL-ORIGVEND, POL-TACOST, and POL-SODEADLINE appear as grey-blue nodes connected from MitigationDecision nodes via `GOVERNED_BY` edges.

**Goal nodes (brown)** — G-SLA, G-COST, G-QTY, G-INV appear as brown nodes connected from the Full MitigationDecisions via `SCORED_AGAINST` edges.

### From the Trade Agreement nodes (hop 2)

The trade agreement nodes at hop 1 each link outward via `has_trade_agreement` edges to the item they cover — bringing those item nodes into the hop-2 neighbourhood. This overlaps with the item nodes reached from the PO nodes, meaning item nodes appear with multiple incoming edges in the graph.

---

## Visual Structure and Layout

Because the spring layout places all nodes in a single plane, the graph has an **oval or elliptical shape** with Vendor 1003 near the top centre. The force-directed algorithm clusters tightly connected nodes together:

- **Upper-centre / right arc**: Vendor 1003, its PO nodes, TradeAgreement nodes, and item nodes — the Layer 1 supply chain cluster.
- **Left arc and lower portion**: Episode nodes, Fact nodes, MitigationDecision nodes, Concept nodes, Reflection nodes — the Layer 2 intelligence cluster.
- **Bottom**: Policy nodes, Goal nodes, and Recommendation nodes — the governance and objective layer.

The edge colours reflect the type taxonomy: orange for `supplies` and `CONCERNS`, sky blue for `has_trade_agreement`, yellow for `DERIVED_FROM`, purple for concept edges, teal for `RESOLVED`, and pink for `TARGETS`. This spectrum of colours across the oval makes visible the variety of relationship types that converge on a single vendor.

---

## Key Insight Visible in the Graph

This view answers the question: **what does the DMA know about Vendor 1003 before it starts evaluating mitigations?**

The answer, made visual by the graph, is comprehensive. The DMA pre-loads:

1. **All eight POs** Vendor 1003 has disrupted, with their item and quantity context.
2. **All seven facts** characterising vendor and item behaviour — including FACT-007 confirming 1003's systemic unreliability.
3. **REF-001** and **REC-001** identifying structural action: qualify alternates.
4. **All 13 prior mitigation decisions** across all six episodes, showing which alternates were effective, their costs, and their lead times.
5. **All five concepts** tagged across the episodes, enabling cross-disruption retrieval even for items not directly involved in this disruption.

The sheer size of this 2-hop neighbourhood — spanning nearly the entire graph — illustrates the central architectural point of the context graph design: **Vendor 1003 is not just a supplier; it is a heavily annotated entity whose history is fully traversable in a single query**. No sequential form navigation, no repeated OData calls. One graph traversal brings everything into the agent's context window.
