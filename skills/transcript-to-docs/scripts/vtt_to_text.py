#!/usr/bin/env python3
"""Turn a .vtt / .srt / plain-text transcript into clean, readable text.

Why: raw VTT is mostly cue numbers, timestamps and one-line fragments of the
same speaker. Collapsing it roughly halves the size and makes it far easier to
read end to end before writing documentation.

Usage:
    python vtt_to_text.py <transcript> [-o out.txt] [--no-times]

Prints a summary (duration, speakers, words) to stderr and the cleaned text to
stdout (or to -o). Speaker turns look like:
    [00:12:30] Alice: merged text of consecutive cues ...
"""
import argparse
import re
import sys
from collections import Counter

TS = re.compile(r"(\d{1,2}:)?(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{1,2}:)?(\d{2}):(\d{2})[.,](\d{3})")
SPEAKER = re.compile(r"^([^:\n]{1,60}?):\s+(.*)$")
TAG = re.compile(r"<[^>]+>")


def stamp(h, m, s):
    return f"{int(h or 0):02d}:{int(m):02d}:{int(s):02d}"


def parse(path):
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    cues, cur_time, buf = [], None, []

    def flush():
        nonlocal buf, cur_time
        if cur_time is not None and buf:
            cues.append((cur_time, " ".join(buf).strip()))
        buf, cur_time = [], None

    for line in raw.splitlines():
        line = line.strip()
        m = TS.search(line)
        if m:
            flush()
            h = (m.group(1) or "0:").rstrip(":")
            cur_time = stamp(h, m.group(2), m.group(3))
        elif not line or line.isdigit() or line.upper().startswith(("WEBVTT", "NOTE")):
            if not line:
                flush()
        elif cur_time is not None:
            buf.append(TAG.sub("", line))
    flush()
    return cues


def merge(cues):
    turns = []  # (time, speaker, text)
    for t, text in cues:
        m = SPEAKER.match(text)
        spk, body = (m.group(1).strip(), m.group(2)) if m else (None, text)
        if spk is None and turns:
            spk = turns[-1][1]
        if turns and turns[-1][1] == spk:
            turns[-1][2].append(body)
        else:
            turns.append((t, spk, [body]))
    return [(t, s, " ".join(b)) for t, s, b in turns]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("-o", "--out")
    ap.add_argument("--no-times", action="store_true")
    a = ap.parse_args()

    cues = parse(a.path)
    if not cues:  # plain text transcript: pass through untouched
        text = open(a.path, encoding="utf-8-sig", errors="replace").read()
        (open(a.out, "w", encoding="utf-8") if a.out else sys.stdout).write(text)
        print(f"No cues found; copied as plain text ({len(text.split())} words).", file=sys.stderr)
        return

    turns = merge(cues)
    lines = []
    for t, s, body in turns:
        prefix = "" if a.no_times else f"[{t}] "
        lines.append(f"{prefix}{s + ': ' if s else ''}{body}")
    out = "\n\n".join(lines) + "\n"
    (open(a.out, "w", encoding="utf-8") if a.out else sys.stdout).write(out)

    words = Counter()
    for _, s, body in turns:
        words[s or "(unknown)"] += len(body.split())
    print(f"Last cue at {cues[-1][0]}; {len(turns)} turns; {sum(words.values())} words", file=sys.stderr)
    for s, n in words.most_common():
        print(f"  {s}: {n} words", file=sys.stderr)


if __name__ == "__main__":
    main()
