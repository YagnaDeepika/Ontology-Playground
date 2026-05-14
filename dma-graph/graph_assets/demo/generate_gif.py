"""
Generate animated GIF: PO-MOTR graph traversal across two layers.
Output: slide4_traversal.gif

9 stages, each ~2 s, with 5-frame zoom transitions between them.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from PIL import Image
import io, os
import numpy as np

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

# ── Shorthand node labels (same as slide 4) ──────────────────────────────────
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
G_SLA  = "G-SLA\n25%"
G_CST  = "G-Cost\n25%"
G_QTY  = "G-Qty\n25%"
G_INV  = "G-Inv\n25%"


def build_graph():
    ntype = {
        V3: "Supplier", V1: "Supplier", V2: "Supplier",
        POM: "PurchaseOrder", MTD: "Item", MTA: "Item",
        IVD: "Inventory", IVA: "Inventory",
        SOM: "SalesOrder", CUS: "Customer",
        "EP-001": "Episode", "EP-002": "Episode", "EP-003": "Episode",
        "EP-004": "Episode", "EP-005": "Episode", EP6:   "Episode",
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
        (V3,  POM, "supplies"),   (POM, MTD, "delivers"),
        (MTD, IVD, "stocked_at"), (MTA, IVA, "stocked_at"),
        (MTD, MTA, "substitutes_for"),
        (POM, SOM, "pegged_to"),  (SOM, CUS, "fulfills"),
    ]
    l2_raw = [
        ("EP-001","EP-002","NEXT"), ("EP-002","EP-003","NEXT"),
        ("EP-003","EP-004","NEXT"), ("EP-004","EP-005","NEXT"),
        ("EP-005", EP6, "NEXT"),
        (DA, EP6, "DERIVED_FROM"), (DB, EP6, "DERIVED_FROM"),
        (DC_, EP6, "DERIVED_FROM"), (DD, EP6, "DERIVED_FROM"),
        (F6,  EP6,        "DERIVED_FROM"),
        (F7, "EP-001",    "DERIVED_FROM"),
        (R3, F6,          "DERIVED_FROM_FACT"),
        (EP6, SS, "HAS_CONCEPT"), (EP6, AV, "HAS_CONCEPT"),
        (F6,  SS, "ABOUT_CONCEPT"),
        (DA, G_SLA, "SCORED_AGAINST"), (DA, G_CST, "SCORED_AGAINST"),
        (DA, G_QTY, "SCORED_AGAINST"), (DA, G_INV, "SCORED_AGAINST"),
        (DA, "POL-ONHOLD", "GOVERNED_BY"),
        (RC1, R3, "SUPPORTED_BY"), (RC2, R3, "SUPPORTED_BY"),
    ]
    cross_raw = [
        ("EP-001", V3, "CONCERNS"), ("EP-002", V3, "CONCERNS"),
        ("EP-003", V3, "CONCERNS"),
        (EP6, POM, "CONCERNS"),  (EP6, MTD, "CONCERNS"),
        (F7, V3,   "CHARACTERIZES"), (F6, MTD,  "CHARACTERIZES"),
        (R3, MTD,  "TARGETS"),   (RC2, MTD, "APPLIES_TO"),
        (DA, POM,  "RESOLVED"),
    ]

    elmap = {}
    for u, v, e in l1_raw + l2_raw:
        G.add_edge(u, v, etype=e, cross=False)
        elmap[(u, v)] = e
    for u, v, e in cross_raw:
        G.add_edge(u, v, etype=e, cross=True)
        elmap[(u, v)] = e

    pos = {
        # Layer 1
        V3:  (-9.0, -1.0), V1: (-9.0, -4.0), V2: (-6.5, -4.0),
        POM: (-5.0, -1.0), MTD: (-1.8, -1.3), MTA: (-1.8, -3.8),
        IVD: ( 1.8, -1.3), IVA: ( 1.8, -3.8),
        SOM: ( 5.0, -1.0), CUS: ( 8.5, -1.0),
        # Layer 2 — episode row
        "EP-001": (-10.5, 9.5), "EP-002": (-7.0, 9.5),
        "EP-003": ( -3.5, 9.5), "EP-004": ( 0.0, 9.5),
        "EP-005": (  3.5, 9.5), EP6:      ( 7.0, 9.5),
        # Decisions
        DA: (2.5, 7.2), DB: (5.5, 7.2), DC_: (8.5, 7.2), DD: (11.5, 7.2),
        # Facts / Reflection
        F6: (-3.5, 7.0), F7: (-8.0, 7.0),
        R3: (-5.8, 4.8),
        # Concepts
        SS: (0.0, 4.8), AV: (3.0, 4.8),
        # Goals / Policy
        G_SLA: (10.5, 5.8), G_CST: (12.5, 5.8),
        G_QTY: (14.5, 5.8), G_INV: (16.0, 5.8),
        "POL-ONHOLD": (13.5, 7.2),
        # Recommendations
        RC1: (-12.0, 4.8), RC2: (-12.0, 3.0),
    }
    return G, pos, ntype, elmap


# ─────────────────────────────────────────────────────────────────────────────
def render_frame(G, pos, ntype, elmap,
                 h_nodes, h_edges,
                 step_label, title, desc,
                 xlim, ylim,
                 figsize=(15, 9), dpi=85):
    """Render one animation frame, return PIL Image (RGB)."""
    all_nodes = set(G.nodes())
    all_edges = set(G.edges())

    if h_nodes is None:          # all bright
        bright_nodes = all_nodes
        bright_edges = all_edges
    else:
        bright_nodes = set(h_nodes)
        bright_edges = set(h_edges) if h_edges else set()

    dim_nodes = all_nodes - bright_nodes
    dim_edges  = all_edges - bright_edges

    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # ── Layer bands ──────────────────────────────────────────────────────────
    for y0, y1, fc, lbl, lc in [
        (-5.0, 1.2,  "#0a1e30", "LAYER 1 — Supply Chain Network", "#5baee0"),
        ( 1.8, 10.5, "#180d2a", "LAYER 2 — Intelligence Layer",   "#b87aff"),
    ]:
        ax.add_patch(mpatches.FancyBboxPatch(
            (-13.5, y0), 29.5, y1-y0,
            boxstyle="round,pad=0.3", facecolor=fc,
            edgecolor="#333", linewidth=1.0, alpha=0.5, zorder=0))
        if xlim[0] <= -12.0:
            ax.text(-13.2, y0 + 0.35, lbl, fontsize=9, color=lc,
                    fontfamily=FONT, fontweight="bold", va="bottom",
                    zorder=1, clip_on=True)

    ax.axhline(1.5, color="#444", linewidth=1.2, linestyle="--", alpha=0.6, zorder=1)

    # ── Dim edges ────────────────────────────────────────────────────────────
    for u, v in dim_edges:
        if u not in pos or v not in pos:
            continue
        style = "dashed" if G[u][v].get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color="#1c2240",
                                   lw=0.7, linestyle=style,
                                   mutation_scale=7, shrinkA=5, shrinkB=5),
                    zorder=2)

    # ── Dim nodes ────────────────────────────────────────────────────────────
    dim_list = [n for n in dim_nodes if n in pos]
    if dim_list:
        nx.draw_networkx_nodes(G, pos, nodelist=dim_list,
                               node_color="#1a2040", node_size=380, ax=ax,
                               edgecolors="#252a50", linewidths=0.5, alpha=0.45)

    # ── Bright edges ─────────────────────────────────────────────────────────
    for u, v in bright_edges:
        if u not in pos or v not in pos:
            continue
        etype = elmap.get((u, v), "supplies")
        color = EDGE_COLORS.get(etype, "#aaaaaa")
        style = "dashed" if G[u][v].get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=2.4, linestyle=style,
                                   mutation_scale=15, shrinkA=8, shrinkB=8))

    # ── Bright nodes ─────────────────────────────────────────────────────────
    for n in bright_nodes:
        if n not in pos:
            continue
        color = NODE_COLORS.get(ntype.get(n, "Item"), "#888")
        sz = 1700 if n == POM else 1200
        nx.draw_networkx_nodes(G, pos, nodelist=[n],
                               node_color=color, node_size=sz, ax=ax,
                               edgecolors="white", linewidths=1.1)

    # ── Yellow ring on POM ───────────────────────────────────────────────────
    if POM in bright_nodes and POM in pos:
        px, py = pos[POM]
        ax.add_patch(mpatches.Circle((px, py), 0.72, color="#f5c518",
                                     fill=False, linewidth=3.5, zorder=8))

    # ── Node labels (bright only) ─────────────────────────────────────────────
    bright_lbls = {n: n for n in bright_nodes if n in pos}
    lbl_objs = nx.draw_networkx_labels(G, pos, labels=bright_lbls,
                                        font_size=8, font_color="white",
                                        font_family=FONT, ax=ax)
    for t in lbl_objs.values():
        t.set_clip_on(False)
        t.set_zorder(9)

    # ── Edge labels (bright only) ─────────────────────────────────────────────
    bright_el = {(u, v): elmap.get((u, v), "")
                 for u, v in bright_edges
                 if u in pos and v in pos}
    if bright_el:
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=bright_el,
            font_size=7, font_color="white", ax=ax,
            label_pos=0.5, rotate=False,
            bbox=dict(boxstyle="round,pad=0.2", fc="#1a1a2e", ec="none", alpha=0.9),
        )

    # ── Stage title (axis-fraction coords — always visible) ──────────────────
    ax.text(0.5, 0.99,
            f"{step_label}  {title}",
            transform=ax.transAxes,
            ha="center", va="top", fontsize=12, fontweight="bold",
            color="white", fontfamily=FONT,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#0d1117",
                      edgecolor="#5566bb", alpha=0.93),
            zorder=15, clip_on=False)

    if desc:
        ax.text(0.5, 0.925,
                desc,
                transform=ax.transAxes,
                ha="center", va="top", fontsize=8.5,
                color="#c4c8ff", fontfamily=FONT, multialignment="center",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#0a0c18",
                          edgecolor="#333", alpha=0.88),
                zorder=15, clip_on=False)

    # ── Convert to PIL RGB ────────────────────────────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, bbox_inches="tight",
                pad_inches=0.12, facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def lerp(a, b, t):
    return a + (b - a) * t


# ─────────────────────────────────────────────────────────────────────────────
def main():
    G, pos, ntype, elmap = build_graph()

    FULL = dict(xlim=(-14.0, 16.5), ylim=(-9.0, 11.5))
    L1   = dict(xlim=(-11.5, 10.5), ylim=(-7.0,  1.5))
    WIDE = dict(xlim=(-14.0, 16.5), ylim=(-7.0, 11.5))
    EP_Z = dict(xlim=(-13.5, 10.0), ylim=( 6.5, 12.0))
    F7_Z = dict(xlim=(-13.5,  3.5), ylim=(-4.0, 11.5))
    F6_Z = dict(xlim=(-10.5,  5.5), ylim=(-4.0, 12.0))
    DEC  = dict(xlim=( -2.0, 17.5), ylim=( 4.0, 12.0))

    stages = [
        dict(
            step="①", title="Disruption Detected",
            desc="PO-MOTR · Vendor 1003 · DC Motor · 14-day delay · 100 units at risk",
            hn=None, he=None, duration=2500,
            **FULL,
        ),
        dict(
            step="②", title="Layer 1 — Trace the Pegging Chain",
            desc="Vendor 1003 → PO-MOTR → DC Motor → SO-MOTR → MegaRetail (Tier 1 customer)",
            hn={V3, POM, MTD, SOM, CUS},
            he={(V3, POM), (POM, MTD), (POM, SOM), (SOM, CUS)},
            duration=2500,
            **L1,
        ),
        dict(
            step="③", title="Anchor Traversal — CONCERNS Edges Into Layer 2",
            desc="From Vendor 1003 + DMA-MTR-DC in L1, follow CONCERNS edges to surface prior episodes",
            hn={V3, POM, MTD, "EP-001","EP-002","EP-003", EP6},
            he={("EP-001",V3),("EP-002",V3),("EP-003",V3),(EP6,POM),(EP6,MTD)},
            duration=2500,
            **WIDE,
        ),
        dict(
            step="④", title="6 Prior Episodes — All Involving Vendor 1003",
            desc="Temporal chain: EP-001 → EP-002 → … → EP-006 (current disruption)",
            hn={"EP-001","EP-002","EP-003","EP-004","EP-005", EP6},
            he={("EP-001","EP-002"),("EP-002","EP-003"),("EP-003","EP-004"),
                ("EP-004","EP-005"),("EP-005", EP6)},
            duration=2500,
            **EP_Z,
        ),
        dict(
            step="⑤", title="FACT-007 Surfaces — Vendor 1003 Pattern Identified",
            desc="'Vendor 1003 is the disruption source in all 6 recorded episodes' · CHARACTERIZES → Layer 1",
            hn={F7, "EP-001", V3},
            he={(F7,"EP-001"), (F7, V3)},
            duration=2500,
            **F7_Z,
        ),
        dict(
            step="⑥", title="FACT-006 + REF-003 — Safety Stock Risk",
            desc="30 units on-hand vs 20-unit safety floor · Reflection: on-hand/floor < 2× → structural risk",
            hn={F6, R3, MTD, SS, EP6},
            he={(F6, EP6),(R3, F6),(F6, MTD),(F6, SS)},
            duration=2500,
            **F6_Z,
        ),
        dict(
            step="⑦", title="Evaluate 4 Mitigation Options Against Goals",
            desc="Each option scored against SLA · Cost · Qty · Inv goals, governed by POL-ONHOLD",
            hn={DA, DB, DC_, DD, G_SLA, G_CST, G_QTY, G_INV, "POL-ONHOLD", EP6},
            he={(DA,EP6),(DB,EP6),(DC_,EP6),(DD,EP6),
               (DA,G_SLA),(DA,G_CST),(DA,G_QTY),(DA,G_INV),(DA,"POL-ONHOLD")},
            duration=2500,
            **DEC,
        ),
        dict(
            step="⑧", title="Rank-1 Selected — Vendor 1002, $52/unit, 8-day Lead",
            desc="Prior Layer 2 context (6 episodes, FACT-007) drove the ranking · DEC-006B–D dimmed",
            hn={DA, G_SLA, G_CST, G_QTY, G_INV, "POL-ONHOLD"},
            he={(DA,G_SLA),(DA,G_CST),(DA,G_QTY),(DA,G_INV),(DA,"POL-ONHOLD")},
            duration=2500,
            xlim=(0.5, 16.5), ylim=(4.5, 12.0),   # tighter zoom than stage 7 → distinct frames
        ),
        dict(
            step="⑨", title="RESOLVED — Decision Anchored · Loop Complete",
            desc="RESOLVED edge written back · Next disruption on Vendor 1003 arrives pre-loaded with 6 episodes, 2 facts, 1 reflection",
            hn={DA, POM, V3, MTD, SOM, CUS, EP6, F7},
            he={(DA, POM),(EP6,POM),(EP6,MTD),(F7,V3)},
            duration=3500,
            **FULL,
        ),
    ]

    frames    = []
    durations = []
    FIGSIZE   = (15, 9)
    DPI       = 85
    N_TRANS   = 5          # interpolation frames per transition

    print("Rendering frames...")
    for i, s in enumerate(stages):
        print(f"  Stage {i+1}/{len(stages)}: {s['step']} {s['title']}")
        frame = render_frame(
            G, pos, ntype, elmap,
            s["hn"], s["he"],
            s["step"], s["title"], s["desc"],
            s["xlim"], s["ylim"],
            figsize=FIGSIZE, dpi=DPI,
        )
        frames.append(frame)
        durations.append(s["duration"])

        # Zoom-transition to next stage
        if i < len(stages) - 1:
            nxt = stages[i + 1]
            for t in np.linspace(0.2, 1.0, N_TRANS):
                xl = (lerp(s["xlim"][0], nxt["xlim"][0], t),
                      lerp(s["xlim"][1], nxt["xlim"][1], t))
                yl = (lerp(s["ylim"][0], nxt["ylim"][0], t),
                      lerp(s["ylim"][1], nxt["ylim"][1], t))
                tf = render_frame(
                    G, pos, ntype, elmap,
                    nxt["hn"], nxt["he"],
                    nxt["step"], nxt["title"], nxt["desc"],
                    xl, yl,
                    figsize=FIGSIZE, dpi=DPI,
                )
                frames.append(tf)
                durations.append(75)

    import imageio.v2 as iio2

    # Normalise all frames to the same pixel size (first frame drives it)
    target = frames[0].size
    frames = [f.resize(target, Image.LANCZOS) for f in frames]

    # Stamp a 1-pixel uniqueness marker in the bottom-right corner of each frame.
    # This prevents GIF encoders from deduplicating perceptually-similar frames.
    np_frames = []
    for idx, f in enumerate(frames):
        arr = np.array(f).copy()
        arr[-1, -1, 0] = idx % 256
        arr[-1, -1, 1] = (idx * 7) % 256
        arr[-1, -1, 2] = (idx * 13) % 256
        np_frames.append(arr)

    out_path = os.path.join(OUT, "slide4_traversal.gif")
    print(f"Saving GIF ({len(np_frames)} frames) → {out_path}")

    # iio2.mimwrite accepts per-frame duration in seconds via fps or via explicit list.
    # We write frame-by-frame to honour mixed stage (2 s) / transition (0.075 s) durations.
    dur_sec = [d / 1000.0 for d in durations]
    with iio2.get_writer(out_path, format="gif", mode="I", loop=0,
                         palettesize=256, quantizer="nq") as writer:
        for arr, d in zip(np_frames, dur_sec):
            writer.append_data(arr, {"duration": d})

    size_mb = os.path.getsize(out_path) / 1_048_576
    print(f"Done. File size: {size_mb:.1f} MB  ({target[0]}×{target[1]}px, {len(np_frames)} frames)")


if __name__ == "__main__":
    main()
