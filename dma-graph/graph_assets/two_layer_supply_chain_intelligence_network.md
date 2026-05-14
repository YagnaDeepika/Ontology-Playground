# Two-Layer Supply Chain Intelligence Network: Prototype Design

## Design Foundations

This prototype draws from four sources:

- **DMA scenario** (`dma_new.yaml`): defines the disruption mitigation agent's entity model and mitigation logic
- **Context Graphs for SCM** (business case document): articulates the gap MCP alone cannot fill and the intelligence layer architecture
- **Paper 2305.04865** (supply chain contagion): establishes the multi-layer propagation model — firms + financial institutions as two coupled networks with contagion flowing across layers
- **GAAMA (2603.27910v1)**: defines the node and edge taxonomy for an agent memory graph (Episodes, Facts, Reflections, Concepts with typed edges: `NEXT`, `DERIVED_FROM`, `DERIVED_FROM_FACT`, `HAS_CONCEPT`, `ABOUT_CONCEPT`)

The core idea: the two-layer network paper shows how supply shocks propagate through *coupled layers* (firms → banks). We repurpose that architecture: **Layer 1** is the operational supply chain, **Layer 2** is the intelligence/memory layer that accumulates decision traces from DMA executions. Cross-layer edges let intelligence nodes anchor to specific supply chain entities, and the agent both reads from and writes to Layer 2.

---

## Layer 1 — Supply Chain Network

This is the operational graph. Nodes are supply chain entities; edges are first-class typed relationships that enable multi-hop traversal (the 5–7 hop queries that relational models cannot serve).

### Node Types

| Node Class | Attributes | DMA Source Entity |
|---|---|---|
| **Supplier** | vendorAccountNumber, vendorName, leadTimeDays, qualityScore (0–1), riskScore, geographicRegion, tier (1/2/3), capacity | `PurchasePriceAgreement` |
| **Item / Material** | itemId, description, safetyStockQty, reorderPoint, onHandQty (uncommitted), isSingleSourced | `ReleasedProductsV2` |
| **PurchaseOrderLine** | purchId, lineNum, orderedQty, confirmedQty, originalDeliveryDate, newDeliveryDate, delayDays, shortfallQty | disruption input JSON |
| **ProductionOrder** | prodOrderId, itemId, requiredQty, requiredDate, status | `impactedOrders` |
| **SalesOrder** | salesOrderId, customerId, requiredQty, requiredDate, customerTier, slaTarget | `impactedOrders` |
| **Inventory / Warehouse** | warehouseId, siteId, onHandQty, allocatedQty, uncommittedQty, inTransitQty | on-hand inventory state |
| **DistributionCenter** | dcId, location, stockQty, allocationStatus | logistics network |
| **Customer** | customerId, customerName, tier, slaCommitment, contractType | downstream of SalesOrder |

### Edge Types (Directed)

```
Supplier ──[supplies]──────────────→ PurchaseOrderLine
PurchaseOrderLine ──[delivers]──────→ Item
Item ──[consumed_by]───────────────→ ProductionOrder
ProductionOrder ──[produces]────────→ Item (finished good)
Item ──[stocked_at]─────────────────→ Inventory
Inventory ──[allocated_to]──────────→ SalesOrder
Inventory ──[transfers_to]──────────→ DistributionCenter
DistributionCenter ──[ships_to]─────→ Customer
SalesOrder ──[fulfills_commitment_of]→ Customer

Supplier ──[alternate_for]──────────→ Supplier   (approved substitute vendors)
Item ──[substitutes_for]────────────→ Item        (approved alternate items)
PurchaseOrderLine ──[pegged_to]─────→ ProductionOrder ──[pegged_to]──→ SalesOrder
Supplier ──[tier2_sourced_from]─────→ Supplier   (sub-supplier dependency)
```

Edge properties carry temporal validity windows (`validFrom`, `validTo`), contract references, and quantities — enabling the agent to reason about what is true *right now* vs. historically.

The **pegging chain** (`PurchaseOrderLine → ProductionOrder → SalesOrder → Customer`) is the critical multi-hop path that the DMA traverses to compute `impactedOrders`. Making this a first-class graph traversal instead of sequential MCP form-navigation means the impact calculation takes milliseconds, not hours.

---

## Layer 2 — Intelligence Layer (Context Graph)

This is the memory and reasoning layer. Every DMA execution writes an Episode; the system periodically distills Episodes into Facts and Reflections. Future DMA executions retrieve relevant past decisions via concept-mediated graph traversal (GAAMA architecture).

### Node Types

| Node Class | Description | Example |
|---|---|---|
| **Episode** | Raw event record from one DMA execution — timestamped, immutable | `Episode-PO4550-2025-05-01: ChemCorp shortfall 4000 units, 7-day delay` |
| **MitigationDecision** | Structured output of one DMA run — rank, selected mitigation type, cost, feasibility | `MIT-001: AlternateVendor=AltChem, Rank=1, Cost=$5200, Feasibility=Full` |
| **Fact** | Atomic, provenance-linked assertion distilled by LLM from one or more Episodes | `ChemCorp has had partial delivery events in 4 of the last 12 months` |
| **Reflection** | Higher-order pattern synthesized across multiple Facts — a structural insight | `M-200 appears in 60% of disruption events; single-source risk is systemic` |
| **Concept** | Thematic label node (2–5 word snake_case) used for concept-mediated retrieval | `supplier_reliability`, `alternate_vendor_qualification`, `safety_stock_erosion`, `tier1_customer_concentration` |
| **Policy** | Embedded business rule — queryable, versioned | `approval_threshold: <$10K single approver, $10K–$50K procurement lead` |
| **Goal** | Weighted business objective — agents score mitigations against these | `SLA_protection: 0.40, cost_minimization: 0.30, risk_reduction: 0.30` |
| **Recommendation** | Structural change proposal generated by resilience agent | `Qualify AltChem as primary for M-200; split 60/40` |

### Edge Types within Layer 2

```
Episode ──[NEXT]───────────────────→ Episode
MitigationDecision ──[DERIVED_FROM]→ Episode
Fact ──[DERIVED_FROM]──────────────→ Episode
Fact ──[DERIVED_FROM]──────────────→ MitigationDecision
Reflection ──[DERIVED_FROM_FACT]───→ Fact
Recommendation ──[SUPPORTED_BY]────→ Reflection
Episode ──[HAS_CONCEPT]────────────→ Concept
Fact ──[ABOUT_CONCEPT]─────────────→ Concept
Reflection ──[ABOUT_CONCEPT]───────→ Concept
MitigationDecision ──[GOVERNED_BY]─→ Policy
MitigationDecision ──[SCORED_AGAINST]→ Goal
```

### Three-Phase Construction (GAAMA)

1. **Preserve**: every DMA execution writes an Episode + MitigationDecision node immediately
2. **Extract**: LLM batch job reads recent Episodes and emits Fact nodes with `DERIVED_FROM` edges
3. **Synthesize**: LLM periodically reads Fact clusters and emits Reflection + Recommendation nodes

---

## Cross-Layer Edges (Layer 2 → Layer 1)

Intelligence nodes are anchored to specific operational entities so a retrieval query on a Supplier or Item pulls both live network state (Layer 1) and accumulated institutional memory (Layer 2).

```
Episode ──[CONCERNS]──────────────→ Supplier
Episode ──[CONCERNS]──────────────→ PurchaseOrderLine
Episode ──[CONCERNS]──────────────→ Item
Fact ──[CHARACTERIZES]────────────→ Supplier
Fact ──[CHARACTERIZES]────────────→ Item
Reflection ──[TARGETS]────────────→ Supplier
Recommendation ──[APPLIES_TO]─────→ Supplier
Recommendation ──[APPLIES_TO]─────→ Item
Policy ──[GOVERNS]────────────────→ PurchaseOrderLine
Goal ──[PRIORITIZES]──────────────→ Customer
MitigationDecision ──[RESOLVED]───→ PurchaseOrderLine
```

---

## Network Diagram

```
══════════════════════════════════════════════════════════════════
  LAYER 2 — INTELLIGENCE / MEMORY LAYER
══════════════════════════════════════════════════════════════════

  [Goal: SLA=0.4]  [Goal: Cost=0.3]  [Goal: Risk=0.3]
        ↑ SCORED_AGAINST ↑                   ↑
  [MitigationDecision-MIT001]──GOVERNED_BY──[Policy: threshold]
        ↑ DERIVED_FROM
  [Episode-PO4550-2025-05-01]──HAS_CONCEPT──[supplier_reliability]
        ↑ NEXT                                    ↑ ABOUT_CONCEPT
  [Episode-PO4551-2025-06-10]──────────────[Fact: ChemCorp 4/12 partial]
                                                  ↑ DERIVED_FROM_FACT
                                           [Reflection: M-200 systemic risk]
                                                  ↑ SUPPORTED_BY
                                           [Recommendation: qualify AltChem primary]

──────────────── CROSS-LAYER EDGES ──────────────────────────────

  Episode ──CONCERNS──────────────→ ╔══════════════════════════════════╗
  Fact ──CHARACTERIZES────────────→ ║  LAYER 1 — SUPPLY CHAIN NETWORK  ║
  Recommendation ──APPLIES_TO────→ ╚══════════════════════════════════╝

══════════════════════════════════════════════════════════════════
  LAYER 1 — SUPPLY CHAIN NETWORK
══════════════════════════════════════════════════════════════════

  [Supplier: ChemCorp]──alternate_for──[Supplier: AltChem]
        │ supplies                             │ supplies
        ▼                                      ▼
  [PO-4550: M-200, 10K units]        [PO-4601: M-200, 4K units]  ← created via MCP
        │ delivers
        ▼
  [Item: M-200]──substitutes_for──[Item: M-200-ALT]
        │ consumed_by
        ▼
  [ProdOrder: PRD-301]──produces──[Inventory: FG-A @ Site1]
        │ pegged_to                     │ transfers_to
        ▼                               ▼
  [SalesOrder: SO-801]         [DC-East: 200 units]──allocated_to──[SO-802]
  (Customer: MegaRetail, Tier1)
```

---

## DMA Execution Trace: What Gets Written to Layer 2

When the DMA processes a disruption, the following happens in Layer 2:

**Step 1 — On execution start**: Create `Episode` node:

```json
{
  "episodeId": "EP-PO4550-20250501",
  "timestamp": "2025-05-01T09:14:00Z",
  "disruptionType": "delivery_delay+quantity_decrease",
  "purchId": "PO-4550",
  "supplierId": "ChemCorp",
  "itemId": "M-200",
  "shortfallQty": 4000,
  "delayDays": 7
}
```

**Step 2 — On mitigation evaluation**: Create `MitigationDecision` nodes for each option evaluated, each linked `DERIVED_FROM` the Episode.

**Step 3 — On recommendation output**: Tag the selected `MitigationDecision` as `rank=1`, write `RESOLVED` edge to `PO-4550`, and `SCORED_AGAINST` edges to Goal nodes.

**Step 4 — Async, batched**: LLM extracts Facts:
- `"AltChem delivered 4000 units of M-200 in 14 days at $1.30/unit"` → `CHARACTERIZES` AltChem Supplier node
- `"ChemCorp shortfall event #4 in 12 months"` → `CHARACTERIZES` ChemCorp Supplier node

**Step 5 — Periodic synthesis**: LLM generates Reflection:
- `"M-200 disruption frequency (4 events) + single approved alternate + Tier 1 customer exposure = high structural risk"` → `TARGETS` [M-200] and [ChemCorp], `SUPPORTED_BY` four Fact nodes

**Step 6 — Future DMA query**: When the next disruption hits M-200 or ChemCorp, retrieval traverses:

```
[ChemCorp] ← CHARACTERIZES ← [Facts] ← DERIVED_FROM_FACT ← [Reflection]
```

The agent surfaces: *"AltChem was used successfully — 14 days, $1.30/unit. Structural recommendation pending: qualify as primary."* Prior context is injected without re-deriving it.

---

## Retrieval Architecture

Following GAAMA's hybrid retrieval, when a DMA execution starts Layer 2 is queried in three passes:

1. **Anchor traversal**: start from the disruption's Supplier and Item nodes in Layer 1, traverse cross-layer `CHARACTERIZES` / `CONCERNS` edges to reach Facts and Episodes
2. **Concept expansion**: from those nodes, follow `ABOUT_CONCEPT` edges to Concept nodes, then back-traverse to all Facts and Reflections sharing those concepts
3. **Temporal + provenance ranking**: weight recent Episodes more heavily; prefer Facts with `DERIVED_FROM` chains traceable to multiple independent Episodes (higher confidence)

Retrieved context is injected into the DMA's context window *before* it starts evaluating mitigations.

---

## Contagion Propagation (from 2305.04865)

The multi-layer contagion model from the financial network paper maps directly: a disruption at one Supplier node propagates through Layer 1 edges (`supplies → consumed_by → pegged_to`) to Sales Orders and Customers, with **amplification** at each hop (analogous to the 4.3× financial loss amplification in the paper). Layer 2 tracks these propagation patterns: a Reflection node encodes *"disruptions at this supplier amplify to 3× downstream customer impact on average"* — enabling the DMA to prioritize by expected propagation severity, not just immediate shortfall.

---

## Implementation Notes

| Concern | Approach |
|---|---|
| **Graph database** | Neo4j or AWS Neptune; both layers in one instance, layer membership as a node property |
| **Write path** | MCP tool calls → D365 (execution) + Context Graph (Episode/Decision write) simultaneously |
| **Read path** | Graph RAG query assembles Layer 2 context before DMA evaluation; injected into agent system prompt alongside live Layer 1 state |
| **Layer 1 sync** | Synchronized from D365 — ERP is source of truth for operational data |
| **Layer 2 ownership** | Exclusive domain of the context graph; no ERP equivalent. This is the *new information* the graph creates. |
| **Episode immutability** | Append-only log; Facts and Reflections are derived and can be updated |

---

## Design Choices

| Decision | Rationale |
|---|---|
| Episodes are immutable | Preserves audit trail; supports provenance-aware retrieval |
| Facts and Reflections are LLM-generated, not rule-based | Handles open-ended patterns that no fixed schema anticipates |
| Concept nodes are the retrieval bridge | Allows cross-disruption learning without requiring identical entity IDs |
| Cross-layer edges are typed | Agent can selectively traverse (e.g., "give me all Facts that CHARACTERIZE this supplier") without loading the full graph |
| Goals are explicit graph nodes | Mitigation scoring is transparent and auditable — the graph shows *which goal* drove the ranking |
| Decision traces write back immediately | Every DMA run enriches the graph; no separate pipeline needed for the primary loop |

---

The two-layer network is not a knowledge base sitting beside the agent — it is the environment the agent *inhabits*: it reads Layer 2 before reasoning, executes on Layer 1 via MCP, and writes the trace back to Layer 2. Each disruption makes the graph more capable of handling the next one.

---

## References

- [Estimating the Impact of Supply Chain Network Contagion on Financial Stability](https://arxiv.org/abs/2305.04865)
- [GAAMA: Graph-based Agent Architecture for Memory and Analysis](https://arxiv.org/html/2603.27910v1)
- Context Graphs for Supply Chain Management — Internal Business Case, March 2026
- DMA scenario definition: `dataset/scenario/dma_new.yaml`
