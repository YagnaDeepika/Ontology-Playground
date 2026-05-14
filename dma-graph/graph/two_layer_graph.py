"""
TwoLayerGraph: A two-layer supply chain intelligence network for DMA.

Layer 1 — Supply Chain Network
    Nodes: Vendor, Item, TradeAgreement, PurchaseOrderLine, SalesOrder,
           Inventory, Customer
    Edges: supplies, delivers, alternate_for, substitutes_for, stocked_at,
           allocated_to, pegged_to, has_trade_agreement

Layer 2 — Intelligence Layer (Context Graph)
    Nodes: Episode, MitigationDecision, Fact, Reflection, Concept, Policy, Goal,
           Recommendation
    Edges: NEXT, DERIVED_FROM, DERIVED_FROM_FACT, HAS_CONCEPT, ABOUT_CONCEPT,
           GOVERNED_BY, SCORED_AGAINST, SUPPORTED_BY

Cross-layer edges anchor intelligence nodes to supply chain entities:
    CONCERNS, CHARACTERIZES, TARGETS, RESOLVED

Each DMA execution writes an Episode + MitigationDecision to Layer 2.
An async LLM batch job periodically distils Facts and Reflections from Episodes.
Future DMA runs retrieve prior context via concept-mediated traversal before
evaluating mitigation options.
"""

from __future__ import annotations

from typing import Optional

import networkx as nx


# ── Node type constants ──────────────────────────────────────────────────────


class NodeType:
    # Layer 1
    VENDOR = "Vendor"
    ITEM = "Item"
    TRADE_AGREEMENT = "TradeAgreement"
    PURCHASE_ORDER_LINE = "PurchaseOrderLine"
    SALES_ORDER = "SalesOrder"
    INVENTORY = "Inventory"
    CUSTOMER = "Customer"

    # Layer 2
    EPISODE = "Episode"
    MITIGATION_DECISION = "MitigationDecision"
    FACT = "Fact"
    REFLECTION = "Reflection"
    CONCEPT = "Concept"
    POLICY = "Policy"
    GOAL = "Goal"
    RECOMMENDATION = "Recommendation"


# ── Edge type constants ──────────────────────────────────────────────────────


class EdgeType:
    # Layer 1 — operational supply chain
    SUPPLIES = "supplies"                      # Vendor → PurchaseOrderLine
    DELIVERS = "delivers"                      # PurchaseOrderLine → Item
    ALTERNATE_FOR = "alternate_for"            # Vendor → Vendor (approved alternate)
    SUBSTITUTES_FOR = "substitutes_for"        # Item → Item (alternate item)
    STOCKED_AT = "stocked_at"                  # Item → Inventory
    ALLOCATED_TO = "allocated_to"              # Inventory → SalesOrder
    PEGGED_TO = "pegged_to"                    # PurchaseOrderLine → SalesOrder
    HAS_TRADE_AGREEMENT = "has_trade_agreement"  # Vendor+Item → TradeAgreement

    # Layer 2 — intelligence / memory
    NEXT = "NEXT"                              # Episode → Episode (temporal)
    DERIVED_FROM = "DERIVED_FROM"              # Fact/Decision → Episode
    DERIVED_FROM_FACT = "DERIVED_FROM_FACT"    # Reflection → Fact
    HAS_CONCEPT = "HAS_CONCEPT"                # Episode → Concept
    ABOUT_CONCEPT = "ABOUT_CONCEPT"            # Fact/Reflection → Concept
    GOVERNED_BY = "GOVERNED_BY"                # MitigationDecision → Policy
    SCORED_AGAINST = "SCORED_AGAINST"          # MitigationDecision → Goal
    SUPPORTED_BY = "SUPPORTED_BY"              # Recommendation → Reflection

    # Cross-layer
    CONCERNS = "CONCERNS"                      # Episode → Vendor/Item/PO
    CHARACTERIZES = "CHARACTERIZES"            # Fact → Vendor/Item
    TARGETS = "TARGETS"                        # Reflection/Recommendation → Vendor/Item
    RESOLVED = "RESOLVED"                      # MitigationDecision → PurchaseOrderLine


# ── Main graph class ─────────────────────────────────────────────────────────


class TwoLayerGraph:
    """
    Directed graph combining supply chain topology (Layer 1) with accumulated
    decision intelligence from DMA executions (Layer 2).

    Node IDs follow the scheme  <prefix>:<entity_id>  so they are globally unique
    across both layers.  Every node carries  layer (1|2)  and  node_type  attrs.
    Every edge carries a  type  attr (an EdgeType constant).
    """

    def __init__(self) -> None:
        self.G: nx.DiGraph = nx.DiGraph()

    # ── Layer 1 node builders ────────────────────────────────────────────────

    def add_vendor(
        self,
        vendor_id: str,
        name: str,
        on_hold: bool = False,
        general_lead_time: int = 0,
        region: str = "N/A",
        tier: int = 1,
        **attrs,
    ) -> str:
        nid = f"vendor:{vendor_id}"
        self.G.add_node(
            nid,
            layer=1,
            node_type=NodeType.VENDOR,
            vendor_id=vendor_id,
            name=name,
            on_hold=on_hold,
            general_lead_time=general_lead_time,
            region=region,
            tier=tier,
            **attrs,
        )
        return nid

    def add_item(
        self,
        item_id: str,
        description: str,
        purchase_price: float = 0.0,
        safety_stock: float = 0.0,
        alternate_item_id: Optional[str] = None,
        proc_lead_time_days: int = 0,
        **attrs,
    ) -> str:
        nid = f"item:{item_id}"
        self.G.add_node(
            nid,
            layer=1,
            node_type=NodeType.ITEM,
            item_id=item_id,
            description=description,
            purchase_price=purchase_price,
            safety_stock=safety_stock,
            alternate_item_id=alternate_item_id,
            proc_lead_time_days=proc_lead_time_days,
            **attrs,
        )
        return nid

    def add_trade_agreement(
        self,
        vendor_id: str,
        item_id: str,
        price: float,
        fixed_charges: float = 0.0,
        lead_time_days: int = 0,
        valid_from: str = "",
        valid_to: str = "",
        **attrs,
    ) -> str:
        ta_id = f"{item_id}:{vendor_id}"
        nid = f"ta:{ta_id}"
        self.G.add_node(
            nid,
            layer=1,
            node_type=NodeType.TRADE_AGREEMENT,
            ta_id=ta_id,
            vendor_id=vendor_id,
            item_id=item_id,
            price=price,
            fixed_charges=fixed_charges,
            lead_time_days=lead_time_days,
            valid_from=valid_from,
            valid_to=valid_to,
            **attrs,
        )
        return nid

    def add_purchase_order_line(
        self,
        po_id: str,
        vendor_id: str,
        item_id: str,
        ordered_qty: float,
        purchase_price: float,
        requested_date: str,
        confirmed_date: str = "",
        warehouse_id: str = "11",
        site_id: str = "1",
        status: str = "Open",
        **attrs,
    ) -> str:
        nid = f"po:{po_id}"
        self.G.add_node(
            nid,
            layer=1,
            node_type=NodeType.PURCHASE_ORDER_LINE,
            po_id=po_id,
            vendor_id=vendor_id,
            item_id=item_id,
            ordered_qty=ordered_qty,
            purchase_price=purchase_price,
            requested_date=requested_date,
            confirmed_date=confirmed_date,
            warehouse_id=warehouse_id,
            site_id=site_id,
            status=status,
            **attrs,
        )
        return nid

    def add_sales_order(
        self,
        so_id: str,
        customer_id: str,
        item_id: str,
        ordered_qty: float,
        required_date: str,
        impact_type: str = "Pegged",
        customer_tier: int = 2,
        **attrs,
    ) -> str:
        nid = f"so:{so_id}"
        self.G.add_node(
            nid,
            layer=1,
            node_type=NodeType.SALES_ORDER,
            so_id=so_id,
            customer_id=customer_id,
            item_id=item_id,
            ordered_qty=ordered_qty,
            required_date=required_date,
            impact_type=impact_type,
            customer_tier=customer_tier,
            **attrs,
        )
        return nid

    def add_inventory(
        self,
        item_id: str,
        warehouse_id: str,
        site_id: str,
        on_hand_qty: float,
        available_qty: float,
        safety_stock: float = 0.0,
        **attrs,
    ) -> str:
        nid = f"inv:{item_id}:{warehouse_id}"
        self.G.add_node(
            nid,
            layer=1,
            node_type=NodeType.INVENTORY,
            item_id=item_id,
            warehouse_id=warehouse_id,
            site_id=site_id,
            on_hand_qty=on_hand_qty,
            available_qty=available_qty,
            safety_stock=safety_stock,
            **attrs,
        )
        return nid

    def add_customer(
        self,
        customer_id: str,
        name: str,
        tier: int = 2,
        sla_target: float = 0.95,
        **attrs,
    ) -> str:
        nid = f"customer:{customer_id}"
        self.G.add_node(
            nid,
            layer=1,
            node_type=NodeType.CUSTOMER,
            customer_id=customer_id,
            name=name,
            tier=tier,
            sla_target=sla_target,
            **attrs,
        )
        return nid

    # ── Layer 2 node builders ────────────────────────────────────────────────

    def add_episode(
        self,
        ep_id: str,
        timestamp: str,
        disruption_type: str,
        po_id: str,
        vendor_id: str,
        item_id: str,
        shortfall_qty: float = 0.0,
        delay_days: int = 0,
        scenario: str = "",
        **attrs,
    ) -> str:
        nid = f"ep:{ep_id}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.EPISODE,
            ep_id=ep_id,
            timestamp=timestamp,
            disruption_type=disruption_type,
            po_id=po_id,
            vendor_id=vendor_id,
            item_id=item_id,
            shortfall_qty=shortfall_qty,
            delay_days=delay_days,
            scenario=scenario,
            **attrs,
        )
        return nid

    def add_mitigation_decision(
        self,
        dec_id: str,
        ep_id: str,
        mitigation_type: str,
        feasibility: str,
        rank: Optional[int],
        quantity_addressed: float,
        quantity_shortfall: float,
        total_monetary_cost: float,
        delay_days: int,
        downstream_delay_days: int,
        vendor_id: str = "",
        item_id: str = "",
        inventory_breached: bool = False,
        **attrs,
    ) -> str:
        nid = f"dec:{dec_id}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.MITIGATION_DECISION,
            dec_id=dec_id,
            ep_id=ep_id,
            mitigation_type=mitigation_type,
            feasibility=feasibility,
            rank=rank,
            quantity_addressed=quantity_addressed,
            quantity_shortfall=quantity_shortfall,
            total_monetary_cost=total_monetary_cost,
            delay_days=delay_days,
            downstream_delay_days=downstream_delay_days,
            vendor_id=vendor_id,
            item_id=item_id,
            inventory_breached=inventory_breached,
            **attrs,
        )
        return nid

    def add_fact(
        self,
        fact_id: str,
        body: str,
        confidence: float = 1.0,
        source_ep_ids: Optional[list[str]] = None,
        **attrs,
    ) -> str:
        nid = f"fact:{fact_id}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.FACT,
            fact_id=fact_id,
            body=body,
            confidence=confidence,
            source_ep_ids=source_ep_ids or [],
            **attrs,
        )
        return nid

    def add_reflection(self, ref_id: str, body: str, **attrs) -> str:
        nid = f"ref:{ref_id}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.REFLECTION,
            ref_id=ref_id,
            body=body,
            **attrs,
        )
        return nid

    def add_concept(self, label: str, **attrs) -> str:
        nid = f"conc:{label}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.CONCEPT,
            label=label,
            **attrs,
        )
        return nid

    def add_policy(self, policy_id: str, name: str, description: str, **attrs) -> str:
        nid = f"pol:{policy_id}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.POLICY,
            policy_id=policy_id,
            name=name,
            description=description,
            **attrs,
        )
        return nid

    def add_goal(self, goal_id: str, name: str, weight: float, **attrs) -> str:
        nid = f"goal:{goal_id}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.GOAL,
            goal_id=goal_id,
            name=name,
            weight=weight,
            **attrs,
        )
        return nid

    def add_recommendation(self, rec_id: str, body: str, **attrs) -> str:
        nid = f"rec:{rec_id}"
        self.G.add_node(
            nid,
            layer=2,
            node_type=NodeType.RECOMMENDATION,
            rec_id=rec_id,
            body=body,
            **attrs,
        )
        return nid

    # ── Edge builder ─────────────────────────────────────────────────────────

    def add_edge(self, src_nid: str, dst_nid: str, edge_type: str, **attrs) -> None:
        if src_nid not in self.G:
            raise ValueError(f"Source node not found: {src_nid}")
        if dst_nid not in self.G:
            raise ValueError(f"Destination node not found: {dst_nid}")
        self.G.add_edge(src_nid, dst_nid, type=edge_type, **attrs)

    # ── Layer 1 query methods ────────────────────────────────────────────────

    def get_alternate_vendors(self, item_id: str) -> list[dict]:
        """
        Return all vendors with a trade agreement for item_id, sorted by lead time.
        Excludes vendors with on_hold=True.
        Annotates each with is_original (vendor_id == "1003" by DMA convention).
        """
        results = []
        for nid, data in self.G.nodes(data=True):
            if (
                data.get("node_type") == NodeType.TRADE_AGREEMENT
                and data.get("item_id") == item_id
            ):
                v_nid = f"vendor:{data['vendor_id']}"
                v_data = self.G.nodes.get(v_nid, {})
                if v_data.get("on_hold", False):
                    continue
                results.append(
                    {
                        "vendor_id": data["vendor_id"],
                        "vendor_name": v_data.get("name", "Unknown"),
                        "price": data["price"],
                        "fixed_charges": data["fixed_charges"],
                        "lead_time_days": data["lead_time_days"],
                        "has_ta": True,
                        "is_original": data["vendor_id"] == "1003",
                    }
                )
        # Also include vendors with only a VendorLeadTime fallback (no TA for this item)
        for nid, data in self.G.nodes(data=True):
            if data.get("node_type") == NodeType.VENDOR:
                vid = data["vendor_id"]
                already = any(r["vendor_id"] == vid for r in results)
                if not already and not data.get("on_hold", False) and data.get("general_lead_time", 0) > 0:
                    results.append(
                        {
                            "vendor_id": vid,
                            "vendor_name": data.get("name", "Unknown"),
                            "price": None,
                            "fixed_charges": 0.0,
                            "lead_time_days": data["general_lead_time"],
                            "has_ta": False,
                            "is_original": vid == "1003",
                        }
                    )
        return sorted(results, key=lambda x: x["lead_time_days"])

    def get_alternate_items(self, item_id: str) -> list[dict]:
        """
        Return all items reachable via substitutes_for from item_id, with inventory.
        """
        item_nid = f"item:{item_id}"
        results = []
        for _, dst, data in self.G.out_edges(item_nid, data=True):
            if data.get("type") == EdgeType.SUBSTITUTES_FOR:
                d = self.G.nodes[dst]
                inv = self._get_inventory(d.get("item_id", ""))
                available = inv.get("available_qty", 0.0)
                safety = inv.get("safety_stock", d.get("safety_stock", 0.0))
                safe_draw = max(0.0, available - safety)
                results.append(
                    {
                        "item_id": d.get("item_id"),
                        "description": d.get("description"),
                        "purchase_price": d.get("purchase_price"),
                        "available_qty": available,
                        "safety_stock": safety,
                        "safe_draw_qty": safe_draw,
                        "proc_lead_time_days": d.get("proc_lead_time_days", 0),
                    }
                )
        return results

    def get_pegged_orders(self, po_id: str) -> list[dict]:
        """
        Return downstream SalesOrders pegged to po_id, sorted by customer tier.
        """
        po_nid = f"po:{po_id}"
        results = []
        for _, dst, data in self.G.out_edges(po_nid, data=True):
            if data.get("type") == EdgeType.PEGGED_TO:
                d = self.G.nodes[dst]
                results.append(
                    {
                        "so_id": d.get("so_id"),
                        "customer_id": d.get("customer_id"),
                        "customer_tier": d.get("customer_tier"),
                        "ordered_qty": d.get("ordered_qty"),
                        "required_date": d.get("required_date"),
                        "impact_type": data.get("impact_type", "Pegged"),
                    }
                )
        return sorted(results, key=lambda x: x["customer_tier"])

    def check_inventory_breach(
        self, item_id: str, units_to_draw: float
    ) -> dict:
        """
        Determine whether drawing units_to_draw from on-hand inventory for item_id
        would breach the safety stock floor (ItemCoverageSettingsV2.MinimumOnHandInventoryQuantity).
        Returns: breached (bool), available_qty, safety_stock, safe_draw_qty, residual_qty.
        """
        inv = self._get_inventory(item_id)
        available = inv.get("available_qty", 0.0)
        safety = inv.get("safety_stock", 0.0)
        safe_draw = max(0.0, available - safety)
        residual = available - units_to_draw
        return {
            "item_id": item_id,
            "available_qty": available,
            "safety_stock": safety,
            "safe_draw_qty": safe_draw,
            "units_drawn": units_to_draw,
            "residual_qty": residual,
            "breached": residual < safety,
            "inventory_depletion": max(0.0, units_to_draw - safe_draw),
        }

    def compute_mitigation_cost(
        self,
        vendor_id: str,
        item_id: str,
        qty: float,
        original_price: float,
    ) -> dict:
        """
        Compute incremental monetary cost for an AlternateVendor mitigation.
        Formula: max(0, Price × qty + FixedPriceCharges − OriginalPrice × qty)
        Source: PurchasePriceAgreements.Price + FixedPriceCharges, PurchaseOrderLinesV2.PurchasePrice
        """
        ta_nid = f"ta:{item_id}:{vendor_id}"
        ta_data = self.G.nodes.get(ta_nid, {})
        if not ta_data:
            return {"vendor_id": vendor_id, "item_id": item_id, "error": "No trade agreement found"}
        price = ta_data["price"]
        fixed = ta_data.get("fixed_charges", 0.0)
        alt_total = price * qty + fixed
        orig_total = original_price * qty
        incremental = max(0.0, alt_total - orig_total)
        return {
            "vendor_id": vendor_id,
            "vendor_name": self.G.nodes.get(f"vendor:{vendor_id}", {}).get("name"),
            "item_id": item_id,
            "qty": qty,
            "price_per_unit": price,
            "fixed_charges": fixed,
            "alt_total": alt_total,
            "orig_total": orig_total,
            "incremental_cost": incremental,
            "lead_time_days": ta_data["lead_time_days"],
        }

    # ── Layer 2 query methods ────────────────────────────────────────────────

    def get_supplier_context(self, vendor_id: str) -> dict:
        """
        Retrieve all Layer 2 intelligence anchored to a vendor.
        Called before DMA mitigation evaluation to inject prior context.
        Traverses: CONCERNS←, CHARACTERIZES← for episodes and facts;
                   TARGETS← for reflections and recommendations.
        """
        vendor_nid = f"vendor:{vendor_id}"
        episodes, facts, reflections, recommendations = [], [], [], []

        for src, _, data in self.G.in_edges(vendor_nid, data=True):
            src_data = self.G.nodes[src]
            nt = src_data.get("node_type")
            edge_type = data.get("type")
            if edge_type == EdgeType.CONCERNS and nt == NodeType.EPISODE:
                episodes.append(src_data)
            elif edge_type == EdgeType.CHARACTERIZES and nt == NodeType.FACT:
                facts.append(src_data)
            elif edge_type == EdgeType.TARGETS:
                if nt == NodeType.REFLECTION:
                    reflections.append(src_data)
                elif nt == NodeType.RECOMMENDATION:
                    recommendations.append(src_data)

        return {
            "vendor_id": vendor_id,
            "vendor_name": self.G.nodes.get(vendor_nid, {}).get("name"),
            "episodes": episodes,
            "facts": facts,
            "reflections": reflections,
            "recommendations": recommendations,
        }

    def get_item_context(self, item_id: str) -> dict:
        """
        Retrieve all Layer 2 intelligence anchored to an item.
        """
        item_nid = f"item:{item_id}"
        facts, reflections, recommendations = [], [], []

        for src, _, data in self.G.in_edges(item_nid, data=True):
            src_data = self.G.nodes[src]
            nt = src_data.get("node_type")
            edge_type = data.get("type")
            if edge_type == EdgeType.CHARACTERIZES and nt == NodeType.FACT:
                facts.append(src_data)
            elif edge_type == EdgeType.TARGETS:
                if nt == NodeType.REFLECTION:
                    reflections.append(src_data)
                elif nt == NodeType.RECOMMENDATION:
                    recommendations.append(src_data)

        return {
            "item_id": item_id,
            "description": self.G.nodes.get(item_nid, {}).get("description"),
            "facts": facts,
            "reflections": reflections,
            "recommendations": recommendations,
        }

    def get_prior_mitigations(
        self, vendor_id: str = "", item_id: str = "", feasibility: str = ""
    ) -> list[dict]:
        """
        Return prior MitigationDecision nodes filtered by vendor, item, and/or feasibility.
        Ordered by timestamp of the parent Episode (most recent first).
        """
        results = []
        for nid, data in self.G.nodes(data=True):
            if data.get("node_type") != NodeType.MITIGATION_DECISION:
                continue
            if vendor_id and data.get("vendor_id") != vendor_id:
                continue
            if item_id and data.get("item_id") != item_id:
                continue
            if feasibility and data.get("feasibility") != feasibility:
                continue
            ep_data = self.G.nodes.get(f"ep:{data.get('ep_id')}", {})
            results.append({**data, "_episode_timestamp": ep_data.get("timestamp", "")})
        return sorted(results, key=lambda x: x["_episode_timestamp"], reverse=True)

    def expand_by_concept(self, concept_label: str) -> dict:
        """
        Concept-mediated retrieval: find all nodes tagged with concept_label.
        Used during DMA pre-query to surface cross-disruption learnings.
        Traverses: concept ← HAS_CONCEPT/ABOUT_CONCEPT ← (Episode|Fact|Reflection)
        """
        concept_nid = f"conc:{concept_label}"
        if concept_nid not in self.G:
            return {"concept": concept_label, "found": False, "episodes": [], "facts": [], "reflections": []}

        episodes, facts, reflections = [], [], []
        for src, _, data in self.G.in_edges(concept_nid, data=True):
            src_data = self.G.nodes[src]
            nt = src_data.get("node_type")
            if nt == NodeType.EPISODE:
                episodes.append(src_data)
            elif nt == NodeType.FACT:
                facts.append(src_data)
            elif nt == NodeType.REFLECTION:
                reflections.append(src_data)

        return {
            "concept": concept_label,
            "found": True,
            "episodes": episodes,
            "facts": facts,
            "reflections": reflections,
        }

    # ── Scoring ──────────────────────────────────────────────────────────────

    def score_mitigation_options(self, options: list[dict]) -> list[dict]:
        """
        Score a list of mitigation option dicts against the Goal nodes embedded in Layer 2.
        Applies the DMA 4-component 25/25/25/25 min-max normalisation formula:

            total_score = 0.25 × norm(MonetaryCost)
                        + 0.25 × norm(DelayDays)
                        + 0.25 × norm(QuantityShortfall)
                        + 0.25 × norm(InventoryDepletion)

        Only Full mitigations are ranked.  Partial and Baseline options pass through unscored.

        Expected keys per option dict:
            name, feasibility, monetary_cost, delay_days,
            qty_shortfall (default 0), inventory_depletion (default 0)
        """
        # Read weights from Goal nodes; fall back to equal 0.25 weighting
        w = {"monetary": 0.25, "delay": 0.25, "qty_shortfall": 0.25, "inventory": 0.25}
        for _, data in self.G.nodes(data=True):
            if data.get("node_type") == NodeType.GOAL:
                gname = data.get("name", "").lower()
                gw = data.get("weight", 0.25)
                if "cost" in gname:
                    w["monetary"] = gw
                elif "sla" in gname or "delay" in gname:
                    w["delay"] = gw
                elif "risk" in gname or "inventory" in gname:
                    w["inventory"] = gw

        full = [o for o in options if o.get("feasibility") == "Full"]
        non_full = [o for o in options if o.get("feasibility") != "Full"]

        if not full:
            return non_full

        def _norm(values: list[float]) -> list[float]:
            lo, hi = min(values), max(values)
            span = hi - lo
            return [0.0 if span == 0 else (v - lo) / span for v in values]

        mc_n = _norm([o["monetary_cost"] for o in full])
        dd_n = _norm([o["delay_days"] for o in full])
        qs_n = _norm([o.get("qty_shortfall", 0.0) for o in full])
        id_n = _norm([o.get("inventory_depletion", 0.0) for o in full])

        for i, opt in enumerate(full):
            opt["total_score"] = round(
                w["monetary"] * mc_n[i]
                + w["delay"] * dd_n[i]
                + w["qty_shortfall"] * qs_n[i]
                + w["inventory"] * id_n[i],
                4,
            )

        full.sort(key=lambda x: x["total_score"])
        for rank, opt in enumerate(full, start=1):
            opt["rank"] = rank

        return full + non_full

    # ── Graph introspection ──────────────────────────────────────────────────

    def summary(self) -> dict:
        """Return a structural summary of the graph."""
        layer1 = [n for n, d in self.G.nodes(data=True) if d.get("layer") == 1]
        layer2 = [n for n, d in self.G.nodes(data=True) if d.get("layer") == 2]
        cross = [
            (s, t)
            for s, t, d in self.G.edges(data=True)
            if self.G.nodes[s].get("layer") != self.G.nodes[t].get("layer")
        ]

        by_type: dict[str, int] = {}
        for _, data in self.G.nodes(data=True):
            nt = data.get("node_type", "Unknown")
            by_type[nt] = by_type.get(nt, 0) + 1

        by_edge: dict[str, int] = {}
        for _, _, data in self.G.edges(data=True):
            et = data.get("type", "unknown")
            by_edge[et] = by_edge.get(et, 0) + 1

        return {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "layer1_nodes": len(layer1),
            "layer2_nodes": len(layer2),
            "cross_layer_edges": len(cross),
            "nodes_by_type": by_type,
            "edges_by_type": by_edge,
        }

    def nodes_by_type(self, node_type: str) -> list[dict]:
        return [
            {"id": nid, **data}
            for nid, data in self.G.nodes(data=True)
            if data.get("node_type") == node_type
        ]

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_inventory(self, item_id: str) -> dict:
        for nid, data in self.G.nodes(data=True):
            if data.get("node_type") == NodeType.INVENTORY and data.get("item_id") == item_id:
                return data
        return {}
