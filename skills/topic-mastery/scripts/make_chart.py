#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
"""Draw small, accurate charts as inline SVG from a JSON spec (no libraries needed).

Why: figures that are computed from the same numbers as the text cannot disagree with it, and
vector charts stay sharp in the PDF and follow the document colours (classes in learning.css).

Spec (one panel, or several side by side in "panels"):
{
  "title": "optional overall title",
  "panels": [{
    "title": "AND after epoch 6",
    "xlim": [-0.5, 1.5], "ylim": [-0.5, 1.5], "xlabel": "x1", "ylabel": "x2",
    "points": [{"x":0,"y":0,"class":0,"label":"0"}, {"x":1,"y":1,"class":1}],
    "lines":  [{"a":2,"b":1,"c":-2,"label":"2x1 + x2 - 2 = 0","style":"ok|bad"}],   # a*x + b*y + c = 0
    "note": "0 mistakes"
  }]
}
Other chart kinds: {"kind":"bars","title":..,"bars":[{"label":"Accuracy","value":99,"style":"ok|bad","text":"99%"}],"max":100}
                   {"kind":"line","title":..,"xlabel":..,"ylabel":..,"series":[{"name":..,"points":[[x,y],..],"style":"ok|bad"}]}
Usage:  python make_chart.py spec.json -o chart.svg
"""
# argparse: command-line options. json: reads the spec file. escape: makes text safe inside SVG/XML.
import argparse
import json
from html import escape

# Layout constants, in SVG units. PW/PH: plot width and height. ML: left margin.
# MT: top margin. MB: bottom margin. GAP: space between side-by-side panels.
PW, PH, ML, MT, MB, GAP = 190, 190, 34, 46, 34, 26


def scale(v, lo, hi, a, b):
    """Map v from the range [lo, hi] onto the range [a, b] (a linear map).

    Example: scale(5, 0, 10, 0, 100) gives 50. It is used to turn data values into pixel positions.
    """
    return a + (v - lo) / (hi - lo) * (b - a)


def clip_line(a, b, c, x0, x1, y0, y1):
    """Segment of a*x + b*y + c = 0 inside the box, or None."""
    pts = []  # points where the line crosses the box edges
    # If b is not (nearly) zero, the line is not vertical. Solve for y at the left and right edges.
    # 1e-12 is a tiny tolerance that stands in for zero, to avoid dividing by a rounding error.
    if abs(b) > 1e-12:
        for x in (x0, x1):
            y = -(a * x + c) / b  # from a*x + b*y + c = 0, solve for y
            if y0 - 1e-9 <= y <= y1 + 1e-9:  # keep it only if it falls inside the box's vertical range
                pts.append((x, y))
    # If a is not (nearly) zero, the line is not horizontal. Solve for x at the bottom and top edges.
    if abs(a) > 1e-12:
        for y in (y0, y1):
            x = -(b * y + c) / a  # from a*x + b*y + c = 0, solve for x
            if x0 - 1e-9 <= x <= x1 + 1e-9:
                pts.append((x, y))
    # Remove duplicates (a corner can be found twice) and round, so equal points compare equal.
    pts = sorted(set((round(x, 9), round(y, 9)) for x, y in pts))
    # A line through the box has exactly two crossing points: its start and end. Fewer means no segment.
    return (pts[0], pts[-1]) if len(pts) >= 2 else None


def panel_svg(p, ox):
    """Return the SVG pieces for one scatter-style panel, placed at horizontal offset ox."""
    x0, x1 = p.get("xlim", [0, 1])  # data range along x
    y0, y1 = p.get("ylim", [0, 1])  # data range along y
    # L, T, R, B: the left, top, right and bottom edges of the plot box in SVG coordinates.
    L, T, R, B = ox + ML, MT, ox + ML + PW, MT + PH
    # Panel title above the box, then the box itself (class "axis" styles it in learning.css).
    o = [f'<text class="ptitle" x="{(L + R) / 2}" y="{MT - 12}">{escape(p.get("title", ""))}</text>',
         f'<rect class="axis" x="{L}" y="{T}" width="{PW}" height="{PH}"/>']
    # Tick labels along the x axis: the two ends and the middle value. {v:g} prints a short number.
    for v in (x0, (x0 + x1) / 2, x1):
        px = scale(v, x0, x1, L, R)
        o.append(f'<text class="tick" x="{px}" y="{B + 12}">{v:g}</text>')
    # Tick labels along the y axis. SVG's y grows downward, so the range is mapped from B (bottom) to T (top).
    for v in (y0, (y0 + y1) / 2, y1):
        py = scale(v, y0, y1, B, T)
        o.append(f'<text class="tick" x="{L - 5}" y="{py + 3}" style="text-anchor:end">{v:g}</text>')
    if p.get("xlabel"):  # axis label under the x axis, if the spec gives one
        o.append(f'<text class="axlabel" x="{(L + R) / 2}" y="{B + 25}">{escape(p["xlabel"])}</text>')
    if p.get("ylabel"):  # axis label beside the y axis, rotated to run up the side
        o.append(f'<text class="axlabel" x="{L - 26}" y="{(T + B) / 2}" transform="rotate(-90 {L - 26} {(T + B) / 2})">{escape(p["ylabel"])}</text>')
    # Draw each line. clip_line gives the visible part; lines that miss the box are skipped.
    for ln in p.get("lines", []):
        seg = clip_line(ln["a"], ln["b"], ln["c"], x0, x1, y0, y1)
        if seg:
            (ax, ay), (bx, by) = seg  # the two end points of the visible segment
            # The style (for example "ok" or "bad") is added as a CSS class so colours come from the stylesheet.
            o.append(f'<line class="ln {ln.get("style", "")}" x1="{scale(ax, x0, x1, L, R)}" y1="{scale(ay, y0, y1, B, T)}" '
                     f'x2="{scale(bx, x0, x1, L, R)}" y2="{scale(by, y0, y1, B, T)}"/>')
    # Draw each point as a circle. The "c{class}" CSS class picks the colour (c0, c1, ...).
    for pt in p.get("points", []):
        px, py = scale(pt["x"], x0, x1, L, R), scale(pt["y"], y0, y1, B, T)
        o.append(f'<circle class="pt c{pt.get("class", 0)}" cx="{px}" cy="{py}" r="7"/>')
        if "label" in pt:  # optional text centred on the point
            o.append(f'<text class="ptlabel" x="{px}" y="{py + 3.5}">{escape(str(pt["label"]))}</text>')
    if p.get("note"):  # a short note under the panel
        o.append(f'<text class="note" x="{(L + R) / 2}" y="{B + 36}">{escape(p["note"])}</text>')
    return o  # the list of SVG strings; the caller joins them


def bars(spec):
    """Return a complete SVG for a horizontal bar chart."""
    n = len(spec["bars"])  # number of bars
    W, rowh = 660, 34  # total width, and the height of each row
    H = 40 + n * rowh  # total height grows with the number of bars
    # The largest value sets the scale. spec["max"] overrides it when given (for example 100 for percentages).
    mx = spec.get("max") or max(b["value"] for b in spec["bars"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
         f'<text class="ptitle" x="{W / 2}" y="18">{escape(spec.get("title", ""))}</text>']
    for i, b in enumerate(spec["bars"]):
        y = 34 + i * rowh  # top edge of this row
        w = scale(b["value"], 0, mx, 0, 300)  # bar length: 0 to 300 units for 0 to the maximum
        # Label to the left of the bar, right-aligned at x=262.
        o.append(f'<text class="axlabel" x="262" y="{y + 15}" style="text-anchor:end">{escape(b["label"])}</text>')
        # The bar itself, starting at x=272. max(w, 1.5) keeps very small values visible.
        o.append(f'<rect class="bar {b.get("style", "")}" x="272" y="{y}" width="{max(w, 1.5)}" height="22" rx="3"/>')
        # Value text just past the end of the bar. Uses the spec's text if given, else the raw value.
        o.append(f'<text class="tick" x="{278 + w}" y="{y + 15}" style="text-anchor:start">{escape(b.get("text", str(b["value"])))}</text>')
    o.append("</svg>")
    return "\n".join(o)


def lines(spec):
    """Return a complete SVG for a line chart with one or more series."""
    # W, H: the whole SVG size. L, R, T, B: the plot box edges. The plot sits inside the SVG with room for labels.
    W, H, L, R, T, B = 560, 260, 52, 540, 30, 220
    # allp: every point of every series, flattened, used to work out the axis ranges.
    allp = [pt for s in spec["series"] for pt in s["points"]]
    xs, ys = [p[0] for p in allp], [p[1] for p in allp]  # separate lists of the x and y values
    # Axis ranges: use the spec's xlim and ylim if given, otherwise fit the data.
    # The y range starts at 0 or lower, so a line chart of positive values starts at zero.
    x0, x1 = spec.get("xlim", [min(xs), max(xs)])
    y0, y1 = spec.get("ylim", [min(0, min(ys)), max(ys)])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
         f'<text class="ptitle" x="{W / 2}" y="16">{escape(spec.get("title", ""))}</text>',
         f'<rect class="axis" x="{L}" y="{T}" width="{R - L}" height="{B - T}"/>']
    # Tick labels: the two ends and the middle of each axis.
    for v in (x0, (x0 + x1) / 2, x1):
        o.append(f'<text class="tick" x="{scale(v, x0, x1, L, R)}" y="{B + 13}">{v:g}</text>')
    for v in (y0, (y0 + y1) / 2, y1):
        o.append(f'<text class="tick" x="{L - 5}" y="{scale(v, y0, y1, B, T) + 3}" style="text-anchor:end">{v:g}</text>')
    o.append(f'<text class="axlabel" x="{(L + R) / 2}" y="{B + 32}">{escape(spec.get("xlabel", ""))}</text>')
    # The y label is rotated 90 degrees so it runs up the left side.
    o.append(f'<text class="axlabel" x="14" y="{(T + B) / 2}" transform="rotate(-90 14 {(T + B) / 2})">{escape(spec.get("ylabel", ""))}</text>')
    for s in spec["series"]:
        # Build an SVG path "M x,y L x,y ..." : M moves to the first point, L draws a line to each later point.
        # .1f keeps one decimal place so the path stays short.
        d = " ".join(f"{'M' if i == 0 else 'L'}{scale(px, x0, x1, L, R):.1f},{scale(py, y0, y1, B, T):.1f}" for i, (px, py) in enumerate(s["points"]))
        o.append(f'<path class="ln {s.get("style", "")}" d="{d}"/>')
        # Label the series at its last point, just above and to the left of that point.
        lx, ly = s["points"][-1]
        o.append(f'<text class="note" x="{scale(lx, x0, x1, L, R) - 4:.1f}" y="{scale(ly, y0, y1, B, T) - 6:.1f}" style="text-anchor:end">{escape(s.get("name", ""))}</text>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    """Read the spec, pick the chart kind, build the SVG, and write it to the output file."""
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")  # the JSON spec file
    ap.add_argument("-o", "--out", required=True)  # the SVG file to write
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))  # read the spec into a Python dictionary
    kind = spec.get("kind", "panels")  # "panels" is the default kind when none is given
    if kind == "bars":
        svg = bars(spec)
    elif kind == "line":
        svg = lines(spec)
    else:
        # Scatter-style charts: one or more panels side by side.
        panels = spec["panels"]
        # Total width: one slot per panel (margin + plot + gap), plus a small border.
        W = len(panels) * (ML + PW + GAP) + 6
        H = MT + PH + MB + 18  # total height
        body = []
        for i, p in enumerate(panels):
            body += panel_svg(p, i * (ML + PW + GAP))  # each panel starts one slot further right
        # The overall title is optional. An empty string means "no title".
        title = f'<text class="ptitle" x="{W / 2}" y="12">{escape(spec["title"])}</text>' if spec.get("title") else ""
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">{title}\n' + "\n".join(body) + "\n</svg>"
    open(a.out, "w", encoding="utf-8").write(svg)  # write the finished SVG to disk
    print(f"Wrote {a.out} ({kind})")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
