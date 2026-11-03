# Assessment design (end of every major topic)

The goal is evidence that the learner can use the knowledge, not recall it. Assessment is built from the chapter's objectives; every objective is tested at least once, and every test traces to an objective.

## Required parts

1. **Key takeaways** (`.callout.key`): five to eight sentences the learner should be able to say from memory and explain.
2. **Common mistakes** (`.callout.warn`): the errors learners and practitioners really make, why they happen, and how to spot and fix them. Source them where possible (documentation warnings, postmortems, widely reported pitfalls), otherwise label Interpretation.
3. **Practical exercises**: three to six, graded by level (`<span class="diff">Beginner</span>`, Practitioner, Architect, Expert). Each states the task on the running example, the deliverable, and how it is checked. At least one requires building something, one requires debugging a seeded fault, and one requires a written design or decision.
4. **Challenging questions**: five to ten, including scenario-based questions with no single obvious answer and "what would change your mind?" prompts.
5. **Measurable criteria for demonstrating understanding**: a table of observable behaviours per level, each with a pass threshold (for example "explains the mechanism without notes in under three minutes", "reproduces the result within 2 percent", "identifies the injected fault in under 15 minutes").
6. **Self-check checklist** (`ul.check`): "I can..." statements the learner ticks off.
7. **Answer key and rubrics**: model answers with reasoning, common wrong answers and why they are wrong, and a scoring rubric for open-ended work (criteria, levels of performance, what excellent looks like).

## Question design

- Ask the learner to explain, predict, compare, diagnose, design or decide; avoid pure definition recall except for core vocabulary.
- Include at least one transfer question: apply the idea to a context other than the running example.
- Include a teach-back task: "explain this to a colleague who has never seen it" with a rubric.
- Calibrate: label each question's level, and make sure the set spans levels 1 to the chapter's target level.
- For expert-level questions, accept more than one defensible answer and score the reasoning and use of evidence.

## Rubric pattern

| Criterion | Developing | Competent | Expert |
|---|---|---|---|
| Accuracy | Core idea right, details wrong | Correct and complete for the case | Correct, with limits and exceptions stated |
| Reasoning | Asserts conclusions | Justifies with evidence | Weighs alternatives and says what would change the decision |
| Application | Follows the walkthrough | Adapts to a new case | Designs and validates a solution unprompted |
| Communication | Uses terms loosely | Clear explanation | Teaches it, anticipates misunderstandings |

## Capstone (final module)

An integrated scenario on the running example that touches every dimension: define the problem, design the solution, implement a core part in Python and C#, evaluate it, assess security, ethics and governance, build the business case, and defend the decision against a critical reviewer. Provide a rubric. Completing it at the Competent level or above, with a written defence, is the evidence that the learner can independently understand, explain, apply, evaluate, troubleshoot, teach and make expert-level decisions on the subject.
