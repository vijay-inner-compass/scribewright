#!/usr/bin/env python3
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
import argparse
import json
from html import escape

PW, PH, ML, MT, MB, GAP = 190, 190, 34, 46, 34, 26


def scale(v, lo, hi, a, b):
    return a + (v - lo) / (hi - lo) * (b - a)


def clip_line(a, b, c, x0, x1, y0, y1):
    """Segment of a*x + b*y + c = 0 inside the box, or None."""
    pts = []
    if abs(b) > 1e-12:
        for x in (x0, x1):
            y = -(a * x + c) / b
            if y0 - 1e-9 <= y <= y1 + 1e-9:
                pts.append((x, y))
    if abs(a) > 1e-12:
        for y in (y0, y1):
            x = -(b * y + c) / a
            if x0 - 1e-9 <= x <= x1 + 1e-9:
                pts.append((x, y))
    pts = sorted(set((round(x, 9), round(y, 9)) for x, y in pts))
    return (pts[0], pts[-1]) if len(pts) >= 2 else None


def panel_svg(p, ox):
    x0, x1 = p.get("xlim", [0, 1])
    y0, y1 = p.get("ylim", [0, 1])
    L, T, R, B = ox + ML, MT, ox + ML + PW, MT + PH
    o = [f'<text class="ptitle" x="{(L + R) / 2}" y="{MT - 12}">{escape(p.get("title", ""))}</text>',
         f'<rect class="axis" x="{L}" y="{T}" width="{PW}" height="{PH}"/>']
    for v in (x0, (x0 + x1) / 2, x1):
        px = scale(v, x0, x1, L, R)
        o.append(f'<text class="tick" x="{px}" y="{B + 12}">{v:g}</text>')
    for v in (y0, (y0 + y1) / 2, y1):
        py = scale(v, y0, y1, B, T)
        o.append(f'<text class="tick" x="{L - 5}" y="{py + 3}" style="text-anchor:end">{v:g}</text>')
    if p.get("xlabel"):
        o.append(f'<text class="axlabel" x="{(L + R) / 2}" y="{B + 25}">{escape(p["xlabel"])}</text>')
    if p.get("ylabel"):
        o.append(f'<text class="axlabel" x="{L - 26}" y="{(T + B) / 2}" transform="rotate(-90 {L - 26} {(T + B) / 2})">{escape(p["ylabel"])}</text>')
    for ln in p.get("lines", []):
        seg = clip_line(ln["a"], ln["b"], ln["c"], x0, x1, y0, y1)
        if seg:
            (ax, ay), (bx, by) = seg
            o.append(f'<line class="ln {ln.get("style", "")}" x1="{scale(ax, x0, x1, L, R)}" y1="{scale(ay, y0, y1, B, T)}" '
                     f'x2="{scale(bx, x0, x1, L, R)}" y2="{scale(by, y0, y1, B, T)}"/>')
    for pt in p.get("points", []):
        px, py = scale(pt["x"], x0, x1, L, R), scale(pt["y"], y0, y1, B, T)
        o.append(f'<circle class="pt c{pt.get("class", 0)}" cx="{px}" cy="{py}" r="7"/>')
        if "label" in pt:
            o.append(f'<text class="ptlabel" x="{px}" y="{py + 3.5}">{escape(str(pt["label"]))}</text>')
    if p.get("note"):
        o.append(f'<text class="note" x="{(L + R) / 2}" y="{B + 36}">{escape(p["note"])}</text>')
    return o


def bars(spec):
    n = len(spec["bars"])
    W, rowh = 660, 34
    H = 40 + n * rowh
    mx = spec.get("max") or max(b["value"] for b in spec["bars"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
         f'<text class="ptitle" x="{W / 2}" y="18">{escape(spec.get("title", ""))}</text>']
    for i, b in enumerate(spec["bars"]):
        y = 34 + i * rowh
        w = scale(b["value"], 0, mx, 0, 300)
        o.append(f'<text class="axlabel" x="262" y="{y + 15}" style="text-anchor:end">{escape(b["label"])}</text>')
        o.append(f'<rect class="bar {b.get("style", "")}" x="272" y="{y}" width="{max(w, 1.5)}" height="22" rx="3"/>')
        o.append(f'<text class="tick" x="{278 + w}" y="{y + 15}" style="text-anchor:start">{escape(b.get("text", str(b["value"])))}</text>')
    o.append("</svg>")
    return "\n".join(o)


def lines(spec):
    W, H, L, R, T, B = 560, 260, 52, 540, 30, 220
    allp = [pt for s in spec["series"] for pt in s["points"]]
    xs, ys = [p[0] for p in allp], [p[1] for p in allp]
    x0, x1 = spec.get("xlim", [min(xs), max(xs)])
    y0, y1 = spec.get("ylim", [min(0, min(ys)), max(ys)])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
         f'<text class="ptitle" x="{W / 2}" y="16">{escape(spec.get("title", ""))}</text>',
         f'<rect class="axis" x="{L}" y="{T}" width="{R - L}" height="{B - T}"/>']
    for v in (x0, (x0 + x1) / 2, x1):
        o.append(f'<text class="tick" x="{scale(v, x0, x1, L, R)}" y="{B + 13}">{v:g}</text>')
    for v in (y0, (y0 + y1) / 2, y1):
        o.append(f'<text class="tick" x="{L - 5}" y="{scale(v, y0, y1, B, T) + 3}" style="text-anchor:end">{v:g}</text>')
    o.append(f'<text class="axlabel" x="{(L + R) / 2}" y="{B + 32}">{escape(spec.get("xlabel", ""))}</text>')
    o.append(f'<text class="axlabel" x="14" y="{(T + B) / 2}" transform="rotate(-90 14 {(T + B) / 2})">{escape(spec.get("ylabel", ""))}</text>')
    for s in spec["series"]:
        d = " ".join(f"{'M' if i == 0 else 'L'}{scale(px, x0, x1, L, R):.1f},{scale(py, y0, y1, B, T):.1f}" for i, (px, py) in enumerate(s["points"]))
        o.append(f'<path class="ln {s.get("style", "")}" d="{d}"/>')
        lx, ly = s["points"][-1]
        o.append(f'<text class="note" x="{scale(lx, x0, x1, L, R) - 4:.1f}" y="{scale(ly, y0, y1, B, T) - 6:.1f}" style="text-anchor:end">{escape(s.get("name", ""))}</text>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    kind = spec.get("kind", "panels")
    if kind == "bars":
        svg = bars(spec)
    elif kind == "line":
        svg = lines(spec)
    else:
        panels = spec["panels"]
        W = len(panels) * (ML + PW + GAP) + 6
        H = MT + PH + MB + 18
        body = []
        for i, p in enumerate(panels):
            body += panel_svg(p, i * (ML + PW + GAP))
        title = f'<text class="ptitle" x="{W / 2}" y="12">{escape(spec["title"])}</text>' if spec.get("title") else ""
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">{title}\n' + "\n".join(body) + "\n</svg>"
    open(a.out, "w", encoding="utf-8").write(svg)
    print(f"Wrote {a.out} ({kind})")


if __name__ == "__main__":
    main()
