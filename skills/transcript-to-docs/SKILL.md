---
name: transcript-to-docs
description: Turn a meeting, class, workshop or call transcript (.vtt, .srt, .txt, pasted text) into polished, enterprise-styled, research-enriched documentation that a beginner can learn from - landscape A4 PDF pages with cards, decision tables, steps, key facts, code, troubleshooting, plain-language concept explainers, a practice path and cited sources. The skill reads the whole transcript, then searches the web to verify facts and add the background the speaker skipped, keeping researched content clearly labelled. Use this whenever the user wants notes, a study note, setup guide, cheat sheet, runbook, learning guide, one-pager, meeting summary or decision record made from a transcript or recording, even if they only say "write this up", "make notes from this session", "help freshers learn this" or point at a .vtt file. Output is HTML plus a rendered PDF in a navy/slate/teal palette.
---

# Transcript to documentation, with research

Produce a dense, scannable document from a transcript in the house format: landscape A4 pages, each one topic, built from reusable cards. Then enrich it with researched background so a fresher can understand the topic in depth, not just recall what was said. The format exists so a reader finds the answer in seconds; every element must earn its space.

Two kinds of content, never mixed up:
- **From the session**: everything comes from the transcript.
- **Researched**: verified background, definitions, examples and sources added by you, labelled with the "Researched" pill and numbered citations.

## Workflow

1. **Ingest.** For `.vtt`/`.srt`, run
   `python <skill>/scripts/vtt_to_text.py <file> -o <workdir>/clean.txt`
   It merges cue fragments into speaker turns and prints duration, speakers and word counts. Read the whole cleaned text; a two to three hour session is about 150 KB, so read it in three or four chunks (`Read` with `offset`/`limit`, `allow_large`). Do not summarise from the first minutes: decisions and corrections come late.
2. **Decide the document set.** Read `references/document-types.md`. Pick the type from the content (teaching session, meeting, client workshop) and the pages. Ask the user only if audience or purpose is genuinely unclear; otherwise state your choice in one line and proceed. Ask once, early, if they want research depth: default is the full research pass for teaching sessions, a light pass (verify facts, define terms) for meetings.
3. **Extract from the transcript.** Build a fact list: decisions, numbers, names, dates, commands, steps, caveats, errors and fixes, definitions, open questions, owners. Drop chatter and repetition. Keep the speaker's corrected version. Keep ambiguous or garbled items (ASR errors on names, numbers, products) as your best reading and list them under "Verify".
4. **Research.** Read `references/research-guide.md` and follow it: list what a beginner would be stuck on, verify time-sensitive and numeric claims, find the best beginner source for each follow-up the speaker mentioned, and prepare plain-language explainers. Search generic concepts, not private session details. Open every source you cite. If research disagrees with the transcript, show the verified fact and flag the difference rather than overwriting the speaker. If web tools are unavailable, say so and add only plain background you are sure of, marked as general background without sources.
5. **Compose pages** from `references/components.md`, starting from `assets/template.html`. Order: session pages first (what was taught, decided or done), then the research pages (Foundations, Go deeper explainers, Practice path), then Sources and further reading. Keep the style and script blocks untouched; colours change only through the `:root` tokens.
   Write the page body to a file with the Write tool and assemble it with a short script (template head + body + template final script block). Pushing a long HTML string through a shell heredoc breaks on quotes.
   Rows marked `grow` stretch to fill the page, so short content leaves a card mostly empty. Use `grow` only where the content is enough, or add the missing content. The overflow check cannot detect empty space, so look at the page images.
6. **Render and check.**
   `python <skill>/scripts/render_pdf.py <doc>.html`
   It writes the PDF next to the HTML and reports overflowing pages (exit code 2). Fix overflow by cutting words first, then moving a card; do not shrink fonts. Then look at every page image: nothing clipped, no mostly-empty card, citations match the Sources list.
7. **Report.** Give the PDF and HTML paths, one line per page, then two short lists: **Verify** (uncertain items from the transcript, and any place research disagreed with it) and **Added from research** (topics added and the main sources). A reader should be able to tell at a glance what was said and what you added.

## Style rules (why they matter)

- **Titles are uppercase nouns or verb phrases**; the teal tagline is one sentence promising what the reader can do afterwards. Readers skim these to decide whether to read the page.
- **Lead with the mental model** when the transcript explains one: a flow strip or one clear statement. Most mistakes come from a wrong model.
- **Tables for choices, numbered steps for procedures, bullets for failures.**
- **Foundations before application** in the research pages: define each term the first time, then use it consistently. A beginner cannot use a term they were never given.
- **Cite where claims need defending**: transcript timestamps for session facts, numbered citations for researched facts.
- **Plain, concrete, active sentences**: name the exact button, file, command, field or person. No filler or marketing adjectives, no emojis, no em dashes.
- **Accurate simplicity**: explain simply, but never so simply it is wrong. State where an analogy stops working.
- **Only coin a name or mnemonic if the speaker did**, and mark it "named in the session".
- **Enterprise tone**: neutral and factual. Remove profanity, personal remarks and complaints about individuals. Keep attributed decisions and owners.
- **Sensitive data**: passwords, tokens, keys, account numbers and personal details spoken in a session are replaced by a placeholder and mentioned in your message. They never go into search queries either.
- **Density is a feature but must fit**: a card needing more than about eight lines of body text should be split or cut.

## Output conventions

- Folder: the user's chosen location, otherwise next to the source transcript. Name `<Topic>_<Doc type>_<YYYY-MM-DD>.html/.pdf` using the session date from the transcript or file name.
- Meta line on each page: `Part n of N · <session title or date> · <organisation>`. Take the organisation from the user or transcript; leave it out if unknown.
- Footer glossary: only terms a newcomer would not know, one line each, six at most per page.
- Page numbers are in the template; keep them in sync.

## Files

- `scripts/vtt_to_text.py` cleans transcripts. `scripts/render_pdf.py` renders HTML to PDF and checks overflow (needs Chrome, Edge or Chromium; no Python packages).
- `assets/template.html`: styled starter with every component, including the research page.
- `references/components.md`: when to use each component, with content rules.
- `references/document-types.md`: pages to build for training sessions, meetings and client workshops.
- `references/research-guide.md`: what to research, how to search and cite, how to write for a fresher, and checks before rendering.

