#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
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
# argparse: command-line options. re: regular expressions. sys: sys.exit() for the exit code.
import argparse
import re
import sys
# HTMLParser: a standard-library class that reads HTML one tag at a time and calls our methods.
from html.parser import HTMLParser
# Path: reads the document file.
from pathlib import Path


class P(HTMLParser):
    """Walks the HTML and records what the checks need: citations, sources, headings, code and word counts."""

    def __init__(self):
        super().__init__()  # set up the HTMLParser base class
        # cites: S-ids found in citation text. sources: ids of reference <li> entries.
        # ev: the evidence class of every label found. code_no_lang: code blocks missing data-lang.
        self.cites, self.sources, self.ev, self.code_no_lang = [], [], [], 0
        # headings: text of every h1/h2. _h: text of the heading being read (None when not in one).
        # _cite: True while inside a citation tag. _ev: class of the label being read.
        # _text: all text seen (not used by the checks but kept for debugging).
        self.headings, self._h, self._cite, self._ev, self._text = [], None, False, None, []
        self.code_blocks = []  # full text of every <pre class="code"> block
        self._code = None  # collects the text of the code block being read (None outside one)
        # sections: word count per "h1:Title" / "h2:Title". _sec: the section currently being read.
        # _in_refs: True inside the reference list. _skip: nesting depth of tags whose text is not prose.
        self.sections, self._sec, self._in_refs, self._skip = {}, "(front matter)", False, 0
        self._prose = []  # text that counts as prose: no code, scripts, styles or SVG

    def handle_starttag(self, tag, attrs):
        """Called by HTMLParser for every opening tag, such as <h2 class="x">."""
        a = dict(attrs)  # the attributes as a dictionary, e.g. a["class"]
        cls = (a.get("class") or "").split()  # the class names as a list
        if tag in ("h1", "h2"):
            self._h = []  # start collecting the heading text
        if tag == "ol" and "refs" in cls:
            self._in_refs = True  # the reference list starts here
        if tag in ("pre", "script", "style", "svg"):
            self._skip += 1  # entering non-prose content; the counter allows nesting
        if "cite" in cls and tag in ("a", "sup"):
            self._cite = True  # the text that follows is a citation
        # A reference entry looks like <li id="S3">. Its id is recorded as a listed source.
        if tag == "li" and a.get("id", "").startswith("S"):
            self.sources.append(a["id"])
        # Evidence spans look like <span class="ev est">. Record which class (est, int, ...) it has.
        # The generator picks the first matching class name, or "?" if none matches.
        if tag == "span" and "ev" in cls:
            self._ev = next((c for c in cls if c in ("est", "int", "ass", "pre", "gap")), "?")
            self.ev.append(self._ev)
        if tag == "pre" and "code" in cls:
            # Code blocks must declare their language. "out" marks an output-only block that needs no language.
            if not a.get("data-lang") and "out" not in cls:
                self.code_no_lang += 1
            self._code = []  # start collecting this code block's text

    def handle_endtag(self, tag):
        """Called for every closing tag, such as </h2>."""
        if tag in ("pre", "script", "style", "svg") and self._skip:
            self._skip -= 1  # leaving non-prose content
        if tag == "ol":
            self._in_refs = False  # the reference list has ended
        if tag in ("h1", "h2") and self._h is not None:
            title = "".join(self._h).strip()  # join the pieces of the heading text
            self.headings.append(title)
            self._sec = f"{tag}:{title}"  # the section key, for example "h2:Foundations"
            self.sections.setdefault(self._sec, 0)  # start a word count for this section
            self._h = None  # stop collecting heading text
        if tag in ("a", "sup"):
            self._cite = False  # the citation text has ended
        if tag == "pre" and self._code is not None:
            self.code_blocks.append("".join(self._code))  # store the whole code block
            self._code = None

    def handle_data(self, d):
        """Called for every run of text between tags. d is the raw text."""
        self._text.append(d)
        if not self._skip:
            self._prose.append(d)  # keep only prose text for the placeholder and dash checks
        # Count words for the current section, but not inside code, scripts, headings or references.
        if not self._skip and not self._in_refs and self._h is None:
            self.sections[self._sec] = self.sections.get(self._sec, 0) + len(d.split())
        if self._h is not None:
            self._h.append(d)  # add this text to the heading being read
        if self._cite:
            # Pull out S-ids such as S12 from the citation text.
            self.cites += re.findall(r"S\d+", d)
        if self._code is not None:
            self._code.append(d)  # add this text to the code block being read


def main():
    """Parse the command-line options, run every check, print a report, and exit 1 on errors."""
    ap = argparse.ArgumentParser()
    ap.add_argument("html")  # the document to check
    # --expect-sections: comma-separated phrases that must appear in some heading.
    ap.add_argument("--expect-sections", default="")
    # --allow-no-sources: skip the citation and reference checks (for body fragments).
    ap.add_argument("--allow-no-sources", action="store_true", help="for body fragments without a sources list")
    # --min-words-per-h2: every h2 section must reach this word count.
    ap.add_argument("--min-words-per-h2", type=int, default=0,
                    help="elaboration standard: every h2 section (code and references excluded) needs at least this many words")
    # --min-total-words: the whole document must reach this word count.
    ap.add_argument("--min-total-words", type=int, default=0, help="minimum words across the document body")
    # --words: print the word count of each section.
    ap.add_argument("--words", action="store_true", help="print the word count of every section")
    a = ap.parse_args()
    raw = Path(a.html).read_text(encoding="utf-8")  # the whole file as one string
    p = P()  # create the parser
    p.feed(raw)  # run it over the document; this fills in all of p's lists and counts
    # errors stop the build (exit 1). warns are printed but do not fail the check.
    errors, warns = [], []

    # cited: S-ids used in the text. listed: S-ids that have a reference entry.
    cited, listed = set(p.cites), set(p.sources)
    if not a.allow_no_sources:
        # Every citation must match a reference entry. sorted(..., key=...) orders them by number.
        for c in sorted(cited - listed, key=lambda s: int(s[1:])):
            errors.append(f"citation {c} has no source entry")
        # A listed source that is never cited is only a warning: it is untidy, not wrong.
        for s in sorted(listed - cited, key=lambda s: int(s[1:])):
            warns.append(f"source {s} is listed but never cited")
        if not listed:
            errors.append("no sources list found (ol.refs with li id=S1...)")
    if not p.ev:
        # A document with no evidence labels is not following the house standard.
        errors.append("no evidence labels (span.ev est/int/ass/pre/gap) found")
    if p.code_no_lang:
        errors.append(f"{p.code_no_lang} code block(s) without data-lang")
    # Long code blocks (over 70 lines) are a warning, to suggest splitting them.
    # enumerate(..., 1) numbers the blocks from 1 for the message.
    for i, b in enumerate(p.code_blocks, 1):
        if len(b.splitlines()) > 70:
            warns.append(f"code block {i} has {len(b.splitlines())} lines; consider splitting or adding class long")

    # Check the prose only, so TODO comments inside starter code do not trip the placeholder check.
    text = " ".join(p._prose)
    # Placeholder patterns that must not appear in a finished document. \b = word boundary;
    # re.I = ignore case. The last pattern matches the literal text [citation needed].
    for pat in (r"\bTODO\b", r"lorem ipsum", r"\bTBD\b", r"\bXXX\b", r"\[citation needed\]"):
        if re.search(pat, text, re.I):
            errors.append(f"placeholder text matches /{pat}/")
    # The house style avoids em dashes (the long dash character). chr(0x2014) is that character.
    if "—" in text:
        warns.append(f"{text.count(chr(0x2014))} em dash(es) in text; the house style avoids them")

    # Every phrase given to --expect-sections must appear in some heading (case-insensitive).
    for ph in [s.strip() for s in a.expect_sections.split(",") if s.strip()]:
        if not any(ph.lower() in h.lower() for h in p.headings):
            errors.append(f"expected a heading containing '{ph}'")

    # Word-count checks for the elaboration standard.
    total_words = sum(p.sections.values())
    if a.min_total_words and total_words < a.min_total_words:
        errors.append(f"document has {total_words} words of explanation; the elaboration standard asks for {a.min_total_words}+")
    if a.min_words_per_h2:
        for k, n in p.sections.items():
            # k[3:] strips the "h2:" prefix so the message shows only the heading text.
            if k.startswith("h2:") and n < a.min_words_per_h2:
                errors.append(f"section '{k[3:]}' has {n} words; needs {a.min_words_per_h2}+ (explain more: why, how, worked example, pitfalls)")
    if a.words:
        for k, n in p.sections.items():
            print(f"  {n:>6} words  {k}")  # right-align the number in a 6-character column
    print(f"Explanation words (excluding code and references): {total_words}")

    from collections import Counter  # counts how many times each evidence class appears
    c = Counter(p.ev)  # for example Counter({"est": 4, "gap": 1})
    print(f"Headings: {len(p.headings)} | citations: {len(p.cites)} ({len(cited)} distinct) | sources: {len(listed)}")
    # Print the count for each evidence class, using 0 for any class that never appears.
    print("Evidence labels: " + ", ".join(f"{k}={c.get(k, 0)}" for k in ("est", "int", "ass", "pre", "gap")))
    print(f"Code blocks: {len(p.code_blocks)}")
    for w in warns:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    if errors:
        sys.exit(1)  # any error means the check failed
    print("Check passed.")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
