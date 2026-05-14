# Demo Script — Two-Layer Supply Chain Context Graph
**Duration:** ~2 min 30 sec · 6 slides · Presenter notes below each cue

---

## Slide 0 — Title Card
**[0:00 – 0:20]**

> "Today I want to show you a concept we call the Two-Layer Supply Chain Context Graph. The core idea is simple: every time our Disruption Mitigation Agent handles a supply chain problem, it doesn't just fix that problem and forget it happened. It writes a trace into a memory layer — and the next agent that faces a similar disruption starts smarter. Let's walk through the two layers, and then see a real example."

---

## Slide 1 — Layer 1: Supply Chain Network
**[0:20 – 0:55]**

> "Layer 1 is the operational supply chain. The nodes here are the physical and commercial entities you'd find in any ERP: **Suppliers**, **Items**, **Purchase Orders**, **Production Orders**, **Inventory**, **Distribution Centers**, **Sales Orders**, and **Customers**."

> "The edges are typed, directed relationships — `supplies`, `delivers`, `consumed_by`, `produces`, `stocked_at`, `allocated_to`, and so on. What makes this powerful is the **pegging chain** — highlighted here — which links a Purchase Order directly to the Production Order that needs it, to the Sales Order that's at risk, all the way to the customer. This multi-hop traversal, which would take hours in a relational model, happens in milliseconds as a graph query."

> "Critically, Layer 1 is also where the agent *acts* — it issues new POs, triggers inventory transfers, and modifies delivery dates — all via MCP calls back to D365."

---

## Slide 2 — Layer 2: Intelligence Layer
**[0:55 – 1:30]**

> "Layer 2 is the intelligence layer, sometimes called the context graph. This is what makes the agent accumulate institutional memory over time."

> "The nodes here are not supply chain entities — they're **memory constructs**. An **Episode** is a timestamped, immutable record of one DMA execution. A **MitigationDecision** captures which option was chosen and why. A **Fact** is an LLM-distilled atomic insight — something like 'Vendor 1003 has been the disruption source in all 6 recorded episodes.' A **Reflection** is a higher-order pattern synthesized from multiple Facts. And **Concepts** are thematic anchor nodes — labels like `safety_stock_erosion` or `alt_vendor_switch` — that allow retrieval to work across disruptions involving completely different PO numbers."

> "Layer 2 is built in three phases, shown on the left: **Preserve** — every DMA run writes immediately. **Extract** — a batch LLM job distils Facts. **Synthesize** — a periodic LLM job generates Reflections and Recommendations."

---

## Slide 3 — The Two-Layer Combined
**[1:30 – 1:55]**

> "Now here's what makes the architecture work: the two layers are **coupled** through typed cross-layer edges, shown as dashed lines. A `CHARACTERIZES` edge from a Fact in Layer 2 down to a Supplier node in Layer 1 means: when the agent queries that supplier, those Facts surface automatically. A `RESOLVED` edge from a MitigationDecision to a Purchase Order records which decision was actually selected. A `TARGETS` edge from a Reflection to an Item flags structural risk on that item."

> "The agent doesn't just sit on top of these layers — it *inhabits* them. It reads Layer 2 before it reasons. It acts on Layer 1 via MCP. It writes the trace back to Layer 2 when it's done."

---

## Slide 4 — Worked Example: PO-MOTR
**[1:55 – 2:20]**

> "Let me make this concrete with a real scenario. Purchase Order PO-MOTR — marked here with the yellow ring — is a delivery of 100 DC Motors from Vendor 1003, now 14 days late. The Layer 1 pegging chain shows exactly who's at risk: the DC Motor feeds into inventory, which is allocated to Sales Order SO-MOTR, which belongs to MegaRetail — a Tier 1 customer."

> "Now look at Layer 2. There are **six prior episodes** all involving Vendor 1003 — six past disruptions the agent has handled. FACT-007 says: 'Vendor 1003 is the disruption source in all 6 recorded episodes.' That fact is connected back to the Vendor 1003 node in Layer 1 via a CHARACTERIZES edge — so the instant the agent sees this vendor, that history is surfaced."

> "The agent evaluates four mitigation options. The rank-1 decision — **switch to Vendor 1002 at $52/unit, 8-day lead time** — is recorded with a `RESOLVED` edge back to PO-MOTR. And a Recommendation node has already been generated: *qualify Vendor 1001 and 1002 as permanent alternates*. The agent doesn't just react to this disruption — it proposes a structural fix."

---

## Slide 5 — Retrieval & Execution Flow
**[2:20 – 2:45]**

> "Here's the full loop in six steps. The disruption is detected. The agent starts an **anchor traversal** — following CHARACTERIZES edges from Vendor 1003 and DMA-MTR-DC up into Layer 2. It then does **concept expansion** — hopping through concept nodes to pull in all related Facts and Reflections. It ranks that context by recency and injects it into its system prompt before evaluating a single mitigation option. It scores mitigations against Goals and Policies, selects Vendor 1002, executes via MCP, and **writes the new Episode and Decision back to Layer 2**."

> "That last step is the compounding effect. Every run enriches the graph. The next time a disruption hits Vendor 1003 or a DC Motor, the agent arrives pre-loaded with 6 episodes, 2 facts, 1 reflection, and 2 recommendations — none of which had to be re-derived."

---

## Closing — 3-sentence summary
**[2:45 – 2:55]**

> "To recap: Layer 1 is the live operational supply chain — nodes and edges the agent acts on. Layer 2 is the growing institutional memory — episodes, facts, reflections, and recommendations distilled from every past run. Cross-layer edges are what couple them — anchoring intelligence to specific suppliers and items so context retrieval is automatic. The graph doesn't sit beside the agent. It's what the agent *thinks with*."

---

## Slide Reference

| Slide | File | Duration |
|---|---|---|
| 0 | `slide0_title.png` | 0:00 – 0:20 |
| 1 | `slide1_layer1_supply_chain.png` | 0:20 – 0:55 |
| 2 | `slide2_layer2_intelligence.png` | 0:55 – 1:30 |
| 3 | `slide3_two_layer_combined.png` | 1:30 – 1:55 |
| 4 | `slide4_po_motr_example.png` | 1:55 – 2:20 |
| 5 | `slide5_retrieval_flow.png` | 2:20 – 2:55 |

---

## Key Talking Points (quick-reference card)

**Layer 1 node types:** Supplier · Item · Purchase Order · Production Order · Inventory · Distribution Center · Sales Order · Customer

**Layer 1 edge types:** `supplies` · `delivers` · `consumed_by` · `produces` · `stocked_at` · `allocated_to` · `transfers_to` · `ships_to` · `pegged_to` · `alternate_for` · `substitutes_for`

**Layer 2 node types:** Episode · MitigationDecision · Fact · Reflection · Concept · Policy · Goal · Recommendation

**Layer 2 edge types:** `NEXT` · `DERIVED_FROM` · `DERIVED_FROM_FACT` · `HAS_CONCEPT` · `ABOUT_CONCEPT` · `GOVERNED_BY` · `SCORED_AGAINST` · `SUPPORTED_BY`

**Cross-layer edge types:** `CONCERNS` · `CHARACTERIZES` · `TARGETS` · `APPLIES_TO` · `GOVERNS` · `PRIORITIZES` · `RESOLVED`

**The compounding insight:** Layer 2 is append-only and grows with every DMA run. The graph is a cumulative record of all past decision-making. An agent facing a known vendor or item never starts from zero.
