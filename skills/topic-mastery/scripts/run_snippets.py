#!/usr/bin/env python3
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
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from html import unescape
from pathlib import Path

BLOCK = re.compile(r"<pre\b([^>]*)>(.*?)</pre>", re.S | re.I)


def attr(attrs, name):
    m = re.search(rf'{name}\s*=\s*"([^"]*)"', attrs)
    return unescape(m.group(1)) if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--timeout", type=int, default=120)
    a = ap.parse_args()
    raw = Path(a.html).read_text(encoding="utf-8")
    dotnet = shutil.which("dotnet")
    results, skipped = [], 0
    for i, m in enumerate(BLOCK.finditer(raw), 1):
        attrs, inner = m.group(1), m.group(2)
        if "code" not in attr(attrs, "class").split() or attr(attrs, "data-run") != "yes":
            if "code" in attr(attrs, "class").split():
                skipped += 1
            continue
        lang = attr(attrs, "data-lang").lower()
        # strip only formatting tags (e.g. <span class="c">); a raw "<" in code such as "i < n" must survive
        code = unescape(re.sub(r"</?(?:span|b|i|em|strong|u|mark)\b[^>]*>", "", inner))
        expect = attr(attrs, "data-expect")
        with tempfile.TemporaryDirectory() as d:
            if lang == "python":
                f = Path(d) / "snippet.py"
                f.write_text(code, encoding="utf-8")
                cmd = [sys.executable, "-I", str(f)]
            elif lang in ("csharp", "cs", "c#"):
                if not dotnet:
                    results.append((i, lang, "SKIP", "dotnet SDK not found"))
                    continue
                f = Path(d) / "snippet.cs"
                f.write_text(code, encoding="utf-8")
                cmd = [dotnet, "run", str(f)]
            else:
                results.append((i, lang, "SKIP", "unsupported language"))
                continue
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout, cwd=d)
                out = (r.stdout + r.stderr).strip()
                ok = r.returncode == 0 and (not expect or expect in out)
                note = "" if ok else (f"exit {r.returncode}; " + out[-300:].replace("\n", " | "))
                if r.returncode == 0 and expect and expect not in out:
                    note = f"output missing expected text {expect!r}; got: {out[-200:]!r}"
                results.append((i, lang, "PASS" if ok else "FAIL", note))
            except subprocess.TimeoutExpired:
                results.append((i, lang, "FAIL", f"timeout after {a.timeout}s"))
    for i, lang, status, note in results:
        print(f"block {i:>3} [{lang or '?':7}] {status} {note}")
    p = sum(1 for r in results if r[2] == "PASS")
    f = sum(1 for r in results if r[2] == "FAIL")
    s = sum(1 for r in results if r[2] == "SKIP")
    print(f"{p} passed, {f} failed, {s} skipped (tooling), {skipped} not marked runnable")
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
