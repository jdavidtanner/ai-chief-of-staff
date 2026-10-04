#!/usr/bin/env bash
# Headless run for one department: works its open, done and rework handoffs, then stops.
#   bin/run-dept.sh marketing
# File tools only by default, so an unwatched run can't send, browse or run commands.
# Give one department more with TOOLS, e.g. TOOLS="Read Write Edit Glob Grep Agent Skill WebSearch WebFetch"
set -euo pipefail
dept="${1:?usage: bin/run-dept.sh <department>}"
cd "$(dirname "$0")/.."
[ -d "departments/$dept" ] || { echo "no departments/$dept"; exit 1; }
tools="${TOOLS:-Read Write Edit Glob Grep Agent Skill}"
today="$(date +%F)"
mkdir -p briefs

claude -p "Use the chief-of-staff skill. Scheduled run for the $dept department only.
For every file in departments/$dept/handoffs/ with Status open or rework: dispatch the role named on it.
For every one with Status done: dispatch reviewer.
Follow the rework and blocked rules in the skill. Don't create new handoffs and don't touch other departments.
Then update departments/$dept/STATUS.md (Last run: $today) and write a five-line summary to briefs/run-$dept-$today.md." \
  --allowedTools $tools \
  --permission-mode acceptEdits < /dev/null
