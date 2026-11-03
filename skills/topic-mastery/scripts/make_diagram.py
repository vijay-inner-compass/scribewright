#!/usr/bin/env python3
"""Draw a layered left-to-right diagram (prerequisite map, architecture, workflow) as inline SVG.

Why: hand-written SVG coordinates are error prone; this lays nodes out by dependency depth so
a diagram can be generated from a list of nodes and edges, and styled by the document CSS.

Input JSON:
{
  "nodes": [{"id":"a","label":"Linear algebra","sub":"vectors, matrices","style":"hl|dk|"}],
  "edges": [["a","b"], ["b","c","optional edge label"]],
  "direction": "LR"            (LR default, or TB)
}
Usage:
    python make_diagram.py spec.json -o diagram.svg
Embed with <!--svg:diagram.svg--> in body.html (build_doc.py inlines it), inside a
<figure class="diagram"> with a figcaption and an "In words" description.
Edges that point backwards (cycles) are drawn dashed.
"""
import argparse
import json
import sys
import textwrap
from html import escape

W, H, GX, GY, PAD = 150, 46, 56, 18, 14


def layout(nodes, edges):
    ids = [n["id"] for n in nodes]
    out = {i: [] for i in ids}
    for e in edges:
        out[e[0]].append(e[1])
    level, state, back = {}, {}, set()

    def visit(n):  # DFS: depth = longest path from a source, ignoring back edges
        state[n] = 1
        level.setdefault(n, 0)
        for m in out[n]:
            if state.get(m) == 1:
                back.add((n, m))
                continue
            level[m] = max(level.get(m, 0), level[n] + 1)
            if state.get(m) != 2:
                visit(m)
        state[n] = 2

    indeg = {i: 0 for i in ids}
    for e in edges:
        indeg[e[1]] += 1
    for i in [x for x in ids if indeg[x] == 0] + ids:
        if state.get(i) != 2:
            visit(i)
    return level, back


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    global W, GX
    W, GX = spec.get("node_width", W), spec.get("gap_x", GX)   # compact boxes for wide flows
    wrap_at = max(10, int(W / 6.8))
    nodes, edges = spec["nodes"], spec.get("edges", [])
    known = {n["id"] for n in nodes}
    for e in edges:
        if e[0] not in known or e[1] not in known:
            sys.exit(f"edge {e} references an unknown node id")
    tb = spec.get("direction", "LR") == "TB"
    level, back = layout(nodes, edges)
    cols = {}
    for n in nodes:
        cols.setdefault(level[n["id"]], []).append(n["id"])
    pos = {}
    for lv, members in cols.items():
        for k, nid in enumerate(members):
            if tb:
                pos[nid] = (PAD + k * (W + GX), PAD + lv * (H + GY + 22))
            else:
                pos[nid] = (PAD + lv * (W + GX), PAD + k * (H + GY))
    width = max(x for x, _ in pos.values()) + W + PAD
    height = max(y for _, y in pos.values()) + H + PAD
    by = {n["id"]: n for n in nodes}
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
         '<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
         '<path d="M0,0 L8,4 L0,8 z" fill="#7B8CA3"/></marker></defs>']
    for e in edges:
        (x1, y1), (x2, y2) = pos[e[0]], pos[e[1]]
        if tb:
            sx, sy, ex, ey = x1 + W / 2, y1 + H, x2 + W / 2, y2
            d = f"M{sx},{sy} C{sx},{sy + 20} {ex},{ey - 20} {ex},{ey}"
        else:
            sx, sy, ex, ey = x1 + W, y1 + H / 2, x2, y2 + H / 2
            if (e[0], e[1]) in back:
                sx, sy, ex, ey = x1, y1 + H / 2, x2 + W, y2 + H / 2
            mx = (sx + ex) / 2
            d = f"M{sx},{sy} C{mx},{sy} {mx},{ey} {ex},{ey}"
        cls = "e back" if (e[0], e[1]) in back else "e"
        p.append(f'<path class="{cls}" d="{d}" marker-end="url(#ah)"/>')
        if len(e) > 2 and e[2]:
            p.append(f'<text class="elbl" x="{(sx + ex) / 2}" y="{(sy + ey) / 2 - 3}">{escape(e[2])}</text>')
    for n in nodes:
        x, y = pos[n["id"]]
        lines = textwrap.wrap(n["label"], wrap_at)[:2]
        sub = n.get("sub", "")
        cls = "n " + n.get("style", "")
        p.append(f'<g class="{cls.strip()}"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="5"/>')
        base = y + (17 if sub else 21) - (6 if len(lines) == 2 else 0)
        for i, ln in enumerate(lines):
            p.append(f'<text x="{x + W / 2}" y="{base + i * 13}">{escape(ln)}</text>')
        if sub:
            p.append(f'<text class="sub" x="{x + W / 2}" y="{y + H - 7}">{escape(sub[:int(W / 5)])}</text>')
        p.append("</g>")
    p.append("</svg>")
    open(a.out, "w", encoding="utf-8").write("\n".join(p))
    print(f"Wrote {a.out}: {len(nodes)} nodes, {len(edges)} edges, {len(cols)} levels")


if __name__ == "__main__":
    main()
