"""
Generate demo slides for the Two-Layer Supply Chain Intelligence Network presentation.
Outputs 6 PNG slides to the same directory.

Fix note: ax.legend() replaces the active legend on every call.  Always call
ax.add_artist(leg) on the first legend before creating the second one.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import networkx as nx
import os

OUT = os.path.dirname(os.path.abspath(__file__))

BG   = "#0d1117"
FONT = "DejaVu Sans"

NODE_COLORS = {
    # Layer 1
    "Supplier":           "#1e6eb5",
    "Item":               "#29a6d4",
    "PurchaseOrder":      "#d4a017",
    "ProductionOrder":    "#e87c25",
    "Inventory":          "#2ea84f",
    "DistributionCenter": "#27c9a0",
    "SalesOrder":         "#5ab552",
    "Customer":           "#f0a500",
    # Layer 2
    "Episode":            "#e07b39",
    "MitigationDecision": "#c03d3d",
    "Fact":               "#c8b800",
    "Reflection":         "#a855f7",
    "Concept":            "#7e3af2",
    "Policy":             "#6b7fa3",
    "Goal":               "#34c9eb",
    "Recommendation":     "#f472b6",
}

EDGE_COLORS = {
    "supplies":          "#4a90d9",
    "delivers":          "#4a90d9",
    "consumed_by":       "#29a6d4",
    "produces":          "#e87c25",
    "stocked_at":        "#2ea84f",
    "allocated_to":      "#5ab552",
    "transfers_to":      "#27c9a0",
    "ships_to":          "#f0a500",
    "fulfills":          "#f0a500",
    "alternate_for":     "#8ecef5",
    "substitutes_for":   "#8ecef5",
    "pegged_to":         "#d4a017",
    "NEXT":              "#e07b39",
    "DERIVED_FROM":      "#c8b800",
    "DERIVED_FROM_FACT": "#a855f7",
    "HAS_CONCEPT":       "#7e3af2",
    "ABOUT_CONCEPT":     "#7e3af2",
    "GOVERNED_BY":       "#6b7fa3",
    "SCORED_AGAINST":    "#34c9eb",
    "SUPPORTED_BY":      "#f472b6",
    "CONCERNS":          "#ff8c42",
    "CHARACTERIZES":     "#ff5c5c",
    "TARGETS":           "#cc2222",
    "APPLIES_TO":        "#cc2222",
    "RESOLVED":          "#00c9b1",
}


def savefig(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.3, facecolor=BG)
    plt.close(fig)
    print(f"  saved → {path}")


def make_legend(ax, items, title, loc, fontsize=8, linestyle_map=None):
    """Create a legend; caller must ax.add_artist() if a second legend is needed."""
    handles = []
    for label, color, kind in items:
        if kind == "patch":
            handles.append(mpatches.Patch(
                facecolor=color, edgecolor="white", linewidth=0.5, label=label))
        else:
            ls = "--" if kind == "dashed" else "-"
            handles.append(mlines.Line2D(
                [], [], color=color, linewidth=2, linestyle=ls, label=label))
    leg = ax.legend(
        handles=handles, title=title, loc=loc, fontsize=fontsize,
        title_fontsize=fontsize + 1, framealpha=0.4, facecolor="#161630",
        edgecolor="#555", labelcolor="white",
        handlelength=1.6, borderpad=0.6, labelspacing=0.4,
    )
    if leg.get_title():
        leg.get_title().set_color("#ccccff")
    return leg


def draw_graph(ax, G, pos, node_type_map, edge_label_map,
               node_size=800, font_size=7, edge_lw=1.5, edge_font_size=6):
    for ntype, color in NODE_COLORS.items():
        nodes = [n for n, t in node_type_map.items() if t == ntype and n in G]
        if nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=color,
                                   node_size=node_size, ax=ax,
                                   edgecolors="white", linewidths=0.6)
    label_objs = nx.draw_networkx_labels(G, pos, font_size=font_size, font_color="white",
                                          font_family=FONT, ax=ax)
    for txt in label_objs.values():
        txt.set_clip_on(False)
    for u, v, data in G.edges(data=True):
        etype = edge_label_map.get((u, v), data.get("etype", "supplies"))
        color = EDGE_COLORS.get(etype, "#aaaaaa")
        style = "dashed" if data.get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=edge_lw,
                                   linestyle=style, mutation_scale=12,
                                   shrinkA=7, shrinkB=7))
    mid = {(u, v): edge_label_map.get((u, v), "") for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=mid,
                                 font_size=edge_font_size, font_color="white", ax=ax,
                                 label_pos=0.5, rotate=False,
                                 bbox=dict(boxstyle="round,pad=0.25",
                                           fc="#1a1a2e", ec="none", alpha=0.9))


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 0 — Title Card
# ══════════════════════════════════════════════════════════════════════════════
def slide0_title():
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(-6, 6)
    ax.set_ylim(-1.5, 5.5)

    # gradient header band
    for y, h, a in [(3.8, 1.0, 0.6), (3.0, 0.85, 0.4), (2.2, 0.85, 0.2)]:
        ax.add_patch(mpatches.FancyBboxPatch(
            (-5.5, y), 11, h, boxstyle="round,pad=0.15",
            facecolor="#7e3af2", edgecolor="none", alpha=a))

    ax.text(0, 4.8, "Two-Layer Supply Chain Context Graph",
            ha="center", va="center", fontsize=20, fontweight="bold",
            color="white", fontfamily=FONT)
    ax.text(0, 4.0,
            "A Framework for Accumulating Institutional Memory Across Disruption Mitigation Agent Executions",
            ha="center", va="center", fontsize=11, color="#c4a8ff", fontfamily=FONT)

    ax.text(0, 2.8,
            "Layer 1 — Operational Supply Chain Network\n"
            "Layer 2 — Intelligence / Memory Context Graph\n"
            "Cross-layer edges anchor memory to supply chain entities",
            ha="center", va="center", fontsize=10.5, color="#ccccff",
            fontfamily=FONT, multialignment="center", linespacing=2.0)

    ax.text(0, 1.5,
            "Worked example: PO-MOTR — DC Motor, Vendor 1003, 14-day delivery delay",
            ha="center", va="center", fontsize=10, color="#f5c518", fontfamily=FONT,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1422",
                      edgecolor="#f5c518", alpha=0.85))

    # Layer schematic
    for y, fc, ec, lbl in [
        (0.2,  "#0a2035", "#5baee0", "LAYER 1 — Supply Chain Network"),
        (-0.5, "#180d2a", "#b87aff", "LAYER 2 — Intelligence Layer (Context Graph)"),
    ]:
        ax.add_patch(mpatches.FancyBboxPatch(
            (-3.5, y), 7, 0.55, boxstyle="round,pad=0.12",
            facecolor=fc, edgecolor=ec, linewidth=1.5, alpha=0.9))
        ax.text(0, y + 0.27, lbl, ha="center", va="center",
                fontsize=9, color=ec, fontfamily=FONT, fontweight="bold")

    savefig(fig, "slide0_title.png")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Layer 1: Supply Chain Network
# ══════════════════════════════════════════════════════════════════════════════
def slide1_layer1():
    # Wide canvas: left band (-11.5 → -4.5) reserved for legends; nodes start at -4
    fig, ax = plt.subplots(figsize=(20, 9), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("Layer 1 — Supply Chain Network",
                 color="white", fontsize=18, fontweight="bold", pad=16, fontfamily=FONT)

    G = nx.DiGraph()
    nodes = {
        "ChemCorp":   "Supplier",
        "AltChem":    "Supplier",
        "M-200":      "Item",
        "M-200-ALT":  "Item",
        "PO-4550":    "PurchaseOrder",
        "PO-4601":    "PurchaseOrder",
        "PRD-301":    "ProductionOrder",
        "INV-FG-A":   "Inventory",
        "DC-East":    "DistributionCenter",
        "SO-801":     "SalesOrder",
        "SO-802":     "SalesOrder",
        "MegaRetail": "Customer",
        "RetailB":    "Customer",
    }
    G.add_nodes_from(nodes.keys())

    raw_edges = [
        ("ChemCorp", "PO-4550",   "supplies"),
        ("AltChem",  "PO-4601",   "supplies"),
        ("PO-4550",  "M-200",     "delivers"),
        ("PO-4601",  "M-200",     "delivers"),
        ("M-200",    "PRD-301",   "consumed_by"),
        ("PRD-301",  "INV-FG-A",  "produces"),
        ("M-200",    "INV-FG-A",  "stocked_at"),
        ("INV-FG-A", "SO-801",    "allocated_to"),
        ("INV-FG-A", "DC-East",   "transfers_to"),
        ("DC-East",  "SO-802",    "ships_to"),
        ("SO-801",   "MegaRetail","fulfills"),
        ("SO-802",   "RetailB",   "fulfills"),
        ("ChemCorp", "AltChem",   "alternate_for"),
        ("M-200",    "M-200-ALT", "substitutes_for"),
        ("PO-4550",  "PRD-301",   "pegged_to"),
        ("PRD-301",  "SO-801",    "pegged_to"),
    ]
    elmap = {}
    for u, v, e in raw_edges:
        G.add_edge(u, v, etype=e)
        elmap[(u, v)] = e

    # Nodes in x ∈ [-3.5, 10.5]; legend band is x ∈ [-11.5, -5]  (6-unit clear gap)
    pos = {
        "ChemCorp":   (-3.0,  3.0),
        "AltChem":    (-3.0, -0.8),
        "PO-4550":    (-0.2,  3.0),
        "PO-4601":    (-0.2, -0.8),
        "M-200":      ( 2.2,  1.0),
        "M-200-ALT":  ( 2.2, -0.8),
        "PRD-301":    ( 4.8,  3.0),
        "INV-FG-A":   ( 6.8,  2.2),
        "DC-East":    ( 5.8, -0.8),
        "SO-801":     ( 8.8,  3.0),
        "SO-802":     ( 8.8, -0.8),
        "MegaRetail": (10.5,  3.0),
        "RetailB":    (10.5, -0.8),
    }

    draw_graph(ax, G, pos, nodes, elmap, node_size=2000, font_size=11, edge_font_size=9.5)

    # Legend 1: node types — far-left reserved band, no node closer than x=-3
    leg1 = make_legend(ax, [
        ("Supplier",            NODE_COLORS["Supplier"],           "patch"),
        ("Item / Material",     NODE_COLORS["Item"],               "patch"),
        ("Purchase Order",      NODE_COLORS["PurchaseOrder"],      "patch"),
        ("Production Order",    NODE_COLORS["ProductionOrder"],    "patch"),
        ("Inventory",           NODE_COLORS["Inventory"],          "patch"),
        ("Distribution Center", NODE_COLORS["DistributionCenter"], "patch"),
        ("Sales Order",         NODE_COLORS["SalesOrder"],         "patch"),
        ("Customer",            NODE_COLORS["Customer"],           "patch"),
    ], title="Node Types", loc="upper left", fontsize=10)
    ax.add_artist(leg1)

    # Legend 2: edge types
    make_legend(ax, [
        ("supplies / delivers",     EDGE_COLORS["supplies"],      "line"),
        ("consumed_by / produces",  EDGE_COLORS["consumed_by"],   "line"),
        ("stocked_at / allocated",  EDGE_COLORS["stocked_at"],    "line"),
        ("transfers_to / ships_to", EDGE_COLORS["transfers_to"],  "line"),
        ("pegged_to",               EDGE_COLORS["pegged_to"],     "line"),
        ("alternate_for / subst.",  EDGE_COLORS["alternate_for"], "line"),
    ], title="Edge Types", loc="lower left", fontsize=10)

    # Pegging chain callout — points to PRD-301
    ax.annotate(
        "Pegging chain: PO-4550 → PRD-301 → SO-801 → MegaRetail\n"
        "Critical multi-hop path: impact calculated in milliseconds",
        xy=(4.8, 3.0), xytext=(3.5, -2.2),
        fontsize=10, color="#d4a017", fontfamily=FONT,
        arrowprops=dict(arrowstyle="->", color="#d4a017", lw=1.4),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1422", edgecolor="#d4a017", alpha=0.9),
    )

    ax.set_xlim(-11.5, 13.2)
    ax.set_ylim(-3.2, 4.5)
    savefig(fig, "slide1_layer1_supply_chain.png")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Layer 2: Intelligence Layer
# ══════════════════════════════════════════════════════════════════════════════
def slide2_layer2():
    # Left band x ∈ [-12, -7] reserved for phase boxes + legend; nodes start at x=-5
    fig, ax = plt.subplots(figsize=(22, 11), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("Layer 2 — Intelligence Layer (Context Graph)",
                 color="white", fontsize=18, fontweight="bold", pad=16, fontfamily=FONT)

    G = nx.DiGraph()
    ntype = {
        "G-SLA":         "Goal",
        "G-Cost":        "Goal",
        "G-Risk":        "Goal",
        "POL-Approval":  "Policy",
        "EP-001":        "Episode",
        "EP-002":        "Episode",
        "EP-003":        "Episode",
        "EP-004":        "Episode",
        "DEC-001":       "MitigationDecision",
        "DEC-002":       "MitigationDecision",
        "FACT-001":      "Fact",
        "FACT-002":      "Fact",
        "REF-001":       "Reflection",
        "supp_rel":      "Concept",
        "alt_vendor":    "Concept",
        "REC-001":       "Recommendation",
    }
    G.add_nodes_from(ntype.keys())

    raw_edges = [
        ("EP-001", "EP-002",   "NEXT"),
        ("EP-002", "EP-003",   "NEXT"),
        ("EP-003", "EP-004",   "NEXT"),
        ("DEC-001","EP-003",   "DERIVED_FROM"),
        ("DEC-002","EP-004",   "DERIVED_FROM"),
        ("FACT-001","EP-002",  "DERIVED_FROM"),
        ("FACT-001","EP-003",  "DERIVED_FROM"),
        ("FACT-001","DEC-001", "DERIVED_FROM"),
        ("FACT-002","EP-004",  "DERIVED_FROM"),
        ("REF-001","FACT-001", "DERIVED_FROM_FACT"),
        ("REF-001","FACT-002", "DERIVED_FROM_FACT"),
        ("EP-003","supp_rel",  "HAS_CONCEPT"),
        ("EP-004","alt_vendor","HAS_CONCEPT"),
        ("FACT-001","supp_rel","ABOUT_CONCEPT"),
        ("FACT-002","alt_vendor","ABOUT_CONCEPT"),
        ("REC-001","REF-001",  "SUPPORTED_BY"),
        ("DEC-001","POL-Approval","GOVERNED_BY"),
        ("DEC-002","POL-Approval","GOVERNED_BY"),
        ("DEC-001","G-SLA",    "SCORED_AGAINST"),
        ("DEC-001","G-Cost",   "SCORED_AGAINST"),
        ("DEC-002","G-SLA",    "SCORED_AGAINST"),
        ("DEC-002","G-Risk",   "SCORED_AGAINST"),
    ]
    elmap = {}
    for u, v, e in raw_edges:
        G.add_edge(u, v, etype=e)
        elmap[(u, v)] = e

    # Nodes in x ∈ [-5, 16]; left band x ∈ [-12, -6] reserved for phase boxes + legend
    pos = {
        "G-SLA":        (11.0,  5.5),
        "G-Cost":       (13.5,  5.5),
        "G-Risk":       (16.0,  5.5),
        "POL-Approval": (13.5,  3.2),
        "EP-001":       (-4.5,  5.5),
        "EP-002":       (-1.5,  5.5),
        "EP-003":       ( 1.5,  5.5),
        "EP-004":       ( 4.5,  5.5),
        "DEC-001":      ( 1.5,  3.0),
        "DEC-002":      ( 4.5,  3.0),
        "FACT-001":     (-1.0,  1.0),
        "FACT-002":     ( 2.0,  1.0),
        "REF-001":      ( 0.5, -1.2),
        "supp_rel":     (-4.5,  3.0),
        "alt_vendor":   ( 8.0,  3.0),
        "REC-001":      ( 0.5, -3.2),
    }

    draw_graph(ax, G, pos, ntype, elmap, node_size=1800, font_size=11, edge_font_size=9)

    # Phase annotation boxes in the reserved left band
    phases = [
        (-11.5,  4.2, 3.0, 2.2, "① PRESERVE",
         "Every Disruption Mitigation\nAgent run writes Episode +\nMitigationDecision immediately"),
        (-11.5,  1.2, 3.0, 2.2, "② EXTRACT",
         "LLM batch job distils\nFact nodes from\nrecent Episodes"),
        (-11.5, -2.8, 3.0, 2.2, "③ SYNTHESIZE",
         "LLM generates Reflections\n& Recommendations\nfrom Fact clusters"),
    ]
    for x, y, w, h, title, body in phases:
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.3",
            facecolor="#1a1a2e", edgecolor="#5566aa", linewidth=1.5, alpha=0.9))
        ax.text(x + w/2, y + h - 0.28, title, ha="center", va="top",
                fontsize=10, fontweight="bold", color="#aac4ff", fontfamily=FONT)
        ax.text(x + w/2, y + h/2 - 0.1, body, ha="center", va="center",
                fontsize=8.5, color="#e0e0ff", fontfamily=FONT, multialignment="center")

    # Legend 1 (node types) — far left, below phase boxes
    leg1 = make_legend(ax, [
        ("Episode",             NODE_COLORS["Episode"],           "patch"),
        ("MitigationDecision",  NODE_COLORS["MitigationDecision"],"patch"),
        ("Fact",                NODE_COLORS["Fact"],              "patch"),
        ("Reflection",          NODE_COLORS["Reflection"],        "patch"),
        ("Concept",             NODE_COLORS["Concept"],           "patch"),
        ("Policy",              NODE_COLORS["Policy"],            "patch"),
        ("Goal",                NODE_COLORS["Goal"],              "patch"),
        ("Recommendation",      NODE_COLORS["Recommendation"],    "patch"),
    ], title="Node Types", loc="lower left", fontsize=10)
    ax.add_artist(leg1)

    # Legend 2 (edge types) — lower right
    make_legend(ax, [
        ("NEXT (temporal sequence)",    EDGE_COLORS["NEXT"],             "line"),
        ("DERIVED_FROM",                EDGE_COLORS["DERIVED_FROM"],     "line"),
        ("DERIVED_FROM_FACT",           EDGE_COLORS["DERIVED_FROM_FACT"],"line"),
        ("HAS_CONCEPT / ABOUT_CONCEPT", EDGE_COLORS["HAS_CONCEPT"],      "line"),
        ("GOVERNED_BY",                 EDGE_COLORS["GOVERNED_BY"],      "line"),
        ("SCORED_AGAINST",              EDGE_COLORS["SCORED_AGAINST"],   "line"),
        ("SUPPORTED_BY",                EDGE_COLORS["SUPPORTED_BY"],     "line"),
    ], title="Edge Types", loc="lower right", fontsize=10)

    ax.set_xlim(-12.5, 18.0)
    ax.set_ylim(-5.0, 7.5)
    savefig(fig, "slide2_layer2_intelligence.png")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Full Two-Layer Combined
# ══════════════════════════════════════════════════════════════════════════════
def slide3_two_layer():
    # Legends sit BELOW both layer bands (y < -4.5); bands start at y=-4.0
    fig, ax = plt.subplots(figsize=(22, 15), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("Two-Layer Supply Chain Intelligence Network",
                 color="white", fontsize=18, fontweight="bold", pad=16, fontfamily=FONT)
    ax.set_xlim(-11.0, 13.0)
    ax.set_ylim(-8.5, 10.5)

    # Layer bands — chosen so legend area sits below y=-4.5
    for y0, y1, fc, label, lc in [
        (-4.0, 1.2,  "#0a1e30", "LAYER 1 — Supply Chain Network",  "#5baee0"),
        ( 1.8, 9.5,  "#180d2a", "LAYER 2 — Intelligence Layer",    "#b87aff"),
    ]:
        ax.add_patch(mpatches.FancyBboxPatch(
            (-10.5, y0), 23.0, y1-y0, boxstyle="round,pad=0.3",
            facecolor=fc, edgecolor="#333", linewidth=1.5, alpha=0.7, zorder=0))
        ax.text(-10.2, y0+0.35, label, fontsize=10, color=lc,
                fontfamily=FONT, fontweight="bold", va="bottom", zorder=1)

    ax.axhline(1.5, color="#555", linewidth=1.5, linestyle="--", alpha=0.7)
    ax.text(0, 1.65, "— CROSS-LAYER EDGES —", fontsize=9, color="#777",
            ha="center", va="bottom", fontfamily=FONT)

    G = nx.DiGraph()
    ntype = {}
    for n, t in {
        "ChemCorp": "Supplier", "AltChem": "Supplier",
        "PO-4550":  "PurchaseOrder", "M-200": "Item",
        "PRD-301":  "ProductionOrder", "INV":  "Inventory",
        "SO-801":   "SalesOrder", "MegaRetail": "Customer",
    }.items():
        ntype[n] = t
    for n, t in {
        "EP-001": "Episode", "EP-002": "Episode", "EP-003": "Episode",
        "DEC-001": "MitigationDecision",
        "FACT-001": "Fact", "FACT-002": "Fact",
        "REF-001": "Reflection", "supp_rel": "Concept",
        "REC-001": "Recommendation", "G-SLA": "Goal", "POL": "Policy",
    }.items():
        ntype[n] = t
    G.add_nodes_from(ntype.keys())

    l1_edges = [
        ("ChemCorp","PO-4550","supplies"), ("PO-4550","M-200","delivers"),
        ("M-200","PRD-301","consumed_by"), ("PRD-301","INV","produces"),
        ("INV","SO-801","allocated_to"),   ("SO-801","MegaRetail","fulfills"),
        ("PO-4550","PRD-301","pegged_to"), ("ChemCorp","AltChem","alternate_for"),
    ]
    l2_edges = [
        ("EP-001","EP-002","NEXT"), ("EP-002","EP-003","NEXT"),
        ("DEC-001","EP-003","DERIVED_FROM"),
        ("FACT-001","EP-001","DERIVED_FROM"), ("FACT-001","EP-002","DERIVED_FROM"),
        ("FACT-002","DEC-001","DERIVED_FROM"),
        ("REF-001","FACT-001","DERIVED_FROM_FACT"), ("REF-001","FACT-002","DERIVED_FROM_FACT"),
        ("EP-003","supp_rel","HAS_CONCEPT"), ("FACT-001","supp_rel","ABOUT_CONCEPT"),
        ("REC-001","REF-001","SUPPORTED_BY"),
        ("DEC-001","G-SLA","SCORED_AGAINST"), ("DEC-001","POL","GOVERNED_BY"),
    ]
    cross_edges = [
        ("EP-001","ChemCorp","CONCERNS"),  ("EP-002","M-200","CONCERNS"),
        ("EP-003","PO-4550","CONCERNS"),
        ("FACT-001","ChemCorp","CHARACTERIZES"), ("FACT-002","M-200","CHARACTERIZES"),
        ("REF-001","M-200","TARGETS"), ("REC-001","ChemCorp","APPLIES_TO"),
        ("DEC-001","PO-4550","RESOLVED"),
    ]

    elmap = {}
    for u, v, e in l1_edges + l2_edges:
        G.add_edge(u, v, etype=e, cross=False); elmap[(u, v)] = e
    for u, v, e in cross_edges:
        G.add_edge(u, v, etype=e, cross=True); elmap[(u, v)] = e

    # L1 nodes in y ∈ [-1.2, -3.0]; L2 nodes in y ∈ [2.8, 9.0]
    pos = {
        # L1
        "ChemCorp":   (-5.5, -1.2), "AltChem":   (-5.5, -3.0),
        "PO-4550":    (-2.5, -1.2), "M-200":     ( 0.0, -2.0),
        "PRD-301":    ( 2.5, -1.2), "INV":       ( 5.0, -2.0),
        "SO-801":     ( 7.5, -1.2), "MegaRetail":( 9.8, -1.2),
        # L2
        "EP-001":     (-7.0, 8.5), "EP-002":    (-4.0, 8.5),
        "EP-003":     (-1.0, 8.5), "DEC-001":   (-1.0, 6.0),
        "FACT-001":   (-4.5, 6.0), "FACT-002":  (-1.0, 4.2),
        "REF-001":    (-4.5, 4.2), "supp_rel":  ( 2.5, 7.2),
        "REC-001":    (-7.5, 4.2), "G-SLA":     ( 7.0, 6.5),
        "POL":        ( 7.0, 5.0),
    }

    draw_graph(ax, G, pos, ntype, elmap, node_size=1600, font_size=10, edge_font_size=8.5)

    # Annotations
    ax.annotate("Agent reads Layer 2 context\nbefore evaluating mitigations",
                xy=(-1.0, 4.2), xytext=(2.5, 3.0),
                fontsize=9.5, color="#b87aff", fontfamily=FONT,
                arrowprops=dict(arrowstyle="->", color="#b87aff", lw=1.4),
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#180d2a",
                          edgecolor="#b87aff", alpha=0.9))
    ax.annotate("Agent executes via MCP\non Layer 1 (D365)",
                xy=(-2.5, -1.2), xytext=(0.5, -6.2),
                fontsize=9.5, color="#5baee0", fontfamily=FONT,
                arrowprops=dict(arrowstyle="->", color="#5baee0", lw=1.4),
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#0a1e30",
                          edgecolor="#5baee0", alpha=0.9))
    ax.annotate("Decision trace written\nback to Layer 2",
                xy=(-1.0, 6.0), xytext=(2.5, 5.0),
                fontsize=9.5, color="#c8b800", fontfamily=FONT,
                arrowprops=dict(arrowstyle="->", color="#c8b800", lw=1.4),
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#1a1800",
                          edgecolor="#c8b800", alpha=0.9))

    # Both legends sit in the area below y=-4.5, clear of both layer bands
    leg1 = make_legend(ax, [
        ("Supplier",           NODE_COLORS["Supplier"],           "patch"),
        ("Item",               NODE_COLORS["Item"],               "patch"),
        ("Purchase Order",     NODE_COLORS["PurchaseOrder"],      "patch"),
        ("Production Order",   NODE_COLORS["ProductionOrder"],    "patch"),
        ("Inventory",          NODE_COLORS["Inventory"],          "patch"),
        ("Sales Order",        NODE_COLORS["SalesOrder"],         "patch"),
        ("Customer",           NODE_COLORS["Customer"],           "patch"),
        ("Episode",            NODE_COLORS["Episode"],            "patch"),
        ("MitigationDecision", NODE_COLORS["MitigationDecision"], "patch"),
        ("Fact",               NODE_COLORS["Fact"],               "patch"),
        ("Reflection",         NODE_COLORS["Reflection"],         "patch"),
        ("Concept",            NODE_COLORS["Concept"],            "patch"),
        ("Goal",               NODE_COLORS["Goal"],               "patch"),
        ("Policy",             NODE_COLORS["Policy"],             "patch"),
        ("Recommendation",     NODE_COLORS["Recommendation"],     "patch"),
    ], title="Node Types", loc="lower left", fontsize=9)
    ax.add_artist(leg1)

    make_legend(ax, [
        ("CONCERNS (Episode → L1)",   EDGE_COLORS["CONCERNS"],      "dashed"),
        ("CHARACTERIZES (Fact → L1)", EDGE_COLORS["CHARACTERIZES"], "dashed"),
        ("TARGETS / APPLIES_TO",      EDGE_COLORS["TARGETS"],       "dashed"),
        ("RESOLVED (Decision → PO)",  EDGE_COLORS["RESOLVED"],      "dashed"),
    ], title="Cross-Layer Edges", loc="lower right", fontsize=10)

    savefig(fig, "slide3_two_layer_combined.png")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — PO-MOTR Disruption Example
# ══════════════════════════════════════════════════════════════════════════════
def slide4_po_motr():
    # Legends sit below y=-5.5 (outside both layer bands); nodes spread widely
    fig, ax = plt.subplots(figsize=(26, 17), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("Worked Example — Disruption: PO-MOTR  |  DC Motor, Vendor 1003, 14-day delay",
                 color="white", fontsize=16, fontweight="bold", pad=16, fontfamily=FONT)
    ax.set_xlim(-14.0, 16.5)
    ax.set_ylim(-9.0, 11.5)

    for y0, y1, fc, label, lc in [
        (-5.0, 1.2,  "#0a1e30", "LAYER 1 — Supply Chain Network", "#5baee0"),
        ( 1.8, 10.5, "#180d2a", "LAYER 2 — Intelligence Layer",   "#b87aff"),
    ]:
        ax.add_patch(mpatches.FancyBboxPatch(
            (-13.5, y0), 29.5, y1-y0, boxstyle="round,pad=0.3",
            facecolor=fc, edgecolor="#333", linewidth=1.5, alpha=0.7, zorder=0))
        ax.text(-13.2, y0+0.35, label, fontsize=10, color=lc,
                fontfamily=FONT, fontweight="bold", va="bottom", zorder=1)

    ax.axhline(1.5, color="#555", linewidth=1.5, linestyle="--", alpha=0.7)

    # ── define node labels ──
    V3  = "Vendor 1003\n(Ade Supply)"
    V1  = "Vendor 1001\n(Acme)"
    V2  = "Vendor 1002\n(Lande)"
    POM = "PO-MOTR\n★ disrupted"
    MTD = "DMA-MTR-DC\n(DC Motor)"
    MTA = "DMA-MTR-AC\n(AC Motor)"
    IVD = "INV-DC\n30 units"
    IVA = "INV-AC\n30 units"
    SOM = "SO-MOTR\n100 units"
    CUS = "US-001\n(MegaRetail T1)"

    ntype = {
        V3: "Supplier", V1: "Supplier", V2: "Supplier",
        POM: "PurchaseOrder", MTD: "Item", MTA: "Item",
        IVD: "Inventory", IVA: "Inventory",
        SOM: "SalesOrder", CUS: "Customer",
        "EP-001": "Episode", "EP-002": "Episode", "EP-003": "Episode",
        "EP-004": "Episode", "EP-005": "Episode", "EP-006\n(PO-MOTR)": "Episode",
        "DEC-006A\nVend1002 rank1": "MitigationDecision",
        "DEC-006B\nVend1001 rank2": "MitigationDecision",
        "DEC-006C\nUseOnHand":      "MitigationDecision",
        "DEC-006D\nAltItem":        "MitigationDecision",
        "FACT-006\n30u on-hand\nvs 20u floor":        "Fact",
        "FACT-007\nVend1003 sourced\nall 6 episodes": "Fact",
        "REF-003\non-hand/floor\n< 2× → risk":        "Reflection",
        "ss_erosion": "Concept",
        "alt_vendor":  "Concept",
        "G-SLA\n25%": "Goal", "G-Cost\n25%": "Goal",
        "G-Qty\n25%":  "Goal", "G-Inv\n25%":  "Goal",
        "POL-ONHOLD": "Policy",
        "REC-001\nQualify 1001/1002\nas alternates":    "Recommendation",
        "REC-002\nIncrease on-hand\ntarget ≥ 40 units": "Recommendation",
    }
    G = nx.DiGraph()
    G.add_nodes_from(ntype.keys())

    l1_edges = [
        (V3,  POM, "supplies"),   (POM, MTD, "delivers"),
        (MTD, IVD, "stocked_at"), (MTA, IVA, "stocked_at"),
        (MTD, MTA, "substitutes_for"),
        (POM, SOM, "pegged_to"),  (SOM, CUS, "fulfills"),
    ]
    l2_edges = [
        ("EP-001","EP-002","NEXT"), ("EP-002","EP-003","NEXT"),
        ("EP-003","EP-004","NEXT"), ("EP-004","EP-005","NEXT"),
        ("EP-005","EP-006\n(PO-MOTR)","NEXT"),
        ("DEC-006A\nVend1002 rank1","EP-006\n(PO-MOTR)","DERIVED_FROM"),
        ("DEC-006B\nVend1001 rank2","EP-006\n(PO-MOTR)","DERIVED_FROM"),
        ("DEC-006C\nUseOnHand",     "EP-006\n(PO-MOTR)","DERIVED_FROM"),
        ("DEC-006D\nAltItem",       "EP-006\n(PO-MOTR)","DERIVED_FROM"),
        ("FACT-006\n30u on-hand\nvs 20u floor","EP-006\n(PO-MOTR)","DERIVED_FROM"),
        ("FACT-007\nVend1003 sourced\nall 6 episodes","EP-001","DERIVED_FROM"),
        ("REF-003\non-hand/floor\n< 2× → risk","FACT-006\n30u on-hand\nvs 20u floor","DERIVED_FROM_FACT"),
        ("EP-006\n(PO-MOTR)","ss_erosion","HAS_CONCEPT"),
        ("EP-006\n(PO-MOTR)","alt_vendor","HAS_CONCEPT"),
        ("FACT-006\n30u on-hand\nvs 20u floor","ss_erosion","ABOUT_CONCEPT"),
        ("DEC-006A\nVend1002 rank1","G-SLA\n25%",  "SCORED_AGAINST"),
        ("DEC-006A\nVend1002 rank1","G-Cost\n25%", "SCORED_AGAINST"),
        ("DEC-006A\nVend1002 rank1","G-Qty\n25%",  "SCORED_AGAINST"),
        ("DEC-006A\nVend1002 rank1","G-Inv\n25%",  "SCORED_AGAINST"),
        ("DEC-006A\nVend1002 rank1","POL-ONHOLD",  "GOVERNED_BY"),
        ("REC-001\nQualify 1001/1002\nas alternates","REF-003\non-hand/floor\n< 2× → risk","SUPPORTED_BY"),
        ("REC-002\nIncrease on-hand\ntarget ≥ 40 units","REF-003\non-hand/floor\n< 2× → risk","SUPPORTED_BY"),
    ]
    cross_edges = [
        ("EP-001",V3,"CONCERNS"), ("EP-002",V3,"CONCERNS"), ("EP-003",V3,"CONCERNS"),
        ("EP-006\n(PO-MOTR)",POM,"CONCERNS"),
        ("EP-006\n(PO-MOTR)",MTD,"CONCERNS"),
        ("FACT-007\nVend1003 sourced\nall 6 episodes",V3,"CHARACTERIZES"),
        ("FACT-006\n30u on-hand\nvs 20u floor",MTD,"CHARACTERIZES"),
        ("REF-003\non-hand/floor\n< 2× → risk",MTD,"TARGETS"),
        ("REC-002\nIncrease on-hand\ntarget ≥ 40 units",MTD,"APPLIES_TO"),
        ("DEC-006A\nVend1002 rank1",POM,"RESOLVED"),
    ]

    elmap = {}
    for u, v, e in l1_edges + l2_edges:
        G.add_edge(u, v, etype=e, cross=False); elmap[(u, v)] = e
    for u, v, e in cross_edges:
        G.add_edge(u, v, etype=e, cross=True); elmap[(u, v)] = e

    # Positions — L1 in y ∈ [-1, -4], L2 in y ∈ [2.5, 10]
    # Horizontal spread: L1 x ∈ [-9, 8], L2 x ∈ [-10, 15]
    pos = {
        # Layer 1
        V3:  (-9.0, -1.0), V1: (-9.0, -4.0), V2: (-6.5, -4.0),
        POM: (-5.0, -1.0), MTD: (-1.8, -1.3), MTA: (-1.8, -3.8),
        IVD: ( 1.8, -1.3), IVA: ( 1.8, -3.8),
        SOM: ( 5.0, -1.0), CUS: ( 8.5, -1.0),
        # Layer 2 episodes (top row, 3-unit spacing)
        "EP-001": (-10.5, 9.5), "EP-002": (-7.0, 9.5),
        "EP-003": ( -3.5, 9.5), "EP-004": ( 0.0, 9.5),
        "EP-005": (  3.5, 9.5), "EP-006\n(PO-MOTR)": ( 7.0, 9.5),
        # Decisions (2.5-unit spacing)
        "DEC-006A\nVend1002 rank1": ( 2.5, 7.2),
        "DEC-006B\nVend1001 rank2": ( 5.5, 7.2),
        "DEC-006C\nUseOnHand":      ( 8.5, 7.2),
        "DEC-006D\nAltItem":        (11.5, 7.2),
        # Facts (3-unit horizontal gap)
        "FACT-006\n30u on-hand\nvs 20u floor":        (-3.5, 7.0),
        "FACT-007\nVend1003 sourced\nall 6 episodes": (-8.0, 7.0),
        # Reflection
        "REF-003\non-hand/floor\n< 2× → risk": (-5.8, 4.8),
        # Concepts
        "ss_erosion": ( 0.0, 4.8), "alt_vendor": ( 3.0, 4.8),
        # Goals (2-unit spacing)
        "G-SLA\n25%":  (10.5, 5.8), "G-Cost\n25%": (12.5, 5.8),
        "G-Qty\n25%":  (14.5, 5.8), "G-Inv\n25%":  (16.0, 5.8),
        "POL-ONHOLD":  (13.5, 7.2),
        # Recommendations
        "REC-001\nQualify 1001/1002\nas alternates":    (-12.0, 4.8),
        "REC-002\nIncrease on-hand\ntarget ≥ 40 units": (-12.0, 3.0),
    }

    draw_graph(ax, G, pos, ntype, elmap, node_size=1400, font_size=9, edge_font_size=8, edge_lw=1.2)

    # Yellow ring on disrupted PO
    px, py = pos[POM]
    ax.add_patch(plt.Circle((px, py), 0.65, color="#f5c518",
                             fill=False, linewidth=3.5, zorder=5))

    # Callouts
    ax.annotate(
        "6 prior disruptions by Vendor 1003\ninstantly surfaced via CHARACTERIZES edges\n"
        "→ Agent knows: unreliable vendor, use alternates",
        xy=pos["FACT-007\nVend1003 sourced\nall 6 episodes"],
        xytext=(-13.0, 2.0),
        fontsize=9.5, color="#f5e642", fontfamily=FONT, multialignment="left",
        arrowprops=dict(arrowstyle="->", color="#f5e642", lw=1.4),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1422",
                  edgecolor="#f5e642", alpha=0.9), zorder=10)

    ax.annotate(
        "RESOLVED edge records\nVendor 1002 selected\n(rank 1, $52/unit, 8-day lead)",
        xy=(px, py), xytext=(4.0, -6.5),
        fontsize=9.5, color="#00c9b1", fontfamily=FONT, multialignment="left",
        arrowprops=dict(arrowstyle="->", color="#00c9b1", lw=1.4),
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#0d1e1a",
                  edgecolor="#00c9b1", alpha=0.9), zorder=10)

    # Legends — below both layer bands (y < -5.5)
    leg1 = make_legend(ax, [
        ("Supplier",           NODE_COLORS["Supplier"],           "patch"),
        ("Item",               NODE_COLORS["Item"],               "patch"),
        ("Purchase Order ★",   NODE_COLORS["PurchaseOrder"],      "patch"),
        ("Inventory",          NODE_COLORS["Inventory"],          "patch"),
        ("Sales Order",        NODE_COLORS["SalesOrder"],         "patch"),
        ("Customer",           NODE_COLORS["Customer"],           "patch"),
        ("Episode",            NODE_COLORS["Episode"],            "patch"),
        ("MitigationDecision", NODE_COLORS["MitigationDecision"], "patch"),
        ("Fact",               NODE_COLORS["Fact"],               "patch"),
        ("Reflection",         NODE_COLORS["Reflection"],         "patch"),
        ("Concept",            NODE_COLORS["Concept"],            "patch"),
        ("Goal",               NODE_COLORS["Goal"],               "patch"),
        ("Policy",             NODE_COLORS["Policy"],             "patch"),
        ("Recommendation",     NODE_COLORS["Recommendation"],     "patch"),
    ], title="Node Types", loc="lower left", fontsize=9)
    ax.add_artist(leg1)

    make_legend(ax, [
        ("CONCERNS (Episode → L1)",  EDGE_COLORS["CONCERNS"],      "dashed"),
        ("CHARACTERIZES (Fact → L1)",EDGE_COLORS["CHARACTERIZES"], "dashed"),
        ("TARGETS / APPLIES_TO",     EDGE_COLORS["TARGETS"],       "dashed"),
        ("RESOLVED (Decision → PO)", EDGE_COLORS["RESOLVED"],      "dashed"),
    ], title="Cross-Layer Edges", loc="lower right", fontsize=10)

    savefig(fig, "slide4_po_motr_example.png")


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — Retrieval / Execution Flow
# ══════════════════════════════════════════════════════════════════════════════
def slide5_retrieval_flow():
    fig, ax = plt.subplots(figsize=(16, 8), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("How the Agent Uses the Two-Layer Graph — Query & Execution Flow",
                 color="white", fontsize=15, fontweight="bold", pad=14, fontfamily=FONT)
    ax.set_xlim(-7.5, 11.5)
    ax.set_ylim(-4.0, 4.0)

    BOX_W, BOX_H = 2.6, 2.4

    steps = [
        (-6.5,  0.5, "#0a2a1a", "#27c9a0",
         "① Disruption\nDetected",
         "PO-MOTR:\nVendor 1003, DC Motor\n14-day delay, 100 units"),
        (-2.8,  0.5, "#0a1e30", "#5baee0",
         "② Anchor\nTraversal",
         "Start at Vendor 1003 +\nDMA-MTR-DC in Layer 1.\nFollow CHARACTERIZES\nedges into Layer 2"),
        ( 0.9,  0.5, "#1a0d2a", "#b87aff",
         "③ Concept\nExpansion",
         "Reach Concept nodes:\nsafety_stock_erosion,\nalt_vendor_switch.\nBack-traverse to all\nFacts & Reflections"),
        ( 4.6,  0.5, "#2a1a0a", "#c8b800",
         "④ Rank &\nInject Context",
         "Weight recent episodes\nhigher. Inject top-k\nFacts + Reflections\ninto agent system prompt"),
        ( 8.3,  0.5, "#0d1422", "#f472b6",
         "⑤ Evaluate\nMitigations",
         "Score options vs Goals\n& Policies.\nRank 1 → Vendor 1002\n(known good alternate)"),
        (-6.5, -3.0, "#2a0d0d", "#c03d3d",
         "⑥ Execute\nvia MCP",
         "Issue PO to Vendor 1002.\nUpdate D365.\nWrite Episode + Decision\nback to Layer 2 ♻"),
    ]

    centres = []
    for x, y, fc, ec, title, body in steps:
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), BOX_W, BOX_H, boxstyle="round,pad=0.3",
            facecolor=fc, edgecolor=ec, linewidth=2.0, alpha=0.97, zorder=2))
        ax.text(x + BOX_W/2, y + BOX_H - 0.28, title, ha="center", va="top",
                fontsize=9, fontweight="bold", color=ec, fontfamily=FONT)
        ax.text(x + BOX_W/2, y + BOX_H/2 - 0.1, body, ha="center", va="center",
                fontsize=7.5, color="white", fontfamily=FONT, multialignment="center")
        centres.append((x + BOX_W/2, y + BOX_H/2))

    # Arrows 1→2, 2→3, 3→4, 4→5
    for i in range(4):
        ax.annotate("", xy=(centres[i+1][0] - BOX_W/2, centres[i+1][1]),
                    xytext=(centres[i][0] + BOX_W/2, centres[i][1]),
                    arrowprops=dict(arrowstyle="-|>", color="#888",
                                   lw=1.8, mutation_scale=14), zorder=3)

    # Arrow 5→6 curved
    ax.annotate("", xy=(centres[5][0] + BOX_W/2, centres[5][1]),
                xytext=(centres[4][0] + BOX_W/2, centres[4][1]),
                arrowprops=dict(arrowstyle="-|>", color="#c03d3d",
                                lw=1.8, mutation_scale=14,
                                connectionstyle="arc3,rad=0.45"), zorder=3)

    # "each run enriches" banner
    ax.text(2.0, -3.8,
            "Every execution enriches Layer 2 — the next disruption on Vendor 1003 or DMA-MTR-DC\n"
            "arrives pre-loaded with 6 episodes, 2 facts, 1 reflection, and 2 recommendations.",
            ha="center", va="center", fontsize=9.5, color="#e8e0ff",
            fontfamily=FONT, multialignment="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1030",
                      edgecolor="#7e3af2", alpha=0.9), zorder=3)

    savefig(fig, "slide5_retrieval_flow.png")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating demo slides...")
    slide0_title()
    slide1_layer1()
    slide2_layer2()
    slide3_two_layer()
    slide4_po_motr()
    slide5_retrieval_flow()
    print("Done.")
