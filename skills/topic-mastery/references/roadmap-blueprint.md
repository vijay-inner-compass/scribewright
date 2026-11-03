# Roadmap document blueprint

The roadmap is the first deliverable: a complete plan that lets the learner see the whole subject before any chapter is taught. Output `Roadmap_<Topic>.html` and `.pdf`, plus `roadmap.json` and `sources.json` that the chapters reuse.

## Required sections, in order

1. **Cover**: title, subtitle ("Learning roadmap: from first principles to expert decisions"), meta grid (audience, target level, estimated effort, languages C# and Python, date, version).
2. **How to use this roadmap** (half page): the sequence (roadmap, then one major topic at a time), how evidence labels work (legend), how to measure progress.
3. **Contents**.
4. **The mental model** (1 page): one-paragraph definition, an analogy followed by the rigorous version, a diagram described in words, and the **running example** introduced with its starting state and how it will grow.
5. **Topic taxonomy**: a nested outline of major concepts and subtopics (use `h3` per major area and tables or lists of subtopics). It must be comprehensive: foundational and specialised areas, adjacent topics, and tools. Mark each subtopic with the module that teaches it. Show the taxonomy diagram.
6. **Prerequisite map**: a diagram (make_diagram.py) of what must be understood before what, plus a table "Prerequisite | Why needed | Quick check | Where to learn it". Include external prerequisites (maths, programming, domain knowledge) with the fastest route to cover them.
7. **Competence levels**: the four-level ladder from `dimensions.md`, with the topic's own observable skills at each level.
8. **Historical timeline**: `ol.timeline` with year, event, contributor, and significance; mark present state and emerging developments. Cite every date.
9. **Curriculum plan**: a table of major topics (modules) in teaching order: id, title, level reached, dimensions emphasised, prerequisites, estimated hours, assessment. Then one short paragraph per module: objective, what the learner will be able to do, which part of the running example it advances.
10. **Dimension coverage matrix**: modules (rows) against the 13 dimensions (columns), cells `c-strong`, `c-part`, or `c-gap`, so omissions are visible and deliberate.
11. **Source-coverage gap analysis**: the matrix and gap list described in `research-protocol.md`, with next steps for each gap and an honest note on currency.
12. **Assessment and mastery plan**: how progress is measured across modules (checkpoints, capstone, rubric summary) and the final competence statement: what the learner will independently be able to do.
13. **Sources**: `ol.refs` with `li id="S#"`, title, publisher, URL, published and accessed dates, tier.

Length: as long as needed for completeness (typically 12 to 25 pages). Do not shorten the taxonomy, timeline or gap analysis to save space.

## Sizing the curriculum

- Roughly 6 to 14 major topics. Fewer means topics are overloaded; more usually means artificial fragmentation. Each should be teachable as one substantial chapter (20 to 40 pages) without being split mid-concept.
- Order by dependency, then by usefulness to the running example. Place a practical milestone early so motivation survives the theory.
- End with a capstone module that integrates the running example end to end and requires expert-level decisions.
- Every dimension in `dimensions.md` must appear in at least one module at strong coverage, unless a documented exception applies.

## `roadmap.json` (hand-off to chapters)

```json
{
  "topic": "...", "audience": "...", "goal": "...", "target_level": 4,
  "languages": ["python", "csharp"], "organisation": "...", "created": "2026-11-02",
  "running_example": {"name": "...", "description": "...", "growth": ["start state", "after module 3", "..."]},
  "modules": [{
    "id": "M3", "title": "...", "level": 2, "est_hours": 6,
    "prerequisites": ["M1","M2"], "dimensions": [2,3,5,7],
    "objectives": ["..."], "key_questions": ["..."], "source_ids": ["S4","S9"],
    "coverage": {"2":"strong","3":"strong","5":"partial","9":"gap"}
  }],
  "timeline": [{"year":"1958","event":"...","source_id":"S3"}],
  "gaps": [{"area":"...","missing":"...","next_step":"..."}]
}
```

## HTML patterns

All patterns use classes from `assets/learning.css`; see `assets/roadmap-skeleton.html` for a working copy.

- Section heading: `<h1><span class="kicker">Part 5</span>Topic taxonomy</h1>` (h1 starts a new page).
- Evidence legend: `<div class="legend"><span><span class="ev est">Established</span> agreed fact...</span>...</div>`.
- Level cards: `<div class="levels4"><div class="lvl"><h4>1 Beginner</h4><p>...</p></div>...</div>`.
- Diagram: `<figure class="diagram"><!--svg:prereq.svg--><figcaption><b>Figure 2.</b> Prerequisite map.<div class="inwords"><b>In words</b> ...</div></figcaption></figure>`.
- Coverage matrix: `<table class="tbl"><tr><th>Module</th><th>1</th>...<th>13</th></tr><tr><td>M1</td><td class="c-strong">S</td><td class="c-part">P</td><td class="c-gap">G</td>...</tr></table>`, with a one-line legend under it.
- Citations: `<a class="cite" href="#S12">S12</a>`; sources: `<li id="S12"><span class="id">S12</span> ...</li>` inside `<ol class="refs">`.
