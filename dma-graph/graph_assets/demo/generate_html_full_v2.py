"""
Rebuild the full click-through HTML with a side-by-side layout:
  image on the left (~65 % width) · script panel on the right (~35 % width)
Reads the existing slide4_clickthrough_full.html for all stage data
(no re-rendering needed).
Output: slide4_clickthrough_full_v2.html
"""

import json, re, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_HTML   = os.path.join(SCRIPT_DIR, "slide4_clickthrough_full.html")
OUT_HTML   = os.path.join(SCRIPT_DIR, "slide4_clickthrough_full_v2.html")


def load_stages(src):
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
    padding: 20px 16px 36px;
  }

  /* ── Header ── */
  .header {
    width: 100%;
    max-width: 1400px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .header-title {
    font-size: 12px;
    color: var(--muted);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .step-counter {
    font-size: 12px;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }

  /* ── Stage title bar ── */
  .stage-bar {
    width: 100%;
    max-width: 1400px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .stage-num {
    font-size: 16px;
    color: var(--accent);
    min-width: 36px;
  }
  .stage-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
  }

  /* ── Main content: image left, script right ── */
  .main-content {
    width: 100%;
    max-width: 1400px;
    display: flex;
    gap: 14px;
    align-items: stretch;
    margin-bottom: 14px;
  }

  /* ── Image ── */
  .img-wrap {
    flex: 0 0 64%;
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    align-items: center;
  }
  .img-wrap img {
    width: 100%;
    display: block;
  }

  /* ── Script panel ── */
  .script-panel {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 16px 18px;
    font-size: 13px;
    line-height: 1.8;
    color: #c9d1d9;
    overflow-y: auto;
    max-height: 600px;
  }
  .script-panel b  { color: var(--text); }
  .script-panel em { color: var(--gold); font-style: normal; }
  .script-panel code {
    background: #1c2333;
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 11.5px;
    color: #79c0ff;
    font-family: "Cascadia Code", "Consolas", monospace;
  }

  /* ── Navigation ── */
  .nav {
    width: 100%;
    max-width: 1400px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
  .btn {
    padding: 8px 26px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
    user-select: none;
  }
  .btn:hover { background: #21262d; border-color: #8b949e; }
  .btn:disabled { opacity: 0.3; cursor: default; }
  .btn.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
  .btn.primary:hover { background: #6d28d9; border-color: #6d28d9; }

  /* ── Progress dots ── */
  .dots {
    display: flex;
    gap: 6px;
    align-items: center;
    flex-wrap: wrap;
    justify-content: center;
    max-width: 700px;
  }
  .dot {
    width: 9px; height: 9px;
    border-radius: 50%;
    background: var(--border);
    cursor: pointer;
    transition: background 0.15s, transform 0.15s;
  }
  .dot.active { background: var(--accent); transform: scale(1.35); }
  .dot:hover  { background: var(--muted); }

  /* ── Keyboard hint ── */
  .kbd-hint {
    font-size: 11px;
    color: var(--muted);
    margin-top: 10px;
  }
  kbd {
    display: inline-block;
    padding: 1px 5px;
    font-size: 10px;
    border: 1px solid var(--border);
    border-radius: 3px;
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
  <span class="stage-num"  id="step-num"></span>
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
    with open(SRC_HTML, encoding="utf-8") as f:
        src = f.read()

    stages = load_stages(src)
    print(f"Loaded {len(stages)} stages from source HTML")

    stages_json = json.dumps(stages, ensure_ascii=False)
    total       = len(stages)

    html = (HTML_TEMPLATE
            .replace("{n}", str(total))
            .replace("{stages_json}", stages_json))

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUT_HTML) // 1024
    print(f"Saved → {OUT_HTML}  ({size_kb} KB, {total} stages)")


if __name__ == "__main__":
    main()
