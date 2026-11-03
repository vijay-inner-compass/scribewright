#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
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
# argparse: command-line options. json: reads the spec. sys: sys.exit() for error messages.
# textwrap: breaks long labels over several lines. escape: makes text safe inside SVG.
import argparse
import json
import sys
import textwrap
from html import escape

# Default sizes, in SVG units. W, H: the width and height of one node box.
# GX, GY: gaps between boxes horizontally and vertically. PAD: margin around the whole diagram.
W, H, GX, GY, PAD = 150, 46, 56, 18, 14


def layout(nodes, edges):
    """Work out each node's column (its depth) and which edges point backwards.

    Returns (level, back): level maps node id to its column number, and back is the set of
    edges that close a loop (cycles), which are drawn differently.
    """
    ids = [n["id"] for n in nodes]  # every node id
    out = {i: [] for i in ids}  # out[a] = list of nodes that a points to
    for e in edges:
        out[e[0]].append(e[1])
    level, state, back = {}, {}, set()  # level: depth of each node. state: 0 = unvisited, 1 = on the stack, 2 = done

    def visit(n):  # DFS: depth = longest path from a source, ignoring back edges
        state[n] = 1  # mark n as on the current path
        level.setdefault(n, 0)  # a node reached first gets depth 0 unless a longer path sets it later
        for m in out[n]:
            if state.get(m) == 1:
                # m is still on the current path, so the edge n -> m closes a cycle: record it as "back".
                back.add((n, m))
                continue
            # Depth of m is at least one more than n; keep the largest value found (longest path).
            level[m] = max(level.get(m, 0), level[n] + 1)
            if state.get(m) != 2:  # visit m unless it is already finished
                visit(m)
        state[n] = 2  # n and everything reachable from it are finished

    indeg = {i: 0 for i in ids}  # number of arrows pointing into each node
    for e in edges:
        indeg[e[1]] += 1
    # Start from nodes with no incoming arrows (true sources) first, then from any node left over (cycles).
    for i in [x for x in ids if indeg[x] == 0] + ids:
        if state.get(i) != 2:  # skip nodes already finished
            visit(i)
    return level, back


def main():
    """Read the spec, lay out the nodes, draw the boxes and arrows, and write the SVG."""
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")  # the JSON spec file
    ap.add_argument("-o", "--out", required=True)  # the SVG file to write
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    # "global" lets this function change the module-level W and GX that the other functions read.
    # spec may set a narrower node width or a smaller horizontal gap for wide flows.
    global W, GX
    W, GX = spec.get("node_width", W), spec.get("gap_x", GX)   # compact boxes for wide flows
    # Characters per line for label wrapping: scales with the box width, never less than 10.
    wrap_at = max(10, int(W / 6.8))
    nodes, edges = spec["nodes"], spec.get("edges", [])
    known = {n["id"] for n in nodes}  # set of valid node ids
    for e in edges:
        # Stop early with a clear message if an edge points at a node that does not exist.
        if e[0] not in known or e[1] not in known:
            sys.exit(f"edge {e} references an unknown node id")
    tb = spec.get("direction", "LR") == "TB"  # True for top-to-bottom, False for left-to-right
    level, back = layout(nodes, edges)  # column of each node, and the backward edges
    cols = {}  # cols[level] = list of node ids in that column
    for n in nodes:
        cols.setdefault(level[n["id"]], []).append(n["id"])
    pos = {}  # pos[node id] = (x, y) of the node's top-left corner
    for lv, members in cols.items():
        for k, nid in enumerate(members):  # k is the node's position within its column
            if tb:
                # Top-to-bottom: levels go down the page, nodes in a level go across. 22 extra units leave room for edge labels.
                pos[nid] = (PAD + k * (W + GX), PAD + lv * (H + GY + 22))
            else:
                # Left-to-right: levels go across the page, nodes in a level stack down.
                pos[nid] = (PAD + lv * (W + GX), PAD + k * (H + GY))
    # The SVG size is the furthest node edge plus the padding.
    width = max(x for x, _ in pos.values()) + W + PAD
    height = max(y for _, y in pos.values()) + H + PAD
    by = {n["id"]: n for n in nodes}  # look up a node's record by its id
    # Open the SVG and define the arrowhead marker (a small triangle) that edges reference by id "ah".
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
         '<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
         '<path d="M0,0 L8,4 L0,8 z" fill="#7B8CA3"/></marker></defs>']
    for e in edges:
        (x1, y1), (x2, y2) = pos[e[0]], pos[e[1]]  # top-left corners of the two nodes
        if tb:
            # Leave from the bottom centre of the source and enter the top centre of the target.
            # The curve's control points make a smooth S-shape.
            sx, sy, ex, ey = x1 + W / 2, y1 + H, x2 + W / 2, y2
            d = f"M{sx},{sy} C{sx},{sy + 20} {ex},{ey - 20} {ex},{ey}"
        else:
            # Leave from the right edge of the source and enter the left edge of the target.
            sx, sy, ex, ey = x1 + W, y1 + H / 2, x2, y2 + H / 2
            if (e[0], e[1]) in back:
                # A backward edge runs from the left of the source to the right of the target, so it curves back.
                sx, sy, ex, ey = x1, y1 + H / 2, x2 + W, y2 + H / 2
            mx = (sx + ex) / 2  # the horizontal midpoint, used for the curve's control points
            d = f"M{sx},{sy} C{mx},{sy} {mx},{ey} {ex},{ey}"
        # Backward edges get the "back" class, which the stylesheet draws dashed.
        cls = "e back" if (e[0], e[1]) in back else "e"
        p.append(f'<path class="{cls}" d="{d}" marker-end="url(#ah)"/>')  # marker-end puts the arrowhead at the target
        if len(e) > 2 and e[2]:  # an optional third item is a label for the edge
            p.append(f'<text class="elbl" x="{(sx + ex) / 2}" y="{(sy + ey) / 2 - 3}">{escape(e[2])}</text>')
    for n in nodes:
        x, y = pos[n["id"]]
        # Wrap the label into at most two lines of wrap_at characters each.
        lines = textwrap.wrap(n["label"], wrap_at)[:2]
        sub = n.get("sub", "")  # optional smaller text under the label
        cls = "n " + n.get("style", "")  # the style (for example "hl") becomes a CSS class
        # A group holds the box and its text, so the stylesheet can colour them together.
        p.append(f'<g class="{cls.strip()}"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="5"/>')
        # Place the first text line. It sits higher when there is a sub-line or when the label wraps to two lines.
        base = y + (17 if sub else 21) - (6 if len(lines) == 2 else 0)
        for i, ln in enumerate(lines):
            p.append(f'<text x="{x + W / 2}" y="{base + i * 13}">{escape(ln)}</text>')  # centred horizontally
        if sub:  # sub-line near the bottom of the box, cut to a length that fits
            p.append(f'<text class="sub" x="{x + W / 2}" y="{y + H - 7}">{escape(sub[:int(W / 5)])}</text>')
        p.append("</g>")
    p.append("</svg>")
    open(a.out, "w", encoding="utf-8").write("\n".join(p))  # join the pieces and write the file
    print(f"Wrote {a.out}: {len(nodes)} nodes, {len(edges)} edges, {len(cols)} levels")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
