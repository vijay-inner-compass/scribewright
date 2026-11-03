#!/usr/bin/env python3
# Shebang: lets macOS and Linux run this file directly with the first python3 on PATH.
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
# argparse: command-line options. re: regular expressions. sys: stdout and stderr.
# Counter: counts words per speaker.
import argparse
import re
import sys
from collections import Counter

# TS matches a cue's timing line, such as "00:01:02.500 --> 00:01:05.000" (SRT uses a comma instead of a dot).
# Each (...)? group is optional, so hours can be left out. Groups 2 and 3 are minutes and seconds
# of the start time; groups 6 and 7 are minutes and seconds of the end time (the end time is not used).
TS = re.compile(r"(\d{1,2}:)?(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{1,2}:)?(\d{2}):(\d{2})[.,](\d{3})")
# SPEAKER matches "Name: text" at the start of a line. The name is up to 60 characters with no colon or newline.
SPEAKER = re.compile(r"^([^:\n]{1,60}?):\s+(.*)$")
# TAG matches any HTML-style tag, such as <i> or <c.colour>, which some caption files contain.
TAG = re.compile(r"<[^>]+>")


def stamp(h, m, s):
    """Format an hour, minute and second as HH:MM:SS. h may be None or an empty string, which counts as 0."""
    return f"{int(h or 0):02d}:{int(m):02d}:{int(s):02d}"


def parse(path):
    """Read a caption file and return a list of (time, text) pairs, one per cue."""
    # utf-8-sig removes a byte-order mark if the file starts with one. errors="replace" avoids a crash
    # on bad characters by swapping them for a replacement symbol.
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    cues, cur_time, buf = [], None, []  # cues: finished (time, text) pairs. cur_time: start time of the open cue. buf: its text lines.

    def flush():
        """Save the open cue (if it has a time and some text) and reset for the next one."""
        nonlocal buf, cur_time  # these two names belong to parse(), so they must be declared nonlocal
        if cur_time is not None and buf:
            cues.append((cur_time, " ".join(buf).strip()))  # join the cue's lines with spaces
        buf, cur_time = [], None

    for line in raw.splitlines():
        line = line.strip()  # remove spaces at both ends of the line
        m = TS.search(line)  # is this a timing line?
        if m:
            flush()  # a new cue starts, so save the previous one first
            # The hour group may be missing; "0:" then rstrip(":") gives "0". Otherwise it is "01:" -> "01".
            h = (m.group(1) or "0:").rstrip(":")
            cur_time = stamp(h, m.group(2), m.group(3))  # keep only the start time
        elif not line or line.isdigit() or line.upper().startswith(("WEBVTT", "NOTE")):
            # A blank line ends the cue. Other lines here are headers or cue numbers, which are ignored.
            if not line:
                flush()
        elif cur_time is not None:
            # A line of caption text inside a cue. Remove any tags such as <i> first.
            buf.append(TAG.sub("", line))
    flush()  # save the last cue, which has no blank line after it
    return cues


def merge(cues):
    """Join consecutive cues from the same speaker into one turn."""
    turns = []  # each turn is [time, speaker, [text pieces]]; the text pieces are joined at the end
    for t, text in cues:
        m = SPEAKER.match(text)  # does the cue start with "Name: "?
        # If it does, the speaker is the name and the body is the rest. Otherwise the speaker is unknown for now.
        spk, body = (m.group(1).strip(), m.group(2)) if m else (None, text)
        if spk is None and turns:
            spk = turns[-1][1]  # no name given: assume the same speaker as the previous turn
        if turns and turns[-1][1] == spk:
            turns[-1][2].append(body)  # same speaker as before, so add to the current turn
        else:
            turns.append((t, spk, [body]))  # a new speaker starts a new turn
    # Return (time, speaker, one combined text string) for each turn.
    return [(t, s, " ".join(b)) for t, s, b in turns]


def main():
    """Read the transcript, write the cleaned text, and print a summary of speakers and words."""
    ap = argparse.ArgumentParser()
    ap.add_argument("path")  # the transcript file
    ap.add_argument("-o", "--out")  # optional output file; default is the screen
    ap.add_argument("--no-times", action="store_true")  # leave the [time] prefixes off each line
    a = ap.parse_args()

    cues = parse(a.path)
    if not cues:  # plain text transcript: pass through untouched
        # No timing lines were found, so the file is treated as plain text and copied as it is.
        text = open(a.path, encoding="utf-8-sig", errors="replace").read()
        # Write to the output file if one was given, otherwise to the screen.
        (open(a.out, "w", encoding="utf-8") if a.out else sys.stdout).write(text)
        print(f"No cues found; copied as plain text ({len(text.split())} words).", file=sys.stderr)
        return

    turns = merge(cues)  # combine consecutive cues from the same speaker
    lines = []
    for t, s, body in turns:
        prefix = "" if a.no_times else f"[{t}] "  # the time prefix, unless --no-times was given
        lines.append(f"{prefix}{s + ': ' if s else ''}{body}")  # "[time] Speaker: text"
    out = "\n\n".join(lines) + "\n"  # a blank line between turns for readability
    (open(a.out, "w", encoding="utf-8") if a.out else sys.stdout).write(out)

    words = Counter()  # word count per speaker
    for _, s, body in turns:
        words[s or "(unknown)"] += len(body.split())  # len(split()) counts words
    # Summary goes to stderr, so it does not mix with the transcript text sent to stdout.
    print(f"Last cue at {cues[-1][0]}; {len(turns)} turns; {sum(words.values())} words", file=sys.stderr)
    for s, n in words.most_common():  # speakers, most words first
        print(f"  {s}: {n} words", file=sys.stderr)


# Run main() only when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    main()
