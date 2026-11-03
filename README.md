# Claude skills

Three Claude skills for turning notes, transcripts and topics into learning material and LinkedIn content.

| Skill | What it does | Input | Output |
|---|---|---|---|
| [`transcript-to-docs`](skills/transcript-to-docs/) | Turns a meeting, class or call transcript into enterprise-styled study notes, with researched background and cited sources | `.vtt`, `.srt`, `.txt` or pasted text | HTML and a landscape A4 PDF |
| [`topic-mastery`](skills/topic-mastery/) | Takes any topic from beginner to expert: a learning roadmap, then one chapter per major topic with runnable Python and C# labs and assessments | A topic, plus optional level and goals | Roadmap and chapter PDFs and HTML, lab packs |
| [`linkedin-post-generator`](skills/linkedin-post-generator/) | Turns notes into a series of LinkedIn posts for an objective you choose, after asking you about audience, tone, format and count | Notes, transcripts or rough ideas | A Markdown file with the posts, ready to paste |

## Requirements

- [Claude Code](https://claude.com/claude-code), or a Claude app that supports skills.
- Python 3.8 or newer (`transcript-to-docs` and `topic-mastery`). Check with `python --version`.
- Chrome, Edge or Chromium, for PDF output (`transcript-to-docs` and `topic-mastery`).
- Optional: the .NET SDK 10 or newer, to run the C# examples in `topic-mastery`.

`topic-mastery` ships a checker. Run `python skills/topic-mastery/scripts/doctor.py` from this folder to see what is missing and how to fix it on your system.

## Install

A skill is a folder that contains a `SKILL.md` file. Copy the skill folders into one of these locations:

- **All projects** (recommended): your user skills folder.
  - Windows: `C:\Users\<you>\.claude\skills\`
  - macOS or Linux: `~/.claude/skills/`
- **One project only**: that project's `.claude/skills/` folder.

Install one skill:

```bash
cp -r skills/transcript-to-docs ~/.claude/skills/
```

Install all three:

```bash
cp -r skills/* ~/.claude/skills/
```

On Windows PowerShell, use:

```powershell
Copy-Item -Recurse skills\* "$env:USERPROFILE\.claude\skills\"
```

Then restart Claude Code, or start a new session, so the skills are loaded. To confirm, ask Claude "what skills do you have?" or type the skill name after a slash.

### Other coding agents

The skills follow the open [Agent Skills](https://agentskills.io) format, so any agent that reads `SKILL.md` folders can use them. Copy each skill folder into that agent's global skills folder. Pick the agents you use:

| Agent | Global skills folder |
|---|---|
| Claude Code | `~/.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| GitHub Copilot CLI | `~/.copilot/skills/` |
| Cursor | `~/.cursor/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Amp, Replit and other universal agents | `~/.config/agents/skills/` |

Folder names are taken from the agents' published paths and may change between versions. Check your agent's documentation if a skill does not load.

Or use the [skills CLI](https://github.com/vercel-labs/skills), which detects the agents you have installed and copies the skills to them:

```bash
npx skills add vijay-inner-compass/claude-skills --skill '*' -g
```

The CLI runs third-party code from npm. Review it first if you are installing on a shared or work machine.

## Use them

### transcript-to-docs

Give Claude a transcript file or paste the text. Say what kind of document you want, or let the skill decide.

Example prompts:

```
Turn C:\Recordings\kubernetes-workshop.vtt into study notes for freshers.
```

```
Make a one-pager and a decision record from this meeting transcript: <paste text>
```

What happens: the skill reads the whole transcript, writes pages from the session content, then adds researched background. Researched content is labelled and cited, so you can tell what came from the speaker and what was checked online.

### topic-mastery

Name a topic and your goal. The skill asks at most three questions, then does research, builds a roadmap, and writes chapters one at a time.

Example prompts:

```
Teach me distributed systems from zero to expert.
```

```
I am a backend developer and want to design event-driven systems with Kafka. Build me a roadmap, then teach it one module at a time.
```

```
Start Chapter 3 of the distributed-systems roadmap.
```

Run the labs for a chapter from that chapter's folder:

```bash
python labs/run_all.py
```

The default output folder is `<Topic>-Mastery/`. Keep that folder out of this repository, since it is generated for you.

### linkedin-post-generator

Give Claude notes or a transcript, and say you want LinkedIn posts. The skill then asks you to choose:

1. Objective: personal branding, thought leadership, lead generation, hiring, launch announcement, or engagement.
2. Audience: engineers, hiring managers, business leaders, or another group.
3. Tone: practical, warm and personal, or expert and analytical.
4. Format mix and post count: for example five mixed posts, three text posts, or eight posts with a carousel outline.
5. Call to action, hashtags, and whether to write in first person.

After you confirm, it shows a plan, drafts the posts, and saves a Markdown file in your working folder.

Example prompt:

```
Turn the notes in C:\Notes\cloud-data-session.txt into five LinkedIn posts. I want thought leadership for business leaders, in an expert tone.
```

Example of the output structure (the content depends on your notes):

```markdown
# LinkedIn post series: Thought leadership

## Post 1: <angle>
Format: Hot take | Suggested day: Monday

<post text, ready to paste>

Notes for you: <items to verify, and any names to check before publishing>
```

If the notes name other people, the skill asks before naming them, and it credits or paraphrases someone else's teaching rather than presenting it as your own.

## Keep outputs out of your repository

These skills write generated files into the folder where you run them: PDFs, HTML, lab packs, research ledgers, and LinkedIn Markdown files. Keep them out of any repository. The `.gitignore` in this repository already excludes the common names.

## Layout

```
skills/
  transcript-to-docs/
  topic-mastery/
  linkedin-post-generator/
```

## Licence

Add a licence before you share this repository publicly.
