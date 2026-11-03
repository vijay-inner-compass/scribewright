#!/usr/bin/env python3
# The line above is a "shebang": when the file is run directly on macOS or Linux, it tells the
# shell to use the first python3 found on PATH. On Windows it is ignored and `python` is used.
"""Check that this machine can run the topic-mastery toolchain, and say exactly how to fix gaps.

Why: the skill depends on Python, a Chromium-based browser (for PDF), optionally the .NET SDK
(to run C# examples) and internet access (for research). Running this first turns a vague
mid-run failure into a clear to-do list.

Usage:  python doctor.py        (or python3 doctor.py)
Exit code 0 if all REQUIRED checks pass; optional gaps only warn.
"""
# Standard-library imports only, so the check runs before any optional package is installed.
import os  # file-system checks, such as whether a browser path exists
import platform  # tells us the operating system (Windows, Darwin for macOS, Linux)
import re  # regular expressions, used to read the .NET version number
import shutil  # shutil.which() finds a program on PATH; also used to look up commands
import subprocess  # runs external commands such as `dotnet --version`
import sys  # interpreter version and path, and sys.exit() for the final exit code
import urllib.error  # the exception type raised for HTTP error responses
import urllib.request  # makes the internet reachability request

# Module-level constant: the operating system name, e.g. "Windows", "Darwin" or "Linux".
# Used as the key into HINTS so the install advice matches the machine.
OS =platform.system()

# Known install locations of Chromium-based browsers. Used only if the browser is not on PATH.
# The r"..." prefix makes backslashes literal, so "\P" in a Windows path is not read as an escape.
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # Chrome, 64-bit Windows install
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",  # Chrome, 32-bit install on 64-bit Windows
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",  # Edge ships with Windows 10 and 11
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",  # Edge, alternative install folder
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Chrome on macOS
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",  # Edge on macOS
]

# Install advice per tool and per operating system. The outer key is the tool, the inner key is
# the OS name from platform.system(). Each value is a short command or instruction for the user.
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
    """Run a command and return its combined stdout and stderr as one stripped string."""
    try:
        # capture_output=True collects the output instead of printing it; text=True returns str, not bytes;
        # timeout=30 stops a command that hangs and raises subprocess.TimeoutExpired.
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001  (the comment tells linters the broad catch is deliberate)
        # Any failure (missing program, timeout, permission error) becomes a readable string
        # instead of crashing the whole check.
        return f"ERR {e}"


def find_browser():
    """Return the path of a Chromium-based browser, or None if none is found."""
    # First look for common command names on PATH. shutil.which returns the full path or None.
    for n in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        p = shutil.which(n)
        if p:  # the first name found wins
            return p
    # Fall back to the known install folders. next() returns the first existing path,
    # or None when the generator is empty.
    return next((p for p in BROWSERS if os.path.exists(p)), None)


def main():
    """Run every check, print a table of results, and exit with 1 if a required check failed."""
    # rows collects (name, status, detail, required) tuples for the printed table.
    # required_fail becomes True as soon as a required check fails.
    rows, required_fail = [], False

    # --- Check 1: Python version (required) ---
    v = sys.version_info  # a named tuple: major, minor, micro, ...
    ok = v >= (3, 8)  # tuple comparison: (3, 9, 1) >= (3, 8) is True
    rows.append(("Python 3.8+", "OK" if ok else "FAIL", f"{v.major}.{v.minor}.{v.micro} ({sys.executable})", True))
    required_fail |= not ok  # |= sets required_fail to True if this check failed; it never resets it
    # Note only: some systems have python3 but no plain `python` command, so the skill's advice needs adjusting.
    if not shutil.which("python") and shutil.which("python3"):
        rows.append(("Command name", "NOTE", "'python' not found but 'python3' is: use python3 wherever the skill says python", False))

    # --- Check 2: a Chromium-based browser for PDF output (required) ---
    b = find_browser()
    rows.append(("Chrome/Edge/Chromium (PDF)", "OK" if b else "FAIL", b or HINTS["browser"].get(OS, ""), True))
    required_fail |= not b  # a missing browser means no PDF can be made

    # --- Check 3: .NET SDK version (optional, only warns) ---
    d = shutil.which("dotnet")  # path to the dotnet program, or None
    if d:
        ver = run([d, "--version"])  # for example "10.0.100"
        m = re.match(r"(\d+)\.", ver)  # captures the major version number before the first dot
        major = int(m.group(1)) if m else 0  # 0 if the output did not look like a version
        rows.append((".NET SDK 10+ (C# examples)", "OK" if major >= 10 else "WARN",
                     f"{ver}" + ("" if major >= 10 else "  file-based apps need 10+: " + HINTS["dotnet"].get(OS, "")), False))
    else:
        rows.append((".NET SDK 10+ (C# examples)", "WARN", "not found: " + HINTS["dotnet"].get(OS, "") +
                     "  (C# will be written but marked 'not executed')", False))

    # --- Check 4: internet access for research (optional, only warns) ---
    try:
        # A HEAD request asks for headers only, which is quick. timeout=8 seconds.
        urllib.request.urlopen(urllib.request.Request("https://www.wikipedia.org", method="HEAD"), timeout=8)
        rows.append(("Internet (research)", "OK", "reachable", False))
    except urllib.error.HTTPError as e:
        # An HTTP error page (for example 403) still proves the network connection works.
        # any HTTP answer, even an error status, proves the network works
        rows.append(("Internet (research)", "OK", f"reachable (HTTP {e.code})", False))
    except Exception as e:  # noqa: BLE001  (any other failure, such as no DNS or a timeout, means "not reachable")
        rows.append(("Internet (research)", "WARN", f"not reachable ({type(e).__name__}); research needs web access", False))

    # --- Check 5: PyMuPDF, optional, used only to preview PDF pages as images ---
    try:
        import warnings  # imported here because it is only needed for this check
        warnings.simplefilter("ignore")  # hides noisy import warnings from the optional package
        import fitz  # noqa: F401  (PyMuPDF's import name; F401 = "imported but unused" is intended)
        rows.append(("PyMuPDF (optional, page previews)", "OK", "installed", False))
    except ImportError:  # the package is not installed; this is optional, so only a note
        rows.append(("PyMuPDF (optional, page previews)", "NOTE", "pip install pymupdf  (only to preview PDF pages as images)", False))

    # Column width: pad every check name to the longest one so the table lines up.
    w = max(len(r[0]) for r in rows)
    print(f"topic-mastery environment check ({OS}, {platform.platform()})\n")
    # Print each row. The format spec {status:4} pads the status to 4 characters and
    # {name:<{w}} left-aligns the name to width w. The last part adds "(optional)" to
    # optional rows that did not pass, and nothing to optional rows that did.
    for name, status, detail, req in rows:
        print(f"[{status:4}] {name:<{w}}  {detail}{'' if req else '   (optional)' if status != 'OK' else ''}")
    print()
    if required_fail:
        print("RESULT: fix the FAIL items above, then run this again.")
        sys.exit(1)  # exit code 1 tells the caller (or the user's shell) that the check failed
    print("RESULT: ready. Warnings only reduce features (C# execution, research, previews).")


# Run main() only when this file is executed directly (python doctor.py), not when it is imported.
if __name__ == "__main__":
    main()
