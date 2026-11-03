# Chapter blueprint (one major topic at a time)

A chapter is a complete, in-depth treatment of one module from `roadmap.json`. It should read like the best chapter of a textbook combined with a lab manual: the reader finishes it able to explain, apply, evaluate, troubleshoot and teach the module's subject. Output `Chapter_<NN>_<Title>.html` and `.pdf`.

Do not trade depth for brevity. Do not split a coherent concept across artificial pieces. A chapter of 20 to 40 pages is normal; add pages rather than cutting essential content.

## Explanation pattern (use for every concept)

For each concept answer, in this order, and label the evidence:

1. **What** it is (precise definition, with the term's origin if it helps).
2. **Why** it exists: the problem it solves and what happens without it.
3. **Analogy**: a clear everyday picture (`.analogy` box), and where the analogy breaks.
4. **How** it works: rigorous mechanism, components, steps, mathematics where relevant (state symbols, show a worked calculation).
5. **When** to use it and when not to (decision rule).
6. **Alternatives** and how it compares (comparison table).
7. **Limits and trade-offs**: failure modes, costs, assumptions.
8. **Worked example** on the running example, with real numbers or data.

## Section order

1. **Chapter opener**: `h1` with kicker "Chapter N", then a `.meta-grid` (level reached, estimated hours, prerequisites, running-example stage), **learning objectives** (observable verbs), **why this matters**, and a **chapter map** (diagram or list of sections).
2. **Mental model and taxonomy** for this module: a short overview before the detail, and a mini-glossary of the terms about to be used.
3. **History and evolution** of this module's subject: milestones, contributors, what changed and why, present state, emerging work. Cite dates. Keep proportionate; link history to design decisions the reader will meet.
4. **Foundations**: definitions, terminology, first principles, prerequisites (with a quick self-check), underlying theory, **common misconceptions** (`.callout.warn`).
5. **Deep technical understanding**: internals, mechanisms, components, processes, mathematics, relationships to adjacent concepts. Use diagrams and worked calculations.
6. **Architecture and frameworks**: models, structures, workflows, design patterns, reference architecture, end-to-end process; at least one diagram plus its description in words.
7. **Practical application**: step-by-step tutorial on the running example with tools, expected outcome at each step, troubleshooting table, and validation. Code in Python and C# (see `code-and-labs.md`).
8. **Advanced concepts**: specialised approaches, recent developments, complex scenarios, alternatives, limitations, trade-offs; use a decision matrix.
9. **Evaluation and improvement**: quality criteria, metrics and how to measure them, test methods, failure analysis, optimisation, how to demonstrate competence.
10. **Real-world applications**: industry examples and case studies (sourced), operational challenges, lessons learned. If no sourced case exists, say so (Gap) and use a clearly labelled hypothetical.
11. **Security, ethics and governance**: risks, applicable standards and regulations (with currency date), accountability, responsible practice, a checklist.
12. **Business and strategic value**: problem identification, decision framework, cost-benefit sketch with stated assumptions, build vs buy, adoption challenges, measurable outcomes.
13. **Expert perspectives**: hard questions, scenario challenges, competing approaches, research gaps, unresolved debates (`.callout.expert`). Present each side fairly and say where evidence is thin.
14. **Future outlook**: trends, opportunities, uncertainties, what to monitor. Everything here is labelled Prediction or Gap unless it is a published roadmap with a date.
15. **Mastery assessment** (see `assessment-design.md`): key takeaways, common mistakes, practical exercises, challenging questions, measurable criteria, self-check checklist.
16. **Answer key and rubrics**.
17. **Coverage note**: dimensions strong, partial or not applicable for this chapter, with reasons, plus gaps found.
18. **Sources**: only the sources cited in this chapter, with the same `S#` ids as the roadmap.

If a section is genuinely not applicable to the module (for example a pure-theory module has no deployment security), keep the heading, write two lines explaining why, and record it in the coverage note. Never delete a section silently.

## Style

- Plain, concrete, active sentences. Define each term at first use, then use it consistently.
- Analogy first, rigour second, and say where the analogy stops.
- Distinguish established facts, interpretations, assumptions and predictions with the evidence labels.
- Use tables for comparisons and decision matrices, steps for procedures, checklists for review.
- Diagrams: every diagram has a caption and an "In words" paragraph so it works for readers who cannot see it.
- No emojis, no filler, no marketing adjectives, no em dashes.
- Show reasoning, not just conclusions: a learner should be able to reproduce a decision, not memorise it.
- Keep the running example consistent: same names, same data, escalating difficulty. State which stage it is at.

## HTML patterns

See `assets/chapter-skeleton.html` for a working copy of each:

- Callouts: `.callout.key` (takeaways), `.callout.warn` (mistakes, misconceptions), `.callout.try` (exercises), `.callout.expert`, `.analogy`.
- Evidence label: `<span class="ev est">Established</span>` (also `int`, `ass`, `pre`, `gap`).
- Code: `<pre class="code" data-lang="python" data-run="yes" data-expect="text">`; output: `<pre class="code out">`.
- Steps: `<ol class="steps">`; checklist: `<ul class="check">`; timeline: `<ol class="timeline">`.
- Difficulty tag on exercises: `<span class="diff">Practitioner</span>`.

## Elaboration standard (explain fully; do not compress)

The reader is learning from scratch and cannot ask you a follow-up question. Write the way a patient expert tutor talks through a problem on a whiteboard: complete paragraphs that say what is happening and why, not clipped notes. A short answer that is correct but leaves the reader to guess the missing step has failed.

For every concept, in prose:

1. **Motivation.** The problem people had before this idea, told as a small story, so the idea feels necessary rather than arbitrary.
2. **Intuition first.** The plain-language picture, with the analogy and where it breaks.
3. **Precise statement.** The definition or rule, with every symbol and term explained the first time it appears.
4. **Walk-through.** The mechanism narrated step by step ("first we... because...; this gives us...; now notice that..."). Show every arithmetic step; never skip algebra or write "it can be shown that" without showing it or citing where.
5. **At least two worked examples.** One tiny with easy numbers so the logic is visible, one realistic on the running example. Add a counter-example or edge case where the idea fails or behaves oddly.
6. **What usually goes wrong.** The misreadings and mistakes, why they are tempting, and how to notice them.
7. **Pause and check.** One quick question per section with the answer and reasoning given straight after, so the reader can test understanding before moving on.
8. **In plain words.** A one- or two-sentence restatement that a beginner could repeat, and a link back to earlier modules and forward to what comes next.

Lists and tables are for things that are naturally lists or comparisons. Do not turn explanation into bullet fragments. Use a heading about every 250 to 350 words so long text stays navigable, and close each major section with a short recap in a `.callout.key` box.

**Length targets** (explanation words, excluding code, source lists and the answer key): a chapter should reach 12,000+ words; every `h2` section at least 500 words; the technical, practical, evaluation and mastery sections at least 900. Verify with
`python scripts/check_doc.py chapter.html --min-words-per-h2 500 --min-total-words 12000 --words`.
If a section is short because the topic is genuinely small, say why in the coverage note instead of padding. Never pad with filler, repeated content or the same point reworded. Elaboration means more reasoning, more worked steps and more examples, not more words for their own sake.

## Lab pack

The practical section is backed by a runnable lab pack, not just snippets in the PDF. See `practical-implementation.md` for the folder layout and rules, and mark code with `data-file` so `scripts/extract_labs.py` can write it out.
