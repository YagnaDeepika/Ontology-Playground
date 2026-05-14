"""
Convert context_graph_one_pager.md to a formatted Word document.
"""

import os, re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH   = os.path.join(SCRIPT_DIR, "two_layer_network.png")
OUT_PATH   = os.path.join(SCRIPT_DIR, "context_graph_one_pager.docx")

# ── colours ───────────────────────────────────────────────────────────────────
C_H1     = RGBColor(0x0d, 0x2b, 0x5e)   # deep navy
C_H2     = RGBColor(0x15, 0x5a, 0xa0)   # medium blue
C_BODY   = RGBColor(0x1a, 0x1a, 0x1a)   # near-black
C_CODE   = RGBColor(0x2b, 0x6c, 0xb0)   # blue-grey for inline code
C_RULE   = RGBColor(0xcc, 0xcc, 0xcc)   # light grey for HR
C_THEAD  = RGBColor(0x1e, 0x3a, 0x6e)   # table header bg
C_TROW   = RGBColor(0xf0, 0xf4, 0xfa)   # table alt row bg


def set_cell_bg(cell, rgb_hex):
    """Fill a table cell with a solid background colour (hex e.g. '1e3a6e')."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  rgb_hex)
    tcPr.append(shd)


def add_inline(para, text):
    """
    Add a run to `para` that handles **bold** and `code` inline markers.
    Alternates between normal, bold, and code spans.
    """
    # Split on **...** and `...`
    tokens = re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', text)
    for tok in tokens:
        if tok.startswith("**") and tok.endswith("**"):
            run = para.add_run(tok[2:-2])
            run.bold = True
            run.font.color.rgb = C_BODY
        elif tok.startswith("`") and tok.endswith("`"):
            run = para.add_run(tok[1:-1])
            run.font.name  = "Consolas"
            run.font.size  = Pt(9)
            run.font.color.rgb = C_CODE
        else:
            if tok:
                run = para.add_run(tok)
                run.font.color.rgb = C_BODY


def add_h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(10)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(20)
    run.font.color.rgb = C_H1
    run.font.name = "Calibri"
    return p


def add_h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(13)
    run.font.color.rgb = C_H2
    run.font.name = "Calibri"
    # Bottom border as a subtle rule
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot  = OxmlElement("w:bottom")
    bot.set(qn("w:val"),   "single")
    bot.set(qn("w:sz"),    "4")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "4472C4")
    pBdr.append(bot)
    pPr.append(pBdr)
    return p


def add_body(doc, text, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.line_spacing = Pt(14)
    add_inline(p, text)
    for run in p.runs:
        run.font.size = Pt(10.5)
        run.font.name = "Calibri"
    return p


def add_hr(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot  = OxmlElement("w:bottom")
    bot.set(qn("w:val"),   "single")
    bot.set(qn("w:sz"),    "6")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "CCCCCC")
    pBdr.append(bot)
    pPr.append(pBdr)


def add_layer_table(doc, node_types, edge_types):
    table = doc.add_table(rows=2, cols=2)
    table.style = "Table Grid"
    table.autofit = False
    col_w = Inches(3.0)
    for col in table.columns:
        for cell in col.cells:
            cell.width = col_w

    # Header row
    for i, hdr in enumerate(["Node Types", "Edge Types"]):
        cell = table.cell(0, i)
        set_cell_bg(cell, "1e3a6e")
        p    = cell.paragraphs[0]
        run  = p.add_run(hdr)
        run.bold = True
        run.font.color.rgb = RGBColor(0xff, 0xff, 0xff)
        run.font.size = Pt(10)
        run.font.name = "Calibri"

    # Data row
    for i, content in enumerate([node_types, edge_types]):
        cell = table.cell(1, i)
        set_cell_bg(cell, "e8f0fb")
        p    = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after  = Pt(2)
        run  = p.add_run(content)
        run.font.size  = Pt(9.5)
        run.font.name  = "Calibri"
        run.font.color.rgb = C_BODY

    # Space after table
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


# ── build document ────────────────────────────────────────────────────────────
doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin    = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin   = Inches(1.0)
    section.right_margin  = Inches(1.0)

# ── Title ─────────────────────────────────────────────────────────────────────
add_h1(doc, "The Decision Intelligence Layer for Agentic Supply Chain")

# ── Section 1 ─────────────────────────────────────────────────────────────────
add_h2(doc, "Why Context Graphs Matter in Supply Chain")

add_body(doc,
    "Modern supply chains are instrumented with vast ERP data — purchase orders, "
    "inventory positions, production schedules, supplier records — but AI agents "
    "operating on this data face a fundamental limitation: they reason in isolation. "
    "Each disruption event is evaluated from scratch, with no memory of how similar "
    "situations were handled, which vendors have chronic reliability issues, or which "
    "mitigations actually held up under pressure. The result is reactive, inconsistent "
    "decision-making that fails to compound organizational learning over time."
)

add_body(doc,
    "A **context graph** addresses this directly. Rather than treating every disruption "
    "as a novel problem, it maintains a structured, queryable record of past decisions, "
    "outcomes, and synthesized patterns — anchored to the same supply chain entities "
    "the agent acts upon. The agent enters each situation pre-loaded with relevant "
    "institutional knowledge, not just live ERP state.",
    space_after=8,
)

add_hr(doc)

# ── Section 2 ─────────────────────────────────────────────────────────────────
add_h2(doc, "Two-Layer Architecture")

add_body(doc,
    "The graph is organized into two co-existing layers connected by cross-layer edges."
)

# L1
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(3)
r = p.add_run("Layer 1 — Supply Chain Network")
r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x15,0x65,0xc0)
r.font.name = "Calibri"
r2 = p.add_run(
    " is the live operational fabric sourced from ERP (e.g., Dynamics 365). "
    "It captures the entities and relationships that define how supply moves "
    "through the organization:"
)
r2.font.size = Pt(10.5); r2.font.color.rgb = C_BODY; r2.font.name = "Calibri"

add_layer_table(doc,
    "Supplier, Item, PurchaseOrder, ProductionOrder,\nInventory, SalesOrder, Customer",
    "supplies, delivers, consumed_by, produces,\nallocated_to, fulfills, pegged_to, alternate_for",
)

# L2
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(3)
r = p.add_run("Layer 2 — Intelligence Layer")
r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = RGBColor(0x6a,0x0d,0xad)
r.font.name = "Calibri"
r2 = p.add_run(
    " accumulates institutional memory across agent runs. It is populated and "
    "updated automatically each time the agent handles a disruption:"
)
r2.font.size = Pt(10.5); r2.font.color.rgb = C_BODY; r2.font.name = "Calibri"

add_layer_table(doc,
    "Episode, MitigationDecision, Fact, Reflection,\nConcept, Goal, Policy, Recommendation",
    "NEXT, DERIVED_FROM, DERIVED_FROM_FACT,\nHAS_CONCEPT, ABOUT_CONCEPT, GOVERNED_BY,\nSCORED_AGAINST, SUPPORTED_BY",
)

add_body(doc,
    "Cross-layer edges — `CONCERNS`, `CHARACTERIZES`, `RESOLVED`, `TARGETS`, `APPLIES_TO` "
    "— anchor every memory construct to the specific supply chain entity it pertains to, "
    "keeping context traceable and auditable.",
    space_after=8,
)

# ── Image ─────────────────────────────────────────────────────────────────────
if os.path.exists(IMG_PATH):
    ip = doc.add_paragraph()
    ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ip.paragraph_format.space_before = Pt(4)
    ip.paragraph_format.space_after  = Pt(8)
    run = ip.add_run()
    run.add_picture(IMG_PATH, width=Inches(6.2))
else:
    add_body(doc, "[Image: two_layer_network.png not found]")

add_hr(doc)

# ── Section 3 ─────────────────────────────────────────────────────────────────
add_h2(doc, "Graph Traversal in Practice")

add_body(doc,
    "When a disruption arrives — a 14-day delay from Vendor 1003 on a DC Motor "
    "component pegged to a Tier 1 retail sales order — the agent traverses both "
    "layers simultaneously rather than consulting Layer 1 alone."
)

add_body(doc,
    "Starting from Vendor 1003 in Layer 1, the agent follows `CHARACTERIZES` edges "
    "upward into Layer 2, reaching six historical Episodes involving the same vendor. "
    "From these Episodes, distilled **Fact** nodes surface a repeating pattern: "
    "Vendor 1003 delays on this component class more than three times per year, and "
    "safety stock erosion is a documented downstream consequence. A **Reflection** "
    "synthesized from these Facts identifies an alternate supplier — Vendor 1002 — "
    "with a strong prior fulfillment record, captured in earlier MitigationDecision outcomes."
)

add_body(doc,
    "The agent scores candidate mitigations against active **Goal** nodes (SLA attainment, "
    "cost) and **Policy** nodes (procurement approval thresholds). The top-ranked "
    "recommendation — issue a replacement purchase order to Vendor 1002 — arrives with "
    "a documented rationale grounded in organizational history, not just current inventory math."
)

add_body(doc,
    "Upon execution, a new Episode and MitigationDecision are written back to Layer 2. "
    "The intelligence layer compounds with every run: the next disruption on the same "
    "vendor or component class arrives with richer context, higher-confidence recommendations, "
    "and a shorter path to resolution.",
    space_after=0,
)

doc.save(OUT_PATH)
print(f"Saved → {OUT_PATH}  ({os.path.getsize(OUT_PATH)//1024} KB)")
