#!/usr/bin/env python3
"""P2PLLM autonomous development coordinator v1.

Stdlib-only, deterministic and fail-closed. Planning is read-only. Execution is
explicit, single-task and bounded; no Git write/push/merge is performed here.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
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


def git_metadata_path(root: Path, name: str) -> Path:
    result = subprocess.run(["git", "rev-parse", "--git-path", name],
                            cwd=root, capture_output=True, text=True, check=True)
    value = Path(result.stdout.strip())
    return value if value.is_absolute() else root / value


@contextlib.contextmanager
def execution_lease(root: Path):
    """Exclusive OS-held lease; automatically released on process death."""
    if os.name != "posix":
        raise RuntimeError("v1 execution lease requires POSIX/Linux")
    lock_path = git_metadata_path(root, "autodev.lock")
    with lock_path.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as err:
            raise RuntimeError("An autonomous task already owns this worktree") from err
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_event(root: Path, event: dict):
    """Append minimal machine-readable metadata, never prompts or subprocess output."""
    path = git_metadata_path(root, "autodev-runs.jsonl")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def invoke(root: Path, selected: dict, timeout_seconds: int) -> int:
    check = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                           cwd=root, capture_output=True, text=True, check=True)
    if check.stdout.strip() != "true":
        raise RuntimeError("Execution requires a local non-bare Git worktree")
    with execution_lease(root):
        status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                                cwd=root, capture_output=True, text=True, check=True)
        if status.stdout.strip():
            raise RuntimeError("Worktree is not clean; refuse unattended execution")
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
        now = lambda: dt.datetime.now(dt.timezone.utc).isoformat()
        append_event(root, {"run_id": run_id, "work_id": selected["id"],
                            "time": now(), "state": "started"})
        exit_code = 3
        try:
            exit_code = subprocess.run(cmd, cwd=root, timeout=timeout_seconds,
                                       check=False).returncode
        except subprocess.TimeoutExpired:
            exit_code = 124
        except KeyboardInterrupt:
            exit_code = 130
        finally:
            append_event(root, {"run_id": run_id, "work_id": selected["id"],
                                "time": now(), "state": "ended",
                                "exit_code": exit_code})
        return exit_code


def shutil_which(command: str) -> str | None:
    from shutil import which
    return which(command)



def run_status(root: Path) -> dict:
    path = git_metadata_path(root, "autodev-runs.jsonl")
    if not path.exists():
        return {"runs": 0, "active_or_unreconciled": [], "last": None}
    starts, ends, last = {}, set(), None
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as err:
            raise ValueError(f"Corrupt run ledger at line {line_no}") from err
        rid, state = event.get("run_id"), event.get("state")
        if not isinstance(rid, str) or state not in ("started", "ended"):
            raise ValueError(f"Invalid run ledger event at line {line_no}")
        if state == "started":
            if rid in starts:
                raise ValueError(f"Duplicate started run {rid}")
            starts[rid] = event
        else:
            if rid not in starts or rid in ends:
                raise ValueError(f"Orphan or duplicate ended run {rid}")
            ends.add(rid)
        last = event
    return {"runs": len(starts),
            "active_or_unreconciled": [starts[k] for k in starts if k not in ends],
            "last": last}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "status", "execute"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(json.dumps(run_status(args.root.resolve()), indent=2))
            return 0
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
