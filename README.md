# AI Chief of Staff

An AI team you run from one conversation. You talk to a chief of staff. It hands work to the right role, has a second agent check it, and gives you one brief. Work moves between roles as files on your computer, so you never copy and paste between chats.

Built on Claude Code. No servers, no database, no extra installs. Markdown files and two small scripts.

Lots of repos give you role files. What they skip is the operating layer that keeps a team of agents from drifting off task, writing over each other, burning your usage, or grading their own homework. That layer is most of this repo. Every rule in it came from something that broke in a real setup, listed in [LESSONS.md](LESSONS.md).

## How it works

```
You
 |
 v
chief-of-staff (skill)      the only one you talk to
 |  1. reads registry.csv, picks the role
 |  2. writes a handoff file into that department's handoffs/
 |  3. dispatches the role agent with only that file
 v
role agent                  does the job, fills in Result in the same file
 |
 v
reviewer agent              checks Result against "Done when" before you see it
 |
 v
briefs/YYYY-MM-DD.md        one brief for you, needs-you items first
```

Three files carry everything:

- **Handoff** (`departments/<dept>/handoffs/<date>-<slug>.md`): one file per job. Why the agent is here, the job, inputs, what done looks like, then the result and the review. When one department's output is another's input, the chief of staff writes a new handoff that points at the first one.
- **STATUS.md** (one per department, 20 lines max): status, last run, what needs you, what's next. The chief of staff sweeps these to build your brief.
- **Brief** (`briefs/`): what changed, what needs you, what AI handled, what's blocked.

Around them:

- **The brain** (`brain/`) is the source for business facts, voice, offers and clients. Agents copy from it and don't keep their own version.
- **Memory** (`memory/`) is what happened: decisions, changed facts, outcomes. The brain is what's true. Memory is the history.
- **Role files** (`.claude/agents/`) load their body only when called. Each description line loads every session, used or not, so keep them under 240 characters. `bin/sweep.py` flags longer ones.
- **The registry** (`registry.csv`) is the org chart.

## Why it's built this way

Claude subagents can't start other subagents. So there are no live department heads managing their own team. The chief of staff does all the dispatching, and each department's PLAYBOOK.md tells it who does what and what the quality bar is.

Agents also get handed only the handoff file, not your conversation. An agent that can see your chat will work on whatever you talked about last instead of its job. So every handoff also says the latest chat message may be about something else and isn't the agent's task. That's lesson 1.

## Quick start

```bash
git clone https://github.com/<you>/ai-chief-of-staff
cd ai-chief-of-staff
claude
```

1. Fill in `brain/business.md` and `brain/voice.md`. Twenty minutes is enough.
2. Say `chief of staff, onboard me`. It walks the registry and playbooks with you and fixes what doesn't match your business.
3. Give it real work: `chief of staff, draft Friday's email and find 10 past customers worth a win-back note.`
4. Check the org any time: `python3 bin/sweep.py`.

Handoffs and briefs are gitignored so the public repo stays clean. If this is your private copy, delete those lines from `.gitignore` or back the folders up, since that's where every Result and Review lives.

## Adding roles

Don't write 100 roles up front. Write a role the second time a job shows up. Most roles you'd invent today won't match the work you actually get.

1. Copy any file in `.claude/agents/` and change the role, inputs, outputs and rules.
2. Add a row to `registry.csv`.
3. Add it to its department's `PLAYBOOK.md`.
4. Run `python3 bin/sweep.py`. It fails if those three don't match.

A role isn't free while it sits unused. Its description loads every session, and parking it in `registry.csv` doesn't change that. Delete the agent file and its registry row if you won't use it.

For a large library of ready-made roles, see [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents). Copy only what you need, then do steps 2 to 4.

## Scheduled runs

```bash
bin/run-dept.sh marketing     # works every open handoff in marketing, then stops
```

`bin/schedule.example` has crontab lines. By default a scheduled run can read and write files, dispatch role agents and use skills, and nothing else (no shell, no web, no sending), so a run nobody is watching can't send, browse or run commands. It can still edit files in this repo, so keep the repo in git and read the diff before the next scheduled run. The daily brief line adds two read-only commands. Turn on more per department when it needs it: `sales-researcher` needs `TOOLS="Read Write Edit Glob Grep Agent Skill WebSearch WebFetch"` for the sales department. Web tools mean the run reads text you didn't write, so when you turn them on, make `bin/` and `.claude/` read-only for that run if you can.

They run only while your computer is awake. Use Claude Code cloud routines for overnight work.

## What's here

| Path | What it is |
|---|---|
| `CLAUDE.md` | Operating rules every agent loads every session |
| `LESSONS.md` | What broke and the rule it turned into. Add to it. |
| `registry.csv` | The org chart |
| `brain/` | Business facts, the source of truth |
| `memory/` | Decisions and changed facts, append only |
| `.claude/skills/chief-of-staff/` | The one skill you talk to |
| `.claude/agents/` | Role files and the reviewer |
| `departments/<dept>/` | PLAYBOOK.md, STATUS.md, handoffs/ |
| `templates/` | Handoff and status formats |
| `bin/sweep.py` | Checks registry vs agents vs playbooks, status files, stuck handoffs, handoff inputs, file sizes |
| `bin/run-dept.sh` | Headless run for one department |

## Scaling past one computer

Files work for one person on one machine. Once agents live in more than one place (Claude Code, a phone bot, claude.ai, a second model doing reviews), two upgrades matter:

1. **Shared memory as a service.** Move `memory/` into an MCP memory server every surface reads and writes, so a decision made from your phone shows up in Claude Code.
2. **A message relay.** An MCP relay with threads lets agents ask each other questions and answer without you in the middle.

Start with files. Upgrade when moving files between places becomes the bottleneck.

## How my full setup works

This repo is the small version of what I run every day: a hook that refuses risky shell commands until the agent has written a decision down, a shared memory service, a message relay, a build ledger with a reviewer on another model, and reapers for the processes agents leave behind. [How my AI team actually works](docs/BACKLINE.md) walks through every layer and what broke to make each one. For each idea that fits in plain files, it names the starter file here.

## License

MIT
