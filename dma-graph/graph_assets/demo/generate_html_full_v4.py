"""
Generate slide4_clickthrough_full_v4.html

Fixes vs v3:
  View 3 (Layer 2 Intelligence Layer): the ③ SYNTHESIZE phase box overlapped
  the Node Types legend (lower left).  Fix: shift all three phase boxes upward
  so the bottom of ③ SYNTHESIZE sits at y=-0.5, well above the legend region
  (≈ y=-5.0 to y=-2.5).  ylim extended to (-5.0, 8.0) to keep ① PRESERVE
  fully visible.

All other stages loaded unchanged from v3 HTML.
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
SRC_HTML    = os.path.join(SCRIPT_DIR, "slide4_clickthrough_full_v3.html")
OUT_HTML    = os.path.join(SCRIPT_DIR, "slide4_clickthrough_full_v4.html")
TARGET_SIZE = (1760, 990)
BG          = "#0d1117"


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


def load_template():
    """Extract the HTML template string from the v3 generator (reuse it verbatim)."""
    v3_path = os.path.join(SCRIPT_DIR, "generate_html_full_v3.py")
    with open(v3_path, encoding="utf-8") as f:
        src = f.read()
    # Extract the HTML_TEMPLATE triple-quoted string
    m = re.search(r'HTML_TEMPLATE = """\\\n(.*?)"""', src, re.DOTALL)
    return '"""\\\n' + m.group(1) + '"""'


# ── View 3 — Layer 2 Intelligence Layer (fixed phase-box positions) ───────────
def render_slide2_fixed():
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
        "EP-003": (1.5, 5.5),  "EP-004": (4.5, 5.5),
        "DEC-001": (1.5, 3.0), "DEC-002": (4.5, 3.0),
        "FACT-001": (-1.0, 1.0), "FACT-002": (2.0, 1.0),
        "REF-001": (0.5, -1.2),
        "supp_rel": (-4.5, 3.0), "alt_vendor": (8.0, 3.0),
        "REC-001": (0.5, -3.2),
    }

    draw_graph(ax, G, pos, ntype, elmap, node_size=2200, font_size=15, edge_font_size=12)

    # Phase boxes — shifted upward so ③ SYNTHESIZE bottom (y=-0.5) is well
    # above the Node Types legend (which occupies approx y=-5.0 to y=-2.5).
    # Gaps between boxes: ~0.8 data units each.
    phases = [
        (-11.5, 5.5, 3.0, 2.2, "① PRESERVE",
         "Every Disruption Mitigation\nAgent run writes Episode +\nMitigationDecision immediately"),
        (-11.5, 2.5, 3.0, 2.2, "② EXTRACT",
         "LLM batch job distils\nFact nodes from\nrecent Episodes"),
        (-11.5, -0.5, 3.0, 2.2, "③ SYNTHESIZE",
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

    # ylim extended at top to keep ① PRESERVE fully visible (5.5 + 2.2 = 7.7 < 8.0)
    ax.set_xlim(-12.5, 18.0)
    ax.set_ylim(-5.0, 8.0)
    return slide_to_b64(fig)


# ── HTML template (copy of v3: 75% image / 25% script, 11 px script font) ─────
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


def main():
    print("Loading stages from v3 HTML...")
    stages = load_stages()
    print(f"  {len(stages)} stages loaded")

    print("Re-rendering View 3 (Layer 2, fixed phase-box positions)...")
    stages[2]["img"] = render_slide2_fixed()

    total       = len(stages)
    stages_json = json.dumps(stages, ensure_ascii=False)
    html = (HTML_TEMPLATE
            .replace("{n}", str(total))
            .replace("{stages_json}", stages_json))

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUT_HTML) // 1024
    print(f"Saved → {OUT_HTML}  ({size_kb} KB, {total} stages)")


if __name__ == "__main__":
    main()
