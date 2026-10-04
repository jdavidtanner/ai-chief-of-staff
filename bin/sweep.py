#!/usr/bin/env python3
"""Check the org. Prints one line per department, then problems. Exit 1 if any.

    python3 bin/sweep.py             sweep this repo
    python3 bin/sweep.py --selftest  check the checker
"""
import csv, datetime, re, sys, tempfile
from pathlib import Path

STALE_DAYS = 3  # fixed threshold; make it per-department if one runs on a slower rhythm
STATUS_KEYS = ("Status:", "Last run:", "Needs owner:", "Next:")
DASHES = re.compile("[\u2013\u2014]")
TEXT_SUFFIXES = {".md", ".py", ".sh", ".csv", ".example"}
MAX_CLAUDE_LINES = 60  # root CLAUDE.md loads every session
MAX_DESC_CHARS = 240  # every agent and skill description loads every session


def status_of(text):
    m = re.search(r"^Status:\s*(\w+)", text, re.M)
    return m.group(1).lower() if m else "missing"


def created_of(text, path):
    m = re.search(r"^Created:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    if m:
        try:
            return datetime.date.fromisoformat(m.group(1))
        except ValueError:
            pass
    return datetime.date.fromtimestamp(path.stat().st_mtime)


def input_paths(text):
    """Paths listed under '## Inputs'. Per bullet: the backticked path, else the first path-like token.
    A trailing note in parentheses, like (Result section), is dropped first."""
    m = re.search(r"^## Inputs[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    paths = []
    for line in (m.group(1).splitlines() if m else []):
        b = re.match(r"\s*(?:[-*]|\d+\.)\s+(?:\[[ xX]\]\s+)?(.*)", line)
        if not b:
            continue
        item = re.sub(r"\([^)]*\)", "", b.group(1))
        tick = re.search(r"`([^`]+)`", item)
        if tick:
            paths.append(tick.group(1).strip())
            continue
        for tok in item.split():
            tok = tok.strip(".,;:")
            if tok.startswith(("http://", "https://")):
                break
            if "/" in tok or re.fullmatch(r"[\w-]+\.[A-Za-z]{2,5}", tok):
                paths.append(tok)
                break
    return paths


def path_exists(root, p):
    p = Path(p).expanduser()
    if p.is_absolute():
        return p.exists()
    return any(root.glob(str(p))) if "*" in str(p) else (root / p).exists()


def description_of(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    d = re.search(r"^description:[ \t]*(.*(?:\n[ \t]+.*)*)", m.group(1), re.M)
    if not d:
        return None
    val = " ".join(x.strip() for x in d.group(1).splitlines()).strip()
    val = re.sub(r"^[>|][-+]?\s*", "", val)  # folded or literal block: the text is the indented lines
    return val.strip("\"'")


def sweep(root, today=None):
    root = Path(root)
    today = today or datetime.date.today()
    problems, lines = [], []

    rows = list(csv.DictReader(open(root / "registry.csv", newline="")))
    agents = {p.stem for p in (root / ".claude/agents").glob("*.md")}
    names = {r["name"] for r in rows}

    for r in rows:
        n, dept = r["name"], r["department"]
        if n == "chief-of-staff":
            if not (root / ".claude/skills/chief-of-staff/SKILL.md").exists():
                problems.append("chief-of-staff skill file missing")
            continue
        if n not in agents:
            problems.append(f"registry has {n} but .claude/agents/{n}.md is missing")
        if dept != "top" and r["status"] == "active":
            pb = root / "departments" / dept / "PLAYBOOK.md"
            if not pb.exists():
                problems.append(f"{n}: departments/{dept}/PLAYBOOK.md missing")
            elif n not in pb.read_text():
                problems.append(f"{n} is active but not in departments/{dept}/PLAYBOOK.md")
    for a in sorted(agents - names):
        problems.append(f".claude/agents/{a}.md has no row in registry.csv")

    cm = root / "CLAUDE.md"
    if cm.exists():
        n = len(cm.read_text().splitlines())
        if n > MAX_CLAUDE_LINES:
            problems.append(f"CLAUDE.md is {n} lines, over {MAX_CLAUDE_LINES}")
    for f in sorted(list((root / ".claude/agents").glob("*.md")) + list((root / ".claude/skills").glob("*/SKILL.md"))):
        d = description_of(f.read_text())
        if d is not None and len(d) > MAX_DESC_CHARS:
            problems.append(f"{f.relative_to(root)}: description is {len(d)} chars, over {MAX_DESC_CHARS}")

    for d in sorted(p for p in (root / "departments").iterdir() if p.is_dir()):
        st = d / "STATUS.md"
        if not st.exists():
            problems.append(f"{d.name}: STATUS.md missing")
        else:
            t = st.read_text()
            if len(t.splitlines()) > 20:
                problems.append(f"{d.name}: STATUS.md over 20 lines")
            for k in STATUS_KEYS:
                if not re.search(rf"^{re.escape(k)}", t, re.M):
                    problems.append(f"{d.name}: STATUS.md missing '{k}'")
        counts = {}
        for h in sorted((d / "handoffs").glob("*.md")):
            t = h.read_text()
            s = status_of(t)
            counts[s] = counts.get(s, 0) + 1
            rel = h.relative_to(root)
            if "## WHY YOU ARE HERE" not in t:
                problems.append(f"{rel}: no WHY YOU ARE HERE section")
            if "## Done when" not in t:
                problems.append(f"{rel}: no Done when section")
            if s == "missing":
                problems.append(f"{rel}: no Status line")
            for p in input_paths(t):
                if not path_exists(root, p):
                    problems.append(f"{rel}: input {p} not found")
            fm = re.search(r"^Follows:[ \t]*(.*)$", t, re.M)
            if fm:
                fv = re.sub(r"\([^)]*\)", "", fm.group(1)).strip().strip("`").strip()
                if fv and fv.lower() != "none" and not path_exists(root, fv):
                    problems.append(f"{rel}: Follows {fv} not found")
            if s == "blocked":
                problems.append(f"{rel}: blocked, needs the owner")
            if s in ("open", "done", "rework") and (today - created_of(t, h)).days > STALE_DAYS:
                problems.append(f"{rel}: {s} for over {STALE_DAYS} days")
        summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items())) or "no handoffs"
        lines.append(f"{d.name}: {summary}")

    for f in sorted(root.rglob("*")):
        if ".git" in f.parts or not f.is_file() or f.suffix not in TEXT_SUFFIXES:
            continue
        if DASHES.search(f.read_text()):
            problems.append(f"{f.relative_to(root)}: has an em or en dash")

    return lines, problems


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        r = Path(tmp)
        (r / ".claude/agents").mkdir(parents=True)
        (r / ".claude/skills/chief-of-staff").mkdir(parents=True)
        (r / ".claude/skills/chief-of-staff/SKILL.md").write_text("x")
        (r / ".claude/agents/writer.md").write_text("---\nname: writer\ndescription: " + "a" * MAX_DESC_CHARS + "\n---\nx")
        (r / ".claude/agents/orphan.md").write_text("---\nname: orphan\ndescription: " + "b" * (MAX_DESC_CHARS + 1) + "\n---\nx")
        (r / "CLAUDE.md").write_text("rule\n" * (MAX_CLAUDE_LINES + 1))
        (r / "brain").mkdir()
        (r / "brain/voice.md").write_text("x")
        (r / "departments/mkt/handoffs").mkdir(parents=True)
        (r / "departments/mkt/PLAYBOOK.md").write_text("- writer: drafts")
        (r / "departments/mkt/STATUS.md").write_text("Status: active\nLast run: never\nNeeds owner: none\nNext: x\n")
        (r / "registry.csv").write_text(
            "name,department,triggers,inputs,outputs,status\n"
            "chief-of-staff,top,a,b,c,active\nwriter,mkt,a,b,c,active\nghost,mkt,a,b,c,active\n")
        h = r / "departments/mkt/handoffs"
        (h / "good.md").write_text(
            "Status: reviewed\nCreated: 2026-01-01\nFollows: departments/mkt/PLAYBOOK.md\n"
            "## WHY YOU ARE HERE\nx\n## Inputs\n- `brain/voice.md` (Result section)\n"
            "- departments/mkt/PLAYBOOK.md (the quality bar)\n- the owner's notes pasted in the Job section\n"
            "## Done when\nx\n")
        (h / "gone.md").write_text(
            "Status: reviewed\nCreated: 2026-01-01\nFollows: departments/mkt/handoffs/nope.md\n"
            "## WHY YOU ARE HERE\nx\n## Inputs\n- `brain/missing.md` (Result section)\n"
            "- brain/also-missing.md (Result section)\n- brain/voice.md\n"
            "## Done when\nx\n")
        (h / "old.md").write_text("Status: open\nCreated: 2026-01-01\n## WHY YOU ARE HERE\nx\n## Done when\nx\n")
        (h / "bad.md").write_text("Created: 2026-01-09\nno sections \u2014 here\n")
        lines, probs = sweep(r, today=datetime.date(2026, 1, 10))
        joined = "\n".join(probs)
        assert "ghost but .claude/agents/ghost.md is missing" in joined, joined
        assert "orphan.md has no row" in joined, joined
        assert "ghost is active but not in" in joined, joined
        assert "old.md: open for over" in joined, joined
        assert "good.md" not in joined, joined
        assert "gone.md: input brain/missing.md not found" in joined, joined
        assert "gone.md: input brain/also-missing.md not found" in joined, joined
        assert "gone.md: input brain/voice.md not found" not in joined, joined
        assert "gone.md: Follows departments/mkt/handoffs/nope.md not found" in joined, joined
        assert f"CLAUDE.md is {MAX_CLAUDE_LINES + 1} lines" in joined, joined
        assert f"orphan.md: description is {MAX_DESC_CHARS + 1} chars" in joined, joined
        assert "writer.md: description" not in joined, joined
        assert "bad.md: no WHY YOU ARE HERE" in joined and "bad.md: no Status line" in joined, joined
        assert "bad.md: has an em or en dash" in joined, joined
        assert lines == ["mkt: 1 missing, 1 open, 2 reviewed"], lines
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    root = Path(__file__).resolve().parent.parent
    lines, problems = sweep(root)
    print("\n".join(lines))
    if problems:
        print("\nProblems:")
        print("\n".join(f"- {p}" for p in problems))
        sys.exit(1)
    print("\nClean.")
