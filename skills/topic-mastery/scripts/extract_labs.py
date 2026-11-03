#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
"""Turn a chapter's code blocks into a runnable, self-explaining lab pack.

Why: code that only lives inside a PDF cannot be run, edited or version-controlled. Mark any code
block with data-file and it is written out as a real file; a README and a one-command runner
are generated, so a learner can set up, run and check every example without copying text.

In the chapter HTML:
    <pre class="code" data-lang="python" data-file="python/01_neuron.py" data-run="yes" data-expect="0.94">
    <pre class="code" data-lang="csharp" data-file="csharp/01_neuron.cs" data-run="yes" data-expect="0.94">
    optional: data-pip="numpy,torch" (Python packages the file needs), data-title="One neuron"

Usage:
    python extract_labs.py chapter.html -o labs/ [--title "Chapter 1 labs"]
Creates <out>/<files>, README.md (setup + run + expected output table), requirements.txt, run_all.py.
"""
# argparse: command-line options. re: regular expressions. unescape: turns &lt; back into <, and so on.
# Path: file and folder paths.
import argparse
import re
from html import unescape
from pathlib import Path

# Matches one whole <pre ...>...</pre> block. Group 1 is the attribute text inside the opening tag;
# group 2 is the code between the tags. re.S lets "." cross line breaks; re.I ignores case.
BLOCK = re.compile(r"<pre\b([^>]*)>(.*?)</pre>", re.S | re.I)

# RUN_ALL is the text of the run_all.py file that is written into every lab folder.
# It is a Python string, so the code inside it is NOT run here. Its contents are copied verbatim
# into the generated run_all.py. What the generated script does, in order:
#   1. load labs.json (the list of lab files, whether to run them, and the expected text)
#   2. run each .py file with this Python, and each .cs file with `dotnet run`
#   3. print PASS when the exit code is 0 and the expected text appears in the output
#   4. print a summary and exit 1 if any lab failed
RUN_ALL = '''#!/usr/bin/env python3
"""Run every lab file and compare with the expected output. Usage: python run_all.py"""
import json, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
LABS = json.loads((HERE / "labs.json").read_text(encoding="utf-8"))
dotnet = shutil.which("dotnet")
failed = 0
for lab in LABS:
    f = HERE / lab["file"]
    if not lab["run"]:
        print(f"SKIP  {lab['file']}  (not a standalone program)"); continue
    if f.suffix == ".py":
        cmd = [sys.executable, str(f)]
    elif f.suffix == ".cs":
        if not dotnet:
            print(f"SKIP  {lab['file']}  (.NET 10 SDK not installed)"); continue
        cmd = [dotnet, "run", str(f)]
    else:
        print(f"SKIP  {lab['file']}  (unknown type)"); continue
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(f.parent))
    out = (r.stdout + r.stderr)
    ok = r.returncode == 0 and (not lab["expect"] or lab["expect"] in out)
    print(("PASS  " if ok else "FAIL  ") + lab["file"] + ("" if ok else "\\n" + out[-400:]))
    failed += (not ok)
print("\\nAll labs passed." if not failed else f"\\n{failed} lab(s) failed.")
sys.exit(1 if failed else 0)
'''


def attr(attrs, name):
    """Return the value of one attribute, such as data-file, from an attribute string, or "" if absent."""
    # rf'...' is a raw f-string: {name} is filled in, and backslashes stay as written.
    # The pattern finds name="value" and captures the value between the double quotes.
    m = re.search(rf'{name}\s*=\s*"([^"]*)"', attrs)
    return unescape(m.group(1)) if m else ""  # unescape turns &quot; and similar back into characters


def main():
    """Read the chapter HTML, write each marked code block as a file, and write the support files."""
    ap = argparse.ArgumentParser()
    ap.add_argument("html")  # the chapter HTML file
    ap.add_argument("-o", "--out", required=True)  # the output folder
    ap.add_argument("--title", default="Lab pack")  # the heading used in the generated README
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)  # create the output folder and any missing parents; no error if it exists
    raw = Path(a.html).read_text(encoding="utf-8")
    labs, pips = [], set()  # labs: one record per lab file. pips: the set of pip packages needed.
    for m in BLOCK.finditer(raw):  # visit every <pre> block in the chapter
        attrs, inner = m.group(1), m.group(2)  # the attributes and the code inside the block
        rel = attr(attrs, "data-file")  # the relative path to write, e.g. "python/01_neuron.py"
        if not rel:
            continue  # blocks without data-file are only for reading, so skip them
        # Strip only formatting tags (span, b, i, ...) and turn HTML entities back into characters.
        # A raw "<" in code such as "i < n" must survive, so only known formatting tags are removed.
        # strip("\n") removes blank lines at the ends; the final "+ '\n'" adds one newline at the end of the file.
        code = unescape(re.sub(r"</?(?:span|b|i|em|strong|u|mark)\b[^>]*>", "", inner)).strip("\n") + "\n"
        dest = out / rel  # the full output path, e.g. labs/python/01_neuron.py
        dest.parent.mkdir(parents=True, exist_ok=True)  # create the subfolder, such as "python"
        dest.write_text(code, encoding="utf-8")
        # data-pip may list several packages separated by commas. filter(None, ...) drops the empty entries.
        for p in filter(None, (x.strip() for x in attr(attrs, "data-pip").split(","))):
            pips.add(p)
        # Record what the runner needs to know about this file.
        # title falls back to the file name without its extension; run is True only for data-run="yes".
        labs.append({"file": rel, "lang": attr(attrs, "data-lang"), "title": attr(attrs, "data-title") or Path(rel).stem,
                     "run": attr(attrs, "data-run") == "yes", "expect": attr(attrs, "data-expect")})
    import json  # imported here because only the next few lines use it
    (out / "labs.json").write_text(json.dumps(labs, indent=1), encoding="utf-8")  # the list read by run_all.py
    (out / "run_all.py").write_text(RUN_ALL, encoding="utf-8")  # the runner script
    # requirements.txt: one package per line, sorted. If there are none, say so.
    (out / "requirements.txt").write_text("\n".join(sorted(pips)) + ("\n" if pips else "# standard library only\n"), encoding="utf-8")
    # One markdown table row per lab file, for the README. "-" stands in for a missing language or expected value.
    rows = "\n".join(f"| `{l['file']}` | {l['title']} | {l['lang'] or '-'} | {('`' + l['expect'] + '`') if l['expect'] else '-'} |" for l in labs)
    # The README is an f-string, so {...} parts are filled in with values. The text itself is teaching content.
    readme = f"""# {a.title}

Runnable code for the chapter. Every file here is the same code printed in the chapter.

## 1. Set up (once)

| You need | Check with | Install |
|---|---|---|
| Python 3.8 or newer | `python --version` (or `python3 --version`) | python.org, `winget install Python.Python.3.12`, or `brew install python` |
| .NET SDK 10 or newer (for the C# files) | `dotnet --version` | dotnet.microsoft.com/download, or `winget install Microsoft.DotNet.SDK.10` |
| Python packages | `pip install -r requirements.txt` | listed in `requirements.txt` ({'none beyond the standard library' if not pips else ', '.join(sorted(pips))}) |

C# files are single-file programs: run one with `dotnet run csharp/<file>.cs`. A line such as `#:package Name@1.2.3` at the top downloads its NuGet package automatically.

## 2. Run everything and check the results

```
python run_all.py
```

Each file prints `PASS` when it runs and its output contains the expected text.

## 3. Files

| File | What it shows | Language | Expected output contains |
|---|---|---|---|
{rows}

## 4. How to learn from these

1. Read the chapter section first, then run the file and compare its output with the chapter.
2. Change one number (a weight, a learning rate, a seed) and predict the result before you run it.
3. Break it on purpose, read the error, and fix it. This is the fastest way to build troubleshooting skill.
4. Do the exercises at the end of the chapter; they build on these files.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `python` not found | Command is `python3` on macOS and Linux | Use `python3` |
| `dotnet run` says the file is unknown or needs a project | .NET SDK older than 10 | Install SDK 10 or newer |
| First C# run is slow | NuGet restore and first compile | Normal; later runs are fast |
| Numbers differ slightly | Different random seed or library version | Check the seed and versions; the chapter says which values must match exactly |
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    print(f"Wrote {len(labs)} lab file(s) plus README.md, run_all.py, labs.json, requirements.txt to {out}")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
