# Lessons

Each one broke in a real multi-agent setup. Each turned into a rule that now lives in CLAUDE.md, a playbook, or a script. When something breaks in yours, add it here with the date and the rule, then put the rule where agents will load it. A lesson that only lives in this file gets forgotten.

Format: what happened, then the rule.

## 1. Workers follow the latest chat, not their ticket

A worker agent could see the recent conversation. It worked on whatever was discussed last instead of the job it was handed. Nine of twelve tickets in one run went sideways this way. A `WHY YOU ARE HERE` line alone didn't fully fix it: the next day an unrelated message sent mid-run took out nine of nine workers, because the line never said to ignore the chat.

**Rule:** a role agent gets the handoff file and nothing else. Every handoff opens with a `WHY YOU ARE HERE` line (one sentence, one job) and says the owner's latest chat message may be about something else and is not the agent's task. The chief of staff never pastes conversation into a dispatch.

## 2. "Done" without proof

Agents reported work finished that wasn't. Tests that never ran, pages that didn't load, a feature described but not built.

**Rule:** every handoff has a `Done when` list of checkable items. The result has to show proof for each one (a path, a number, a pasted output). A separate reviewer agent checks the proof. The agent that did the work never signs off on it.

## 3. One run ate a week of usage

One big fan-out of agents burned most of a week's plan limit in an afternoon.

**Rule:** before dispatching more than a few agents, check usage and write a one-line estimate (agents times tokens, which models). Over half the week used means a big run needs the owner's yes. Cheap models do reviews and recaps. Expensive models do judgment.

## 4. Two writers, one file

Two agents edited the same database at the same time. Another time two agents committed to the same repo and one undid the other.

**Rule:** one writer per shared resource: a file, a sheet, a database, a repo, an ad account. Others read freely and wait to write. Department STATUS.md is written only by that department.

## 5. A paid campaign launched with settings nobody checked

An ad campaign went live with the wrong setup. Money spent, zero results, and the problem was visible in the settings the whole time.

**Rule:** before anything that spends, sends to a person, deploys or deletes, the agent reads the live settings back and the owner says go. Anything outward-facing is drafted by agents and fired by a human.

## 6. Scheduled jobs that never let things sleep

Several scheduled jobs polled every few minutes at different times. Together they kept a pay-per-use database awake around the clock and the bill showed it.

**Rule:** schedule as rarely as the work allows, and line the jobs up on the same minute so things can sleep in between. Every schedule gets a written reason.

## 7. A review step threw away unsaved work

An automated review-and-fix pass reset the working folder and wiped changes that hadn't been committed.

**Rule:** commit work in progress before any review or repair pass runs.

## 8. Memory said a price that had changed

An agent quoted a price from memory. The price had changed weeks earlier.

**Rule:** a memory that names a price, a file, or a setting is a claim from the day it was written. Check the live source before repeating it. `brain/offers.md` is the source for prices and offers. Copies in pages, ads and emails get checked against it, and it wins.

## 9. Copy invented features

Sales copy promised features that didn't exist and a plan tier that wasn't for sale.

**Rule:** no feature, price, number or result goes in copy unless it's in `brain/`. Missing facts get marked `[NEED OWNER: ...]`, never guessed.

## 10. Re-running slow checks to "confirm a fluke"

Agents re-ran a multi-minute test suite again and again to confirm a failure was a fluke. Each run cost tokens and proved nothing.

**Rule:** green once is green. Three tries max on anything flaky, then fix the cause or report it.

## 11. Background jobs nobody owned

Agents started background processes and walked away. They piled up until the machine slowed down.

**Rule:** agents run checks in the foreground with a timeout and report once. Nothing is left running unless a schedule owns it.

## 12. The shiny idea took over the week

A new tool or idea showed up mid-week and quietly replaced the actual priority for days.

**Rule:** a new idea is not a new priority. Ideas go to `memory/IDEAS.md`. Only the owner promotes one. The chief of staff's drift check says where the time actually went.

## 13. Agents handed the owner a to-do list

Asked to fix something, agents wrote step-by-step instructions for the owner to follow, for tasks they could have done with their own tools.

**Rule:** if an agent can do it with the tools it has, it does it. It only hands something to the owner when that really takes their login, their presence, or their judgment.
