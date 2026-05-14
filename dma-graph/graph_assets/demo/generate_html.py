"""
Generate click-through HTML presentation: PO-MOTR graph traversal.
Output: slide4_clickthrough.html  (fully self-contained, no server needed)

Renders 9 high-quality PNG frames (base64-embedded) with per-stage
narration scripts and keyboard / button navigation.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from PIL import Image
import base64, io, os

OUT  = os.path.dirname(os.path.abspath(__file__))
BG   = "#0d1117"
FONT = "DejaVu Sans"

NODE_COLORS = {
    "Supplier": "#1e6eb5", "Item": "#29a6d4", "PurchaseOrder": "#d4a017",
    "ProductionOrder": "#e87c25", "Inventory": "#2ea84f",
    "DistributionCenter": "#27c9a0", "SalesOrder": "#5ab552", "Customer": "#f0a500",
    "Episode": "#e07b39", "MitigationDecision": "#c03d3d", "Fact": "#c8b800",
    "Reflection": "#a855f7", "Concept": "#7e3af2", "Policy": "#6b7fa3",
    "Goal": "#34c9eb", "Recommendation": "#f472b6",
}
EDGE_COLORS = {
    "supplies": "#4a90d9", "delivers": "#4a90d9",
    "consumed_by": "#29a6d4", "produces": "#e87c25",
    "stocked_at": "#2ea84f", "allocated_to": "#5ab552",
    "transfers_to": "#27c9a0", "ships_to": "#f0a500", "fulfills": "#f0a500",
    "alternate_for": "#8ecef5", "substitutes_for": "#8ecef5",
    "pegged_to": "#d4a017",
    "NEXT": "#e07b39", "DERIVED_FROM": "#c8b800", "DERIVED_FROM_FACT": "#a855f7",
    "HAS_CONCEPT": "#7e3af2", "ABOUT_CONCEPT": "#7e3af2",
    "GOVERNED_BY": "#6b7fa3", "SCORED_AGAINST": "#34c9eb", "SUPPORTED_BY": "#f472b6",
    "CONCERNS": "#ff8c42", "CHARACTERIZES": "#ff5c5c",
    "TARGETS": "#cc2222", "APPLIES_TO": "#cc2222", "RESOLVED": "#00c9b1",
}

# ── Node shorthand labels ─────────────────────────────────────────────────────
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
EP6 = "EP-006\n(PO-MOTR)"
DA  = "DEC-006A\nVend1002 rank1"
DB  = "DEC-006B\nVend1001 rank2"
DC_ = "DEC-006C\nUseOnHand"
DD  = "DEC-006D\nAltItem"
F6  = "FACT-006\n30u on-hand\nvs 20u floor"
F7  = "FACT-007\nVend1003 sourced\nall 6 episodes"
R3  = "REF-003\non-hand/floor\n< 2× → risk"
RC1 = "REC-001\nQualify 1001/1002\nas alternates"
RC2 = "REC-002\nIncrease on-hand\ntarget ≥ 40 units"
SS  = "ss_erosion"
AV  = "alt_vendor"
G_SLA = "G-SLA\n25%";  G_CST = "G-Cost\n25%"
G_QTY = "G-Qty\n25%";  G_INV = "G-Inv\n25%"


def build_graph():
    ntype = {
        V3: "Supplier", V1: "Supplier", V2: "Supplier",
        POM: "PurchaseOrder", MTD: "Item", MTA: "Item",
        IVD: "Inventory", IVA: "Inventory",
        SOM: "SalesOrder", CUS: "Customer",
        "EP-001": "Episode", "EP-002": "Episode", "EP-003": "Episode",
        "EP-004": "Episode", "EP-005": "Episode", EP6: "Episode",
        DA: "MitigationDecision", DB: "MitigationDecision",
        DC_: "MitigationDecision", DD: "MitigationDecision",
        F6: "Fact", F7: "Fact",
        R3: "Reflection",
        SS: "Concept", AV: "Concept",
        G_SLA: "Goal", G_CST: "Goal", G_QTY: "Goal", G_INV: "Goal",
        "POL-ONHOLD": "Policy",
        RC1: "Recommendation", RC2: "Recommendation",
    }
    G = nx.DiGraph()
    G.add_nodes_from(ntype.keys())

    l1_raw = [
        (V3, POM, "supplies"), (POM, MTD, "delivers"),
        (MTD, IVD, "stocked_at"), (MTA, IVA, "stocked_at"),
        (MTD, MTA, "substitutes_for"),
        (POM, SOM, "pegged_to"), (SOM, CUS, "fulfills"),
    ]
    l2_raw = [
        ("EP-001","EP-002","NEXT"), ("EP-002","EP-003","NEXT"),
        ("EP-003","EP-004","NEXT"), ("EP-004","EP-005","NEXT"),
        ("EP-005", EP6, "NEXT"),
        (DA, EP6, "DERIVED_FROM"), (DB, EP6, "DERIVED_FROM"),
        (DC_, EP6, "DERIVED_FROM"), (DD, EP6, "DERIVED_FROM"),
        (F6, EP6, "DERIVED_FROM"),
        (F7, "EP-001", "DERIVED_FROM"),
        (R3, F6, "DERIVED_FROM_FACT"),
        (EP6, SS, "HAS_CONCEPT"), (EP6, AV, "HAS_CONCEPT"),
        (F6, SS, "ABOUT_CONCEPT"),
        (DA, G_SLA, "SCORED_AGAINST"), (DA, G_CST, "SCORED_AGAINST"),
        (DA, G_QTY, "SCORED_AGAINST"), (DA, G_INV, "SCORED_AGAINST"),
        (DA, "POL-ONHOLD", "GOVERNED_BY"),
        (RC1, R3, "SUPPORTED_BY"), (RC2, R3, "SUPPORTED_BY"),
    ]
    cross_raw = [
        ("EP-001", V3, "CONCERNS"), ("EP-002", V3, "CONCERNS"),
        ("EP-003", V3, "CONCERNS"),
        (EP6, POM, "CONCERNS"), (EP6, MTD, "CONCERNS"),
        (F7, V3, "CHARACTERIZES"), (F6, MTD, "CHARACTERIZES"),
        (R3, MTD, "TARGETS"), (RC2, MTD, "APPLIES_TO"),
        (DA, POM, "RESOLVED"),
    ]

    elmap = {}
    for u, v, e in l1_raw + l2_raw:
        G.add_edge(u, v, etype=e, cross=False); elmap[(u, v)] = e
    for u, v, e in cross_raw:
        G.add_edge(u, v, etype=e, cross=True);  elmap[(u, v)] = e

    pos = {
        V3: (-9.0,-1.0), V1: (-9.0,-4.0), V2: (-6.5,-4.0),
        POM: (-5.0,-1.0), MTD: (-1.8,-1.3), MTA: (-1.8,-3.8),
        IVD: (1.8,-1.3), IVA: (1.8,-3.8),
        SOM: (5.0,-1.0), CUS: (8.5,-1.0),
        "EP-001": (-10.5,9.5), "EP-002": (-7.0,9.5),
        "EP-003": (-3.5,9.5), "EP-004": (0.0,9.5),
        "EP-005": (3.5,9.5), EP6: (7.0,9.5),
        DA: (2.5,7.2), DB: (5.5,7.2), DC_: (8.5,7.2), DD: (11.5,7.2),
        F6: (-3.5,7.0), F7: (-8.0,7.0),
        R3: (-5.8,4.8),
        SS: (0.0,4.8), AV: (3.0,4.8),
        G_SLA: (10.5,5.8), G_CST: (12.5,5.8),
        G_QTY: (14.5,5.8), G_INV: (16.0,5.8),
        "POL-ONHOLD": (13.5,7.2),
        RC1: (-12.0,4.8), RC2: (-12.0,3.0),
    }
    return G, pos, ntype, elmap


def render_stage(G, pos, ntype, elmap,
                 h_nodes, h_edges,
                 step_label, title,
                 xlim, ylim,
                 figsize=(16, 9), dpi=130):
    """Render one stage frame. Returns PIL Image (RGB)."""
    all_nodes = set(G.nodes())
    all_edges = set(G.edges())

    if h_nodes is None:
        bright_nodes = all_nodes
        bright_edges = all_edges
    else:
        bright_nodes = set(h_nodes)
        bright_edges = set(h_edges) if h_edges else set()

    dim_nodes = all_nodes - bright_nodes
    dim_edges  = all_edges  - bright_edges

    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Layer bands
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

    # Dim edges
    for u, v in dim_edges:
        if u not in pos or v not in pos:
            continue
        style = "dashed" if G[u][v].get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color="#1c2240",
                                   lw=0.7, linestyle=style,
                                   mutation_scale=7, shrinkA=5, shrinkB=5),
                    zorder=2)

    # Dim nodes
    dim_list = [n for n in dim_nodes if n in pos]
    if dim_list:
        nx.draw_networkx_nodes(G, pos, nodelist=dim_list,
                               node_color="#1a2040", node_size=420, ax=ax,
                               edgecolors="#252a50", linewidths=0.5, alpha=0.45)

    # Bright edges
    for u, v in bright_edges:
        if u not in pos or v not in pos:
            continue
        etype = elmap.get((u, v), "supplies")
        color = EDGE_COLORS.get(etype, "#aaaaaa")
        style = "dashed" if G[u][v].get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=2.5, linestyle=style,
                                   mutation_scale=16, shrinkA=9, shrinkB=9),
                    zorder=4)

    # Bright nodes
    for n in bright_nodes:
        if n not in pos:
            continue
        color = NODE_COLORS.get(ntype.get(n, "Item"), "#888")
        sz = 1900 if n == POM else 1400
        nx.draw_networkx_nodes(G, pos, nodelist=[n],
                               node_color=color, node_size=sz, ax=ax,
                               edgecolors="white", linewidths=1.2)

    # Yellow ring on POM
    if POM in bright_nodes and POM in pos:
        px, py = pos[POM]
        ax.add_patch(mpatches.Circle((px, py), 0.72, color="#f5c518",
                                     fill=False, linewidth=4.0, zorder=8))

    # Node labels (bright only)
    bright_lbls = {n: n for n in bright_nodes if n in pos}
    lbl_objs = nx.draw_networkx_labels(G, pos, labels=bright_lbls,
                                        font_size=9, font_color="white",
                                        font_family=FONT, ax=ax)
    for t in lbl_objs.values():
        t.set_clip_on(False)

    # Edge labels (bright only)
    bright_el = {(u, v): elmap.get((u, v), "")
                 for u, v in bright_edges if u in pos and v in pos}
    if bright_el:
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=bright_el,
            font_size=7.5, font_color="white", ax=ax,
            label_pos=0.5, rotate=False,
            bbox=dict(boxstyle="round,pad=0.2", fc="#1a1a2e", ec="none", alpha=0.9),
        )

    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, bbox_inches="tight", pad_inches=0.15, facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


TARGET_SIZE = (1760, 990)   # 16:9, consistent across all stages

def img_to_b64(img):
    # Letterbox to consistent 16:9 if aspect ratio differs
    img = img.resize(TARGET_SIZE, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


# ─────────────────────────────────────────────────────────────────────────────
STAGES = [
    dict(
        step="① / 9", title="Disruption Detected",
        hn=None, he=None,
        xlim=(-14.0, 16.5), ylim=(-9.0, 11.5),
        script="""\
<b>PO-MOTR has just been flagged.</b> Vendor 1003 — Ade Supply — is reporting a
14-day delay on 100 DC Motors at $50/unit.

Every node visible here belongs to one of two layers separated by the dashed line.
<b>Below</b>: Layer 1, the live operational supply chain — suppliers, purchase orders,
items, inventory, sales orders, customers.
<b>Above</b>: Layer 2, the accumulated intelligence layer — episodes, facts, reflections,
and decisions written by every prior Disruption Mitigation Agent execution.

The agent's job: use both layers to arrive at the right mitigation decision.
""",
    ),
    dict(
        step="② / 9", title="Layer 1 — Trace the Pegging Chain",
        hn={V3, POM, MTD, SOM, CUS},
        he={(V3, POM), (POM, MTD), (POM, SOM), (SOM, CUS)},
        xlim=(-11.5, 10.5), ylim=(-7.0, 1.5),
        script="""\
The agent's first move is to traverse <b>Layer 1 — the live supply chain</b>.

Following the pegging chain from PO-MOTR exposes the full blast radius:
the DC Motor is delivered by PO-MOTR, and that PO is pegged to
Sales Order SO-MOTR, which belongs to <b>MegaRetail — a Tier 1 customer</b>
with a hard SLA commitment.

This multi-hop traversal — from a delayed purchase order all the way to an at-risk
customer — happens as a <b>single graph query in milliseconds</b>. In a relational
ERP model this would require sequential form navigation and joins across multiple tables.
""",
    ),
    dict(
        step="③ / 9", title="Anchor Traversal — CONCERNS Edges Into Layer 2",
        hn={V3, POM, MTD, "EP-001","EP-002","EP-003", EP6},
        he={("EP-001",V3),("EP-002",V3),("EP-003",V3),(EP6,POM),(EP6,MTD)},
        xlim=(-14.0, 16.5), ylim=(-7.0, 11.5),
        script="""\
With the blast radius mapped, the agent crosses into <b>Layer 2</b> via
<b>CONCERNS edges</b> — the dashed orange lines that span both layers.

These edges were written by past DMA executions and anchor memory nodes
to the specific operational entities they concern. Starting from
<b>Vendor 1003</b> and <b>DMA-MTR-DC</b> in Layer 1, the agent follows
CONCERNS edges upward into the intelligence layer.

<b>Six prior episodes surface immediately.</b> All six involve Vendor 1003.
The agent is not starting cold.
""",
    ),
    dict(
        step="④ / 9", title="6 Prior Episodes — All Involving Vendor 1003",
        hn={"EP-001","EP-002","EP-003","EP-004","EP-005", EP6},
        he={("EP-001","EP-002"),("EP-002","EP-003"),("EP-003","EP-004"),
            ("EP-004","EP-005"),("EP-005", EP6)},
        xlim=(-13.5, 10.0), ylim=(6.5, 12.0),
        script="""\
The six episodes form a <b>temporal chain</b> connected by NEXT edges.

EP-001 through EP-005 are disruptions the agent has already handled and
recorded memory for. EP-006 is the <b>current disruption</b> — it was
written to Layer 2 at the start of this execution, before the agent
evaluated a single mitigation option.

This is the first compounding effect: <b>the agent doesn't just react to
today's disruption — it inherits the full recorded history</b> of every
prior disruption involving this vendor. Six data points instead of zero.
""",
    ),
    dict(
        step="⑤ / 9", title="FACT-007 Surfaces — Vendor 1003 Pattern Identified",
        hn={F7, "EP-001", V3},
        he={(F7,"EP-001"), (F7, V3)},
        xlim=(-13.5, 3.5), ylim=(-4.0, 11.5),
        script="""\
<b>FACT-007</b> is the key insight distilled from the episode history:
<em>"Vendor 1003 is the disruption source across all 6 recorded episodes."</em>

This fact was produced by an <b>LLM Extract job</b> that read the episode
chain and extracted the pattern — it was not hardcoded by any rule engine.
The DERIVED_FROM edge traces it back to EP-001.

The <b>CHARACTERIZES</b> edge (dashed red) anchors FACT-007 to the
Vendor 1003 node in Layer 1. Any future DMA query on this vendor surfaces
this fact automatically — no re-derivation required.
""",
    ),
    dict(
        step="⑥ / 9", title="Safety Stock Risk — FACT-006 + REF-003",
        hn={F6, R3, MTD, SS, EP6},
        he={(F6, EP6),(R3, F6),(F6, MTD),(F6, SS)},
        xlim=(-10.5, 5.5), ylim=(-4.0, 12.0),
        script="""\
<b>FACT-006</b> flags a second risk: 30 units on-hand against a
20-unit safety stock floor. Drawing all 30 units to cover the DC Motor
shortfall would breach the floor — leaving zero buffer.

<b>REF-003</b> generalizes this to a structural pattern via
DERIVED_FROM_FACT: <em>"Items where on-hand inventory is less than
twice the safety floor are inherently fragile."</em>
This Reflection was synthesized by an LLM across multiple fact clusters.

The <b>CHARACTERIZES</b> edge anchors FACT-006 to DMA-MTR-DC (the DC Motor)
in Layer 1. The <b>ss_erosion</b> Concept node enables cross-disruption
retrieval — any future disruption tagged with this concept will find
FACT-006 and REF-003 in its context window.
""",
    ),
    dict(
        step="⑦ / 9", title="Evaluate 4 Mitigation Options Against Goals",
        hn={DA, DB, DC_, DD, G_SLA, G_CST, G_QTY, G_INV, "POL-ONHOLD", EP6},
        he={(DA,EP6),(DB,EP6),(DC_,EP6),(DD,EP6),
            (DA,G_SLA),(DA,G_CST),(DA,G_QTY),(DA,G_INV),(DA,"POL-ONHOLD")},
        xlim=(-2.0, 17.5), ylim=(4.0, 12.0),
        script="""\
Context loaded, the agent evaluates <b>four mitigation options</b>:

• <b>DEC-006A</b> — Switch to Vendor 1002 (Lande), $52/unit, 8-day lead. Full coverage.
• <b>DEC-006B</b> — Switch to Vendor 1001 (Acme), $55/unit, 5-day lead. Full coverage.
• <b>DEC-006C</b> — Draw from on-hand inventory (30 units). Breaches safety floor.
• <b>DEC-006D</b> — Substitute AC Motor (alternate item). Also a floor breach.

Each decision is <b>scored against four Goals</b> — SLA protection (25%),
cost minimisation (25%), quantity coverage (25%), inventory health (25%) —
and validated against <b>POL-ONHOLD</b>, the business policy governing
purchase order changes. The scoring is transparent: the graph records exactly
which goal drove which ranking.
""",
    ),
    dict(
        step="⑧ / 9", title="Rank-1 Selected — Vendor 1002, $52/unit, 8-day Lead",
        hn={DA, G_SLA, G_CST, G_QTY, G_INV, "POL-ONHOLD"},
        he={(DA,G_SLA),(DA,G_CST),(DA,G_QTY),(DA,G_INV),(DA,"POL-ONHOLD")},
        xlim=(0.5, 16.5), ylim=(4.5, 12.0),
        script="""\
<b>DEC-006A wins.</b> Switch to Vendor 1002 — Lande — at $52/unit,
8-day lead time.

The ranking was not arbitrary. <b>FACT-007's six-episode failure record</b>
on Vendor 1003 made the alternate vendor switch the only viable full-coverage
option. DEC-006C and DEC-006D are partial mitigations that both breach the
safety floor — FACT-006 and REF-003 penalised them heavily in the Goal scoring.

This is the second compounding effect: <b>the agent did not reason from
scratch</b>. The conclusion — "switch to a known alternate" — was implicit
in the Layer 2 context before the evaluation even started.
DEC-006B through DEC-006D are dimmed; they were considered and rejected.
""",
    ),
    dict(
        step="⑨ / 9", title="RESOLVED — Decision Anchored · Loop Complete",
        hn={DA, POM, V3, MTD, SOM, CUS, EP6, F7},
        he={(DA, POM),(EP6,POM),(EP6,MTD),(F7,V3)},
        xlim=(-14.0, 16.5), ylim=(-9.0, 11.5),
        script="""\
The decision is recorded. A <b>RESOLVED edge</b> (teal dashed) is written
from DEC-006A back to PO-MOTR in Layer 1 — the specific purchase order
that triggered this run. The loop is closed.

<b>CONCERNS edges</b> from EP-006 anchor the new episode to Vendor 1003
and DMA-MTR-DC. <b>CHARACTERIZES</b> from FACT-007 stays live in Layer 1.

The next disruption involving Vendor 1003 or DC Motors will arrive
pre-loaded with:
• <b>6 episodes</b> in the temporal chain
• <b>2 facts</b> (unreliable vendor, safety floor risk)
• <b>1 reflection</b> (on-hand/floor structural fragility)
• <b>2 recommendations</b> (qualify alternates, increase on-hand target)

<em>None of this had to be re-derived. The graph doesn't forget.
Every execution makes it smarter.</em>
""",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
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
    padding: 24px 16px 40px;
    gap: 0;
  }

  /* ── Header ── */
  .header {
    width: 100%;
    max-width: 1200px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .header-title {
    font-size: 13px;
    color: var(--muted);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .step-counter {
    font-size: 13px;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }

  /* ── Stage title bar ── */
  .stage-bar {
    width: 100%;
    max-width: 1200px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 18px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .stage-num {
    font-size: 18px;
    color: var(--accent);
    min-width: 36px;
  }
  .stage-title {
    font-size: 17px;
    font-weight: 600;
    color: var(--text);
  }

  /* ── Image ── */
  .img-wrap {
    width: 100%;
    max-width: 1200px;
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 14px;
  }
  .img-wrap img {
    width: 100%;
    display: block;
  }

  /* ── Script panel ── */
  .script-panel {
    width: 100%;
    max-width: 1200px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 14px;
    line-height: 1.75;
    color: #c9d1d9;
    margin-bottom: 18px;
    white-space: pre-line;
  }
  .script-panel b { color: var(--text); }
  .script-panel em { color: var(--gold); font-style: normal; }

  /* ── Navigation ── */
  .nav {
    width: 100%;
    max-width: 1200px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
  .btn {
    padding: 9px 28px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s, color 0.15s;
    user-select: none;
  }
  .btn:hover { background: #21262d; border-color: #8b949e; }
  .btn:disabled { opacity: 0.3; cursor: default; }
  .btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
  .btn.primary:hover { background: #6d28d9; border-color: #6d28d9; }

  /* ── Progress dots ── */
  .dots {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--border);
    cursor: pointer;
    transition: background 0.15s, transform 0.15s;
  }
  .dot.active { background: var(--accent); transform: scale(1.3); }
  .dot:hover { background: var(--muted); }

  /* ── Keyboard hint ── */
  .kbd-hint {
    font-size: 12px;
    color: var(--muted);
    margin-top: 12px;
  }
  kbd {
    display: inline-block;
    padding: 1px 6px;
    font-size: 11px;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--surface);
    font-family: monospace;
  }
</style>
</head>
<body>

<div class="header">
  <span class="header-title">Two-Layer Supply Chain Context Graph — PO-MOTR Traversal</span>
  <span class="step-counter" id="counter">1 / {n}</span>
</div>

<div class="stage-bar">
  <span class="stage-num" id="step-num"></span>
  <span class="stage-title" id="stage-title"></span>
</div>

<div class="img-wrap">
  <img id="frame-img" src="" alt="Graph traversal frame">
</div>

<div class="script-panel" id="script-text"></div>

<div class="nav">
  <button class="btn" id="btn-prev" onclick="go(-1)">← Prev</button>
  <div class="dots" id="dots"></div>
  <button class="btn primary" id="btn-next" onclick="go(1)">Next →</button>
</div>
<div class="kbd-hint">
  Navigate: <kbd>←</kbd> <kbd>→</kbd> arrow keys &nbsp;|&nbsp; <kbd>Space</kbd> advance
</div>

<script>
const STAGES = {stages_json};
let cur = 0;

function render(idx) {
  cur = idx;
  const s = STAGES[idx];
  document.getElementById("counter").textContent = (idx+1) + " / " + STAGES.length;
  document.getElementById("step-num").textContent = s.step_num;
  document.getElementById("stage-title").textContent = s.title;
  document.getElementById("frame-img").src = "data:image/png;base64," + s.img;
  document.getElementById("script-text").innerHTML = s.script;
  document.getElementById("btn-prev").disabled = (idx === 0);
  document.getElementById("btn-next").disabled = (idx === STAGES.length - 1);
  document.querySelectorAll(".dot").forEach((d,i) => d.classList.toggle("active", i===idx));
}

function go(delta) {
  const next = cur + delta;
  if (next >= 0 && next < STAGES.length) render(next);
}

// Build dots
const dotsEl = document.getElementById("dots");
STAGES.forEach((_,i) => {
  const d = document.createElement("div");
  d.className = "dot";
  d.onclick = () => render(i);
  dotsEl.appendChild(d);
});

// Keyboard
document.addEventListener("keydown", e => {
  if (e.key === "ArrowRight" || e.key === " ") { e.preventDefault(); go(1); }
  if (e.key === "ArrowLeft")                   { e.preventDefault(); go(-1); }
});

render(0);
</script>
</body>
</html>
"""


def main():
    G, pos, ntype, elmap = build_graph()

    print("Rendering stage frames...")
    stage_data = []
    for i, s in enumerate(STAGES):
        print(f"  Stage {i+1}/{len(STAGES)}: {s['title']}")
        img = render_stage(
            G, pos, ntype, elmap,
            s["hn"], s["he"],
            s["step"], s["title"],
            s["xlim"], s["ylim"],
        )
        b64 = img_to_b64(img)
        step_num = s["step"].split("/")[0].strip()
        stage_data.append({
            "step_num": step_num,
            "title": s["title"],
            "img": b64,
            "script": s["script"].strip(),
        })

    import json
    stages_json = json.dumps(stage_data, ensure_ascii=False)

    # Use replace() rather than .format() — stages_json contains { } characters
    # that would trip up Python's str.format() template engine.
    html = (HTML_TEMPLATE
            .replace("{n}", str(len(STAGES)))
            .replace("{stages_json}", stages_json))

    out_path = os.path.join(OUT, "slide4_clickthrough.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) // 1024
    print(f"Saved → {out_path}  ({size_kb} KB, {len(STAGES)} stages)")


if __name__ == "__main__":
    main()
