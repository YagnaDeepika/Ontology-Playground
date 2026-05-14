"""
Generate slide4_clickthrough_full_v3.html

Changes vs v2:
  Layout  : image pane 75% (was 64%), script pane 25%, script font 11 px (was 13 px)
  View  3 : Layer 2 slide — bigger node labels, edge labels, legend fonts
  View  4 : Architecture slide — bigger node labels, edge labels, legend fonts
  View  5 : Agent Loop slide — bigger box title/body fonts
  View  9 : ④ 6 Prior Episodes — bigger fonts
  View 10 : ⑤ FACT-007 — bigger fonts
  View 11 : ⑥ Safety Stock Risk — bigger fonts

All other stages (including the View-7 patch) loaded from v2 HTML unchanged.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import sys, os, io, json, re, base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_html as gh
from generate_slides import NODE_COLORS, EDGE_COLORS, FONT, draw_graph, make_legend

from PIL import Image

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
SRC_HTML    = os.path.join(SCRIPT_DIR, "slide4_clickthrough_full_v2.html")
OUT_HTML    = os.path.join(SCRIPT_DIR, "slide4_clickthrough_full_v3.html")
TARGET_SIZE = (1760, 990)
BG          = "#0d1117"


# ── helpers ───────────────────────────────────────────────────────────────────
def slide_to_b64(fig, dpi=160):
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, bbox_inches="tight", pad_inches=0.3, facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGB").resize(TARGET_SIZE, Image.LANCZOS)
    buf2 = io.BytesIO()
    img.save(buf2, format="PNG", optimize=True)
    return base64.b64encode(buf2.getvalue()).decode()


def load_stages():
    with open(SRC_HTML, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"const STAGES = (\[)", src)
    start = m.start(1)
    depth = 0
    for i, c in enumerate(src[start:]):
        if c == "[":   depth += 1
        elif c == "]": depth -= 1
        if depth == 0:
            end = start + i + 1
            break
    return json.loads(src[start:end])


# ── View 3 — Layer 2 Intelligence Layer (bigger fonts) ───────────────────────
def render_slide2_large():
    fig, ax = plt.subplots(figsize=(22, 11), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("Layer 2 — Intelligence Layer (Context Graph)",
                 color="white", fontsize=20, fontweight="bold", pad=16, fontfamily=FONT)

    G = nx.DiGraph()
    ntype = {
        "G-SLA": "Goal", "G-Cost": "Goal", "G-Risk": "Goal",
        "POL-Approval": "Policy",
        "EP-001": "Episode", "EP-002": "Episode",
        "EP-003": "Episode", "EP-004": "Episode",
        "DEC-001": "MitigationDecision", "DEC-002": "MitigationDecision",
        "FACT-001": "Fact", "FACT-002": "Fact",
        "REF-001": "Reflection",
        "supp_rel": "Concept", "alt_vendor": "Concept",
        "REC-001": "Recommendation",
    }
    G.add_nodes_from(ntype.keys())

    raw_edges = [
        ("EP-001","EP-002","NEXT"), ("EP-002","EP-003","NEXT"), ("EP-003","EP-004","NEXT"),
        ("DEC-001","EP-003","DERIVED_FROM"), ("DEC-002","EP-004","DERIVED_FROM"),
        ("FACT-001","EP-002","DERIVED_FROM"), ("FACT-001","EP-003","DERIVED_FROM"),
        ("FACT-001","DEC-001","DERIVED_FROM"), ("FACT-002","EP-004","DERIVED_FROM"),
        ("REF-001","FACT-001","DERIVED_FROM_FACT"), ("REF-001","FACT-002","DERIVED_FROM_FACT"),
        ("EP-003","supp_rel","HAS_CONCEPT"), ("EP-004","alt_vendor","HAS_CONCEPT"),
        ("FACT-001","supp_rel","ABOUT_CONCEPT"), ("FACT-002","alt_vendor","ABOUT_CONCEPT"),
        ("REC-001","REF-001","SUPPORTED_BY"),
        ("DEC-001","POL-Approval","GOVERNED_BY"), ("DEC-002","POL-Approval","GOVERNED_BY"),
        ("DEC-001","G-SLA","SCORED_AGAINST"), ("DEC-001","G-Cost","SCORED_AGAINST"),
        ("DEC-002","G-SLA","SCORED_AGAINST"), ("DEC-002","G-Risk","SCORED_AGAINST"),
    ]
    elmap = {}
    for u, v, e in raw_edges:
        G.add_edge(u, v, etype=e); elmap[(u, v)] = e

    pos = {
        "G-SLA": (11.0, 5.5), "G-Cost": (13.5, 5.5), "G-Risk": (16.0, 5.5),
        "POL-Approval": (13.5, 3.2),
        "EP-001": (-4.5, 5.5), "EP-002": (-1.5, 5.5),
        "EP-003": (1.5, 5.5), "EP-004": (4.5, 5.5),
        "DEC-001": (1.5, 3.0), "DEC-002": (4.5, 3.0),
        "FACT-001": (-1.0, 1.0), "FACT-002": (2.0, 1.0),
        "REF-001": (0.5, -1.2),
        "supp_rel": (-4.5, 3.0), "alt_vendor": (8.0, 3.0),
        "REC-001": (0.5, -3.2),
    }

    # Larger fonts: node labels 15pt, edge labels 12pt
    draw_graph(ax, G, pos, ntype, elmap, node_size=2200, font_size=15, edge_font_size=12)

    # Phase boxes
    phases = [
        (-11.5, 4.2, 3.0, 2.2, "① PRESERVE",
         "Every Disruption Mitigation\nAgent run writes Episode +\nMitigationDecision immediately"),
        (-11.5, 1.2, 3.0, 2.2, "② EXTRACT",
         "LLM batch job distils\nFact nodes from\nrecent Episodes"),
        (-11.5, -2.8, 3.0, 2.2, "③ SYNTHESIZE",
         "LLM generates Reflections\n& Recommendations\nfrom Fact clusters"),
    ]
    for x, y, w, h, title, body in phases:
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.3",
            facecolor="#1a1a2e", edgecolor="#5566aa", linewidth=1.5, alpha=0.9))
        ax.text(x + w/2, y + h - 0.28, title, ha="center", va="top",
                fontsize=12, fontweight="bold", color="#aac4ff", fontfamily=FONT)
        ax.text(x + w/2, y + h/2 - 0.1, body, ha="center", va="center",
                fontsize=10.5, color="#e0e0ff", fontfamily=FONT, multialignment="center")

    leg1 = make_legend(ax, [
        ("Episode",            NODE_COLORS["Episode"],           "patch"),
        ("MitigationDecision", NODE_COLORS["MitigationDecision"],"patch"),
        ("Fact",               NODE_COLORS["Fact"],              "patch"),
        ("Reflection",         NODE_COLORS["Reflection"],        "patch"),
        ("Concept",            NODE_COLORS["Concept"],           "patch"),
        ("Policy",             NODE_COLORS["Policy"],            "patch"),
        ("Goal",               NODE_COLORS["Goal"],              "patch"),
        ("Recommendation",     NODE_COLORS["Recommendation"],    "patch"),
    ], title="Node Types", loc="lower left", fontsize=13)
    ax.add_artist(leg1)

    make_legend(ax, [
        ("NEXT (temporal sequence)",    EDGE_COLORS["NEXT"],              "line"),
        ("DERIVED_FROM",                EDGE_COLORS["DERIVED_FROM"],      "line"),
        ("DERIVED_FROM_FACT",           EDGE_COLORS["DERIVED_FROM_FACT"], "line"),
        ("HAS_CONCEPT / ABOUT_CONCEPT", EDGE_COLORS["HAS_CONCEPT"],       "line"),
        ("GOVERNED_BY",                 EDGE_COLORS["GOVERNED_BY"],       "line"),
        ("SCORED_AGAINST",              EDGE_COLORS["SCORED_AGAINST"],    "line"),
        ("SUPPORTED_BY",                EDGE_COLORS["SUPPORTED_BY"],      "line"),
    ], title="Edge Types", loc="lower right", fontsize=13)

    ax.set_xlim(-12.5, 18.0)
    ax.set_ylim(-5.0, 7.5)
    return slide_to_b64(fig)


# ── View 4 — Two-Layer Architecture (bigger fonts) ───────────────────────────
def render_slide3_large():
    fig, ax = plt.subplots(figsize=(22, 15), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("Two-Layer Supply Chain Intelligence Network",
                 color="white", fontsize=20, fontweight="bold", pad=16, fontfamily=FONT)
    ax.set_xlim(-11.0, 13.0)
    ax.set_ylim(-8.5, 10.5)

    for y0, y1, fc, label, lc in [
        (-4.0, 1.2, "#0a1e30", "LAYER 1 — Supply Chain Network", "#5baee0"),
        ( 1.8, 9.5, "#180d2a", "LAYER 2 — Intelligence Layer",   "#b87aff"),
    ]:
        ax.add_patch(mpatches.FancyBboxPatch(
            (-10.5, y0), 23.0, y1-y0, boxstyle="round,pad=0.3",
            facecolor=fc, edgecolor="#333", linewidth=1.5, alpha=0.7, zorder=0))
        ax.text(-10.2, y0+0.35, label, fontsize=12, color=lc,
                fontfamily=FONT, fontweight="bold", va="bottom", zorder=1)

    ax.axhline(1.5, color="#555", linewidth=1.5, linestyle="--", alpha=0.7)
    ax.text(0, 1.65, "— CROSS-LAYER EDGES —", fontsize=11, color="#777",
            ha="center", va="bottom", fontfamily=FONT)

    G = nx.DiGraph()
    ntype = {}
    for n, t in {
        "ChemCorp": "Supplier", "AltChem": "Supplier",
        "PO-4550": "PurchaseOrder", "M-200": "Item",
        "PRD-301": "ProductionOrder", "INV": "Inventory",
        "SO-801": "SalesOrder", "MegaRetail": "Customer",
    }.items(): ntype[n] = t
    for n, t in {
        "EP-001": "Episode", "EP-002": "Episode", "EP-003": "Episode",
        "DEC-001": "MitigationDecision",
        "FACT-001": "Fact", "FACT-002": "Fact",
        "REF-001": "Reflection", "supp_rel": "Concept",
        "REC-001": "Recommendation", "G-SLA": "Goal", "POL": "Policy",
    }.items(): ntype[n] = t
    G.add_nodes_from(ntype.keys())

    l1_edges = [
        ("ChemCorp","PO-4550","supplies"), ("PO-4550","M-200","delivers"),
        ("M-200","PRD-301","consumed_by"), ("PRD-301","INV","produces"),
        ("INV","SO-801","allocated_to"), ("SO-801","MegaRetail","fulfills"),
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
        ("EP-001","ChemCorp","CONCERNS"), ("EP-002","M-200","CONCERNS"),
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

    pos = {
        "ChemCorp": (-5.5,-1.2), "AltChem": (-5.5,-3.0),
        "PO-4550":  (-2.5,-1.2), "M-200":   ( 0.0,-2.0),
        "PRD-301":  ( 2.5,-1.2), "INV":     ( 5.0,-2.0),
        "SO-801":   ( 7.5,-1.2), "MegaRetail":( 9.8,-1.2),
        "EP-001":   (-7.0, 8.5), "EP-002":  (-4.0, 8.5),
        "EP-003":   (-1.0, 8.5), "DEC-001": (-1.0, 6.0),
        "FACT-001": (-4.5, 6.0), "FACT-002":(-1.0, 4.2),
        "REF-001":  (-4.5, 4.2), "supp_rel":( 2.5, 7.2),
        "REC-001":  (-7.5, 4.2), "G-SLA":   ( 7.0, 6.5),
        "POL":      ( 7.0, 5.0),
    }

    # Larger fonts: 13pt labels, 11pt edge labels
    draw_graph(ax, G, pos, ntype, elmap, node_size=2000, font_size=13, edge_font_size=11)

    ax.annotate("Agent reads Layer 2 context\nbefore evaluating mitigations",
                xy=(-1.0, 4.2), xytext=(2.5, 3.0),
                fontsize=11, color="#b87aff", fontfamily=FONT,
                arrowprops=dict(arrowstyle="->", color="#b87aff", lw=1.4),
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#180d2a",
                          edgecolor="#b87aff", alpha=0.9))
    ax.annotate("Agent executes via MCP\non Layer 1 (D365)",
                xy=(-2.5, -1.2), xytext=(0.5, -6.2),
                fontsize=11, color="#5baee0", fontfamily=FONT,
                arrowprops=dict(arrowstyle="->", color="#5baee0", lw=1.4),
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#0a1e30",
                          edgecolor="#5baee0", alpha=0.9))
    ax.annotate("Decision trace written\nback to Layer 2",
                xy=(-1.0, 6.0), xytext=(2.5, 5.0),
                fontsize=11, color="#c8b800", fontfamily=FONT,
                arrowprops=dict(arrowstyle="->", color="#c8b800", lw=1.4),
                bbox=dict(boxstyle="round,pad=0.45", facecolor="#1a1800",
                          edgecolor="#c8b800", alpha=0.9))

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
    ], title="Node Types", loc="lower left", fontsize=12)
    ax.add_artist(leg1)

    make_legend(ax, [
        ("CONCERNS (Episode → L1)",   EDGE_COLORS["CONCERNS"],      "dashed"),
        ("CHARACTERIZES (Fact → L1)", EDGE_COLORS["CHARACTERIZES"], "dashed"),
        ("TARGETS / APPLIES_TO",      EDGE_COLORS["TARGETS"],       "dashed"),
        ("RESOLVED (Decision → PO)",  EDGE_COLORS["RESOLVED"],      "dashed"),
    ], title="Cross-Layer Edges", loc="lower right", fontsize=13)

    return slide_to_b64(fig)


# ── View 5 — Agent Loop (bigger fonts) ───────────────────────────────────────
def render_slide5_large():
    fig, ax = plt.subplots(figsize=(16, 8), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_title("How the Agent Uses the Two-Layer Graph — Query & Execution Flow",
                 color="white", fontsize=17, fontweight="bold", pad=14, fontfamily=FONT)
    ax.set_xlim(-7.5, 11.5)
    ax.set_ylim(-4.0, 4.0)

    BOX_W, BOX_H = 2.6, 2.4
    steps = [
        (-6.5,  0.5, "#0a2a1a", "#27c9a0", "① Disruption\nDetected",
         "PO-MOTR:\nVendor 1003, DC Motor\n14-day delay, 100 units"),
        (-2.8,  0.5, "#0a1e30", "#5baee0", "② Anchor\nTraversal",
         "Start at Vendor 1003 +\nDMA-MTR-DC in Layer 1.\nFollow CHARACTERIZES\nedges into Layer 2"),
        ( 0.9,  0.5, "#1a0d2a", "#b87aff", "③ Concept\nExpansion",
         "Reach Concept nodes:\nsafety_stock_erosion,\nalt_vendor_switch.\nBack-traverse to all\nFacts & Reflections"),
        ( 4.6,  0.5, "#2a1a0a", "#c8b800", "④ Rank &\nInject Context",
         "Weight recent episodes\nhigher. Inject top-k\nFacts + Reflections\ninto agent system prompt"),
        ( 8.3,  0.5, "#0d1422", "#f472b6", "⑤ Evaluate\nMitigations",
         "Score options vs Goals\n& Policies.\nRank 1 → Vendor 1002\n(known good alternate)"),
        (-6.5, -3.0, "#2a0d0d", "#c03d3d", "⑥ Execute\nvia MCP",
         "Issue PO to Vendor 1002.\nUpdate D365.\nWrite Episode + Decision\nback to Layer 2 ♻"),
    ]
    centres = []
    for x, y, fc, ec, title, body in steps:
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), BOX_W, BOX_H, boxstyle="round,pad=0.3",
            facecolor=fc, edgecolor=ec, linewidth=2.0, alpha=0.97, zorder=2))
        ax.text(x + BOX_W/2, y + BOX_H - 0.28, title,
                ha="center", va="top", fontsize=11, fontweight="bold",   # was 9
                color=ec, fontfamily=FONT)
        ax.text(x + BOX_W/2, y + BOX_H/2 - 0.1, body,
                ha="center", va="center", fontsize=9.5, color="white",   # was 7.5
                fontfamily=FONT, multialignment="center")
        centres.append((x + BOX_W/2, y + BOX_H/2))

    for i in range(4):
        ax.annotate("", xy=(centres[i+1][0] - BOX_W/2, centres[i+1][1]),
                    xytext=(centres[i][0] + BOX_W/2, centres[i][1]),
                    arrowprops=dict(arrowstyle="-|>", color="#888",
                                   lw=1.8, mutation_scale=14), zorder=3)

    ax.text(2.0, -3.8,
            "Every execution enriches Layer 2 — the next disruption on Vendor 1003 or DMA-MTR-DC\n"
            "arrives pre-loaded with 6 episodes, 2 facts, 1 reflection, and 2 recommendations.",
            ha="center", va="center", fontsize=11.5, color="#e8e0ff",   # was 9.5
            fontfamily=FONT, multialignment="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1030",
                      edgecolor="#7e3af2", alpha=0.9), zorder=3)

    return slide_to_b64(fig)


# ── Traversal stage re-render with larger fonts (Views 9, 10, 11) ─────────────
def render_stage_large(G, pos, ntype, elmap, s):
    """Re-render a traversal stage with bigger fonts and nodes."""
    h_nodes   = s["hn"]
    h_edges   = s["he"]
    xlim, ylim = s["xlim"], s["ylim"]

    all_nodes    = set(G.nodes())
    all_edges    = set(G.edges())
    bright_nodes = set(h_nodes) if h_nodes else all_nodes
    bright_edges = set(h_edges) if h_edges else all_edges
    dim_nodes    = all_nodes - bright_nodes
    dim_edges    = all_edges - bright_edges

    fig, ax = plt.subplots(figsize=(16, 9), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    for y0, y1, fc, lbl, lc in [
        (-5.0,  1.2, "#0a1e30", "LAYER 1 — Supply Chain Network", "#5baee0"),
        ( 1.8, 10.5, "#180d2a", "LAYER 2 — Intelligence Layer",   "#b87aff"),
    ]:
        ax.add_patch(mpatches.FancyBboxPatch(
            (-13.5, y0), 29.5, y1-y0,
            boxstyle="round,pad=0.3", facecolor=fc,
            edgecolor="#333", linewidth=1.0, alpha=0.5, zorder=0))
        if xlim[0] <= -12.0:
            ax.text(-13.2, y0+0.35, lbl, fontsize=9.5, color=lc,
                    fontfamily=FONT, fontweight="bold", va="bottom",
                    zorder=1, clip_on=True)

    ax.axhline(1.5, color="#444", linewidth=1.2, linestyle="--", alpha=0.6, zorder=1)

    for u, v in dim_edges:
        if u not in pos or v not in pos: continue
        style = "dashed" if G[u][v].get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color="#1c2240",
                                   lw=0.7, linestyle=style,
                                   mutation_scale=7, shrinkA=5, shrinkB=5), zorder=2)

    dim_list = [n for n in dim_nodes if n in pos]
    if dim_list:
        nx.draw_networkx_nodes(G, pos, nodelist=dim_list,
                               node_color="#1a2040", node_size=520, ax=ax,
                               edgecolors="#252a50", linewidths=0.5, alpha=0.45)

    for u, v in bright_edges:
        if u not in pos or v not in pos: continue
        color = gh.EDGE_COLORS.get(elmap.get((u, v), "supplies"), "#aaaaaa")
        style = "dashed" if G[u][v].get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=2.8, linestyle=style,
                                   mutation_scale=18, shrinkA=11, shrinkB=11), zorder=4)

    for n in bright_nodes:
        if n not in pos: continue
        color = gh.NODE_COLORS.get(ntype.get(n, "Item"), "#888")
        sz = 2400 if n == gh.POM else 1900   # bigger than default 1900/1400
        nx.draw_networkx_nodes(G, pos, nodelist=[n],
                               node_color=color, node_size=sz, ax=ax,
                               edgecolors="white", linewidths=1.2)

    if gh.POM in bright_nodes and gh.POM in pos:
        px, py = pos[gh.POM]
        ax.add_patch(mpatches.Circle((px, py), 0.72, color="#f5c518",
                                     fill=False, linewidth=4.0, zorder=8))

    bright_lbls = {n: n for n in bright_nodes if n in pos}
    lbl_objs = nx.draw_networkx_labels(G, pos, labels=bright_lbls,
                                        font_size=12, font_color="white",   # was 9
                                        font_family=FONT, ax=ax)
    for t in lbl_objs.values():
        t.set_clip_on(False)

    bright_el = {(u, v): elmap.get((u, v), "")
                 for u, v in bright_edges if u in pos and v in pos}
    if bright_el:
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=bright_el,
            font_size=10, font_color="white", ax=ax,          # was 7.5
            label_pos=0.5, rotate=False,
            bbox=dict(boxstyle="round,pad=0.2", fc="#1a1a2e", ec="none", alpha=0.9))

    buf = io.BytesIO()
    fig.savefig(buf, dpi=130, bbox_inches="tight", pad_inches=0.15, facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGB").resize(TARGET_SIZE, Image.LANCZOS)
    buf2 = io.BytesIO()
    img.save(buf2, format="PNG", optimize=True)
    return base64.b64encode(buf2.getvalue()).decode()


# ── HTML template (74 % image / 26 % script, 11 px script font) ──────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PO-MOTR Graph Traversal — Two-Layer Supply Chain Intelligence</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg:       #0d1117;
    --surface:  #161b22;
    --border:   #30363d;
    --text:     #e6edf3;
    --muted:    #8b949e;
    --accent:   #7e3af2;
    --accent2:  #5baee0;
    --gold:     #f5c518;
  }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: "Segoe UI", system-ui, sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 18px 14px 32px;
  }

  .header {
    width: 100%;
    max-width: 1500px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  .header-title { font-size: 11px; color: var(--muted); letter-spacing: 0.04em; text-transform: uppercase; }
  .step-counter  { font-size: 11px; color: var(--muted); font-variant-numeric: tabular-nums; }

  .stage-bar {
    width: 100%;
    max-width: 1500px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 7px 14px;
    margin-bottom: 9px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .stage-num   { font-size: 15px; color: var(--accent); min-width: 36px; }
  .stage-title { font-size: 15px; font-weight: 600; color: var(--text); }

  /* ── Main content: 75% image | 25% script ── */
  .main-content {
    width: 100%;
    max-width: 1500px;
    display: flex;
    gap: 12px;
    align-items: stretch;
    margin-bottom: 12px;
  }

  .img-wrap {
    flex: 0 0 75%;
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    align-items: center;
  }
  .img-wrap img { width: 100%; display: block; }

  .script-panel {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 11px;
    line-height: 1.75;
    color: #c9d1d9;
    overflow-y: auto;
    max-height: 600px;
  }
  .script-panel b  { color: var(--text); }
  .script-panel em { color: var(--gold); font-style: normal; }
  .script-panel code {
    background: #1c2333;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: 10px;
    color: #79c0ff;
    font-family: "Cascadia Code", "Consolas", monospace;
  }

  .nav {
    width: 100%;
    max-width: 1500px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
  }
  .btn {
    padding: 7px 22px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
    user-select: none;
  }
  .btn:hover    { background: #21262d; border-color: #8b949e; }
  .btn:disabled { opacity: 0.3; cursor: default; }
  .btn.primary  { background: var(--accent); border-color: var(--accent); color: #fff; }
  .btn.primary:hover { background: #6d28d9; border-color: #6d28d9; }

  .dots { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; justify-content: center; max-width: 700px; }
  .dot  { width: 8px; height: 8px; border-radius: 50%; background: var(--border); cursor: pointer; transition: background 0.15s, transform 0.15s; }
  .dot.active { background: var(--accent); transform: scale(1.35); }
  .dot:hover  { background: var(--muted); }

  .kbd-hint { font-size: 11px; color: var(--muted); margin-top: 9px; }
  kbd { display: inline-block; padding: 1px 5px; font-size: 10px; border: 1px solid var(--border); border-radius: 3px; background: var(--surface); font-family: monospace; }
</style>
</head>
<body>

<div class="header">
  <span class="header-title">Two-Layer Supply Chain Context Graph — PO-MOTR Traversal</span>
  <span class="step-counter" id="counter">1 / {n}</span>
</div>

<div class="stage-bar">
  <span class="stage-num"   id="step-num"></span>
  <span class="stage-title" id="stage-title"></span>
</div>

<div class="main-content">
  <div class="img-wrap">
    <img id="frame-img" src="" alt="Graph traversal frame">
  </div>
  <div class="script-panel" id="script-text"></div>
</div>

<div class="nav">
  <button class="btn"         id="btn-prev" onclick="go(-1)">&#8592; Prev</button>
  <div class="dots"           id="dots"></div>
  <button class="btn primary" id="btn-next" onclick="go(1)">Next &#8594;</button>
</div>
<div class="kbd-hint">
  Navigate: <kbd>&#8592;</kbd> <kbd>&#8594;</kbd> arrow keys &nbsp;|&nbsp; <kbd>Space</kbd> advance
</div>

<script>
const STAGES = {stages_json};
let cur = 0;

function render(idx) {
  cur = idx;
  const s = STAGES[idx];
  document.getElementById("counter").textContent     = (idx+1) + " / " + STAGES.length;
  document.getElementById("step-num").textContent    = s.step_num;
  document.getElementById("stage-title").textContent = s.title;
  document.getElementById("frame-img").src           = "data:image/png;base64," + s.img;
  document.getElementById("script-text").innerHTML   = s.script;
  document.getElementById("btn-prev").disabled = (idx === 0);
  document.getElementById("btn-next").disabled = (idx === STAGES.length - 1);
  document.querySelectorAll(".dot").forEach((d,i) => d.classList.toggle("active", i===idx));
}

function go(delta) {
  const next = cur + delta;
  if (next >= 0 && next < STAGES.length) render(next);
}

const dotsEl = document.getElementById("dots");
STAGES.forEach((_,i) => {
  const d = document.createElement("div");
  d.className = "dot";
  d.onclick   = () => render(i);
  dotsEl.appendChild(d);
});

document.addEventListener("keydown", e => {
  if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); go(1); }
  if (e.key === "ArrowLeft")                    { e.preventDefault(); go(-1); }
});

render(0);
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("Loading stages from v2 HTML...")
    stages = load_stages()
    print(f"  {len(stages)} stages loaded")

    G, pos, ntype, elmap = gh.build_graph()

    # ── Re-render Views 3, 4, 5 (indices 2, 3, 4) ────────────────────────────
    print("Re-rendering View 3 (Layer 2, bigger fonts)...")
    stages[2]["img"] = render_slide2_large()

    print("Re-rendering View 4 (Architecture, bigger fonts)...")
    stages[3]["img"] = render_slide3_large()

    print("Re-rendering View 5 (Agent Loop, bigger fonts)...")
    stages[4]["img"] = render_slide5_large()

    # ── Re-render Views 9, 10, 11 (gh.STAGES indices 3, 4, 5 → global 8, 9, 10) ──
    for view_num, gh_idx, global_idx in [(9, 3, 8), (10, 4, 9), (11, 5, 10)]:
        s = gh.STAGES[gh_idx]
        print(f"Re-rendering View {view_num} ({s['title']}, bigger fonts)...")
        stages[global_idx]["img"] = render_stage_large(G, pos, ntype, elmap, s)

    # ── Assemble HTML ─────────────────────────────────────────────────────────
    total       = len(stages)
    stages_json = json.dumps(stages, ensure_ascii=False)
    html = (HTML_TEMPLATE
            .replace("{n}", str(total))
            .replace("{stages_json}", stages_json))

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUT_HTML) // 1024
    print(f"\nSaved → {OUT_HTML}  ({size_kb} KB, {total} stages)")


if __name__ == "__main__":
    main()
