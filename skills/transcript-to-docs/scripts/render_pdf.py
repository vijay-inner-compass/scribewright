#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
"""Render a finished HTML document to PDF with headless Chrome/Edge and check
that no page overflows.

Why the overflow check: each .page is a fixed A4-landscape sheet. Content that
doesn't fit is silently clipped in the PDF, which is the most common defect in
this format, so it is reported here instead of being discovered by the reader.

Usage:
    python render_pdf.py doc.html [-o doc.pdf]

Exit code 2 means at least one page overflows (the PDF is still written).
"""
# argparse: command-line options. os: file checks. re: regular expressions.
# shutil: finds programs on PATH. subprocess: runs the browser. sys: exit codes and messages.
# tempfile: a temporary browser profile folder. Path: file paths.
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Known install locations of Chrome and Edge, used only when the program is not on PATH.
# r"..." keeps the backslashes in Windows paths as written.
CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # Chrome, 64-bit Windows
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",  # Chrome, 32-bit install
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",  # Edge, ships with Windows
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",  # Edge, alternative folder
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Chrome on macOS
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",  # Edge on macOS
]


def find_browser():
    """Return the path to a Chromium-based browser, or exit with a message if none is found."""
    # Try common command names on PATH first.
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    # Then try the known install folders.
    for p in CANDIDATES:
        if os.path.exists(p):
            return p
    sys.exit("No Chrome/Edge/Chromium found. Install one or add it to PATH.")


def run(browser, args):
    """Run the browser headless with a fresh temporary profile and the given extra arguments."""
    # The profile folder is deleted when the "with" block ends, so no browser state is left behind.
    with tempfile.TemporaryDirectory() as profile:
        # --headless=new runs without a window; --disable-gpu and --no-sandbox make it work on
        # machines without a GPU or with restricted sandboxes; *args adds the task-specific options.
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
               f"--user-data-dir={profile}", *args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # give up after 120 seconds


def main():
    """Check the layout of the document, then print it to PDF."""
    ap = argparse.ArgumentParser()
    ap.add_argument("html")  # the document to render
    ap.add_argument("-o", "--out")  # optional PDF path

    a = ap.parse_args()

    html = Path(a.html).resolve()  # absolute path to the HTML file
    out = Path(a.out).resolve() if a.out else html.with_suffix(".pdf")  # default: same name, .pdf
    url = html.as_uri()  # a file:// address the browser can open
    browser = find_browser()

    # 1) layout check: the template's script marks overflowing pages in the DOM
    # Ask the browser for the page's final HTML after its scripts have run (--dump-dom).
    dom = run(browser, ["--virtual-time-budget=4000", "--dump-dom", url]).stdout
    # strip comments so example markup inside them is not counted as a page
    dom = re.sub(r"<!--.*?-->", "", dom, flags=re.S)
    # Find every opening <section class="page ..."> tag, in order.
    pages = re.findall(r'<section[^>]*class="page[^"]*"[^>]*>', dom)
    # Page numbers (counted from 1) of the sections the template script marked as overflowing.
    bad = [i + 1 for i, tag in enumerate(pages) if 'data-overflow="true"' in tag]

    # 2) print: write the PDF with the browser's own print engine.
    run(browser, ["--no-pdf-header-footer", "--virtual-time-budget=4000",
                  f"--print-to-pdf={out}", url])
    if not out.exists():
        sys.exit("PDF was not produced.")

    print(f"Wrote {out} ({len(pages)} page(s))")
    if not pages:
        # No page sections means the document was not built from the template, so the check cannot run.
        print("Warning: no <section class=\"page\"> found; is this built from the template?")
    if bad:
        print(f"OVERFLOW on page(s) {bad}: trim text or move content to another page, then re-render.")
        sys.exit(2)  # the PDF exists, but it has clipped content
    print("Layout check: all pages fit.")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
