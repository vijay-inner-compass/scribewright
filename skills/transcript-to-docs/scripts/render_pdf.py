#!/usr/bin/env python3
"""Render a finished HTML document to PDF with headless Chrome/Edge and check
that no page overflows.

Why the overflow check: each .page is a fixed A4-landscape sheet. Content that
doesn't fit is silently clipped in the PDF, which is the most common defect in
this format, so it is reported here instead of being discovered by the reader.

Usage:
    python render_pdf.py doc.html [-o doc.pdf]

Exit code 2 means at least one page overflows (the PDF is still written).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def find_browser():
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    for p in CANDIDATES:
        if os.path.exists(p):
            return p
    sys.exit("No Chrome/Edge/Chromium found. Install one or add it to PATH.")


def run(browser, args):
    with tempfile.TemporaryDirectory() as profile:
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
               f"--user-data-dir={profile}", *args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    html = Path(a.html).resolve()
    out = Path(a.out).resolve() if a.out else html.with_suffix(".pdf")
    url = html.as_uri()
    browser = find_browser()

    # 1) layout check: the template's script marks overflowing pages in the DOM
    dom = run(browser, ["--virtual-time-budget=4000", "--dump-dom", url]).stdout
    # strip comments so example markup inside them is not counted as a page
    dom = re.sub(r"<!--.*?-->", "", dom, flags=re.S)
    pages = re.findall(r'<section[^>]*class="page[^"]*"[^>]*>', dom)
    bad = [i + 1 for i, tag in enumerate(pages) if 'data-overflow="true"' in tag]

    # 2) print
    run(browser, ["--no-pdf-header-footer", "--virtual-time-budget=4000",
                  f"--print-to-pdf={out}", url])
    if not out.exists():
        sys.exit("PDF was not produced.")

    print(f"Wrote {out} ({len(pages)} page(s))")
    if not pages:
        print("Warning: no <section class=\"page\"> found; is this built from the template?")
    if bad:
        print(f"OVERFLOW on page(s) {bad}: trim text or move content to another page, then re-render.")
        sys.exit(2)
    print("Layout check: all pages fit.")


if __name__ == "__main__":
    main()
