#!/usr/bin/env python3
"""Check that this machine can run the topic-mastery toolchain, and say exactly how to fix gaps.

Why: the skill depends on Python, a Chromium-based browser (for PDF), optionally the .NET SDK
(to run C# examples) and internet access (for research). Running this first turns a vague
mid-run failure into a clear to-do list.

Usage:  python doctor.py        (or python3 doctor.py)
Exit code 0 if all REQUIRED checks pass; optional gaps only warn.
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

OS =platform.system()
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

HINTS = {
    "browser": {"Windows": "Install Google Chrome or use the built-in Microsoft Edge (already on Windows 10/11).",
                "Darwin": "brew install --cask google-chrome   (or download Chrome from google.com/chrome)",
                "Linux": "sudo apt install chromium   (or: sudo dnf install chromium)"},
    "dotnet": {"Windows": "winget install Microsoft.DotNet.SDK.10   (or download from dotnet.microsoft.com/download)",
               "Darwin": "brew install --cask dotnet-sdk   (needs version 10 or newer)",
               "Linux": "See dotnet.microsoft.com/download for your distribution (needs version 10 or newer)"},
    "python": {"Windows": "winget install Python.Python.3.12", "Darwin": "brew install python", "Linux": "sudo apt install python3"},
}


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return f"ERR {e}"


def find_browser():
    for n in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        p = shutil.which(n)
        if p:
            return p
    return next((p for p in BROWSERS if os.path.exists(p)), None)


def main():
    rows, required_fail = [], False

    v = sys.version_info
    ok = v >= (3, 8)
    rows.append(("Python 3.8+", "OK" if ok else "FAIL", f"{v.major}.{v.minor}.{v.micro} ({sys.executable})", True))
    required_fail |= not ok
    if not shutil.which("python") and shutil.which("python3"):
        rows.append(("Command name", "NOTE", "'python' not found but 'python3' is: use python3 wherever the skill says python", False))

    b = find_browser()
    rows.append(("Chrome/Edge/Chromium (PDF)", "OK" if b else "FAIL", b or HINTS["browser"].get(OS, ""), True))
    required_fail |= not b

    d = shutil.which("dotnet")
    if d:
        ver = run([d, "--version"])
        m = re.match(r"(\d+)\.", ver)
        major = int(m.group(1)) if m else 0
        rows.append((".NET SDK 10+ (C# examples)", "OK" if major >= 10 else "WARN",
                     f"{ver}" + ("" if major >= 10 else "  file-based apps need 10+: " + HINTS["dotnet"].get(OS, "")), False))
    else:
        rows.append((".NET SDK 10+ (C# examples)", "WARN", "not found: " + HINTS["dotnet"].get(OS, "") +
                     "  (C# will be written but marked 'not executed')", False))

    try:
        urllib.request.urlopen(urllib.request.Request("https://www.wikipedia.org", method="HEAD"), timeout=8)
        rows.append(("Internet (research)", "OK", "reachable", False))
    except urllib.error.HTTPError as e:
        # any HTTP answer, even an error status, proves the network works
        rows.append(("Internet (research)", "OK", f"reachable (HTTP {e.code})", False))
    except Exception as e:  # noqa: BLE001
        rows.append(("Internet (research)", "WARN", f"not reachable ({type(e).__name__}); research needs web access", False))

    try:
        import warnings
        warnings.simplefilter("ignore")
        import fitz  # noqa: F401
        rows.append(("PyMuPDF (optional, page previews)", "OK", "installed", False))
    except ImportError:
        rows.append(("PyMuPDF (optional, page previews)", "NOTE", "pip install pymupdf  (only to preview PDF pages as images)", False))

    w = max(len(r[0]) for r in rows)
    print(f"topic-mastery environment check ({OS}, {platform.platform()})\n")
    for name, status, detail, req in rows:
        print(f"[{status:4}] {name:<{w}}  {detail}{'' if req else '   (optional)' if status != 'OK' else ''}")
    print()
    if required_fail:
        print("RESULT: fix the FAIL items above, then run this again.")
        sys.exit(1)
    print("RESULT: ready. Warnings only reduce features (C# execution, research, previews).")


if __name__ == "__main__":
    main()
