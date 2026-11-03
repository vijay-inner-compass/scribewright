#!/usr/bin/env python3
"""Lint a learning document (body fragment or built HTML) before rendering.

Checks, because these are the failures that make a learning resource untrustworthy:
  1. every citation (<a class="cite">S12</a> or <sup class="cite">S12</sup>) has a matching source entry
     (<li id="S12"> inside ol.refs), and every listed source is cited at least once
  2. evidence labels are used (Established / Interpretation / Assumption / Prediction / Gap) and
     reported by count, so a document with no labels is caught
  3. code blocks declare data-lang (python, csharp, ...), long ones are flagged for review
  4. placeholder text (TODO, lorem, TBD, XXX, [citation needed]) and em dashes
  5. optional --expect-sections "a,b,c": each phrase appears in some h1/h2 heading

Usage:
    python check_doc.py doc.html [--expect-sections "History,Foundations,..."]
Exit code 1 if any error; warnings do not fail.
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cites, self.sources, self.ev, self.code_no_lang = [], [], [], 0
        self.headings, self._h, self._cite, self._ev, self._text = [], None, False, None, []
        self.code_blocks = []
        self._code = None
        self.sections, self._sec, self._in_refs, self._skip = {}, "(front matter)", False, 0
        self._prose = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag in ("h1", "h2"):
            self._h = []
        if tag == "ol" and "refs" in cls:
            self._in_refs = True
        if tag in ("pre", "script", "style", "svg"):
            self._skip += 1
        if "cite" in cls and tag in ("a", "sup"):
            self._cite = True
        if tag == "li" and a.get("id", "").startswith("S"):
            self.sources.append(a["id"])
        if tag == "span" and "ev" in cls:
            self._ev = next((c for c in cls if c in ("est", "int", "ass", "pre", "gap")), "?")
            self.ev.append(self._ev)
        if tag == "pre" and "code" in cls:
            if not a.get("data-lang") and "out" not in cls:
                self.code_no_lang += 1
            self._code = []

    def handle_endtag(self, tag):
        if tag in ("pre", "script", "style", "svg") and self._skip:
            self._skip -= 1
        if tag == "ol":
            self._in_refs = False
        if tag in ("h1", "h2") and self._h is not None:
            title = "".join(self._h).strip()
            self.headings.append(title)
            self._sec = f"{tag}:{title}"
            self.sections.setdefault(self._sec, 0)
            self._h = None
        if tag in ("a", "sup"):
            self._cite = False
        if tag == "pre" and self._code is not None:
            self.code_blocks.append("".join(self._code))
            self._code = None

    def handle_data(self, d):
        self._text.append(d)
        if not self._skip:
            self._prose.append(d)
        if not self._skip and not self._in_refs and self._h is None:
            self.sections[self._sec] = self.sections.get(self._sec, 0) + len(d.split())
        if self._h is not None:
            self._h.append(d)
        if self._cite:
            self.cites += re.findall(r"S\d+", d)
        if self._code is not None:
            self._code.append(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--expect-sections", default="")
    ap.add_argument("--allow-no-sources", action="store_true", help="for body fragments without a sources list")
    ap.add_argument("--min-words-per-h2", type=int, default=0,
                    help="elaboration standard: every h2 section (code and references excluded) needs at least this many words")
    ap.add_argument("--min-total-words", type=int, default=0, help="minimum words across the document body")
    ap.add_argument("--words", action="store_true", help="print the word count of every section")
    a = ap.parse_args()
    raw = Path(a.html).read_text(encoding="utf-8")
    p = P()
    p.feed(raw)
    errors, warns = [], []

    cited, listed = set(p.cites), set(p.sources)
    if not a.allow_no_sources:
        for c in sorted(cited - listed, key=lambda s: int(s[1:])):
            errors.append(f"citation {c} has no source entry")
        for s in sorted(listed - cited, key=lambda s: int(s[1:])):
            warns.append(f"source {s} is listed but never cited")
        if not listed:
            errors.append("no sources list found (ol.refs with li id=S1...)")
    if not p.ev:
        errors.append("no evidence labels (span.ev est/int/ass/pre/gap) found")
    if p.code_no_lang:
        errors.append(f"{p.code_no_lang} code block(s) without data-lang")
    for i, b in enumerate(p.code_blocks, 1):
        if len(b.splitlines()) > 70:
            warns.append(f"code block {i} has {len(b.splitlines())} lines; consider splitting or adding class long")

    text = " ".join(p._prose)   # prose only, so TODO comments inside starter code do not trip the placeholder check
    for pat in (r"\bTODO\b", r"lorem ipsum", r"\bTBD\b", r"\bXXX\b", r"\[citation needed\]"):
        if re.search(pat, text, re.I):
            errors.append(f"placeholder text matches /{pat}/")
    if "—" in text:
        warns.append(f"{text.count(chr(0x2014))} em dash(es) in text; the house style avoids them")

    for ph in [s.strip() for s in a.expect_sections.split(",") if s.strip()]:
        if not any(ph.lower() in h.lower() for h in p.headings):
            errors.append(f"expected a heading containing '{ph}'")

    total_words = sum(p.sections.values())
    if a.min_total_words and total_words < a.min_total_words:
        errors.append(f"document has {total_words} words of explanation; the elaboration standard asks for {a.min_total_words}+")
    if a.min_words_per_h2:
        for k, n in p.sections.items():
            if k.startswith("h2:") and n < a.min_words_per_h2:
                errors.append(f"section '{k[3:]}' has {n} words; needs {a.min_words_per_h2}+ (explain more: why, how, worked example, pitfalls)")
    if a.words:
        for k, n in p.sections.items():
            print(f"  {n:>6} words  {k}")
    print(f"Explanation words (excluding code and references): {total_words}")

    from collections import Counter
    c = Counter(p.ev)
    print(f"Headings: {len(p.headings)} | citations: {len(p.cites)} ({len(cited)} distinct) | sources: {len(listed)}")
    print("Evidence labels: " + ", ".join(f"{k}={c.get(k, 0)}" for k in ("est", "int", "ass", "pre", "gap")))
    print(f"Code blocks: {len(p.code_blocks)}")
    for w in warns:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    if errors:
        sys.exit(1)
    print("Check passed.")


if __name__ == "__main__":
    main()
