# topic-mastery

Turns any topic into a complete, research-grounded learning programme: first a **learning roadmap**, then **one in-depth chapter per major topic**, each with runnable **Python and C# labs**, an assessment with answer keys, and a PDF and HTML document in an enterprise navy, slate and teal style. Every factual claim is cited and labelled Established, Interpretation, Assumption, Prediction or Gap.

## What you need

| Need | Why | Check | Required? |
|---|---|---|---|
| Claude Code (or a Claude app with skills and agents) | runs the skill | | yes |
| Python 3.8+ | build, lint and test scripts | `python --version` | yes |
| Chrome, Edge or Chromium | renders the PDF | `python scripts/doctor.py` | yes |
| Internet access | web research | | yes for research |
| .NET SDK 10+ | runs the C# examples | `dotnet --version` | optional (C# is then marked not executed) |
| PyMuPDF | preview PDF pages as images | `pip install pymupdf` | optional |

Check everything at once with `python scripts/doctor.py` (use `python3` on macOS or Linux if `python` is missing). It prints what to install for your operating system.

## Install

Copy this whole folder (`topic-mastery`) into one of:

- `<your project>/.claude/skills/` for one project, or
- `~/.claude/skills/` (Windows: `C:\Users\<you>\.claude\skills\`) for all projects.

Or install the packaged `topic-mastery.skill` file from the Claude app. Restart or reload so the skill is picked up.

## Use it (copy and paste)

```
Teach me <topic> from zero to expert.
```

```
I am a <role> and want to be able to <goal> with <topic>. Build me a roadmap, then teach it one module at a time.
```

```
Start Chapter 3 of the <topic> roadmap.
```

Useful extras to add: your current level ("I know basic Python"), your time budget, your languages, your organisation name, or "keep the explanations very detailed".

## What happens

1. **Quick intake** (at most three questions; sensible defaults otherwise).
2. **Research** by parallel agents over 13 dimensions. Sources are opened, graded by tier and stored in a ledger with stable ids.
3. **Roadmap** (PDF and HTML): mental model, taxonomy, prerequisite map, timeline, curriculum, coverage matrix, evidence-gap analysis.
4. **Chapters**, one at a time: history, foundations, internals, architecture, hands-on labs, advanced topics, evaluation, case studies, security and governance, business value, expert debates, future outlook, mastery assessment, answer key.
5. **Lab packs**: real files you can run with `python labs/run_all.py`.

The default folder is `<Topic>-Mastery/` with `research/` (ledger, findings, gaps), `roadmap/`, and `chapters/` (each chapter's PDF, HTML and `labs/`).

## Make it yours

- **Colours**: edit the `:root` values at the top of `assets/learning.css`; everything restyles.
- **Organisation name, header and footer**: pass `--running` and `--footer` to `build_doc.py`, or tell the skill.
- **Depth**: ask for "very detailed". Chapters are checked for at least 500 words per section and 12,000 per chapter.
- **Languages**: Python and C# by default; ask for others and the labs follow.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python` not found | use `python3`, or install Python |
| PDF not produced | install Chrome or Edge; run `doctor.py` |
| C# blocks marked "not executed" | install the .NET 10 SDK |
| A source could not be opened | it is recorded as a Gap; the note says where to look |
| Output seems too short | ask for more detail; run `check_doc.py --words` to see thin sections |

## Honest limits

It can only cite what it can open: paywalled standards, blocked sites and unreadable PDFs become explicit Gaps rather than guesses. Regulations, prices and package versions change, so each document states the date they were read. Expert-level mastery still needs your own practice; the labs and assessments exist so you can prove it to yourself.

## Folder map

`SKILL.md` (the instructions Claude follows), `references/` (method), `assets/` (stylesheet and skeletons), `scripts/` (doctor, merge_ledger, build_doc, make_diagram, check_doc, run_snippets, extract_labs, render_pdf).
