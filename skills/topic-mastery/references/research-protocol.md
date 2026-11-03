# Research protocol

Goal: every factual claim in the learning material can be traced to evidence, the reader can see how strong that evidence is, and missing or stale evidence is stated instead of papered over.

## 1. The source ledger (`sources.json`)

Keep one ledger for the whole project, with stable ids that never change between the roadmap and the chapters (a citation `S12` always means the same source).

```json
[{"id":"S12","title":"...","author_or_publisher":"...","url":"https://...","published":"2024-03-28",
  "accessed":"2026-11-02","tier":1,"type":"standard|paper|official-doc|book|course|vendor|blog|dataset|regulation",
  "used_for":["foundations","history"],"notes":"what it supports, caveats, how current it is"}]
```

Rules:
- Add a source only after opening it with `WebFetch` (or the `web-fetch` agent) and reading the relevant part. Search snippets are leads, not evidence.
- Record `accessed` and `published` (or "undated"). Undated pages about fast-moving topics count as stale until corroborated.
- Never invent a URL, title, author, date, figure or quote. If you cannot find evidence, record a gap.
- Paraphrase; do not copy passages. Quote only a few words when the wording matters, with the citation.

## 2. Source tiers

| Tier | What | Use for |
|---|---|---|
| 1 | Primary and authoritative: standards, regulations, original papers, official specifications and documentation, official datasets | Definitions, mechanisms, rules, numbers, dates |
| 2 | Strong secondary: textbooks, university course notes, peer-reviewed surveys, recognised bodies (NIST, ISO, IEEE) | Explanations, history, frameworks |
| 3 | Reputable practitioner: vendor engineering blogs, conference talks, well-known tutorials, industry reports | Practice, case studies, trade-offs (note any commercial interest) |
| 4 | Weak or unverified: forums, social posts, unsourced listicles, AI-generated summaries | Leads only; never the sole support for a claim |

Prefer tier 1 or 2 for any claim a reader might act on. A contested or numeric claim needs two independent sources or an explicit "single source" note.

## 3. Evidence labels in the text

Every substantive passage carries one label so the reader knows what kind of statement it is.

| Label (class) | Meaning | Support needed |
|---|---|---|
| Established (`ev est`) | Agreed fact, definition, standard, well-replicated result | Tier 1 or 2 citation |
| Interpretation (`ev int`) | A reasoned reading, synthesis or comparison of evidence | Cite the evidence; say it is a reading |
| Assumption (`ev ass`) | A premise adopted to make an example or decision work | State it and what changes if it is false |
| Prediction (`ev pre`) | A forecast about the future | Cite the trend data; give uncertainty |
| Gap (`ev gap`) | Evidence missing, conflicting, outdated or paywalled | Say what is missing and what would resolve it |

Use the label at the start of a paragraph, list item or table row. A section made only of well-established material may carry one label for the whole block. Do not label every sentence; label every claim a reader could be misled by.

## 4. Research plan

1. **Scope** (before searching): list the 13 dimensions (see `dimensions.md`) that matter for this topic, adapted to its type. Note what the reader likely already knows.
2. **Broad pass**: find 3 to 5 tier 1 or 2 anchors per dimension (survey papers, official docs, standards, a standard textbook). Do the history and "current state" searches with recent dates, because the present state changes.
3. **Parallelise**: for more than about six dimensions, run research agents in parallel, one per cluster (for example: history and foundations; technical, architecture and advanced; practice and evaluation; applications, business and strategy; security, ethics and governance; expert views and future). Each agent returns, per claim: a plain statement, the source title, publisher, URL it opened, date, tier, and any conflict with another source. Tell agents to use generic concepts in queries.
4. **Depth pass per module**: when teaching a module, run a targeted pass for that module only, and extend the ledger.
5. **Conflict handling**: when sources disagree, present both, say which is stronger and why, and label the result Interpretation or Gap.
6. **Currency check**: for versions, prices, regulations, benchmarks and "state of the art", use the newest official page, state the date, and tell the reader how to re-check.

## 5. Source-coverage gap analysis

Produce a matrix: rows are the 13 dimensions (or the module list), columns are Tier 1, Tier 2, Tier 3, Recency, Confidence. Mark each cell strong, partial or gap, then list for each gap: what is missing, why it matters, and a concrete next step (where to look, who to ask, what experiment would settle it). Be candid: an honest gap list is more useful than complete-looking coverage.

## 6. Hygiene

- Do not put private names, credentials or client identifiers into search queries.
- Distinguish vendor claims from independent evidence.
- Note licensing limits when a source is paywalled; summarise only what you could read.
- If web tools are unavailable, say so at the top of the document, label affected material Gap or "general knowledge, unsourced", and keep it to material you are certain of.
