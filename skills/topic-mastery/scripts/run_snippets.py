#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
"""Execute the runnable code blocks of a learning document and report pass or fail.

Why: a tutorial with code that does not run destroys trust. Mark runnable blocks like
    <pre class="code" data-lang="python" data-run="yes" data-expect="expected substring">
    <pre class="code" data-lang="csharp" data-run="yes" data-expect="Total: 6">
Blocks without data-run="yes" (fragments, shell, pseudo-code) are skipped and counted.
Python runs with `python -I`; C# runs as a .NET 10 file-based app (`dotnet run file.cs`) and
is skipped with a clear message if the dotnet SDK is missing.

Usage:
    python run_snippets.py doc.html [--timeout 120]
Exit code 1 if any runnable block fails.
"""
# argparse: command-line options. re: regular expressions. shutil: finds dotnet on PATH.
# subprocess: runs each snippet. sys: the Python executable and exit codes.
# tempfile: a temporary folder for each snippet. unescape: turns &lt; back into <, and so on.
# Path: file paths.
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from html import unescape
from pathlib import Path

# Matches one whole <pre ...>...</pre> block. Group 1 is the attributes; group 2 is the code.
# re.S lets "." match newlines; re.I ignores case.
BLOCK = re.compile(r"<pre\b([^>]*)>(.*?)</pre>", re.S | re.I)


def attr(attrs, name):
    """Return one attribute's value from an attribute string, or "" if it is not there."""
    # The pattern matches name="value" and captures the value between the quotes.
    m = re.search(rf'{name}\s*=\s*"([^"]*)"', attrs)
    return unescape(m.group(1)) if m else ""  # turn entities such as &quot; back into characters


def main():
    """Run each block marked data-run="yes", record pass, fail or skip, and print a summary."""
    ap = argparse.ArgumentParser()
    ap.add_argument("html")  # the document to check
    ap.add_argument("--timeout", type=int, default=120)  # seconds allowed per snippet
    a = ap.parse_args()
    raw = Path(a.html).read_text(encoding="utf-8")
    dotnet = shutil.which("dotnet")  # path to the .NET SDK, or None if it is not installed
    results, skipped = [], 0  # results: one tuple per runnable block. skipped: blocks not marked runnable
    # enumerate(..., 1) numbers the blocks from 1, so the report can say "block 3".
    for i, m in enumerate(BLOCK.finditer(raw), 1):
        attrs, inner = m.group(1), m.group(2)
        # Skip blocks that are not marked runnable. Count the ones that are code blocks, so the summary is accurate.
        if "code" not in attr(attrs, "class").split() or attr(attrs, "data-run") != "yes":
            if "code" in attr(attrs, "class").split():
                skipped += 1
            continue
        lang = attr(attrs, "data-lang").lower()  # language name, normalised to lower case
        # Strip only formatting tags (for example <span class="c">); a raw "<" in code such as "i < n" must survive.
        code = unescape(re.sub(r"</?(?:span|b|i|em|strong|u|mark)\b[^>]*>", "", inner))
        expect = attr(attrs, "data-expect")  # text that must appear in the output, if given
        # A fresh temporary folder for each snippet. It is deleted when the block ends.
        with tempfile.TemporaryDirectory() as d:
            if lang == "python":
                f = Path(d) / "snippet.py"  # the code is written to a file so it can be run
                f.write_text(code, encoding="utf-8")
                # -I runs Python in isolated mode: it ignores PYTHON* environment variables and the user's
                # site-packages, and does not add the script's own folder to sys.path.
                cmd = [sys.executable, "-I", str(f)]
            elif lang in ("csharp", "cs", "c#"):  # three spellings for C#
                if not dotnet:
                    results.append((i, lang, "SKIP", "dotnet SDK not found"))
                    continue  # move on to the next block
                f = Path(d) / "snippet.cs"
                f.write_text(code, encoding="utf-8")
                cmd = [dotnet, "run", str(f)]  # a single .cs file runs as a file-based app
            else:
                results.append((i, lang, "SKIP", "unsupported language"))
                continue
            try:
                # Run the snippet in its own folder. capture_output collects what it prints.
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, cwd=d)
                out = (r.stdout + r.stderr).strip()  # everything the program printed
                # A pass needs exit code 0 and, if an expected text is given, that text in the output.
                ok = r.returncode == 0 and (not expect or expect in out)
                # The note explains a failure: the exit code and the end of the output.
                note = "" if ok else (f"exit {r.returncode}; " + out[-300:].replace("\n", " | "))
                if r.returncode == 0 and expect and expect not in out:
                    # Show the end of the output so the reader can see what was printed instead.
                    note = f"output missing expected text {expect!r}; got: {out[-200:]!r}"
                results.append((i, lang, "PASS" if ok else "FAIL", note))
            except subprocess.TimeoutExpired:
                # The snippet ran longer than --timeout. Count it as a failure.
                results.append((i, lang, "FAIL", f"timeout after {a.timeout}s"))
    # Print one line per runnable block. {i:>3} right-aligns the block number; {lang or '?':7} pads the language.
    for i, lang, status, note in results:
        print(f"block {i:>3} [{lang or '?':7}] {status} {note}")
    # Count each outcome for the summary line.
    p = sum(1 for r in results if r[2] == "PASS")
    f = sum(1 for r in results if r[2] == "FAIL")
    s = sum(1 for r in results if r[2] == "SKIP")
    print(f"{p} passed, {f} failed, {s} skipped (tooling), {skipped} not marked runnable")
    sys.exit(1 if f else 0)  # exit 1 when any runnable block failed, so a build script can stop


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
