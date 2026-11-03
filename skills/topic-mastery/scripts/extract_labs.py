#!/usr/bin/env python3
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
import argparse
import re
from html import unescape
from pathlib import Path

BLOCK = re.compile(r"<pre\b([^>]*)>(.*?)</pre>", re.S | re.I)

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
    m = re.search(rf'{name}\s*=\s*"([^"]*)"', attrs)
    return unescape(m.group(1)) if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", default="Lab pack")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = Path(a.html).read_text(encoding="utf-8")
    labs, pips = [], set()
    for m in BLOCK.finditer(raw):
        attrs, inner = m.group(1), m.group(2)
        rel = attr(attrs, "data-file")
        if not rel:
            continue
        # strip only formatting tags; a raw "<" in code such as "i < n" must survive
        code = unescape(re.sub(r"</?(?:span|b|i|em|strong|u|mark)\b[^>]*>", "", inner)).strip("\n") + "\n"
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(code, encoding="utf-8")
        for p in filter(None, (x.strip() for x in attr(attrs, "data-pip").split(","))):
            pips.add(p)
        labs.append({"file": rel, "lang": attr(attrs, "data-lang"), "title": attr(attrs, "data-title") or Path(rel).stem,
                     "run": attr(attrs, "data-run") == "yes", "expect": attr(attrs, "data-expect")})
    import json
    (out / "labs.json").write_text(json.dumps(labs, indent=1), encoding="utf-8")
    (out / "run_all.py").write_text(RUN_ALL, encoding="utf-8")
    (out / "requirements.txt").write_text("\n".join(sorted(pips)) + ("\n" if pips else "# standard library only\n"), encoding="utf-8")
    rows = "\n".join(f"| `{l['file']}` | {l['title']} | {l['lang'] or '-'} | {('`' + l['expect'] + '`') if l['expect'] else '-'} |" for l in labs)
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


if __name__ == "__main__":
    main()
