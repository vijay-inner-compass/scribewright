#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
"""Render a built learning document to PDF with headless Chrome/Edge and report problems.

Reports: page count, and any code block, table, figure or diagram wider than the page
(clipped content is the usual defect in long-form PDFs). Exit code 2 on overflow.

Usage:
    python render_pdf.py doc.html [-o doc.pdf]
"""
# argparse: command-line options. os: file checks. re: regular expressions.
# shutil: finds programs on PATH. subprocess: runs the browser. sys: sys.exit().
# tempfile: a temporary folder for the browser profile. Path: file paths.
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Known install locations of Chrome and Edge, used only when the program is not on PATH.
# r"..." makes backslashes literal, so Windows paths are not read as escape sequences.
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
    # First try common command names on PATH. shutil.which returns the full path, or None.
    for name in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    # Then try the known install folders.
    for p in CANDIDATES:
        if os.path.exists(p):
            return p
    # sys.exit with a string prints the message and exits with code 1.
    sys.exit("No Chrome/Edge/Chromium found. Install one or add it to PATH.")


def run(browser, args):
    """Run the browser headless with a fresh profile and the given extra arguments."""
    # A temporary profile folder means the browser does not reuse or change the user's own profile.
    # The folder is deleted automatically when the "with" block ends.
    with tempfile.TemporaryDirectory() as profile:
        return subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-sandbox",
                               f"--user-data-dir={profile}", *args],  # *args spreads the extra arguments in
                              capture_output=True, text=True, timeout=180)  # stop after 180 seconds


def main():
    """Read the document, print it to PDF, and report any content that is wider than the page."""
    ap = argparse.ArgumentParser()
    ap.add_argument("html")  # the document to render
    ap.add_argument("-o", "--out")  # optional PDF path; the default is the HTML name with .pdf
    a = ap.parse_args()
    html = Path(a.html).resolve()  # absolute path to the HTML file
    out = Path(a.out).resolve() if a.out else html.with_suffix(".pdf")  # with_suffix swaps .html for .pdf
    browser = find_browser()

    # Ask the browser for the rendered page text (the DOM) after a short wait for scripts to run.
    # --virtual-time-budget lets the page's load script finish before the DOM is printed.
    dom = run(browser, ["--virtual-time-budget=5000", "--dump-dom", html.as_uri()]).stdout
    # Remove comments so example markup inside them is not counted.
    dom = re.sub(r"<!--.*?-->", "", dom, flags=re.S)
    # Find elements that the page script has marked data-overflow-x="true" (see build_doc.py SCRIPT).
    wide = re.findall(r"<(pre|table|figure|svg)[^>]*data-overflow-x=\"true\"[^>]*>", dom)

    # Print the page to a PDF file. --no-pdf-header-footer removes the browser's own header and footer.
    run(browser, ["--no-pdf-header-footer", "--virtual-time-budget=5000", f"--print-to-pdf={out}", html.as_uri()])
    if not out.exists():
        sys.exit("PDF was not produced.")
    # Count the pages by searching the PDF's raw bytes for page objects. "/Type /Page" matches a page,
    # but "[^s]" skips "/Pages", which is the page-tree node rather than a page itself.
    pages = len(re.findall(rb"/Type\s*/Page[^s]", out.read_bytes()))
    # st_size is the file size in bytes; // 1024 converts it to whole kilobytes.
    print(f"Wrote {out} ({pages} page(s), {out.stat().st_size // 1024} KB)")
    if wide:
        # sorted(set(...)) removes duplicate tag names and sorts them for a stable message.
        print(f"OVERFLOW: {len(wide)} element(s) wider than the page ({', '.join(sorted(set(wide)))}). "
              "Shorten lines, split the table, or resize the diagram, then re-render.")
        sys.exit(2)  # exit code 2 means the PDF was made but has overflowing content
    print("Layout check: nothing wider than the page.")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
