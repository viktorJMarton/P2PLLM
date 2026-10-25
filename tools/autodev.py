#!/usr/bin/env python3
"""P2PLLM autonomous development coordinator v1.

Stdlib-only, deterministic and fail-closed. Planning is read-only. Execution is
explicit, single-task and bounded; no Git write/push/merge is performed here.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
STATES = {"not_started", "in_progress", "blocked", "verified"}
CRITICAL = {"WORK-0003", "WORK-0005", "WORK-0006", "WORK-0008"}
WEIGHTS = {"impact": 3, "unblocks": 2, "confidence": 1, "effort": -1, "risk": -2}


def read_briefs(root: Path) -> dict[str, dict]:
    entries = {}
    for path in sorted((root / "work").glob("WORK-*/brief.md")):
        content = path.read_text(encoding="utf-8")
        match = re.search(r"^Status:\s*(\w+)\s*$", content, re.MULTILINE)
        id_match = re.match(r"(WORK-\d{4})-", path.parent.name)
        if not match or not id_match or match.group(1) not in STATES:
            raise ValueError(f"Invalid work state: {path}")
        wid = id_match.group(1)
        if wid in entries:
            raise ValueError(f"Duplicate work ID: {wid}")
        before_objective = content.split("## Objective", 1)[0]
        dep_line = re.search(r"^Dependencies:\s*(.+)$", before_objective, re.MULTILINE)
        if dep_line is None:
            raise ValueError(f"Missing dependency declaration: {wid}")
        deps = re.findall(r"WORK-\d{4}", dep_line.group(1))
        entries[wid] = {"id": wid, "status": match.group(1), "depends_on": deps,
                        "brief": path.relative_to(root).as_posix()}
    for wid, entry in entries.items():
        for dep in entry["depends_on"]:
            if dep not in entries or dep == wid:
                raise ValueError(f"Invalid dependency: {wid} -> {dep}")
    visiting, visited = set(), set()

    def visit(wid):
        if wid in visiting:
            raise ValueError(f"Dependency cycle at {wid}")
        if wid in visited:
            return
        visiting.add(wid)
        for dep in entries[wid]["depends_on"]:
            visit(dep)
        visiting.remove(wid)
        visited.add(wid)

    for wid in entries:
        visit(wid)
    return entries


def read_policy(root: Path) -> dict:
    path = root / "config" / "autodev.tasks.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("tasks"), dict):
        raise ValueError("Invalid autonomy task policy")
    return data


def plan(root: Path) -> dict:
    briefs, policy = read_briefs(root), read_policy(root)
    if set(briefs) != set(policy["tasks"]):
        raise ValueError("Policy/brief WORK IDs differ")
    candidates, blocked = [], []
    for wid, entry in briefs.items():
        meta = policy["tasks"][wid]
        if not isinstance(meta, dict) or any(
            not isinstance(meta.get(k), int) or isinstance(meta.get(k), bool)
            or not 1 <= meta[k] <= 5 for k in WEIGHTS
        ):
            raise ValueError(f"Invalid scoring attributes: {wid}")
        if not isinstance(meta.get("instruction"), str) or not meta["instruction"].strip():
            raise ValueError(f"Missing scoped instruction: {wid}")
        unmet = [d for d in entry["depends_on"] if briefs[d]["status"] != "verified"]
        if entry["status"] in ("verified", "blocked"):
            blocked.append({"id": wid, "reason": entry["status"]})
        elif unmet:
            blocked.append({"id": wid, "reason": "dependencies", "unmet": unmet})
        else:
            score = sum(WEIGHTS[k] * meta[k] for k in WEIGHTS)
            candidates.append({"id": wid, "score": score, "status": entry["status"],
                               "brief": entry["brief"], "instruction": meta["instruction"],
                               "security_review": wid in CRITICAL})
    candidates.sort(key=lambda t: (-t["score"], t["status"] != "in_progress", t["id"]))
    return {"schema_version": 1, "selected": candidates[0] if candidates else None,
            "eligible": candidates, "blocked": blocked,
            "status": "ready" if candidates else "no_eligible_work"}


def invoke(root: Path, selected: dict, timeout_seconds: int) -> int:
    if not (root / ".git").exists():
        raise RuntimeError("Execution requires a local Git worktree")
    if subprocess.run(["git", "diff", "--quiet"], cwd=root, check=False).returncode != 0:
        raise RuntimeError("Tracked files modified; refuse unattended execution")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root, check=False).returncode != 0:
        raise RuntimeError("Staged changes present; refuse unattended execution")
    if not shutil_which("codex"):
        raise RuntimeError("codex CLI unavailable")
    run_id = str(uuid.uuid4())
    instruction = (
        f"Run ID {run_id}. Read AGENTS.md, docs/operations/autonomous-development.md, "
        f"{selected['brief']} and required linked sources. "
        f"Implement one bounded, verifiable next step under {selected['id']}. "
        f"Task: {selected['instruction']} "
        "No merge/push, no unsafe plaintext fallback, no external publication, "
        "no declaring security approval. Run relevant checks, report exact command, "
        "exit code, changed files, evidence and blockers. Stop after this single task."
    )
    cmd = ["codex", "exec", "--sandbox", "workspace-write",
           "--ask-for-approval", "never", instruction]
    try:
        return subprocess.run(cmd, cwd=root, timeout=timeout_seconds, check=False).returncode
    except subprocess.TimeoutExpired:
        return 124


def shutil_which(command: str) -> str | None:
    from shutil import which
    return which(command)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "execute"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args(argv)
    try:
        result = plan(args.root.resolve())
        if args.command == "plan":
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["selected"] else 2
        if not 60 <= args.timeout_seconds <= 7200:
            raise ValueError("Timeout must be 60..7200 seconds")
        if not result["selected"]:
            print(json.dumps(result), file=sys.stderr)
            return 2
        # Deliberate manual command boundary: no auto-loop or auto-merge.
        print(json.dumps({"selected": result["selected"]["id"],
                          "mode": "single-bounded-execution", "at": dt.datetime.now(
                              dt.timezone.utc).isoformat()}), flush=True)
        return invoke(args.root.resolve(), result["selected"], args.timeout_seconds)
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as err:
        print(f"autodev: {err}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
