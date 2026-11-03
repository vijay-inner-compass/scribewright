#!/usr/bin/env python3
"""Render a built learning document to PDF with headless Chrome/Edge and report problems.

Reports: page count, and any code block, table, figure or diagram wider than the page
(clipped content is the usual defect in long-form PDFs). Exit code 2 on overflow.

Usage:
    python render_pdf.py doc.html [-o doc.pdf]
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
        return subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-sandbox",
                               f"--user-data-dir={profile}", *args],
                              capture_output=True, text=True, timeout=180)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    html = Path(a.html).resolve()
    out = Path(a.out).resolve() if a.out else html.with_suffix(".pdf")
    browser = find_browser()

    dom = run(browser, ["--virtual-time-budget=5000", "--dump-dom", html.as_uri()]).stdout
    dom = re.sub(r"<!--.*?-->", "", dom, flags=re.S)
    wide = re.findall(r"<(pre|table|figure|svg)[^>]*data-overflow-x=\"true\"[^>]*>", dom)

    run(browser, ["--no-pdf-header-footer", "--virtual-time-budget=5000", f"--print-to-pdf={out}", html.as_uri()])
    if not out.exists():
        sys.exit("PDF was not produced.")
    pages = len(re.findall(rb"/Type\s*/Page[^s]", out.read_bytes()))
    print(f"Wrote {out} ({pages} page(s), {out.stat().st_size // 1024} KB)")
    if wide:
        print(f"OVERFLOW: {len(wide)} element(s) wider than the page ({', '.join(sorted(set(wide)))}). "
              "Shorten lines, split the table, or resize the diagram, then re-render.")
        sys.exit(2)
    print("Layout check: nothing wider than the page.")


if __name__ == "__main__":
    main()
