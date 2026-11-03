#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
"""Wrap a body fragment in the learning-document shell (CSS inlined, running header/footer).

Why: you write only the content (body.html); the shell, page rules and colour tokens stay
identical across the roadmap and every chapter, so the set looks like one product.

Usage:
    python build_doc.py body.html -o doc.html --title "Neural Networks: Roadmap" \
        --running "Neural Networks | Learning Roadmap" --footer "Organisation or author"

In the body, `<!--svg:file.svg-->` is replaced by that file's contents (path relative to
body.html), which is how make_diagram.py output is embedded.
"""
# argparse: reads command-line options such as -o and --title.
import argparse
# html: html.escape() turns <, >, & and quotes into safe entities for use in HTML text.
import html
# re: regular expressions, used to find and replace citations, evidence labels and SVG markers.
import re
# Path: an object-oriented way to read and write files and to work with folder paths.
from pathlib import Path

# SCRIPT is a block of JavaScript added at the end of every page. It is a Python string,
# so its contents are kept exactly as written; only this comment explains it.
# The script runs in the browser when the page loads. It marks any <pre>, <table>, <figure> or
# <svg> element that is wider than its box, so render_pdf.py can report content that would be
# clipped in the PDF.
SCRIPT = """<script>
/* used by render_pdf.py: flags content wider than the page (code, tables, diagrams) */
window.addEventListener('load',function(){
  document.querySelectorAll('pre,table,figure,svg').forEach(function(e){
    if(e.scrollWidth>e.clientWidth+2){e.setAttribute('data-overflow-x','true');}
  });
});
</script>"""


def css_str(s):
    """Escape a string so it can sit inside a CSS double-quoted string, such as content:"...".

    Backslashes are doubled first, then double quotes get a backslash in front.
    """
    return s.replace("\\", "\\\\").replace('"', '\\"')


# Maps each evidence code to (CSS class suffix, label shown to the reader).
# E = Established, I = Interpretation, A = Assumption, P = Prediction, G = Gap.
LABELS = {"E": ("est", "Established"), "I": ("int", "Interpretation"), "A": ("ass", "Assumption"),
          "P": ("pre", "Prediction"), "G": ("gap", "Gap")}


def expand_shorthand(body):
    """[S12] or [S12, S13] -> citation links; {E} {I} {A} {P} {G} -> evidence labels.
    Text inside <pre> blocks is left alone so code is never rewritten."""
    # re.split with a capture group keeps the <pre>...</pre> blocks in the result list.
    # Blocks sit at odd indexes (1, 3, 5, ...); plain text sits at even indexes (0, 2, 4, ...).
    # re.S lets "." match newlines; re.I ignores case in the tag name.
    parts = re.split(r"(<pre\b.*?</pre>)", body, flags=re.S | re.I)

    def cite(m):
        # m.group(1) is the bracketed text, e.g. "S12, S13". For each S-id found,
        # build a link to the reference list entry with the same id.
        # Multiple links are separated by a small superscript comma.
        return '<sup class="cite">,</sup>'.join(f'<a class="cite" href="#{s}">{s}</a>' for s in re.findall(r"S\d+", m.group(1)))

    for i, p in enumerate(parts):
        if i % 2 == 1:  # odd index = a <pre> block, which must never be changed
            continue
        # Replace [S1], [S2, S3] style citations with links.
        p = re.sub(r"\[(S\d+(?:\s*,\s*S\d+)*)\]", cite, p)
        # Replace {E}, {I}, ... with a styled span. The lambda reads the matched letter
        # and looks up its class and label in LABELS.
        p = re.sub(r"\{([EIAPG])\}", lambda m: f'<span class="ev {LABELS[m.group(1)][0]}">{LABELS[m.group(1)][1]}</span>', p)
        parts[i] = p  # store the changed text back in the list
    return "".join(parts)  # join all pieces into one string again


def refs_html(body, sources_path):
    """Build <ol class="refs"> for exactly the S-ids cited in the body, from the ledger."""
    # Imported here, not at the top, because only this function needs it.
    import json
    # Read the source ledger (a JSON list) and index it by id, so ledger["S3"] is that source.
    ledger = {s["id"]: s for s in json.loads(Path(sources_path).read_text(encoding="utf-8"))}
    # Find every S-id that appears inside a citation link in the body. set() removes duplicates;
    # sorted() orders them numerically (S2 before S10) by comparing the number after the S.
    cited = sorted(set(re.findall(r'class="cite"[^>]*>\s*(S\d+)\s*<', body)), key=lambda x: int(x[1:]))
    out = ['<ol class="refs">']  # start the reference list
    for sid in cited:
        s = ledger.get(sid)  # the source record, or None if the id is not in the ledger
        if not s:
            # A cited id with no ledger entry is written as a visible error, so it cannot pass unnoticed.
            out.append(f'<li id="{sid}"><span class="id">{sid}</span><b>UNKNOWN SOURCE</b></li>')
            continue
        # The note is cut to 170 characters and escaped. "or ''" handles a missing or null field.
        note = html.escape((s.get("notes") or "")[:170])
        # Prefer the publisher; fall back to author_or_publisher if the publisher is missing.
        who = html.escape(s.get("publisher") or s.get("author_or_publisher") or "")
        # One reference entry: id, title, publisher, URL, tier, and publication and access dates.
        out.append(
            f'<li id="{sid}"><span class="id">{sid}</span><b>{html.escape(s["title"])}</b>, {who}. '
            f'<code>{html.escape(s["url"])}</code> <span class="tier">Tier {s.get("tier", "?")}</span> '
            f'<span class="why">Published {html.escape(str(s.get("published", "undated")))}; accessed '
            f'{html.escape(str(s.get("accessed", "")))}. {note}</span></li>')
    out.append("</ol>")  # close the list
    return "\n".join(out)  # one string with a line break between items


def main():
    """Read the command-line options, assemble the page, and write the HTML file."""
    ap = argparse.ArgumentParser()  # creates the option parser
    # --sources is optional: a ledger file used to build the reference list.
    ap.add_argument("--sources", help="sources.json ledger; replaces <!--refs--> with the cited sources")
    ap.add_argument("body")  # positional argument: the input body.html file
    ap.add_argument("-o", "--out", required=True)  # where to write the finished HTML
    ap.add_argument("--title", required=True)  # text for the browser tab, <title>
    ap.add_argument("--running", default="")  # text for the top-left running header on each page
    ap.add_argument("--footer", default="")  # text for the bottom-left footer on each page
    # Default CSS path: ../assets/learning.css, found relative to this script file.
    ap.add_argument("--css", default=str(Path(__file__).resolve().parent.parent / "assets" / "learning.css"))
    a = ap.parse_args()  # reads sys.argv and returns the values as attributes: a.body, a.out and so on

    body_path = Path(a.body)  # keep the path so relative includes can be resolved from its folder
    body = body_path.read_text(encoding="utf-8")

    def inc(m):
        # Read the file named in <!--svg:file.svg--> from the same folder as body.html.
        # m.group(1).strip() removes spaces around the file name.
        p = body_path.parent / m.group(1).strip()
        return p.read_text(encoding="utf-8")

    # Replace every <!--svg:...--> marker with the file's contents. The .*? lazy match stops at the first -->.
    body = re.sub(r"<!--svg:(.*?)-->", inc, body)
    body = expand_shorthand(body)  # turn [S1] and {E} shorthand into HTML
    # repeat table header rows on every page: wrap a leading all-th row in <thead>
    # so the browser repeats the header row when a table runs over a page break.
    body = re.sub(r"(<table[^>]*>\s*(?:<caption>.*?</caption>\s*)?)(<tr>\s*<th.*?</tr>)",
                  lambda m: m.group(1) + "<thead>" + m.group(2) + "</thead>", body, flags=re.S)
    # Fill the reference list only if a ledger was given and the page asks for one.
    if a.sources and "<!--refs-->" in body:
        body = body.replace("<!--refs-->", refs_html(body, a.sources))
    css = Path(a.css).read_text(encoding="utf-8")  # the shared stylesheet
    # The @page rules set the printed page: A4 size, margins, header, footer and page number.
    # The first page drops the header and footer (the cover does not need them).
    page = (
        "@page{size:A4;margin:20mm 16mm 20mm;"
        f'@top-left{{content:"{css_str(a.running)}";font:8pt Segoe UI,Arial,sans-serif;color:#64748B}}'
        f'@bottom-left{{content:"{css_str(a.footer)}";font:8pt Segoe UI,Arial,sans-serif;color:#64748B}}'
        '@bottom-right{content:counter(page);font:8pt Segoe UI,Arial,sans-serif;color:#64748B}}'
        "@page:first{@top-left{content:none}@bottom-left{content:none}@bottom-right{content:none}}"
    )
    # Assemble the full HTML document: doctype, language, charset, viewport, title, the CSS
    # (shared stylesheet plus the page rules), the body inside <main>, and the overflow script.
    doc = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{html.escape(a.title)}</title><style>{css}\n{page}</style></head>"
        f"<body><main>\n{body}\n</main>{SCRIPT}</body></html>"
    )
    Path(a.out).write_text(doc, encoding="utf-8")  # save the file
    # len(doc)//1024 converts characters to whole kilobytes for the message.
    print(f"Wrote {a.out} ({len(doc)//1024} KB)")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
