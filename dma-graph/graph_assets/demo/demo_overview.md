# Two-Layer Supply Chain Context Graph — Demo Overview

## Core Concept

The demo presents a knowledge graph architecture that augments an AI supply chain agent with persistent, structured memory. The graph is organized into two layers that work together: **Layer 1** captures the live ERP supply chain network (suppliers, purchase orders, items, production orders, inventory, sales orders, and customers), while **Layer 2** is an intelligence layer that accumulates institutional memory across disruption events — storing Episodes, Facts, Reflections, MitigationDecisions, Concepts, Goals, Policies, and Recommendations. Cross-layer edges (CONCERNS, CHARACTERIZES, RESOLVED) anchor every memory construct directly to the supply chain entities it pertains to, so context is always traceable to source.

## The Disruption Scenario

The example event is a 14-day delivery delay from **Vendor 1003** (ChemCorp) on a DC Motor component (DMA-MTR-DC), affecting 100 units pegged to a MegaRetail Tier 1 sales order. When the Disruption Mitigation Agent (DMA) receives this alert, it does not evaluate the situation cold. Instead, it performs a structured traversal of the two-layer graph:

1. **Anchor** — Start at Vendor 1003 and the affected item in Layer 1; follow CHARACTERIZES edges up into Layer 2.
2. **Retrieve** — Surface 6 prior Episodes involving Vendor 1003, including past delays and mitigation outcomes.
3. **Synthesize** — FACT-007 emerges: Vendor 1003 has delayed 3+ times per year on this component. FACT-006 flags safety stock erosion risk. REF-003, a Reflection distilled from these Facts, identifies a recurring pattern and a known reliable alternate supplier.
4. **Recommend** — Scored against the organization's SLA goals and procurement policies, the top-ranked mitigation is to issue a purchase order to **Vendor 1002** — a choice already validated by prior Episode outcomes stored in Layer 2.

## Why It Matters

Each time the agent handles a disruption, it writes a new Episode and MitigationDecision back into Layer 2. Over time, the intelligence layer compounds: the next disruption on the same vendor or component arrives pre-loaded with historical context, reducing the reasoning burden on the LLM and making agent recommendations more consistent, auditable, and grounded in organizational experience.
