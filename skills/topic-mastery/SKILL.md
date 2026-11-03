---
name: topic-mastery
description: Turn any topic into a comprehensive, research-grounded learning programme that takes a complete beginner to expert-level mastery. First a learning roadmap (taxonomy, prerequisite map, historical timeline, source-gap analysis, curriculum), then one in-depth chapter per major topic covering history, foundations, internals, architecture, hands-on labs with tested Python and C# code, advanced concepts, evaluation, case studies, security and governance, business value, expert debates, future outlook, and a mastery assessment with answer keys. Claims are cited and labelled Established, Interpretation, Assumption, Prediction or Gap. Output is navy/slate/teal PDF and HTML plus runnable lab packs. Use it whenever the user wants to learn a subject deeply or asks for a learning path, curriculum, course, masterclass, study guide or roadmap, or says "teach me X from basics to expert", "make me an expert in", "I know nothing about X" or "deep dive on X".
---

# Topic mastery: from first principles to expert decisions

Build a learning experience that lets the learner independently understand, explain, apply, evaluate, troubleshoot, teach and make expert-level decisions about a subject, not just memorise it. The work happens in two phases that match how people actually learn: see the whole map first, then master one major topic at a time.

Read these as needed (progressive disclosure):
- `references/research-protocol.md`: source ledger, tiers, evidence labels, research plan, gap analysis. Read before researching.
- `references/dimensions.md`: the 13 dimensions, adapting to topic type, the four competence levels, the running example. Read before planning.
- `references/roadmap-blueprint.md`: required roadmap sections and the `roadmap.json` hand-off. Read for phase 2.
- `references/chapter-blueprint.md`: section order and explanation pattern for a chapter. Read for phase 3.
- `references/code-and-labs.md`: Python and C# rules, lab structure. Read before writing code.
- `references/assessment-design.md`: end-of-topic assessment, rubrics, capstone. Read before writing assessments.
- `references/practical-implementation.md`: lab-pack layout and rules so anyone can run the code. Read before writing labs.
- `README.md`: install, requirements, usage prompts and troubleshooting for people using the skill.

## Workflow

### Phase 0: Intake (keep it short)
Take the topic from the user's message. Infer defaults and state them in one line instead of interrogating the user: audience (assume a motivated beginner with general technical literacy), target level (expert, level 4), languages (Python and C#), output (PDF and HTML), organisation name (omit if unknown). Ask at most three questions, and only if the answer would change the plan: prior knowledge, the user's goal or role (for example "decide whether to adopt X" vs "build X"), and any time budget. First run `python scripts/doctor.py` (or `python3`): it checks Python, a Chromium browser, the .NET SDK and internet access, and prints install commands for the user's operating system. Fix required gaps before starting; if only optional items are missing (for example .NET), continue and say what will be marked "not executed". Create a working folder `<Topic>-Mastery/` in the user's chosen location (default: current directory) with `research/`, `roadmap/`, `chapters/`.

### Phase 1: Research the whole subject
Follow `references/research-protocol.md`. Classify the topic type (`dimensions.md`), then research all 13 dimensions broadly. Run parallel research agents for large topics, one per dimension cluster (a proven split: history and foundations; technical and architecture; practice, evaluation and code; advanced, experts and future; applications and business; security, ethics and governance). Require each to open every source and to write `research/cluster-X.json` in the schema documented in `scripts/merge_ledger.py`, then merge with that script to get `research/sources.json`, `findings.md` and `gaps.md`. Read `findings.md` and `gaps.md` to plan; cite findings with `[S#]` shorthand and let `build_doc.py --sources` generate the reference list. Note conflicts and gaps as you go.

### Phase 2: Deliver the roadmap
Follow `references/roadmap-blueprint.md`. Produce, in this order inside one document: mental model with the running example, topic taxonomy, prerequisite map, competence levels, historical timeline, curriculum plan, dimension coverage matrix, and the source-coverage gap analysis. Write `roadmap/body.html`, generate diagrams with `scripts/make_diagram.py`, build with `scripts/build_doc.py`, lint with `scripts/check_doc.py`, render with `scripts/render_pdf.py`, and look at the pages. Save `roadmap/roadmap.json` and `research/sources.json`.
Then show the user the curriculum summary and ask which major topic to start with (default: the first). Do not generate every chapter at once; depth beats speed, and the learner may want to reshape the plan.

### Phase 3: Teach one major topic at a time
For the chosen module, follow `references/chapter-blueprint.md`:
1. Run a targeted deep research pass for that module; extend the ledger (same ids, never renumber).
2. Write the chapter with the full dimension coverage, the explanation pattern (what, why, analogy, how, when, alternatives, limits, worked example) and the running example. Apply the **elaboration standard** in `references/chapter-blueprint.md`: patient, complete prose with every step shown, at least two worked examples per concept, a pause-and-check question per section; not clipped bullets.
3. Write Python and C# code per `references/code-and-labs.md` and `references/practical-implementation.md`, mark files with `data-file`, and run it: `python scripts/run_snippets.py chapter.html`. Fix every failure. Then generate the lab pack with `python scripts/extract_labs.py chapter.html -o labs/` and confirm `python labs/run_all.py` passes.
4. Write the mastery assessment per `references/assessment-design.md`, with answer key and rubrics.
5. Build, then `python scripts/check_doc.py chapter.html --min-words-per-h2 500 --min-total-words 12000 --words --expect-sections "History,Foundations,Deep technical,Architecture,Practical,Advanced,Evaluation,Real-world,Security,Business,Expert,Future,Mastery"`, then render and inspect the pages. Thin sections mean the explanation is too compressed: add reasoning, worked steps and examples, not filler.
6. Report: paths, what the chapter covers, evidence gaps found, code run results, and what the learner should do next. Offer the next module.

After the last module, deliver the capstone chapter (`assessment-design.md`) and a one-page competence review.

## Non-negotiable standards

- **Grounded**: every factual claim is cited from a source you opened; missing, conflicting or outdated evidence is stated as a Gap. No invented references, numbers, quotes or case studies. If web tools are unavailable, say so on the cover and keep to material you are certain of, labelled accordingly.
- **Labelled**: distinguish Established, Interpretation, Assumption, Prediction and Gap with the evidence labels. Future outlook is Prediction or Gap unless backed by a dated published roadmap.
- **Complete**: all 13 dimensions are covered across the curriculum, and each chapter's coverage note says what is strong, partial or not applicable and why. Never drop a dimension silently, and never fragment a coherent concept to keep a section short.
- **Progressive**: beginner to practitioner to architect to expert, with the level each module reaches stated and tested.
- **Understandable**: analogy first then rigour, one consistent running example, terms defined at first use, diagrams always paired with a description in words.
- **Executable**: all code examples run and show real output, or are clearly marked not executed with the reason.
- **Adapted**: set depth, tooling, governance and assessment to the nature of the topic (a regulation is not taught like a framework); say what you adapted.
- **Elaborate**: explain fully, the way a patient tutor would at a whiteboard. Every step shown, every term defined, motivation and intuition before formalism, worked examples with real numbers. Depth comes from reasoning, never from padding.
- **Usable by anyone**: the learner can set up from a clean machine, run the labs with one command, and check their results against stated expected values (`references/practical-implementation.md`).
- **Confidence-building**: each chapter ends with measurable criteria and a self-check checklist so the learner can see their own competence grow.

## Writing and format

- Body fragments only: write `body.html` using the components in `assets/learning.css` (see `assets/roadmap-skeleton.html` and `assets/chapter-skeleton.html`), then `scripts/build_doc.py` wraps them in the shell with running header, page numbers and colour tokens. Change colours only in the `:root` tokens of the CSS.
- Write each body file with the Write tool; never pass long HTML through a shell heredoc.
- Plain, concrete, active sentences. No emojis, filler or em dashes. Neutral, professional tone.
- Do not put private names, credentials or client details into search queries or documents.
- When a doc will be shared, keep file names `Roadmap_<Topic>` and `Chapter_<NN>_<Title>`.

## Scripts (run from this skill's folder; Python 3, Chrome or Edge, optional .NET 10 SDK)

| Script | Purpose |
|---|---|
| `merge_ledger.py research/cluster-*.json -o research/` | Merge parallel research files into `sources.json` (stable S-ids, de-duplicated), `findings.md` (by dimension) and `gaps.md`. Cluster file schema is in the script header |
| `build_doc.py body.html --sources research/sources.json -o doc.html --title ... --running ... --footer ...` | Wrap body in the styled shell; inlines `<!--svg:file.svg-->`; expands shorthand `[S12, S13]` to citations and `{E} {I} {A} {P} {G}` to evidence labels; replaces `<!--refs-->` with the sources actually cited; repeats table headers across pages |
| `make_diagram.py spec.json -o diagram.svg` | Layered diagram (prerequisite map, architecture, workflow) from nodes and edges |
| `check_doc.py doc.html [--expect-sections ...]` | Lint citations, evidence labels, code blocks, placeholders |
| `doctor.py` | Check Python, browser, .NET SDK and internet; print install commands per OS |
| `extract_labs.py chapter.html -o labs/` | Write `data-file` code blocks as real files plus README, `run_all.py` and requirements |
| `run_snippets.py doc.html` | Execute `data-run="yes"` Python and C# blocks and compare to `data-expect` |
| `render_pdf.py doc.html` | PDF via headless Chrome or Edge; reports page count and overflow |
