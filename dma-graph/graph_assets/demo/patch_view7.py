"""
Patch View 7 (② Layer 1 — Trace the Pegging Chain) in slide4_clickthrough_full_v2.html.

Problems in the original render:
  - ylim=(-7, 1.5) → data aspect ratio 22:8.5 = 2.6:1 on a 16:9 figure
    → mpatches.Circle drawn in data coords becomes a tall ellipse (distortion)
    → node label fonts appear tiny at browser display size
  - bbox_inches="tight" variable crop compounds the aspect ratio issue

Fix:
  - xlim=(-11.5, 10.5)  [unchanged]
  - ylim=(-8.5, 3.9)    [range ≈ 12.4; ratio 22/12.4 = 1.77 ≈ 16/9 → circle is circular]
  - figsize=(16, 9), dpi=150, save WITHOUT bbox_inches="tight" → exact 16:9 pixels
  - Larger node sizes (3500/2800) and font sizes (13/10.5)
  - Yellow ring via ax.scatter (display-space circles, never elliptical)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json, re, base64, io, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_html as gh
from PIL import Image

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
TARGET_HTML = os.path.join(SCRIPT_DIR, "slide4_clickthrough_full_v2.html")
TARGET_SIZE = (1760, 990)
BG          = "#0d1117"
FONT        = "DejaVu Sans"

# Stage 7 is index 6 (0-based) in the 14-stage list
STAGE_IDX = 6


def in_view(n, pos, xlim, ylim):
    """True if node n's position is within the visible data range."""
    if n not in pos:
        return False
    px, py = pos[n]
    return xlim[0] <= px <= xlim[1] and ylim[0] <= py <= ylim[1]


def render_view7(G, pos, ntype, elmap):
    """
    Re-render the pegging-chain view.

    Strategy: render at the natural (wide/flat) aspect ratio of the horizontal
    chain, then letterbox onto a 16:9 dark canvas.  This avoids squashing the
    content into a thin strip while keeping the yellow ring circular.
    """
    import networkx as nx

    h_nodes = {gh.V3, gh.POM, gh.MTD, gh.SOM, gh.CUS}
    h_edges = {(gh.V3, gh.POM), (gh.POM, gh.MTD), (gh.POM, gh.SOM), (gh.SOM, gh.CUS)}

    xlim = (-11.5, 10.5)   # 22 data units wide
    ylim = (-5.5,   2.0)   # 7.5 data units tall  → ratio 22/7.5 = 2.93:1

    # figsize height chosen so data x/y ratio ≈ figure w/h ratio → ring stays circular
    # 22 / 7.5 ≈ 2.93  →  fig_h = 16 / 2.93 ≈ 5.46
    fig_w, fig_h = 16.0, 5.46
    DPI = 160

    all_nodes = set(G.nodes())
    all_edges = set(G.edges())
    bright_nodes = h_nodes
    bright_edges = h_edges

    # Filter dim items: skip anything whose node position is outside the visible area
    dim_nodes = {n for n in all_nodes - bright_nodes if in_view(n, pos, xlim, ylim)}
    dim_edges = {(u, v) for u, v in all_edges - bright_edges
                 if in_view(u, pos, xlim, ylim) and in_view(v, pos, xlim, ylim)}

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Layer band (L1 only visible in this ylim)
    ax.add_patch(mpatches.FancyBboxPatch(
        (-13.5, -5.0), 29.5, 6.2,
        boxstyle="round,pad=0.3", facecolor="#0a1e30",
        edgecolor="#333", linewidth=1.0, alpha=0.55, zorder=0))
    ax.text(-11.2, -4.65 + 0.35, "LAYER 1 — Supply Chain Network",
            fontsize=11, color="#5baee0", fontfamily=FONT,
            fontweight="bold", va="bottom", zorder=1, clip_on=True)

    ax.axhline(1.5, color="#444", linewidth=1.2, linestyle="--", alpha=0.6, zorder=1)

    # Dim edges
    for u, v in dim_edges:
        style = "dashed" if G[u][v].get("cross") else "solid"
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color="#1c2240",
                                   lw=0.8, linestyle=style,
                                   mutation_scale=7, shrinkA=6, shrinkB=6),
                    zorder=2)

    # Dim nodes
    if dim_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=list(dim_nodes),
                               node_color="#1a2040", node_size=600, ax=ax,
                               edgecolors="#252a50", linewidths=0.5, alpha=0.45)

    # Bright edges
    for u, v in bright_edges:
        if u not in pos or v not in pos:
            continue
        color = gh.EDGE_COLORS.get(elmap.get((u, v), "supplies"), "#aaaaaa")
        ax.annotate("", xy=pos[v], xytext=pos[u],
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                   lw=3.2, mutation_scale=22,
                                   shrinkA=30, shrinkB=30),
                    zorder=4)

    # Bright nodes
    for n in bright_nodes:
        if n not in pos:
            continue
        color = gh.NODE_COLORS.get(ntype.get(n, "Item"), "#888")
        sz = 4000 if n == gh.POM else 3200
        nx.draw_networkx_nodes(G, pos, nodelist=[n],
                               node_color=color, node_size=sz, ax=ax,
                               edgecolors="white", linewidths=1.8)

    # Yellow ring — scatter keeps it circular in display space
    px, py = pos[gh.POM]
    ax.scatter([px], [py], s=8500, facecolors="none",
               edgecolors="#f5c518", linewidths=4.5, zorder=8)

    # Node labels
    bright_lbls = {n: n for n in bright_nodes if n in pos}
    lbl_objs = nx.draw_networkx_labels(G, pos, labels=bright_lbls,
                                        font_size=14, font_color="white",
                                        font_family=FONT, ax=ax)
    for t in lbl_objs.values():
        t.set_clip_on(False)

    # Edge labels
    bright_el = {(u, v): elmap.get((u, v), "")
                 for u, v in bright_edges if u in pos and v in pos}
    if bright_el:
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=bright_el,
            font_size=11, font_color="white", ax=ax,
            label_pos=0.5, rotate=False,
            bbox=dict(boxstyle="round,pad=0.3", fc="#1a1a2e", ec="none", alpha=0.9),
        )

    # ── Render at natural (wide/flat) aspect ratio ────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    buf.seek(0)
    content = Image.open(buf).convert("RGB")

    # ── Letterbox onto a 16:9 dark canvas ────────────────────────────────────
    cw, ch = content.size
    canvas_w, canvas_h = 2560, 1440   # high-res 16:9 working canvas
    # Scale content to fill canvas width
    scale   = canvas_w / cw
    new_w   = canvas_w
    new_h   = round(ch * scale)
    content = content.resize((new_w, new_h), Image.LANCZOS)
    canvas  = Image.new("RGB", (canvas_w, canvas_h), (13, 17, 23))
    y_off   = (canvas_h - new_h) // 2
    canvas.paste(content, (0, max(y_off, 0)))

    # Final resize to target
    final = canvas.resize(TARGET_SIZE, Image.LANCZOS)
    buf2  = io.BytesIO()
    final.save(buf2, format="PNG", optimize=True)
    return base64.b64encode(buf2.getvalue()).decode()


def patch_html(new_b64):
    with open(TARGET_HTML, encoding="utf-8") as f:
        src = f.read()

    # Extract full STAGES array
    m = re.search(r'(const STAGES = )(\[)', src)
    start = m.start(2)
    depth = 0
    for i, c in enumerate(src[start:]):
        if c == '[':   depth += 1
        elif c == ']': depth -= 1
        if depth == 0:
            end = start + i + 1
            break

    stages = json.loads(src[start:end])
    print(f"  Replacing image for: [{stages[STAGE_IDX]['step_num']}] {stages[STAGE_IDX]['title']}")
    stages[STAGE_IDX]["img"] = new_b64

    new_json = json.dumps(stages, ensure_ascii=False)
    new_src  = src[:m.start(2)] + new_json + src[end:]

    with open(TARGET_HTML, "w", encoding="utf-8") as f:
        f.write(new_src)

    size_kb = os.path.getsize(TARGET_HTML) // 1024
    print(f"  Updated → {TARGET_HTML}  ({size_kb} KB)")


def main():
    print("Building graph...")
    G, pos, ntype, elmap = gh.build_graph()

    print("Re-rendering View 7...")
    new_b64 = render_view7(G, pos, ntype, elmap)

    print("Patching HTML...")
    patch_html(new_b64)
    print("Done.")


if __name__ == "__main__":
    main()
