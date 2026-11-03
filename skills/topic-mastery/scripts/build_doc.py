#!/usr/bin/env python3
"""Wrap a body fragment in the learning-document shell (CSS inlined, running header/footer).

Why: you write only the content (body.html); the shell, page rules and colour tokens stay
identical across the roadmap and every chapter, so the set looks like one product.

Usage:
    python build_doc.py body.html -o doc.html --title "Neural Networks: Roadmap" \
        --running "Neural Networks | Learning Roadmap" --footer "Organisation or author"

In the body, `<!--svg:file.svg-->` is replaced by that file's contents (path relative to
body.html), which is how make_diagram.py output is embedded.
"""
import argparse
import html
import re
from pathlib import Path

SCRIPT = """<script>
/* used by render_pdf.py: flags content wider than the page (code, tables, diagrams) */
window.addEventListener('load',function(){
  document.querySelectorAll('pre,table,figure,svg').forEach(function(e){
    if(e.scrollWidth>e.clientWidth+2){e.setAttribute('data-overflow-x','true');}
  });
});
</script>"""


def css_str(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


LABELS = {"E": ("est", "Established"), "I": ("int", "Interpretation"), "A": ("ass", "Assumption"),
          "P": ("pre", "Prediction"), "G": ("gap", "Gap")}


def expand_shorthand(body):
    """[S12] or [S12, S13] -> citation links; {E} {I} {A} {P} {G} -> evidence labels.
    Text inside <pre> blocks is left alone so code is never rewritten."""
    parts = re.split(r"(<pre\b.*?</pre>)", body, flags=re.S | re.I)

    def cite(m):
        return '<sup class="cite">,</sup>'.join(f'<a class="cite" href="#{s}">{s}</a>' for s in re.findall(r"S\d+", m.group(1)))

    for i, p in enumerate(parts):
        if i % 2 == 1:
            continue
        p = re.sub(r"\[(S\d+(?:\s*,\s*S\d+)*)\]", cite, p)
        p = re.sub(r"\{([EIAPG])\}", lambda m: f'<span class="ev {LABELS[m.group(1)][0]}">{LABELS[m.group(1)][1]}</span>', p)
        parts[i] = p
    return "".join(parts)


def refs_html(body, sources_path):
    """Build <ol class="refs"> for exactly the S-ids cited in the body, from the ledger."""
    import json
    ledger = {s["id"]: s for s in json.loads(Path(sources_path).read_text(encoding="utf-8"))}
    cited = sorted(set(re.findall(r'class="cite"[^>]*>\s*(S\d+)\s*<', body)), key=lambda x: int(x[1:]))
    out = ['<ol class="refs">']
    for sid in cited:
        s = ledger.get(sid)
        if not s:
            out.append(f'<li id="{sid}"><span class="id">{sid}</span><b>UNKNOWN SOURCE</b></li>')
            continue
        note = html.escape((s.get("notes") or "")[:170])
        who = html.escape(s.get("publisher") or s.get("author_or_publisher") or "")
        out.append(
            f'<li id="{sid}"><span class="id">{sid}</span><b>{html.escape(s["title"])}</b>, {who}. '
            f'<code>{html.escape(s["url"])}</code> <span class="tier">Tier {s.get("tier", "?")}</span> '
            f'<span class="why">Published {html.escape(str(s.get("published", "undated")))}; accessed '
            f'{html.escape(str(s.get("accessed", "")))}. {note}</span></li>')
    out.append("</ol>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", help="sources.json ledger; replaces <!--refs--> with the cited sources")
    ap.add_argument("body")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--running", default="")
    ap.add_argument("--footer", default="")
    ap.add_argument("--css", default=str(Path(__file__).resolve().parent.parent / "assets" / "learning.css"))
    a = ap.parse_args()

    body_path = Path(a.body)
    body = body_path.read_text(encoding="utf-8")

    def inc(m):
        p = body_path.parent / m.group(1).strip()
        return p.read_text(encoding="utf-8")

    body = re.sub(r"<!--svg:(.*?)-->", inc, body)
    body = expand_shorthand(body)
    # repeat table header rows on every page: wrap a leading all-th row in <thead>
    body = re.sub(r"(<table[^>]*>\s*(?:<caption>.*?</caption>\s*)?)(<tr>\s*<th.*?</tr>)",
                  lambda m: m.group(1) + "<thead>" + m.group(2) + "</thead>", body, flags=re.S)
    if a.sources and "<!--refs-->" in body:
        body = body.replace("<!--refs-->", refs_html(body, a.sources))
    css = Path(a.css).read_text(encoding="utf-8")
    page = (
        "@page{size:A4;margin:20mm 16mm 20mm;"
        f'@top-left{{content:"{css_str(a.running)}";font:8pt Segoe UI,Arial,sans-serif;color:#64748B}}'
        f'@bottom-left{{content:"{css_str(a.footer)}";font:8pt Segoe UI,Arial,sans-serif;color:#64748B}}'
        '@bottom-right{content:counter(page);font:8pt Segoe UI,Arial,sans-serif;color:#64748B}}'
        "@page:first{@top-left{content:none}@bottom-left{content:none}@bottom-right{content:none}}"
    )
    doc = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{html.escape(a.title)}</title><style>{css}\n{page}</style></head>"
        f"<body><main>\n{body}\n</main>{SCRIPT}</body></html>"
    )
    Path(a.out).write_text(doc, encoding="utf-8")
    print(f"Wrote {a.out} ({len(doc)//1024} KB)")


if __name__ == "__main__":
    main()
