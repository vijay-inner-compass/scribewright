# Components

All components live in `assets/template.html`; copy the markup from there. This file says what each is for and the content rules, so the page reads well and fits.

Page skeleton, top to bottom: `.head` (title, tagline, meta) → rows of `.card`s → `.gloss` footer → `.pageno`. Rows: `.row.r2` (wide + narrow), `.r2e` (equal), `.r3`, `.r3w` (wide + two narrow). Add `grow` to a row that should absorb spare height. A page normally has 3 to 4 rows.

| Component | Use it for | Content rules |
|---|---|---|
| Flow strip `.flow` with `.node` (`.hl` highlighted, `.dk` outcome) | The chain or architecture the session explained | 3 to 6 nodes; node title 1-3 words, caption under 6 words. Add a one-sentence lead below with the key figure in bold, and an optional `.sub` line with the teaching point. |
| Decision table `table.tbl` in a `.card.accent` | "If you have X, do Y" choices, option comparisons, field-by-field references | Two columns for choices (situation, action); header in teal. 4 to 8 rows. Put the constraint row ("stop here, because...") last. |
| Facts panel `.card.dark` + `ul.facts` | Numbers, versions, dates, limits, commitments that end debates | 3 to 6 items, each starting with the bold figure, then a `.src` with speaker/timestamp. |
| Steps `ol.steps` in `.card.accent` | Procedures | One action per step, imperative, exact control/command named, include the value to enter. End with a verify step. Max 7 steps; split by platform or route if more. |
| Code `pre.code`, inline `code` | Commands, queries, config, file paths | Only code that was said or shown. Comments in `<span class="c">`. Keep lines under about 70 characters. |
| Breakage list `ul.pts` | "Where it actually breaks" | Each item: bold symptom as the user sees it, then real cause and fix. Include look-alikes. |
| Tiles `.tiles` / `.tile` | A small set of values or shortcuts the reader needs every time (3 or 6) | Label small, value bold. |
| Mnemonic `.mnemo` | Only if the speaker coined a memory aid or ordered checklist | Bold the initial letters. Keep the "named in the session" `.coined` tag. |
| Links `ul.links` | "Go deeper" resources mentioned in the session | Only URLs/documents that were named. Otherwise omit the card. |
| Tinted card `.card.tint` | Secondary material that should look different from procedures | Use at most once per page. |
| Glossary `.gloss` | Terms new to the audience | One line each, max 6. |

## Card choice cheat sheet

- Reader must **decide** → decision table.
- Reader must **do** → steps (+ code).
- Reader must **diagnose** → breakage list (+ a debug-order mnemonic if the speaker gave one).
- Reader must **remember** → tiles, facts panel, glossary.
- Reader must **understand** → flow strip + one lead paragraph.

## Fit tips

- A page is 210 mm tall: roughly a flow card (about 80 px), two mid cards, and a bottom row. Overfull pages are fixed by cutting words, not by reducing font size.
- A card that is more than half empty means the row should hold something else or the content belongs on a shorter page. Rebalance columns rather than leaving gaps.
- Escape `<`, `>` and `&` in code samples (`&lt;`, `&gt;`, `&amp;`).

## Research components

| Component | Use it for | Content rules |
|---|---|---|
| `.card.research` with `<span class="pill">Researched</span>` in the heading | Any content you added from outside the transcript | Dashed accent border marks provenance. Always carry at least one `<sup class="cite">n</sup>` that exists in Sources. |
| Explainer `dl.explain` (Plain, Picture, Example, Why it matters, Mistake) | A concept a beginner must understand | Use only the rows that add value; Plain and Example are the minimum. Two to five rows. |
| Practice path `.levels` / `.level` in a `.card.learn` | A beginner to advanced route | Three levels, two or three concrete tasks each, plus a checkable "ready when" outcome. Start with any exercise the speaker assigned. |
| Sources `ol.refs` | The reference list | Number, title, publisher or author, full URL you opened, access date, one line on why. Mark which sources back facts in the note and which are recommended reading. |
| Tinted `.card.learn` | Learning material that is not a citation (paths, checklists) | One per page. |

Content on research pages should read in this order: prerequisites, core idea, worked example, practice, advanced reading.
