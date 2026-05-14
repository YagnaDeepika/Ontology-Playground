# Graph Description: Disruption Subgraph — _PO-SEAL

**File:** `dma_disruption_PO-SEAL.png`
**Scenario:** NBR O-Ring Seal Kit (_DMA-SEAL-NBR) delivery delayed — Vendor 1003 (Ade Supply Company), 100 units at $10/unit
**Graph type:** Two-layer disruption subgraph, 2-hop neighbourhood around _PO-SEAL

---

## Overview

This graph shows the two-layer intelligence network centred on purchase order **_PO-SEAL**, which is the focal PO for the cost-vs-speed tradeoff scenarios from `alternate_vendor.md` (Scenarios 3 and 4). Unlike PO-MOTR, this PO appears in two distinct episodes (EP-002 and EP-003), both involving different disruption delays (10 days and 5 days) against the same item and vendor. The result is a richer Layer 2 — specifically around the concept of how the Full/Partial classification of Vendor 1002 flips depending on the severity of the delay.

The layout follows the same two-layer convention: **Layer 1 (Supply Chain Network)** occupies the lower portion of the image (labelled in blue at left), and **Layer 2 (Intelligence Layer)** occupies the upper portion (labelled in purple). Dashed lines crossing the horizontal midpoint represent cross-layer CONCERNS, CHARACTERIZES, TARGETS, and RESOLVED edges.

---

## Layer 1 — Supply Chain Network (lower half)

The supply chain portion is sparse and clean, with a small set of entities directly involved in the _PO-SEAL disruption.

**The focal node** is **_PO-SEAL**, rendered with a bright yellow border. It is positioned in the lower right of Layer 1, representing 100 units of _DMA-SEAL-NBR ordered from Vendor 1003 at $10/unit.

Key Layer 1 nodes and their relationships:

- **Vendor 1003 (Ade Supply Company)** — deep blue, connected to _PO-SEAL via a `supplies` edge. This is the failing vendor. No on-hold status, but excluded from alternate recommendations by the IsOriginalVendor policy.
- **Item: _DMA-SEAL-NBR** (NBR O-Ring Seal Kit) — sky blue, reached from _PO-SEAL via `delivers`. No alternate item is configured for this item, so the agent must rely entirely on alternate vendor options.
- **Trade Agreement nodes** — small, pale sky-blue nodes. Three are visible: one each for Vendor 1001 ($20/unit, 2-day lead), Vendor 1002 ($12/unit, 7-day lead), and Vendor 1003 ($10/unit, 0-day lead). These are reached from the vendor and item nodes via `has_trade_agreement` edges and represent the `PurchasePriceAgreements` entities the DMA queries.
- **Vendor 1001 (Acme Office Supplies)** and **Vendor 1002 (Lande Packaging Supplies)** — both appear as deep blue nodes in Layer 1, connected to the trade agreement nodes. Their visibility here is important: they represent the alternate sourcing options the agent evaluated.

No sales orders or customers are directly visible in this subgraph because _PO-SEAL's pegging chain does not include a linked sales order with a defined required date in the seeded data. The Full/Partial classification in the associated scenarios is therefore based purely on whether the alternate vendor's lead time beats the PO delay — a simpler decision boundary than the SO-deadline-driven logic visible in the PO-MOTR subgraph.

---

## Layer 2 — Intelligence Layer (upper half)

The intelligence layer for _PO-SEAL is particularly interesting because this PO appears in **two episodes with different delay values**, producing decision nodes that illustrate how the same two vendors can produce opposite Full/Partial outcomes depending on the disruption magnitude.

**Episodes (burnt orange nodes)** — two episodes are directly anchored to _PO-SEAL:

- **EP-002** (10-day delay): Both Vendor 1001 (2-day lead) and Vendor 1002 (7-day lead) beat the 10-day PO delay, making both Full mitigations. The normalised scoring produces a tie (0.25 each), as cost and speed perfectly trade off: Vendor 1001 is faster but $1,000 more expensive; Vendor 1002 is slower but only $200 incremental cost.
- **EP-003** (5-day delay): Vendor 1001 (2-day lead) remains Full. Vendor 1002 (7-day lead) now exceeds the 5-day delay threshold and becomes Partial. The distinction between these two episodes is visible in the Layer 2 structure — EP-002 produces two Full MitigationDecision nodes (DEC-002A for 1002, DEC-002B for 1001), while EP-003 produces one Full (DEC-003A for 1001) and one Partial (DEC-003B for 1002).

The remaining four episodes (EP-001, EP-004, EP-005, EP-006) are also present in the subgraph because they all involve Vendor 1003, which creates CONCERNS edges back to `vendor:1003` — a shared Layer 1 node also connected to _PO-SEAL. The temporal NEXT chain linking all six episodes is visible as a sequence of orange directed arrows tracing left to right across the top of Layer 2.

**MitigationDecision nodes (dark red-orange)** — four decision nodes are visible, corresponding to the two Full and two Partial outcomes from EP-002 and EP-003. They are positioned below the episode chain, connected to their parent episodes by yellow `DERIVED_FROM` edges. The Full decisions also connect to the four Goal nodes (G-SLA, G-COST, G-QTY, G-INV) via brown `SCORED_AGAINST` edges.

**Fact nodes (bright yellow)** — FACT-002 ("At 10-day delay, vendors 1001 and 1002 tie for _DMA-SEAL-NBR — cost-speed tradeoff") and FACT-003 ("Vendor 1002 becomes Partial for _DMA-SEAL-NBR when PO delay ≤ 7 days") are the key distilled insights. These encode the threshold-sensitive behaviour of the vendor classification that would be retrieved when a future DMA query involves _DMA-SEAL-NBR or Vendor 1002.

**Concept nodes (deep purple)** — two concepts are tagged on the _PO-SEAL episodes: `alternate_vendor_switch` and `lead_time_vs_cost_tradeoff`. These are the retrieval anchors. A future DMA query involving any item with a similar cost-speed tradeoff can expand via the `lead_time_vs_cost_tradeoff` concept to surface EP-002, EP-003, FACT-002, and FACT-003 without needing to match the exact item ID.

**Reflection nodes (purple)** — REF-002 ("Fixed charges in trade agreements can invert vendor cost rankings at low quantities") is present in the subgraph because it is connected to FACT-004 via `DERIVED_FROM_FACT`, and FACT-004 is linked via ABOUT_CONCEPT to concepts that overlap with those on EP-003. REF-001 ("Vendor 1003 is a systemic disruption source") is also visible, connected to FACT-007.

**Policy and Goal nodes** — grey-blue Policy nodes (POL-ONHOLD, POL-ORIGVEND, POL-TACOST) and brown Goal nodes are present at the right side of Layer 2, connected from the MitigationDecision nodes via `GOVERNED_BY` and `SCORED_AGAINST` edges respectively.

---

## Cross-Layer Edges (dashed lines)

The dashed lines crossing from Layer 2 down to Layer 1 are dense and clearly distinguish this graph from a simple supply chain diagram:

- **CONCERNS edges** (dashed orange): from EP-002 and EP-003 pointing down to `vendor:1003`, `item:_DMA-SEAL-NBR`, and `po:_PO-SEAL`. EP-001, EP-004, EP-005, EP-006 also fire CONCERNS edges to `vendor:1003`, which appears in Layer 1 as a node shared across all disruption episodes.
- **CHARACTERIZES edges** (dashed orange-red): from FACT-002 and FACT-003 pointing down to `vendor:1001`, `vendor:1002`, and `item:_DMA-SEAL-NBR`. These ground the facts to specific operational entities.
- **RESOLVED edges** (teal dashed): from DEC-002A (Vendor 1002, rank 1, EP-002) and DEC-003A (Vendor 1001, rank 1, EP-003) pointing down to `po:_PO-SEAL`, recording which decision was selected to resolve each episode.

---

## Key Insight Visible in the Graph

The defining feature of this subgraph compared to PO-MOTR is the **dual-episode structure**: the same PO and item appear in two episodes with different delay values, producing two separate clusters of MitigationDecision nodes in Layer 2. This makes visible the threshold-sensitive nature of the Full/Partial classification — the graph effectively encodes the rule "Vendor 1002 is viable for _DMA-SEAL-NBR only when the PO delay exceeds 7 days."

The Layer 2 density around a single pair of vendors and one item also illustrates the concept graph's learning loop: repeated disruption events on the same entities rapidly accumulate Facts and sharpen the retrieval signal. By EP-003, the graph already holds enough context for a future DMA run to pre-know that Vendor 1002 is borderline for this item and delay-sensitive in its Full/Partial classification — information a fresh agent starting from the ERP alone would have to rediscover from scratch via multiple OData queries.
