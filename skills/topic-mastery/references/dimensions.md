# The 13 dimensions and how to adapt them

Cover all thirteen dimensions across the curriculum. Not every module needs every dimension in equal weight, but nothing important may be silently dropped: if a dimension is thin or not applicable for a module, say so in the chapter's coverage note and give the reason.

| # | Dimension | What "covered" looks like | Typical evidence |
|---|---|---|---|
| 1 | History and evolution | Origins, context, milestones with dates, key contributors, breakthroughs, present state, emerging developments; a timeline | Papers, histories, standards revisions |
| 2 | Foundations | Definitions, terminology, mental models, first principles, prerequisites, underlying theory, common misconceptions | Textbooks, standards, official glossaries |
| 3 | Deep technical understanding | Internal mechanisms, components, processes, the mathematics where relevant, links to adjacent concepts | Specs, papers, source documentation |
| 4 | Architecture and frameworks | Models, structures, workflows, design patterns, reference architectures, end-to-end processes, diagrams | Reference architectures, standards, docs |
| 5 | Practical application | Step-by-step tutorials, worked examples, exercises, tools, implementation, expected outcomes, troubleshooting, validation | Official tutorials, tested code |
| 6 | Advanced concepts | Specialised approaches, recent developments, complex scenarios, alternatives, limits, trade-offs | Surveys, recent papers, expert talks |
| 7 | Evaluation and improvement | Quality criteria, metrics, test methods, failure analysis, optimisation, how competence is shown | Standards, benchmarks, evaluation literature |
| 8 | Real-world applications | Industry examples, case studies, operational challenges, lessons learned | Case studies, postmortems, industry reports |
| 9 | Security, ethics, governance | Risks, standards, regulations, accountability, responsible practice | Regulators, ISO/NIST, OWASP and similar |
| 10 | Business and strategic value | Problem identification, decision frameworks, cost-benefit, build vs buy, adoption, measurable outcomes | Industry analyses, TCO studies, adoption research |
| 11 | Expert perspectives | Hard questions, scenario challenges, competing approaches, research gaps, open debates | Position papers, practitioner debates |
| 12 | Future outlook | Trends, opportunities, uncertainties, what to monitor | Roadmaps, research agendas, market data |
| 13 | Coding examples | Working, tested C# and Python that follow the running example | Official docs and the code you ran |

## Adapting depth to the topic type

Identify the type first; it changes which dimensions carry the weight.

| Topic type | Weight up | Weight down or reshape |
|---|---|---|
| Software or AI technology | 3, 4, 5, 7, 9, 13 | 1 short unless the history explains the design |
| Mathematics or science | 2, 3, 6, 11; derivations and proofs | 4 becomes "models and structures"; 13 as computation, simulation |
| Standard, regulation or compliance | 9, 10, 8 (enforcement cases), 11 | 13 becomes tooling for evidence, checks and automation |
| Business, strategy or management method | 10, 8, 7, 11, 4 (frameworks) | 3 becomes "how the method works"; 13 as models, spreadsheets, analysis scripts |
| Engineering practice or process | 4, 5, 7, 8 | 13 as scripts and automation around the process |
| Soft skill or domain craft | 2, 5, 7, 8, 11 | 3 and 13 shrink; practice scenarios and rubrics expand |

When code is not meaningful for a topic, still deliver dimension 13 as the nearest honest equivalent (calculation, simulation, data analysis, automation of a check) and say why.

## Level ladder (use across the whole curriculum)

| Level | The learner can | Evidence of competence |
|---|---|---|
| 1 Beginner | Explain core terms and the mental model; follow a guided example | Correct explanation in own words; reproduces a worked example |
| 2 Practitioner | Apply the method to a new case; use the tools; troubleshoot common failures | Completes a lab without the walkthrough; fixes a seeded fault |
| 3 Architect / specialist | Design end-to-end solutions; choose between alternatives; evaluate quality and risk | A written design with justified trade-offs and a test plan |
| 4 Expert | Judge edge cases and open questions; critique the literature; teach; decide under uncertainty | Defends a decision against counter-arguments; identifies what evidence would change it |

Each module states which level it takes the learner to, and the measurable criteria for that level.

## Running example

Choose one realistic example that can carry the whole curriculum (a company, a product, a system, a dataset). It should be simple enough for a beginner and rich enough to need expert decisions later. Reuse it in every chapter: the same entities, data and constraints, growing in complexity. Record it in `roadmap.json` so every chapter uses it.
