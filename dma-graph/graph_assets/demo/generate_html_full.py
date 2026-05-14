"""
Generate full click-through HTML:
  5 context views (slides 0-3 + slide 5) + 9 PO-MOTR traversal stages = 14 total
Output: slide4_clickthrough_full.html  (fully self-contained, no server needed)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys, os, io, json, base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_html as gh

from PIL import Image

OUT         = os.path.dirname(os.path.abspath(__file__))
TARGET_SIZE = (1760, 990)
BG          = "#0d1117"
FONT        = "DejaVu Sans"


# ── helpers ───────────────────────────────────────────────────────────────────
def load_slide_png(filename):
    path = os.path.join(OUT, filename)
    img  = Image.open(path).convert("RGB").resize(TARGET_SIZE, Image.LANCZOS)
    buf  = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def render_slide5_clean():
    """Slide 5 retrieval flow — the large red curved arc arrow is omitted."""
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
        ax.text(x + BOX_W/2, y + BOX_H - 0.28, title,
                ha="center", va="top", fontsize=9, fontweight="bold",
                color=ec, fontfamily=FONT)
        ax.text(x + BOX_W/2, y + BOX_H/2 - 0.1, body,
                ha="center", va="center", fontsize=7.5, color="white",
                fontfamily=FONT, multialignment="center")
        centres.append((x + BOX_W/2, y + BOX_H/2))

    # Straight arrows 1→2→3→4→5 only (stray curved red arrow omitted)
    for i in range(4):
        ax.annotate("", xy=(centres[i+1][0] - BOX_W/2, centres[i+1][1]),
                    xytext=(centres[i][0] + BOX_W/2, centres[i][1]),
                    arrowprops=dict(arrowstyle="-|>", color="#888",
                                   lw=1.8, mutation_scale=14), zorder=3)

    ax.text(2.0, -3.8,
            "Every execution enriches Layer 2 — the next disruption on Vendor 1003 or DMA-MTR-DC\n"
            "arrives pre-loaded with 6 episodes, 2 facts, 1 reflection, and 2 recommendations.",
            ha="center", va="center", fontsize=9.5, color="#e8e0ff",
            fontfamily=FONT, multialignment="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1030",
                      edgecolor="#7e3af2", alpha=0.9), zorder=3)

    buf = io.BytesIO()
    fig.savefig(buf, dpi=160, bbox_inches="tight", pad_inches=0.3, facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGB").resize(TARGET_SIZE, Image.LANCZOS)
    buf2 = io.BytesIO()
    img.save(buf2, format="PNG", optimize=True)
    return base64.b64encode(buf2.getvalue()).decode()


# ── narration scripts (HTML, rendered via innerHTML) ─────────────────────────
SCRIPT_0 = """\
<b>Two-Layer Supply Chain Context Graph</b><br><br>
Every time the Disruption Mitigation Agent handles a supply chain problem, it doesn't just fix it and forget.
It writes a trace into a memory layer — and the next agent facing a similar disruption <b>starts smarter</b>.<br><br>
<b>Layer 1 — Operational Supply Chain Network:</b> The physical and commercial entities you'd find in any ERP —
Suppliers, Items, Purchase Orders, Production Orders, Inventory, Distribution Centers, Sales Orders, and Customers.<br><br>
<b>Layer 2 — Intelligence Layer (Context Graph):</b> Accumulated institutional memory — Episodes, MitigationDecisions,
Facts, Reflections, Concepts, Policies, Goals, and Recommendations — distilled from every past DMA execution.<br><br>
<b>Cross-layer edges</b> anchor memory to specific supply chain entities so context retrieval is automatic.<br><br>
<em>Worked example: PO-MOTR — DC Motor, Vendor 1003, 14-day delivery delay</em>"""

SCRIPT_1 = """\
<b>Layer 1 is the operational supply chain</b> — nodes and edges the agent acts on via MCP calls to D365.<br><br>
<b>Node types:</b><br>
<span style="color:#1e6eb5;font-size:16px">&#9632;</span>&nbsp;<b>Supplier</b>&nbsp;&nbsp;
<span style="color:#29a6d4;font-size:16px">&#9632;</span>&nbsp;<b>Item / Material</b>&nbsp;&nbsp;
<span style="color:#d4a017;font-size:16px">&#9632;</span>&nbsp;<b>Purchase Order</b>&nbsp;&nbsp;
<span style="color:#e87c25;font-size:16px">&#9632;</span>&nbsp;<b>Production Order</b>&nbsp;&nbsp;
<span style="color:#2ea84f;font-size:16px">&#9632;</span>&nbsp;<b>Inventory</b>&nbsp;&nbsp;
<span style="color:#27c9a0;font-size:16px">&#9632;</span>&nbsp;<b>Distribution Center</b>&nbsp;&nbsp;
<span style="color:#5ab552;font-size:16px">&#9632;</span>&nbsp;<b>Sales Order</b>&nbsp;&nbsp;
<span style="color:#f0a500;font-size:16px">&#9632;</span>&nbsp;<b>Customer</b><br><br>
<b>Edge types:</b>&nbsp;
<code>supplies</code> &middot; <code>delivers</code> &middot; <code>consumed_by</code> &middot; <code>produces</code> &middot;
<code>stocked_at</code> &middot; <code>allocated_to</code> &middot; <code>transfers_to</code> &middot; <code>ships_to</code> &middot;
<code>pegged_to</code> &middot; <code>alternate_for</code> &middot; <code>substitutes_for</code><br><br>
The <b>pegging chain</b> links a Purchase Order directly to the Production Order that needs it,
to the Sales Order at risk, all the way to the customer. This multi-hop traversal happens in <b>milliseconds</b>
as a graph query. In a relational ERP model it would require sequential joins across multiple tables.<br><br>
Layer 1 is also where the agent <b>acts</b> — it issues new POs, triggers inventory transfers,
and modifies delivery dates via MCP calls back to D365."""

SCRIPT_2 = """\
<b>Layer 2 is the intelligence layer</b> — the context graph that makes the agent accumulate institutional
memory over time. The nodes here are not supply chain entities — they are <b>memory constructs</b>.<br><br>
<b>Node types:</b><br>
<span style="color:#e07b39;font-size:16px">&#9632;</span>&nbsp;<b>Episode</b> &mdash; timestamped, immutable record of one DMA execution&nbsp;&nbsp;
<span style="color:#c03d3d;font-size:16px">&#9632;</span>&nbsp;<b>MitigationDecision</b> &mdash; option chosen and why<br>
<span style="color:#c8b800;font-size:16px">&#9632;</span>&nbsp;<b>Fact</b> &mdash; LLM-distilled atomic insight (e.g. &ldquo;Vendor 1003 is disruption source in all 6 episodes&rdquo;)&nbsp;&nbsp;
<span style="color:#a855f7;font-size:16px">&#9632;</span>&nbsp;<b>Reflection</b> &mdash; higher-order pattern synthesized from multiple Facts<br>
<span style="color:#7e3af2;font-size:16px">&#9632;</span>&nbsp;<b>Concept</b> &mdash; thematic anchor enabling cross-disruption retrieval (e.g. <code>safety_stock_erosion</code>)&nbsp;&nbsp;
<span style="color:#6b7fa3;font-size:16px">&#9632;</span>&nbsp;<b>Policy</b>&nbsp;&nbsp;
<span style="color:#34c9eb;font-size:16px">&#9632;</span>&nbsp;<b>Goal</b>&nbsp;&nbsp;
<span style="color:#f472b6;font-size:16px">&#9632;</span>&nbsp;<b>Recommendation</b><br><br>
<b>Edge types:</b>&nbsp;
<code>NEXT</code> (temporal chain) &middot; <code>DERIVED_FROM</code> &middot; <code>DERIVED_FROM_FACT</code> &middot;
<code>HAS_CONCEPT</code> &middot; <code>ABOUT_CONCEPT</code> &middot; <code>GOVERNED_BY</code> &middot;
<code>SCORED_AGAINST</code> &middot; <code>SUPPORTED_BY</code><br><br>
Layer 2 is built in three phases: <b>&#9312; Preserve</b> &mdash; every DMA run writes Episode + MitigationDecision
immediately. <b>&#9313; Extract</b> &mdash; a batch LLM job distils Fact nodes from recent Episodes.
<b>&#9314; Synthesize</b> &mdash; a periodic LLM job generates Reflections and Recommendations from Fact clusters."""

SCRIPT_3 = """\
The two layers are <b>coupled through typed cross-layer edges</b> (dashed lines in the diagram).<br><br>
<b>Layer 1 nodes:</b>&nbsp;
<span style="color:#1e6eb5">&#9632;</span>&nbsp;Supplier&nbsp;
<span style="color:#29a6d4">&#9632;</span>&nbsp;Item&nbsp;
<span style="color:#d4a017">&#9632;</span>&nbsp;Purchase Order&nbsp;
<span style="color:#e87c25">&#9632;</span>&nbsp;Production Order&nbsp;
<span style="color:#2ea84f">&#9632;</span>&nbsp;Inventory&nbsp;
<span style="color:#5ab552">&#9632;</span>&nbsp;Sales Order&nbsp;
<span style="color:#f0a500">&#9632;</span>&nbsp;Customer<br>
<b>Layer 1 edges:</b>&nbsp;<code>supplies</code> &middot; <code>delivers</code> &middot; <code>consumed_by</code> &middot;
<code>stocked_at</code> &middot; <code>allocated_to</code> &middot; <code>pegged_to</code> &middot; <code>alternate_for</code><br><br>
<b>Layer 2 nodes:</b>&nbsp;
<span style="color:#e07b39">&#9632;</span>&nbsp;Episode&nbsp;
<span style="color:#c03d3d">&#9632;</span>&nbsp;MitigationDecision&nbsp;
<span style="color:#c8b800">&#9632;</span>&nbsp;Fact&nbsp;
<span style="color:#a855f7">&#9632;</span>&nbsp;Reflection&nbsp;
<span style="color:#7e3af2">&#9632;</span>&nbsp;Concept&nbsp;
<span style="color:#6b7fa3">&#9632;</span>&nbsp;Policy&nbsp;
<span style="color:#34c9eb">&#9632;</span>&nbsp;Goal&nbsp;
<span style="color:#f472b6">&#9632;</span>&nbsp;Recommendation<br>
<b>Layer 2 edges:</b>&nbsp;<code>NEXT</code> &middot; <code>DERIVED_FROM</code> &middot; <code>DERIVED_FROM_FACT</code> &middot;
<code>HAS_CONCEPT</code> &middot; <code>GOVERNED_BY</code> &middot; <code>SCORED_AGAINST</code> &middot; <code>SUPPORTED_BY</code><br><br>
<b>Cross-layer edges:</b>&nbsp;
<code>CONCERNS</code> (Episode &rarr; L1 entity) &nbsp;&middot;&nbsp;
<code>CHARACTERIZES</code> (Fact &rarr; Supplier/Item) &nbsp;&middot;&nbsp;
<code>TARGETS</code> (Reflection &rarr; Item) &nbsp;&middot;&nbsp;
<code>APPLIES_TO</code> (Recommendation &rarr; Item) &nbsp;&middot;&nbsp;
<code>RESOLVED</code> (Decision &rarr; Purchase Order)<br><br>
The agent <b>reads Layer 2</b> before reasoning, <b>acts on Layer 1</b> via MCP, and
<b>writes the trace back to Layer 2</b> when done. Cross-layer edges ensure that when the agent
queries a vendor or item, all related memory surfaces automatically."""

SCRIPT_5 = """\
<b>The full retrieval and execution loop in six steps:</b><br><br>
<b>&#9312; Disruption Detected</b> &mdash; PO-MOTR flagged: Vendor 1003, DC Motor, 14-day delay, 100 units at risk.<br><br>
<b>&#9313; Anchor Traversal</b> &mdash; Agent follows <code>CHARACTERIZES</code> edges from Vendor 1003 and DMA-MTR-DC
(Layer 1 entities) up into Layer 2. Six prior episodes surface immediately &mdash; the agent is not starting cold.<br><br>
<b>&#9314; Concept Expansion</b> &mdash; Hops through Concept nodes (<code>safety_stock_erosion</code>,
<code>alt_vendor_switch</code>) to pull in all related Facts and Reflections, including those from disruptions
with completely different PO numbers.<br><br>
<b>&#9315; Rank &amp; Inject Context</b> &mdash; Recent episodes weighted higher. Top-k Facts + Reflections injected
into the agent system prompt before evaluating a single mitigation option.<br><br>
<b>&#9316; Evaluate Mitigations</b> &mdash; Score options against Goals and Policies. Rank 1 &rarr; Vendor 1002
(known good alternate, confirmed by prior episode history in Layer 2).<br><br>
<b>&#9317; Execute via MCP</b> &mdash; Issue new PO to Vendor 1002. Update D365. Write new Episode and
MitigationDecision back to Layer 2. &#9851;<br><br>
<em>Every execution enriches Layer 2. The next disruption on Vendor 1003 or DC Motor arrives pre-loaded
with 6 episodes, 2 facts, 1 reflection, and 2 recommendations &mdash; none had to be re-derived.</em>"""


# ── context stage metadata ────────────────────────────────────────────────────
CONTEXT_META = [
    dict(step_num="Overview",     title="Two-Layer Supply Chain Context Graph",  script=SCRIPT_0),
    dict(step_num="Layer 1",      title="Layer 1 — Supply Chain Network",        script=SCRIPT_1),
    dict(step_num="Layer 2",      title="Layer 2 — Intelligence Layer",          script=SCRIPT_2),
    dict(step_num="Architecture", title="Two-Layer Combined Architecture",        script=SCRIPT_3),
    dict(step_num="Agent Loop",   title="Agent Retrieval & Execution Flow",       script=SCRIPT_5),
]


# ─────────────────────────────────────────────────────────────────────────────
def main():
    G, pos, ntype, elmap = gh.build_graph()

    # ── 5 context views ──────────────────────────────────────────────────────
    print("Loading context slides...")
    context_imgs = [
        load_slide_png("slide0_title.png"),
        load_slide_png("slide1_layer1_supply_chain.png"),
        load_slide_png("slide2_layer2_intelligence.png"),
        load_slide_png("slide3_two_layer_combined.png"),
    ]
    print("  Re-rendering slide 5 (removing stray arrow)...")
    context_imgs.append(render_slide5_clean())

    stage_data = []
    for meta, img in zip(CONTEXT_META, context_imgs):
        stage_data.append({
            "step_num": meta["step_num"],
            "title":    meta["title"],
            "img":      img,
            "script":   meta["script"].strip(),
        })

    # ── 9 traversal stages ───────────────────────────────────────────────────
    print("Rendering traversal stages...")
    for i, s in enumerate(gh.STAGES):
        print(f"  Stage {i+1}/{len(gh.STAGES)}: {s['title']}")
        img = gh.render_stage(
            G, pos, ntype, elmap,
            s["hn"], s["he"],
            s["step"], s["title"],
            s["xlim"], s["ylim"],
        )
        b64      = gh.img_to_b64(img)
        step_num = s["step"].split("/")[0].strip()
        stage_data.append({
            "step_num": step_num,
            "title":    s["title"],
            "img":      b64,
            "script":   s["script"].strip(),
        })

    # ── assemble HTML ─────────────────────────────────────────────────────────
    total       = len(stage_data)
    stages_json = json.dumps(stage_data, ensure_ascii=False)

    html = (gh.HTML_TEMPLATE
            .replace("{n}", str(total))
            .replace("{stages_json}", stages_json))

    out_path = os.path.join(OUT, "slide4_clickthrough_full.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) // 1024
    print(f"Saved → {out_path}  ({size_kb} KB, {total} stages)")


if __name__ == "__main__":
    main()
