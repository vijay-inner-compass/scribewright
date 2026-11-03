#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
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
# argparse: command-line options. json: reads and writes the ledger. re: unused here but kept as imported.
# Path: file paths. urlsplit / urlunsplit: take a URL apart and rebuild it, used to normalise URLs.
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

# DIM maps each research dimension number (1 to 13) to its name, used as section headings in findings.md.
DIM = {1: "History and evolution", 2: "Foundations", 3: "Deep technical understanding", 4: "Architecture and frameworks",
       5: "Practical application", 6: "Advanced concepts", 7: "Evaluation and improvement", 8: "Real-world applications",
       9: "Security, ethics, governance", 10: "Business and strategic value", 11: "Expert perspectives",
       12: "Future outlook", 13: "Coding examples"}


def norm(u):
    """Normalise a URL so that small differences do not make one source look like two.

    Lower-cases the scheme and host, drops a leading "www.", removes a trailing slash from the path,
    and removes the #fragment. Query strings are kept, because they can change the page.
    """
    s = urlsplit(u.strip())  # split into scheme, host, path, query and fragment
    # removeprefix("www.") is a Python 3.9+ string method; it only removes the prefix if it is there.
    return urlunsplit((s.scheme.lower(), s.netloc.lower().removeprefix("www."), s.path.rstrip("/"), s.query, ""))


def main():
    """Read the cluster files, merge their sources, and write the ledger and the two markdown reports."""
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")  # one or more cluster files; nargs="+" means at least one
    ap.add_argument("-o", "--outdir", required=True)  # folder for sources.json, findings.md and gaps.md
    a = ap.parse_args()
    out = Path(a.outdir)
    ledger_path = out / "sources.json"
    # If a ledger already exists, load it so earlier ids are kept. Otherwise start empty.
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
    # by_url maps a normalised URL to its ledger entry, so a repeated URL is found quickly.
    by_url = {norm(s["url"]): s for s in ledger}
    # The next free id: one more than the largest existing number ("S7" gives 7, so the next is 8).
    # max([...] + [0]) handles an empty ledger, where the answer is 1.
    next_id = max([int(s["id"][1:]) for s in ledger] + [0]) + 1
    findings, gaps, skipped = [], [], 0  # collected findings, gaps, and a count of unknown source URLs

    for f in a.files:  # process each cluster file in turn
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for s in d.get("sources", []):
            k = norm(s["url"])  # the normalised URL is the key used to spot duplicates
            if k in by_url:
                # A known source: keep the better (lower) tier, and append any new note to the existing one.
                ex = by_url[k]
                ex["tier"] = min(ex.get("tier", 4), s.get("tier", 4))
                if s.get("notes") and s["notes"] not in ex.get("notes", ""):
                    ex["notes"] = (ex.get("notes", "") + " | " + s["notes"]).strip(" |")
            else:
                # A new source: give it the next id, add it to the ledger, and index it by URL.
                # dict(s, id=...) copies the record and adds the id field.
                s = dict(s, id=f"S{next_id}")
                next_id += 1
                ledger.append(s)
                by_url[k] = s
        for fd in d.get("findings", []):
            ids = []  # the S-ids this finding cites
            for u in fd.get("source_urls", []):
                src = by_url.get(norm(u))  # look up the URL in the (now merged) index
                if src:
                    ids.append(src["id"])
                else:
                    skipped += 1  # the finding cites a URL that is not in any sources list
            # Store (dimension, finding, sorted unique ids). sorted(..., key=int(x[1:])) orders S2 before S10.
            findings.append((fd.get("dimension", 0), fd, sorted(set(ids), key=lambda x: int(x[1:]))))
        gaps += d.get("gaps", [])  # add this file's gaps to the running list

    ledger.sort(key=lambda s: int(s["id"][1:]))  # keep the ledger in id order
    # ensure_ascii=False keeps non-English characters as they are, rather than \u escapes.
    ledger_path.write_text(json.dumps(ledger, indent=1, ensure_ascii=False), encoding="utf-8")

    lines = []  # the lines of findings.md
    for dim in range(1, 14):  # dimensions 1 to 13, in order
        rows = [(fd, ids) for dm, fd, ids in findings if dm == dim]  # findings in this dimension
        if not rows:
            continue  # skip dimensions with no findings
        lines.append(f"\n## {dim}. {DIM[dim]}\n")  # section heading
        for fd, ids in rows:
            # Citations as [S1] [S4]; a finding with no source is marked clearly so it cannot go unnoticed.
            cite = " ".join(f"[{i}]" for i in ids) or "[no source]"
            # "?" stands in when the evidence label is missing.
            lines.append(f"- ({fd.get('evidence', '?')}) {fd['statement']} {cite}")
            if fd.get("detail"):  # optional extra detail on an indented line
                lines.append(f"  - {fd['detail']}")
    (out / "findings.md").write_text("\n".join(lines), encoding="utf-8")
    # gaps.md: a title, then one bullet per gap. DIM.get(...) falls back to "?" for an unknown dimension.
    g = ["# Gaps reported by research agents\n"] + [
        f"- Dim {x.get('dimension')} ({DIM.get(x.get('dimension'), '?')}): {x.get('missing')} Next: {x.get('next_step')}" for x in gaps]
    (out / "gaps.md").write_text("\n".join(g), encoding="utf-8")
    by_tier = {}  # count of sources per tier, for example {1: 3, 2: 5}
    for s in ledger:
        by_tier[s.get("tier")] = by_tier.get(s.get("tier"), 0) + 1
    # Print a one-line summary. The sort with str(x[0]) avoids errors when tiers mix numbers and missing values.
    print(f"Ledger: {len(ledger)} sources (by tier: {dict(sorted(by_tier.items(), key=lambda x: str(x[0])))}); "
          f"{len(findings)} findings; {len(gaps)} gaps; {skipped} finding source(s) not in any sources list")


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
