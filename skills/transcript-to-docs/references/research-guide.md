# Research guide: turning a session record into a learning resource

A transcript only holds what was said in the time available. A fresher reading the note later needs the missing foundations, correct definitions and a path to go deeper. This stage adds that, without blurring what the speaker said and what was researched.

## 1. Decide what to research (in this order)

1. **Gaps for a beginner**: every term, tool or concept the speaker used without defining it. Define it plainly.
2. **Claims to verify**: versions, dates, prices, limits, names, statistics and "current" facts in the transcript. Check against an authoritative source; transcripts and ASR are often wrong or out of date.
3. **Promised or implied follow-ups**: homework, "read about X", tools to explore. Find the best beginner resource for each.
4. **Prerequisites and next steps**: what should be understood before this session, and what to learn after.
5. **Common misconceptions and pitfalls** in this topic that newcomers hit.

Aim for 5 to 12 research items per document, not exhaustive coverage. Rank by how much a beginner would be stuck without it.

## 2. How to search

- Use `WebSearch` to find sources and `WebFetch` (or the `web-fetch` agent) to read the page itself. Do not write facts from search snippets alone.
- Prefer, in order: official documentation and standards bodies; the original paper or specification; university course notes and textbooks; reputable vendor engineering blogs; well-regarded tutorials. Avoid content farms, unsourced listicles and AI-generated summaries.
- For anything time-sensitive (versions, pricing, regulations, "latest"), use the current official page and record the access date.
- Two sources for any number or contested claim; one authoritative source is enough for a definition.
- If a topic is large (more than about six items), run research agents in parallel, one per topic cluster, and ask each to return: the plain explanation, the source URL and title, the access date, and any conflict with the transcript.
- If web tools are unavailable, say so in your final message and write only the "explain simply" content you are certain of, labelled as general background without sources. Never invent URLs, titles, authors or figures.

## 3. Keep provenance visible

The reader must always know where a statement came from.

| Source | How it appears |
|---|---|
| Said in the session | Normal cards; cite speaker or timestamp where it matters |
| Added from research | In a `.card.research` with the "Researched" pill, and a numbered citation `<sup class="cite">n</sup>` pointing to the Sources card |
| Researched fact that **disagrees** with the transcript | Show the verified fact, then a line "Session said X; current source says Y" and list it under Verify in your message. Do not silently overwrite the speaker |

Researched content never goes into the facts panel as if the speaker said it.

## 4. Write for a fresher

For each researched concept, use this pattern (short; one card or table row):

1. **Plain definition**: one sentence, no jargon that is not itself defined.
2. **Analogy or picture**: only if it is accurate. Say where the analogy breaks if it does.
3. **Tiny worked example**: real numbers or a real command, small enough to follow by hand.
4. **Why it matters**: the consequence in practice.
5. **Common mistake**: the usual misunderstanding.
6. **Where to learn more**: one best source, cited.

Order learning content from foundations to application: prerequisites, core idea, worked example, practice, then advanced reading. Define each term the first time it appears, then use it consistently.

## 5. Output pages the research adds

Add after the session pages (or instead of padding them):

- **Foundations (before you start)**: prerequisites and a three to six term primer with plain definitions and one analogy each.
- **Go deeper (concept explainers)**: the topics from step 1, using the pattern in section 4.
- **Practice path**: three levels (Beginner, Intermediate, Advanced), each with two or three concrete tasks and the outcome that shows the reader is ready for the next level. Include any exercise the speaker assigned as the first rung.
- **Sources and further reading**: numbered list: title, publisher or author, URL, accessed date, and one line on why it is worth reading. Distinguish "used for facts in this note" from "recommended reading".

If the user asks for a short note only, keep the researched content to one page. Otherwise let the topic decide: a dense technical session usually earns two research pages.

## 6. Quality checks before rendering

- Every researched claim has a citation number that exists in the Sources card.
- Every URL was actually opened and supports the claim. Remove any you did not open.
- No researched statement contradicts the transcript without being flagged.
- Technical content is correct at beginner level; do not oversimplify to the point of being wrong.
- Nothing from the transcript's sensitive-data rule leaks into search queries (no names of private individuals, credentials, client identifiers). Search generic concepts, not session specifics.
