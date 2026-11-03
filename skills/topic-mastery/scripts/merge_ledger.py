#!/usr/bin/env python3
"""Merge per-cluster research files into one source ledger with stable S-ids.

Why: parallel research agents each find sources independently. This merges them, removes
duplicate URLs, assigns S1, S2, ... once, and rewrites every finding to use those ids, so the
roadmap and every later chapter cite the same source with the same id.

Each cluster file (research/cluster-X.json) looks like:
{"cluster":"A","sources":[{"title","publisher","url","published","accessed","tier","type","notes"}],
 "findings":[{"dimension":1,"statement":"...","evidence":"est|int|ass|pre|gap","source_urls":["..."],"detail":"..."}],
 "gaps":[{"dimension":9,"missing":"...","next_step":"..."}]}

Usage:
    python merge_ledger.py research/cluster-*.json -o research/
Writes research/sources.json (the ledger), research/findings.md (all findings grouped by
dimension with S-ids) and research/gaps.md. Existing ids in an existing sources.json are kept.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

DIM = {1: "History and evolution", 2: "Foundations", 3: "Deep technical understanding", 4: "Architecture and frameworks",
       5: "Practical application", 6: "Advanced concepts", 7: "Evaluation and improvement", 8: "Real-world applications",
       9: "Security, ethics, governance", 10: "Business and strategic value", 11: "Expert perspectives",
       12: "Future outlook", 13: "Coding examples"}


def norm(u):
    s = urlsplit(u.strip())
    return urlunsplit((s.scheme.lower(), s.netloc.lower().removeprefix("www."), s.path.rstrip("/"), s.query, ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("-o", "--outdir", required=True)
    a = ap.parse_args()
    out = Path(a.outdir)
    ledger_path = out / "sources.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
    by_url = {norm(s["url"]): s for s in ledger}
    next_id = max([int(s["id"][1:]) for s in ledger] + [0]) + 1
    findings, gaps, skipped = [], [], 0

    for f in a.files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for s in d.get("sources", []):
            k = norm(s["url"])
            if k in by_url:
                ex = by_url[k]
                ex["tier"] = min(ex.get("tier", 4), s.get("tier", 4))
                if s.get("notes") and s["notes"] not in ex.get("notes", ""):
                    ex["notes"] = (ex.get("notes", "") + " | " + s["notes"]).strip(" |")
            else:
                s = dict(s, id=f"S{next_id}")
                next_id += 1
                ledger.append(s)
                by_url[k] = s
        for fd in d.get("findings", []):
            ids = []
            for u in fd.get("source_urls", []):
                src = by_url.get(norm(u))
                if src:
                    ids.append(src["id"])
                else:
                    skipped += 1
            findings.append((fd.get("dimension", 0), fd, sorted(set(ids), key=lambda x: int(x[1:]))))
        gaps += d.get("gaps", [])

    ledger.sort(key=lambda s: int(s["id"][1:]))
    ledger_path.write_text(json.dumps(ledger, indent=1, ensure_ascii=False), encoding="utf-8")

    lines = []
    for dim in range(1, 14):
        rows = [(fd, ids) for dm, fd, ids in findings if dm == dim]
        if not rows:
            continue
        lines.append(f"\n## {dim}. {DIM[dim]}\n")
        for fd, ids in rows:
            cite = " ".join(f"[{i}]" for i in ids) or "[no source]"
            lines.append(f"- ({fd.get('evidence', '?')}) {fd['statement']} {cite}")
            if fd.get("detail"):
                lines.append(f"  - {fd['detail']}")
    (out / "findings.md").write_text("\n".join(lines), encoding="utf-8")
    g = ["# Gaps reported by research agents\n"] + [
        f"- Dim {x.get('dimension')} ({DIM.get(x.get('dimension'), '?')}): {x.get('missing')} Next: {x.get('next_step')}" for x in gaps]
    (out / "gaps.md").write_text("\n".join(g), encoding="utf-8")
    by_tier = {}
    for s in ledger:
        by_tier[s.get("tier")] = by_tier.get(s.get("tier"), 0) + 1
    print(f"Ledger: {len(ledger)} sources (by tier: {dict(sorted(by_tier.items(), key=lambda x: str(x[0])))}); "
          f"{len(findings)} findings; {len(gaps)} gaps; {skipped} finding source(s) not in any sources list")


if __name__ == "__main__":
    main()
