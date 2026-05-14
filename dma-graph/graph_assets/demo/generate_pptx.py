"""
Build slide4_clickthrough_full.pptx from the click-through HTML.
One slide per view: title bar + full-bleed image + speaker notes (script).
"""

import json, re, base64, io, os, html as html_lib
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

OUT      = os.path.dirname(os.path.abspath(__file__))
SRC_HTML = os.path.join(OUT, "slide4_clickthrough_full.html")
OUT_PPTX = os.path.join(OUT, "slide4_clickthrough_full.pptx")

SLIDE_W  = Inches(13.33)   # 16:9 widescreen
SLIDE_H  = Inches(7.5)

BG_RGB   = RGBColor(0x0d, 0x11, 0x17)
TXT_RGB  = RGBColor(0xe6, 0xed, 0xf3)
ACC_RGB  = RGBColor(0x7e, 0x3a, 0xf2)
MUT_RGB  = RGBColor(0x8b, 0x94, 0x9e)


def strip_html(text):
    """Remove HTML tags and decode entities, preserving paragraph breaks."""
    # <br> and <br/> → newline
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # <p> / </p> → newline
    text = re.sub(r'</?p[^>]*>', '\n', text, flags=re.IGNORECASE)
    # Remove all other tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html_lib.unescape(text)
    # Collapse 3+ newlines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def load_stages():
    with open(SRC_HTML, encoding='utf-8') as f:
        src = f.read()
    m = re.search(r'const STAGES = (\[)', src)
    start = m.start(1)
    depth = 0
    for i, c in enumerate(src[start:]):
        if c == '[':   depth += 1
        elif c == ']': depth -= 1
        if depth == 0:
            end = start + i + 1
            break
    return json.loads(src[start:end])


def b64_to_pil(b64_str):
    data = base64.b64decode(b64_str)
    return Image.open(io.BytesIO(data)).convert("RGB")


def add_notes(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text
    for para in tf.paragraphs:
        for run in para.runs:
            run.font.size = Pt(11)


def build_pptx(stages):
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    blank_layout = prs.slide_layouts[6]   # completely blank

    # Title-bar height and image area
    TITLE_H   = Inches(0.52)
    IMG_TOP   = TITLE_H
    IMG_H     = SLIDE_H - TITLE_H

    for s in stages:
        slide = prs.slides.add_slide(blank_layout)

        # ── Dark background ───────────────────────────────────────────────
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_RGB

        # ── Title bar (full width) ────────────────────────────────────────
        title_box = slide.shapes.add_textbox(
            Inches(0), Inches(0), SLIDE_W, TITLE_H)
        tf = title_box.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT

        # step_num in accent colour
        run_num = p.add_run()
        run_num.text = s["step_num"] + "  "
        run_num.font.size  = Pt(13)
        run_num.font.bold  = True
        run_num.font.color.rgb = ACC_RGB
        run_num.font.name  = "Segoe UI"

        # title in light colour
        run_title = p.add_run()
        run_title.text = s["title"]
        run_title.font.size  = Pt(13)
        run_title.font.bold  = True
        run_title.font.color.rgb = TXT_RGB
        run_title.font.name  = "Segoe UI"

        # Tint the title bar background
        txBox_fill = title_box.fill
        txBox_fill.solid()
        txBox_fill.fore_color.rgb = RGBColor(0x16, 0x1b, 0x22)

        # Left accent stripe
        stripe = slide.shapes.add_shape(
            1,   # MSO_SHAPE_TYPE.RECTANGLE
            Inches(0), Inches(0), Inches(0.04), TITLE_H)
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = ACC_RGB
        stripe.line.fill.background()

        # ── Embedded image ────────────────────────────────────────────────
        pil_img = b64_to_pil(s["img"])
        img_buf = io.BytesIO()
        pil_img.save(img_buf, format="PNG")
        img_buf.seek(0)

        slide.shapes.add_picture(
            img_buf,
            Inches(0), IMG_TOP,
            width=SLIDE_W, height=IMG_H)

        # ── Speaker notes ─────────────────────────────────────────────────
        plain_script = strip_html(s["script"])
        add_notes(slide, plain_script)

    prs.save(OUT_PPTX)
    size_kb = os.path.getsize(OUT_PPTX) // 1024
    print(f"Saved → {OUT_PPTX}  ({size_kb} KB, {len(stages)} slides)")


if __name__ == "__main__":
    print("Loading stages from HTML...")
    stages = load_stages()
    print(f"  {len(stages)} stages found")
    print("Building PPTX...")
    build_pptx(stages)
