---
name: linkedin-post-generator
description: Turn raw notes, transcripts, meeting summaries, or rough ideas into a series of LinkedIn posts aimed at a goal the user chooses (personal branding, thought leadership, lead generation, hiring, launch announcements, community engagement, and more). Use this whenever the user wants LinkedIn posts, a LinkedIn content series, a post calendar, or wants to repurpose notes or a transcript for LinkedIn, even if they only say "make this into a post", "turn my notes into LinkedIn content", "I want to build my brand on LinkedIn", or "write something for my feed". The skill asks the user to choose the objective, audience, tone, format and post count before writing, so it fits people who are not sure what they want yet.
---

# LinkedIn Post Generator

Turn source material into a batch of LinkedIn posts. Each post should serve an objective the user picked, sound like the user, and be ready to paste into LinkedIn.

The user should be steered through choices, not handed a finished batch they did not shape. Offer options at each decision point, recommend one, and accept whatever they pick.

## Step 1: Read the source material

Read everything the user gave you: pasted notes, files in the working directory, or a transcript. If the source is a file path, read the whole file. Long transcripts can be read in parts.

Pull out, silently at first:
- The core ideas, claims, and any numbers, names, dates, or quotes that can be verified against the source.
- Stories or moments with a concrete detail (a failure, a decision, a surprising result).
- Lessons or opinions the speaker holds.
- Anything sensitive (client names, internal figures, personnel matters). Flag these and ask before using them.
- Whose material it is. A transcript or recording can name other people: an instructor, a guest, a client, or other attendees. Note who they are, and do not name them in the posts unless the user confirms they can be named. Teaching or ideas that belong to someone else must not be presented as the user's own experience. Ask the user whether to credit the source (for example "based on a recent class on Azure data services") or to paraphrase it as shared learning, and ask whether they have permission to share it.

If the notes are thin, say so and ask for one more detail rather than inventing one.

## Step 2: Offer choices

Ask the user to choose before writing. Use the AskUserQuestion tool when it is available, with 2 to 4 options per question, and put your recommended option first with "(Recommended)" in its label. Ask at most four questions per call, and split into a second call if needed.

Cover these, in roughly this order:

1. **Objective** (the most important choice). Offer the options that fit the material best, plus any they name:
   - Personal branding: be known for a specific expertise (recommended when the notes contain a clear point of view)
   - Thought leadership: share a considered opinion on an industry trend
   - Lead generation: attract clients or inquiries for a product or service
   - Hiring / employer branding: attract candidates or show team culture
   - Launch or announcement: promote a product, feature, event, or milestone
   - Engagement / community: start conversations and build a following
2. **Audience**: who should read it (peers, hiring managers, founders, buyers, students, a specific industry). Default to the audience that matches the objective.
3. **Tone**: practical and direct, warm and personal, expert and analytical, bold and opinionated, or light and conversational.
4. **Format mix**: a single post type, or a varied mix. Options include short text posts, story posts (hook, moment, lesson), numbered lists or "lessons" posts, a how-to, a carousel outline (slide-by-slide text for a PDF carousel), and a poll with options.
5. **How many posts** and **over what time frame**: for example 5 posts across two weeks, or 10 posts for a month. Suggest a number that matches the amount of material; do not pad.
6. **Personal details**: whether to write in first person as the user, whether to include the user's name or role, and any hashtags (none, 3 to 5 relevant ones, or a set they supply).
7. **Call to action**: none, a question to the comments, follow or connect, visit a link, DM me, or book a call.

If the user says "you choose", pick the recommended option for each question, state those choices in one line, and continue.

Confirm the full brief in a short summary before writing: objective, audience, tone, formats, count, schedule, CTA. Wait for a yes or a correction.

## Step 3: Plan the series

Before drafting, plan the batch so the posts do not repeat each other:
- Assign each post one angle from the source material and one job (attract, teach, prove, invite).
- Vary the hook style across posts: a bold claim, a question, a specific number, a short story opening, a contrarian statement.
- Keep a simple calendar line for each post (for example "Post 1, Mon: intro to the idea, story format").

Show the plan as a short table (post number, angle, format, objective link) and let the user drop or swap posts before you draft. This is one more chance to offer choices, so keep it brief.

## Step 4: Draft the posts

Use the writing rules in `references/post-craft.md` for hooks, length, line breaks, and CTAs. Use the format templates in `references/formats.md` for each post type. Read those files before drafting.

Rules that apply to every post:
- **Stay true to the source.** Every fact, number, and quote must come from the notes or be clearly marked as general knowledge. If a claim needs support, flag it with `[verify: ...]` instead of guessing.
- **Write in the user's voice.** Use their words and examples where the notes contain them. Avoid corporate filler ("excited to announce", "game-changer", "in today's fast-paced world") and do not use em-dash-heavy rhythm.
- **Keep the hook above the fold.** LinkedIn shows roughly the first two lines before "see more", so the first line must earn the click.
- **Keep it scannable.** Short paragraphs of one to three lines, white space between them, no walls of text.
- **Length.** Most text posts land between 600 and 1,300 characters. Go longer only for story or list formats that need it, and never beyond about 2,500 characters.
- **Hashtags** go at the end, only if the user chose them, and no more than five.
- **One idea per post.** If a post tries to cover two lessons, split it.

## Step 5: Deliver the batch

Save the output to a Markdown file in the working directory so the user can keep it. Use a name like `linkedin-posts-<objective>-<YYYY-MM-DD>.md`. Structure it like this:

```
# LinkedIn post series: <objective>

Brief: <audience> | <tone> | <N> posts | <schedule>

## Post 1: <short angle name>
Format: <format> | Suggested day: <day> | Objective: <objective>

<post text, ready to paste>

Notes for you: <any [verify] flags, sensitive items, or image suggestions>

---
```

After the file is written, give the user a short summary in chat: how many posts, the schedule, any `[verify]` items they must check, and one or two choices to revise. Offer to rewrite any post, change the tone, or regenerate with a different objective. Do not paste the entire batch into chat unless the user asks; the file is the deliverable.

## Revising

When the user asks for changes:
- Change one post at a time when they name one. Do not regenerate the whole batch.
- If they change the objective or tone, re-run Step 3 and Step 4 for the affected posts only, and confirm before overwriting the file.
- Keep a version rather than overwriting silently: rename the old file or append a `-v2` suffix.

## What this skill does not do

- It does not post to LinkedIn or schedule posts. Give the user the text and let them publish it.
- It does not invent results, testimonials, client names, or statistics.
- It does not present someone else's teaching, stories, or experience as the user's own. Paraphrase or credit the source, and only name people the user has confirmed can be named.
- It does not write posts that impersonate someone else or that make claims the user cannot stand behind. If the notes contain something risky (a competitor attack, a confidential detail), flag it and ask before including it.

## Reference files

- `references/post-craft.md`: hooks, length, line breaks, CTAs, and a checklist to run before delivering each post.
- `references/formats.md`: templates for story posts, lesson lists, how-to posts, carousel outlines, polls, and short announcements, plus which objectives each format suits.

Read `references/post-craft.md` before Step 4. Read `references/formats.md` when a chosen format needs its template.
