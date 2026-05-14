"""
Seed the TwoLayerGraph with actual DMA scenario data.

Layer 1 sources:
  - odata_atl_registry/vendor/AtlEntityVendor.md        → 3 vendors (1001/1002/1003)
  - scenarios/alternate_vendor.md                        → 7 items, trade agreements, POs
  - scenarios/alternate_item.md                          → 4 item substitution pairs
  - scenarios/safety_stock_breach.md                     → DC/AC motor pair, safety stock
  - dma_impact_input_format.md                           → PO/SO pegging structure

Layer 2 sources (distilled from scenario ground-truth runs):
  - 6 Episodes (one per scenario execution)
  - 10 MitigationDecision nodes (selected + ranked outcomes)
  - 7 Facts (LLM-extracted insights)
  - 3 Reflections (higher-order patterns across Facts)
  - 5 Concepts (thematic labels for retrieval)
  - 3 Policies
  - 3 Goals
  - 2 Recommendations
"""

from .two_layer_graph import EdgeType, TwoLayerGraph


def build_dma_graph() -> TwoLayerGraph:
    g = TwoLayerGraph()
    _seed_layer1_vendors(g)
    _seed_layer1_items(g)
    _seed_layer1_trade_agreements(g)
    _seed_layer1_purchase_orders(g)
    _seed_layer1_sales_orders(g)
    _seed_layer1_inventory(g)
    _seed_layer1_customers(g)
    _seed_layer1_edges(g)

    _seed_layer2_goals(g)
    _seed_layer2_policies(g)
    _seed_layer2_concepts(g)
    _seed_layer2_episodes(g)
    _seed_layer2_decisions(g)
    _seed_layer2_facts(g)
    _seed_layer2_reflections(g)
    _seed_layer2_recommendations(g)
    _seed_layer2_edges(g)
    _seed_cross_layer_edges(g)

    return g


# ── Layer 1: Vendors ──────────────────────────────────────────────────────────
#
# Source: AtlEntityVendor.md + alternate_vendor.md
# USMF seeds 1001, 1002, 1003.  By DMA convention 1003 is the always-disrupted
# original PO vendor and is never recommended as an alternate.

def _seed_layer1_vendors(g: TwoLayerGraph) -> None:
    g.add_vendor(
        "1001",
        name="Acme Office Supplies",
        on_hold=False,
        general_lead_time=5,
        region="North America",
        tier=1,
    )
    g.add_vendor(
        "1002",
        name="Lande Packaging Supplies",
        on_hold=False,
        general_lead_time=7,
        region="North America",
        tier=1,
    )
    g.add_vendor(
        "1003",
        name="Ade Supply Company",
        on_hold=False,
        general_lead_time=0,
        region="Southeast Asia",
        tier=2,
        note="DMA convention: original disrupted vendor — never recommend as alternate",
    )


# ── Layer 1: Items ────────────────────────────────────────────────────────────
#
# Sources:
#   alternate_vendor.md  → 6 items (_DMA-BRNG-6205 … _DMA-VLVE-INT)
#   alternate_item.md    → 4 primary + 4 substitute pairs
#   safety_stock_breach.md → DMA-MTR-DC / DMA-MTR-AC

def _seed_layer1_items(g: TwoLayerGraph) -> None:
    # ── Vendor-scenario items (no alternate item configured) ──────────────────
    g.add_item("_DMA-BRNG-6205", "Ball Bearing 6205",       purchase_price=10.0,  safety_stock=15.0)
    g.add_item("_DMA-SEAL-NBR",  "NBR O-Ring Seal Kit",     purchase_price=10.0,  safety_stock=10.0)
    g.add_item("_DMA-FLTR-HYD",  "Hydraulic Filter Element",purchase_price=10.0,  safety_stock=10.0)
    g.add_item("_DMA-PUMP-CTF",  "Centrifugal Pump",        purchase_price=200.0, safety_stock=2.0)
    g.add_item("_DMA-COUP-RGD",  "Rigid Coupling",          purchase_price=25.0,  safety_stock=5.0)
    g.add_item("_DMA-VLVE-INT",  "Intake Valve",            purchase_price=40.0,  safety_stock=10.0)

    # ── Alternate-item scenario pairs ─────────────────────────────────────────
    g.add_item(
        "_DMA-HDMI-CBL", "HDMI Cable 2m",
        purchase_price=8.0, safety_stock=20.0,
        alternate_item_id="_DMA-HDMI-CBL-G",
    )
    g.add_item(
        "_DMA-HDMI-CBL-G", "HDMI Cable 2m Generic",
        purchase_price=5.0, safety_stock=10.0,
    )
    g.add_item(
        "_DMA-USB-HUB", "USB-C Hub 7-Port",
        purchase_price=35.0, safety_stock=5.0,
        alternate_item_id="_DMA-USB-HUB-EC",
    )
    g.add_item(
        "_DMA-USB-HUB-EC", "USB-C Hub 4-Port Economy",
        purchase_price=20.0, safety_stock=5.0, proc_lead_time_days=14,
    )
    g.add_item(
        "_DMA-KEYB-MECH", "Mechanical Keyboard",
        purchase_price=60.0, safety_stock=10.0,
        alternate_item_id="_DMA-KEYB-MEM",
    )
    g.add_item("_DMA-KEYB-MEM", "Membrane Keyboard", purchase_price=25.0, safety_stock=5.0)
    g.add_item(
        "_DMA-WEBCAM-PRO", "Webcam Pro 1080p",
        purchase_price=80.0, safety_stock=10.0,
        alternate_item_id="_DMA-WEBCAM-STD",
    )
    g.add_item(
        "_DMA-WEBCAM-STD", "Webcam Standard 720p",
        purchase_price=120.0, safety_stock=5.0,
        note="Higher cost substitute — agent must surface cost differential",
    )

    # ── Safety-stock breach scenario ──────────────────────────────────────────
    # Source: safety_stock_breach.md — on-hand 30, safety stock 20 for both items.
    # Any standalone full draw (30 units) breaches the 20-unit floor.
    g.add_item(
        "DMA-MTR-DC", "DC Motor",
        purchase_price=50.0, safety_stock=20.0,
        alternate_item_id="DMA-MTR-AC",
    )
    g.add_item("DMA-MTR-AC", "AC Motor (alternate to DC Motor)", purchase_price=50.0, safety_stock=20.0)


# ── Layer 1: Trade Agreements (PurchasePriceAgreements) ───────────────────────
#
# Source: alternate_vendor.md — full vendor × item matrix with price, fixed
# charges, and lead time.  Formula: total_cost = price × qty + fixed_charges.
# Field map: PurchasePriceAgreements.Price, .FixedPriceCharges, .ProcurementLeadTimeDays

def _seed_layer1_trade_agreements(g: TwoLayerGraph) -> None:
    tas = [
        # item,              vendor, price, fixed, lead
        ("_DMA-BRNG-6205",   "1001",  10.0,   0.0,  3),
        ("_DMA-BRNG-6205",   "1003",  10.0,   0.0,  0),

        ("_DMA-SEAL-NBR",    "1001",  20.0,   0.0,  2),
        ("_DMA-SEAL-NBR",    "1002",  12.0,   0.0,  7),
        ("_DMA-SEAL-NBR",    "1003",  10.0,   0.0,  0),

        ("_DMA-FLTR-HYD",    "1001",  25.0,   0.0,  5),
        ("_DMA-FLTR-HYD",    "1002",  15.0,   0.0,  5),
        ("_DMA-FLTR-HYD",    "1003",  10.0,   0.0,  0),

        # Fixed charges flip cost winner depending on quantity — see Scenarios 6 & 7
        ("_DMA-PUMP-CTF",    "1001", 180.0, 100.0,  4),
        ("_DMA-PUMP-CTF",    "1002", 220.0,   0.0,  4),
        ("_DMA-PUMP-CTF",    "1003", 200.0,   0.0,  0),

        # Vendor 1002 has NO trade agreement for _DMA-COUP-RGD; agent must fall back
        # to VendorsV2.VendorLeadTime (seeded on vendor:1002.general_lead_time = 7)
        ("_DMA-COUP-RGD",    "1001",  32.0,   0.0,  5),
        ("_DMA-COUP-RGD",    "1003",  25.0,   0.0,  0),

        ("_DMA-VLVE-INT",    "1001",  50.0,   0.0,  3),
        ("_DMA-VLVE-INT",    "1002",  45.0,   0.0,  8),
        ("_DMA-VLVE-INT",    "1003",  40.0,   0.0,  0),

        # Safety-stock breach scenario
        ("DMA-MTR-DC",       "1001",  55.0,   0.0,  5),
        ("DMA-MTR-DC",       "1002",  52.0,   0.0,  8),
        ("DMA-MTR-DC",       "1003",  50.0,   0.0,  0),
    ]
    for item_id, vendor_id, price, fixed, lead in tas:
        g.add_trade_agreement(vendor_id, item_id, price, fixed, lead)


# ── Layer 1: Purchase Orders ──────────────────────────────────────────────────
#
# Source: alternate_vendor.md (PO Summary table) + safety_stock_breach.md
# Vendor 1003 is the PO vendor for all disruption scenarios.

def _seed_layer1_purchase_orders(g: TwoLayerGraph) -> None:
    pos = [
        # po_id,         item_id,           qty,    price, requested
        ("_PO-BRNG",  "_DMA-BRNG-6205",  100.0,  10.0, "2026-03-15"),
        ("_PO-SEAL",  "_DMA-SEAL-NBR",   100.0,  10.0, "2026-03-20"),
        ("_PO-FLTR",  "_DMA-FLTR-HYD",   100.0,  10.0, "2026-03-25"),
        # Two POs for same item to test fixed-charge quantity sensitivity (Scen 6 vs 7)
        ("_PO-PUMP-S","_DMA-PUMP-CTF",     2.0, 200.0, "2026-04-01"),
        ("_PO-PUMP-L","_DMA-PUMP-CTF",    20.0, 200.0, "2026-04-01"),
        ("_PO-COUP",  "_DMA-COUP-RGD",    50.0,  25.0, "2026-04-10"),
        # _PO-VLVE has a linked sales order — agent must read SO date for Full/Partial
        ("_PO-VLVE",  "_DMA-VLVE-INT",   100.0,  40.0, "2026-04-05"),
        # Safety-stock breach scenario — 14-day delay applied at test time
        ("PO-MOTR",   "DMA-MTR-DC",      100.0,  50.0, "today"),
    ]
    for po_id, item_id, qty, price, req in pos:
        g.add_purchase_order_line(
            po_id, "1003", item_id, qty, price, req,
            confirmed_date=req,
        )


# ── Layer 1: Sales Orders ─────────────────────────────────────────────────────
#
# Source: dma_impact_input_format.md + alternate_vendor.md Scenario 9
#         + safety_stock_breach.md

def _seed_layer1_sales_orders(g: TwoLayerGraph) -> None:
    g.add_sales_order(
        "SO-000704", "US-007", "_DMA-VLVE-INT",
        ordered_qty=50.0, required_date="today+5",
        impact_type="Marking", customer_tier=1,
    )
    g.add_sales_order(
        "SO-000891", "US-012", "_DMA-VLVE-INT",
        ordered_qty=60.0, required_date="today+8",
        impact_type="Pegged", customer_tier=2,
    )
    # Scenario 9: SO due today+5, PO delayed to today+6 → Accept is Partial
    g.add_sales_order(
        "SO-VLVE-9", "US-007", "_DMA-VLVE-INT",
        ordered_qty=100.0, required_date="today+5",
        impact_type="Marking", customer_tier=1,
        note="Scenario 9 — SO deadline tighter than PO delay (6d > 5d)",
    )
    # Safety-stock breach — SO due today+10, PO delayed to today+14
    g.add_sales_order(
        "SO-MOTR", "US-001", "DMA-MTR-DC",
        ordered_qty=100.0, required_date="today+10",
        impact_type="Marking", customer_tier=1,
    )
    # Generic dual-impact example from dma_impact_input_format.md
    g.add_sales_order(
        "SO-000704-GEN", "US-007", "D0001",
        ordered_qty=50.0, required_date="2026-02-14",
        impact_type="Marking", customer_tier=1,
    )
    g.add_sales_order(
        "SO-000891-GEN", "US-012", "D0001",
        ordered_qty=60.0, required_date="2026-02-18",
        impact_type="Pegged", customer_tier=2,
    )


# ── Layer 1: Inventory (WarehousesOnHandV2 + ItemCoverageSettingsV2) ──────────
#
# Source: alternate_item.md (pricing/safety stock table) + safety_stock_breach.md
# Warehouse 11, Site 1 is the USMF default.

def _seed_layer1_inventory(g: TwoLayerGraph) -> None:
    inv = [
        # item_id,            on_hand, available, safety_stock
        ("_DMA-HDMI-CBL-G",    50.0,    50.0,    10.0),
        ("_DMA-USB-HUB-EC",     0.0,     0.0,     5.0),  # zero stock — triggers proc lead time
        ("_DMA-KEYB-MEM",      15.0,    15.0,     5.0),
        ("_DMA-WEBCAM-STD",     8.0,     8.0,     5.0),
        # Motor scenario: 30 on-hand, 20 safety stock → safe draw = 10
        ("DMA-MTR-DC",         30.0,    30.0,    20.0),
        ("DMA-MTR-AC",         30.0,    30.0,    20.0),
        # Minor on-hand buffer for bearing item
        ("_DMA-BRNG-6205",      5.0,     5.0,    15.0),
    ]
    for item_id, on_hand, available, safety in inv:
        g.add_inventory(item_id, "11", "1", on_hand, available, safety)


# ── Layer 1: Customers ────────────────────────────────────────────────────────

def _seed_layer1_customers(g: TwoLayerGraph) -> None:
    g.add_customer("US-001", "MegaRetail Corp",   tier=1, sla_target=0.98)
    g.add_customer("US-007", "EquipFlow Inc",     tier=1, sla_target=0.96)
    g.add_customer("US-012", "SmallShop Ltd",     tier=2, sla_target=0.90)


# ── Layer 1: Edges ────────────────────────────────────────────────────────────

def _seed_layer1_edges(g: TwoLayerGraph) -> None:
    # ── supplies: Vendor → PurchaseOrderLine (original PO vendor = 1003 always) ──
    po_items = [
        "_PO-BRNG", "_PO-SEAL", "_PO-FLTR",
        "_PO-PUMP-S", "_PO-PUMP-L", "_PO-COUP",
        "_PO-VLVE", "PO-MOTR",
    ]
    for po_id in po_items:
        g.add_edge(f"vendor:1003", f"po:{po_id}", EdgeType.SUPPLIES)

    # ── delivers: PurchaseOrderLine → Item ─────────────────────────────────────
    po_to_item = {
        "_PO-BRNG":   "_DMA-BRNG-6205",
        "_PO-SEAL":   "_DMA-SEAL-NBR",
        "_PO-FLTR":   "_DMA-FLTR-HYD",
        "_PO-PUMP-S": "_DMA-PUMP-CTF",
        "_PO-PUMP-L": "_DMA-PUMP-CTF",
        "_PO-COUP":   "_DMA-COUP-RGD",
        "_PO-VLVE":   "_DMA-VLVE-INT",
        "PO-MOTR":    "DMA-MTR-DC",
    }
    for po_id, item_id in po_to_item.items():
        g.add_edge(f"po:{po_id}", f"item:{item_id}", EdgeType.DELIVERS)

    # ── substitutes_for: Item → Item (AlternativeItemNumber in ReleasedProductsV2) ──
    alt_pairs = [
        ("_DMA-HDMI-CBL",   "_DMA-HDMI-CBL-G"),
        ("_DMA-USB-HUB",    "_DMA-USB-HUB-EC"),
        ("_DMA-KEYB-MECH",  "_DMA-KEYB-MEM"),
        ("_DMA-WEBCAM-PRO", "_DMA-WEBCAM-STD"),
        ("DMA-MTR-DC",      "DMA-MTR-AC"),
    ]
    for src, dst in alt_pairs:
        g.add_edge(f"item:{src}", f"item:{dst}", EdgeType.SUBSTITUTES_FOR)

    # ── has_trade_agreement: Vendor → TradeAgreement & TradeAgreement → Item ──────
    for nid, data in list(g.G.nodes(data=True)):
        if data.get("node_type") == "TradeAgreement":
            g.add_edge(f"vendor:{data['vendor_id']}", nid, EdgeType.HAS_TRADE_AGREEMENT)
            g.add_edge(nid, f"item:{data['item_id']}", EdgeType.HAS_TRADE_AGREEMENT)

    # ── stocked_at: Item → Inventory ───────────────────────────────────────────
    for nid, data in list(g.G.nodes(data=True)):
        if data.get("node_type") == "Inventory":
            item_nid = f"item:{data['item_id']}"
            if item_nid in g.G:
                g.add_edge(item_nid, nid, EdgeType.STOCKED_AT)

    # ── pegged_to: PurchaseOrderLine → SalesOrder ─────────────────────────────
    g.add_edge("po:_PO-VLVE", "so:SO-000704",   EdgeType.PEGGED_TO, impact_type="Marking")
    g.add_edge("po:_PO-VLVE", "so:SO-000891",   EdgeType.PEGGED_TO, impact_type="Pegged")
    g.add_edge("po:_PO-VLVE", "so:SO-VLVE-9",   EdgeType.PEGGED_TO, impact_type="Marking")
    g.add_edge("po:PO-MOTR",  "so:SO-MOTR",     EdgeType.PEGGED_TO, impact_type="Marking")

    # ── allocated_to: Inventory → SalesOrder (on-hand buffer) ─────────────────
    g.add_edge("inv:DMA-MTR-DC:11", "so:SO-MOTR",   EdgeType.ALLOCATED_TO, qty_allocated=0)

    # ── SalesOrder → Customer ──────────────────────────────────────────────────
    g.add_edge("so:SO-000704",   "customer:US-007", EdgeType.ALLOCATED_TO)
    g.add_edge("so:SO-000891",   "customer:US-012", EdgeType.ALLOCATED_TO)
    g.add_edge("so:SO-VLVE-9",   "customer:US-007", EdgeType.ALLOCATED_TO)
    g.add_edge("so:SO-MOTR",     "customer:US-001", EdgeType.ALLOCATED_TO)


# ── Layer 2: Goals ────────────────────────────────────────────────────────────
#
# Weighted business objectives. Agents score mitigation options against these.
# The DMA judge uses equal 25/25/25/25 weighting across the 4 cost components.

def _seed_layer2_goals(g: TwoLayerGraph) -> None:
    g.add_goal("G-SLA",  "SLA protection (downstream delay minimisation)", weight=0.25)
    g.add_goal("G-COST", "Cost minimisation (incremental monetary cost)",   weight=0.25)
    g.add_goal("G-QTY",  "Quantity shortfall elimination",                  weight=0.25)
    g.add_goal("G-INV",  "Inventory depletion / safety-stock protection",   weight=0.25)


# ── Layer 2: Policies ─────────────────────────────────────────────────────────

def _seed_layer2_policies(g: TwoLayerGraph) -> None:
    g.add_policy(
        "POL-ONHOLD",
        "Vendor on-hold exclusion",
        "Do not recommend any vendor with VendorsV2.OnHoldStatus != 'No'.",
    )
    g.add_policy(
        "POL-ORIGVEND",
        "Original vendor exclusion",
        "The PO's original vendor (vendor 1003) is never recommended as an alternate. "
        "Exclude with infeasible reason IsOriginalVendor.",
    )
    g.add_policy(
        "POL-TACOST",
        "Total cost includes fixed charges",
        "Always compute total_cost = Price × qty + FixedPriceCharges. "
        "Never rank vendors by unit price alone (see Scenarios 6 & 7).",
    )
    g.add_policy(
        "POL-SODEADLINE",
        "Sales order deadline drives Full/Partial classification",
        "Full iff item arrives on or before SalesOrderLinesV3.RequestedReceiptDate. "
        "Partial otherwise — even if PO delay alone would look acceptable (Scenario 9).",
    )


# ── Layer 2: Concepts ─────────────────────────────────────────────────────────
#
# Thematic labels (2–5 word snake_case).  Used for concept-mediated retrieval:
# HAS_CONCEPT (Episode→Concept) and ABOUT_CONCEPT (Fact/Reflection→Concept).

def _seed_layer2_concepts(g: TwoLayerGraph) -> None:
    for label in [
        "alternate_vendor_switch",
        "lead_time_vs_cost_tradeoff",
        "safety_stock_erosion",
        "fixed_charge_cost_inversion",
        "so_deadline_drives_feasibility",
    ]:
        g.add_concept(label)


# ── Layer 2: Episodes ─────────────────────────────────────────────────────────
#
# One Episode per scenario execution.  Immutable — append-only log.
# Source: alternate_vendor.md Scenarios 1, 3, 4, 5, 6; safety_stock_breach.md.

def _seed_layer2_episodes(g: TwoLayerGraph) -> None:
    episodes = [
        dict(
            ep_id="EP-001",
            timestamp="2026-02-15T09:00:00Z",
            disruption_type="delay",
            po_id="_PO-BRNG",
            vendor_id="1003",
            item_id="_DMA-BRNG-6205",
            delay_days=5,
            scenario="alternate_vendor/Scenario1 — Switch to faster alternate vendor",
        ),
        dict(
            ep_id="EP-002",
            timestamp="2026-02-20T10:00:00Z",
            disruption_type="delay",
            po_id="_PO-SEAL",
            vendor_id="1003",
            item_id="_DMA-SEAL-NBR",
            delay_days=10,
            scenario="alternate_vendor/Scenario3 — Multiple vendors viable, cost-speed tie",
        ),
        dict(
            ep_id="EP-003",
            timestamp="2026-02-25T11:00:00Z",
            disruption_type="delay",
            po_id="_PO-SEAL",
            vendor_id="1003",
            item_id="_DMA-SEAL-NBR",
            delay_days=5,
            scenario="alternate_vendor/Scenario4 — Only vendor 1001 beats 5-day delay",
        ),
        dict(
            ep_id="EP-004",
            timestamp="2026-03-01T09:00:00Z",
            disruption_type="delay",
            po_id="_PO-PUMP-S",
            vendor_id="1003",
            item_id="_DMA-PUMP-CTF",
            delay_days=8,
            scenario="alternate_vendor/Scenario6 — Fixed charges flip cost winner at qty=2",
        ),
        dict(
            ep_id="EP-005",
            timestamp="2026-03-10T14:00:00Z",
            disruption_type="delay",
            po_id="_PO-VLVE",
            vendor_id="1003",
            item_id="_DMA-VLVE-INT",
            delay_days=6,
            scenario="alternate_vendor/Scenario9 — SO deadline determines Full/Partial",
        ),
        dict(
            ep_id="EP-006",
            timestamp="2026-03-20T08:00:00Z",
            disruption_type="delay",
            po_id="PO-MOTR",
            vendor_id="1003",
            item_id="DMA-MTR-DC",
            delay_days=14,
            scenario="safety_stock_breach — 14-day delay; on-hand draw breaches safety stock",
        ),
    ]
    for ep in episodes:
        g.add_episode(**ep)

    # Temporal succession (NEXT edges seeded later in _seed_layer2_edges)


# ── Layer 2: Mitigation Decisions ─────────────────────────────────────────────
#
# Sourced from scenario ground-truth blocks.
# Each Decision links to its parent Episode via DERIVED_FROM (seeded in edges).

def _seed_layer2_decisions(g: TwoLayerGraph) -> None:
    decisions = [
        # EP-001: vendor 1001 beats 5-day delay at same price → only Full, score=0.0
        dict(dec_id="DEC-001", ep_id="EP-001", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=1, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=0.0,   delay_days=3, downstream_delay_days=0,
             vendor_id="1001", item_id="_DMA-BRNG-6205"),

        # EP-002: 10-day delay — both vendors viable, cost-speed tie (score 0.25 each)
        dict(dec_id="DEC-002A", ep_id="EP-002", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=1, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=200.0,  delay_days=7, downstream_delay_days=0,
             vendor_id="1002", item_id="_DMA-SEAL-NBR"),
        dict(dec_id="DEC-002B", ep_id="EP-002", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=1, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=1000.0, delay_days=2, downstream_delay_days=0,
             vendor_id="1001", item_id="_DMA-SEAL-NBR"),

        # EP-003: 5-day delay — 1001 Full (2d < 5d), 1002 Partial (7d > 5d)
        dict(dec_id="DEC-003A", ep_id="EP-003", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=1, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=1000.0, delay_days=2, downstream_delay_days=0,
             vendor_id="1001", item_id="_DMA-SEAL-NBR"),
        dict(dec_id="DEC-003B", ep_id="EP-003", mitigation_type="AlternateVendor",
             feasibility="Partial", rank=None, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=200.0,  delay_days=7, downstream_delay_days=2,
             vendor_id="1002", item_id="_DMA-SEAL-NBR"),

        # EP-004: qty=2, fixed charges flip winner → 1002 cheaper than 1001 at low qty
        dict(dec_id="DEC-004A", ep_id="EP-004", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=1, quantity_addressed=2, quantity_shortfall=0,
             total_monetary_cost=40.0,   delay_days=4, downstream_delay_days=0,
             vendor_id="1002", item_id="_DMA-PUMP-CTF",
             note="Vendor 1002 wins at qty=2: $220×2=$440 vs 1001: $180×2+$100=$460"),
        dict(dec_id="DEC-004B", ep_id="EP-004", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=2, quantity_addressed=2, quantity_shortfall=0,
             total_monetary_cost=60.0,   delay_days=4, downstream_delay_days=0,
             vendor_id="1001", item_id="_DMA-PUMP-CTF",
             note="Fixed charges ($100) make 1001 more expensive at qty=2 despite lower unit price"),

        # EP-005: SO due today+5, PO delayed +6 → Accept is Partial; 1001 Full (3d); 1002 Partial (8d)
        dict(dec_id="DEC-005A", ep_id="EP-005", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=1, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=1000.0, delay_days=3, downstream_delay_days=0,
             vendor_id="1001", item_id="_DMA-VLVE-INT",
             note="Vendor 1001 arrives day 3 < SO deadline day 5 → Full"),
        dict(dec_id="DEC-005B", ep_id="EP-005", mitigation_type="AlternateVendor",
             feasibility="Partial", rank=None, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=500.0,  delay_days=8, downstream_delay_days=3,
             vendor_id="1002", item_id="_DMA-VLVE-INT",
             note="Vendor 1002 arrives day 8 > SO deadline day 5 → Partial (worse than Accept)"),

        # EP-006: Safety-stock breach — AltVendor options Full (no breach); UseOnHand Partial (breach)
        dict(dec_id="DEC-006A", ep_id="EP-006", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=1, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=5200.0, delay_days=8, downstream_delay_days=0,
             vendor_id="1002", item_id="DMA-MTR-DC", inventory_breached=False),
        dict(dec_id="DEC-006B", ep_id="EP-006", mitigation_type="AlternateVendor",
             feasibility="Full",    rank=2, quantity_addressed=100, quantity_shortfall=0,
             total_monetary_cost=5500.0, delay_days=5, downstream_delay_days=0,
             vendor_id="1001", item_id="DMA-MTR-DC", inventory_breached=False),
        dict(dec_id="DEC-006C", ep_id="EP-006", mitigation_type="UseOnHandInventory",
             feasibility="Partial", rank=None, quantity_addressed=30, quantity_shortfall=70,
             total_monetary_cost=0.0, delay_days=0, downstream_delay_days=4,
             item_id="DMA-MTR-DC", inventory_breached=True,
             note="Drawing all 30 on-hand units leaves 0 < safety_stock floor of 20 → breach"),
        dict(dec_id="DEC-006D", ep_id="EP-006", mitigation_type="AlternateItem",
             feasibility="Partial", rank=None, quantity_addressed=30, quantity_shortfall=70,
             total_monetary_cost=0.0, delay_days=0, downstream_delay_days=4,
             item_id="DMA-MTR-AC", inventory_breached=True,
             note="Same breach logic applies to the alternate item (DMA-MTR-AC, 30 on-hand, 20 floor)"),
    ]
    for d in decisions:
        g.add_mitigation_decision(**d)


# ── Layer 2: Facts ────────────────────────────────────────────────────────────
#
# LLM-extracted atomic assertions from Episode + Decision evidence.
# Each Fact links to its source Episodes via DERIVED_FROM (seeded in edges).

def _seed_layer2_facts(g: TwoLayerGraph) -> None:
    facts = [
        dict(
            fact_id="FACT-001",
            body="Vendor 1001 (Acme Office Supplies) is a viable alternate for _DMA-BRNG-6205 "
                 "at the same unit price ($10) with a 3-day lead time, beating any delay > 3 days.",
            confidence=1.0,
            source_ep_ids=["EP-001"],
        ),
        dict(
            fact_id="FACT-002",
            body="For _DMA-SEAL-NBR with a 10-day disruption both vendor 1001 ($20, 2d) and "
                 "vendor 1002 ($12, 7d) achieve Full mitigation, producing an equal total_score "
                 "(0.25 each). Cost-speed preference determines final selection.",
            confidence=1.0,
            source_ep_ids=["EP-002"],
        ),
        dict(
            fact_id="FACT-003",
            body="Vendor 1002 (Lande Packaging Supplies) becomes Partial for _DMA-SEAL-NBR when "
                 "PO delay ≤ 7 days, because its lead time equals the delay threshold.",
            confidence=1.0,
            source_ep_ids=["EP-003"],
        ),
        dict(
            fact_id="FACT-004",
            body="For _DMA-PUMP-CTF at qty=2: vendor 1001's $100 fixed charge makes it more "
                 "expensive ($460) than vendor 1002 ($440) despite a lower unit price ($180 < $220). "
                 "At qty=20 the ranking inverts (1001=$3700, 1002=$4400).",
            confidence=1.0,
            source_ep_ids=["EP-004"],
        ),
        dict(
            fact_id="FACT-005",
            body="SalesOrderLinesV3.RequestedReceiptDate is the decisive criterion for Full/Partial "
                 "classification, not the raw PO delay. For _DMA-VLVE-INT (SO due today+5, PO delayed "
                 "+6): Accept is Partial; vendor 1002 (8d) is worse than Accept from the customer's view.",
            confidence=1.0,
            source_ep_ids=["EP-005"],
        ),
        dict(
            fact_id="FACT-006",
            body="DMA-MTR-DC has 30 units on-hand against a safety-stock floor of 20. Any standalone "
                 "draw of the full 30 units triggers minimumInventoryBreached=true. Safe draw without "
                 "breach is at most 10 units.",
            confidence=1.0,
            source_ep_ids=["EP-006"],
        ),
        dict(
            fact_id="FACT-007",
            body="Vendor 1003 (Ade Supply Company) is the source vendor on every disrupted PO across "
                 "all 6 recorded episodes. It is never a viable alternate (IsOriginalVendor exclusion).",
            confidence=1.0,
            source_ep_ids=["EP-001", "EP-002", "EP-003", "EP-004", "EP-005", "EP-006"],
        ),
    ]
    for f in facts:
        g.add_fact(**f)


# ── Layer 2: Reflections ──────────────────────────────────────────────────────
#
# Higher-order patterns synthesised from multiple Facts.
# Reflections → DERIVED_FROM_FACT → Facts (seeded in edges).

def _seed_layer2_reflections(g: TwoLayerGraph) -> None:
    g.add_reflection(
        "REF-001",
        body="Vendor 1003 (Ade Supply Company) is a systemic disruption source across all "
             "item categories. All 6 recorded episodes involve vendor 1003 as the failing PO vendor. "
             "Strategic action: qualify additional tier-1 alternates and reduce single-source exposure.",
    )
    g.add_reflection(
        "REF-002",
        body="Fixed charges in trade agreements can invert vendor cost rankings at low quantities. "
             "Total cost must always be computed as Price × qty + FixedPriceCharges — ranking by "
             "unit price alone produces incorrect recommendations (confirmed in EP-004, _DMA-PUMP-CTF).",
    )
    g.add_reflection(
        "REF-003",
        body="Safety-stock breach risk is concentrated in items with tight on-hand / floor ratios "
             "(on_hand / safety_stock < 2.0). DMA-MTR-DC and DMA-MTR-AC both have a 30/20 ratio "
             "(1.5×), making UseOnHandInventory and AlternateItem standalone mitigations Partial by "
             "default. These items require either larger on-hand buffers or alternate vendor qualification.",
    )


# ── Layer 2: Recommendations ──────────────────────────────────────────────────

def _seed_layer2_recommendations(g: TwoLayerGraph) -> None:
    g.add_recommendation(
        "REC-001",
        body="Qualify vendor 1001 or vendor 1002 as an approved alternate on all items currently "
             "single-sourced through vendor 1003 to eliminate repeat firefighting.",
    )
    g.add_recommendation(
        "REC-002",
        body="Increase on-hand inventory targets for DMA-MTR-DC and DMA-MTR-AC to at least 2× "
             "safety-stock (≥ 40 units) so that UseOnHandInventory and AlternateItem mitigations "
             "can cover full shortfalls without breaching the safety-stock floor.",
    )


# ── Layer 2: Internal edges ───────────────────────────────────────────────────

def _seed_layer2_edges(g: TwoLayerGraph) -> None:
    # NEXT: temporal episode chain
    ep_chain = ["EP-001", "EP-002", "EP-003", "EP-004", "EP-005", "EP-006"]
    for i in range(len(ep_chain) - 1):
        g.add_edge(f"ep:{ep_chain[i]}", f"ep:{ep_chain[i+1]}", EdgeType.NEXT)

    # DERIVED_FROM: MitigationDecision → Episode
    dec_to_ep = {
        "DEC-001":  "EP-001",
        "DEC-002A": "EP-002", "DEC-002B": "EP-002",
        "DEC-003A": "EP-003", "DEC-003B": "EP-003",
        "DEC-004A": "EP-004", "DEC-004B": "EP-004",
        "DEC-005A": "EP-005", "DEC-005B": "EP-005",
        "DEC-006A": "EP-006", "DEC-006B": "EP-006",
        "DEC-006C": "EP-006", "DEC-006D": "EP-006",
    }
    for dec_id, ep_id in dec_to_ep.items():
        g.add_edge(f"dec:{dec_id}", f"ep:{ep_id}", EdgeType.DERIVED_FROM)

    # DERIVED_FROM: Fact → Episode(s)
    fact_to_eps = {
        "FACT-001": ["EP-001"],
        "FACT-002": ["EP-002"],
        "FACT-003": ["EP-003"],
        "FACT-004": ["EP-004"],
        "FACT-005": ["EP-005"],
        "FACT-006": ["EP-006"],
        "FACT-007": ["EP-001", "EP-002", "EP-003", "EP-004", "EP-005", "EP-006"],
    }
    for fact_id, ep_ids in fact_to_eps.items():
        for ep_id in ep_ids:
            g.add_edge(f"fact:{fact_id}", f"ep:{ep_id}", EdgeType.DERIVED_FROM)

    # DERIVED_FROM_FACT: Reflection → Facts
    g.add_edge("ref:REF-001", "fact:FACT-007", EdgeType.DERIVED_FROM_FACT)
    g.add_edge("ref:REF-002", "fact:FACT-004", EdgeType.DERIVED_FROM_FACT)
    g.add_edge("ref:REF-003", "fact:FACT-006", EdgeType.DERIVED_FROM_FACT)

    # SUPPORTED_BY: Recommendation → Reflection
    g.add_edge("rec:REC-001", "ref:REF-001", EdgeType.SUPPORTED_BY)
    g.add_edge("rec:REC-002", "ref:REF-003", EdgeType.SUPPORTED_BY)

    # HAS_CONCEPT: Episode → Concept
    ep_concepts = {
        "EP-001": ["alternate_vendor_switch"],
        "EP-002": ["alternate_vendor_switch", "lead_time_vs_cost_tradeoff"],
        "EP-003": ["alternate_vendor_switch", "lead_time_vs_cost_tradeoff"],
        "EP-004": ["alternate_vendor_switch", "fixed_charge_cost_inversion"],
        "EP-005": ["alternate_vendor_switch", "so_deadline_drives_feasibility"],
        "EP-006": ["alternate_vendor_switch", "safety_stock_erosion"],
    }
    for ep_id, concepts in ep_concepts.items():
        for c in concepts:
            g.add_edge(f"ep:{ep_id}", f"conc:{c}", EdgeType.HAS_CONCEPT)

    # ABOUT_CONCEPT: Fact → Concept
    fact_concepts = {
        "FACT-001": ["alternate_vendor_switch"],
        "FACT-002": ["lead_time_vs_cost_tradeoff"],
        "FACT-003": ["alternate_vendor_switch", "lead_time_vs_cost_tradeoff"],
        "FACT-004": ["fixed_charge_cost_inversion"],
        "FACT-005": ["so_deadline_drives_feasibility"],
        "FACT-006": ["safety_stock_erosion"],
        "FACT-007": ["alternate_vendor_switch"],
    }
    for fact_id, concepts in fact_concepts.items():
        for c in concepts:
            g.add_edge(f"fact:{fact_id}", f"conc:{c}", EdgeType.ABOUT_CONCEPT)

    # GOVERNED_BY: every MitigationDecision → relevant Policies
    all_dec_ids = [
        "DEC-001", "DEC-002A", "DEC-002B", "DEC-003A", "DEC-003B",
        "DEC-004A", "DEC-004B", "DEC-005A", "DEC-005B",
        "DEC-006A", "DEC-006B", "DEC-006C", "DEC-006D",
    ]
    for dec_id in all_dec_ids:
        g.add_edge(f"dec:{dec_id}", "pol:POL-ONHOLD",   EdgeType.GOVERNED_BY)
        g.add_edge(f"dec:{dec_id}", "pol:POL-ORIGVEND", EdgeType.GOVERNED_BY)
        g.add_edge(f"dec:{dec_id}", "pol:POL-TACOST",   EdgeType.GOVERNED_BY)

    # SCORED_AGAINST: every Full decision → all Goal nodes
    full_dec_ids = [
        "DEC-001", "DEC-002A", "DEC-002B", "DEC-003A",
        "DEC-004A", "DEC-004B", "DEC-005A",
        "DEC-006A", "DEC-006B",
    ]
    for dec_id in full_dec_ids:
        for goal in ["G-SLA", "G-COST", "G-QTY", "G-INV"]:
            g.add_edge(f"dec:{dec_id}", f"goal:{goal}", EdgeType.SCORED_AGAINST)


# ── Cross-layer edges ─────────────────────────────────────────────────────────
#
# Anchor Layer 2 intelligence nodes to their Layer 1 entities.
# This makes a query on vendor:1003 return both the live operational state
# and the accumulated institutional memory from Layer 2.

def _seed_cross_layer_edges(g: TwoLayerGraph) -> None:
    # CONCERNS: Episode → Vendor (disruption source) + Item + PO
    ep_entities = {
        "EP-001": ("1003", "_DMA-BRNG-6205", "_PO-BRNG"),
        "EP-002": ("1003", "_DMA-SEAL-NBR",  "_PO-SEAL"),
        "EP-003": ("1003", "_DMA-SEAL-NBR",  "_PO-SEAL"),
        "EP-004": ("1003", "_DMA-PUMP-CTF",  "_PO-PUMP-S"),
        "EP-005": ("1003", "_DMA-VLVE-INT",  "_PO-VLVE"),
        "EP-006": ("1003", "DMA-MTR-DC",     "PO-MOTR"),
    }
    for ep_id, (vendor_id, item_id, po_id) in ep_entities.items():
        g.add_edge(f"ep:{ep_id}", f"vendor:{vendor_id}", EdgeType.CONCERNS)
        g.add_edge(f"ep:{ep_id}", f"item:{item_id}",     EdgeType.CONCERNS)
        g.add_edge(f"ep:{ep_id}", f"po:{po_id}",         EdgeType.CONCERNS)

    # CHARACTERIZES: Fact → Vendor or Item
    fact_targets = {
        "FACT-001": [("vendor", "1001"), ("item", "_DMA-BRNG-6205")],
        "FACT-002": [("vendor", "1001"), ("vendor", "1002"), ("item", "_DMA-SEAL-NBR")],
        "FACT-003": [("vendor", "1002"), ("item", "_DMA-SEAL-NBR")],
        "FACT-004": [("vendor", "1001"), ("vendor", "1002"), ("item", "_DMA-PUMP-CTF")],
        "FACT-005": [("item", "_DMA-VLVE-INT")],
        "FACT-006": [("item", "DMA-MTR-DC"), ("item", "DMA-MTR-AC")],
        "FACT-007": [("vendor", "1003")],
    }
    for fact_id, targets in fact_targets.items():
        for prefix, entity_id in targets:
            g.add_edge(f"fact:{fact_id}", f"{prefix}:{entity_id}", EdgeType.CHARACTERIZES)

    # TARGETS: Reflection → primary concerned Vendor or Item
    g.add_edge("ref:REF-001", "vendor:1003",    EdgeType.TARGETS)
    g.add_edge("ref:REF-002", "item:_DMA-PUMP-CTF", EdgeType.TARGETS)
    g.add_edge("ref:REF-003", "item:DMA-MTR-DC",    EdgeType.TARGETS)
    g.add_edge("ref:REF-003", "item:DMA-MTR-AC",    EdgeType.TARGETS)

    # TARGETS: Recommendation → actionable Vendor or Item
    g.add_edge("rec:REC-001", "vendor:1003",    EdgeType.TARGETS)
    g.add_edge("rec:REC-002", "item:DMA-MTR-DC", EdgeType.TARGETS)
    g.add_edge("rec:REC-002", "item:DMA-MTR-AC", EdgeType.TARGETS)

    # RESOLVED: MitigationDecision (rank=1 Full only) → PurchaseOrderLine
    resolved = {
        "DEC-001":  "_PO-BRNG",
        "DEC-002A": "_PO-SEAL",
        "DEC-003A": "_PO-SEAL",
        "DEC-004A": "_PO-PUMP-S",
        "DEC-005A": "_PO-VLVE",
        "DEC-006A": "PO-MOTR",
    }
    for dec_id, po_id in resolved.items():
        g.add_edge(f"dec:{dec_id}", f"po:{po_id}", EdgeType.RESOLVED)
