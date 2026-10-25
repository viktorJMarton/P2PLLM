"""Check durable agent workflow instructions and append-only MD meeting receipts.

Checks structure/evidence references, not whether an agent understood a document
or whether unlogged work happened. Independent review remains necessary.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from source_inventory import inventory_bytes

ROOT = Path(__file__).resolve().parents[1]
EVENT = re.compile(r"^## (Iteration (\d+)[^\n]*|Meeting after iteration (\d+)[^\n]*)$", re.M)
RECEIPT = re.compile(r"^- Read: (work/agent-journals/[A-Za-z0-9_-]+\.md) \| bytes: (\d+) \| sha256: ([0-9a-f]{64})$", re.M)


def journal_errors(path: Path, root: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    events = list(EVENT.finditer(text))
    errors = []
    iteration = last_meeting = 0
    for index, event in enumerate(events):
        end = events[index + 1].start() if index + 1 < len(events) else len(text)
        block = text[event.end():end]
        if event.group(2):
            number = int(event.group(2))
            if number != iteration + 1:
                errors.append("iteration counter is not consecutive")
            iteration = number
            if iteration - last_meeting > 3:
                errors.append("more than 3 iterations without a peer meeting")
            continue
        meeting_errors = len(errors)
        number = int(event.group(3))
        if number != iteration or number < 1:
            errors.append("meeting is not bound to the current iteration")
        questions = []
        for line in block.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and re.fullmatch(r"(?:[A-Z][A-Z0-9-]*-)?Q\d+", cells[0]):
                # Response bookkeeping may follow the five-column meeting table
                # before the next iteration and uses an ID/answer table. It is
                # not a new meeting question; the five-question gate remains.
                if len(cells) == 2:
                    continue
                questions.append(cells)
        if len({q[0] for q in questions}) < 5:
            errors.append("meeting requires at least 5 distinct questions")
        for question in questions:
            if len(question) < 5 or any(not cell for cell in question[:5]):
                errors.append("question requires WORK, substance, respondent and status")
            elif len(question[2]) < 20 or not re.search(r"WORK-\d{4}", question[1]):
                errors.append("question must identify a concrete change and WORK")
        receipts = list(RECEIPT.finditer(block))
        if receipts:
            seen = set()
            for receipt in receipts:
                peer = root / receipt.group(1)
                if peer.resolve() == path.resolve() or peer in seen:
                    errors.append("meeting receipt must identify a distinct peer")
                    continue
                seen.add(peer)
                try:
                    data = inventory_bytes(peer)
                    size = int(receipt.group(2))
                    if size <= 0 or size > len(data) or hashlib.sha256(data[:size]).hexdigest() != receipt.group(3):
                        errors.append("peer journal read prefix is missing or rewritten")
                except OSError:
                    errors.append("peer journal receipt does not resolve")
            if len({q[0] for q in questions}) >= 5 and len(errors) == meeting_errors:
                last_meeting = number
        # A genuinely unavailable/initial peer read stays open and cannot reset
        # cadence. Independent work may proceed only within the current budget.
    if not iteration:
        errors.append("journal has no actual iteration entry")
    if not re.search(r"(?:primary )?persona:", text, re.I):
        errors.append("journal must declare its primary professional persona")
    if iteration - last_meeting >= 3:
        errors.append("meeting is due before further development")
    return [f"{path.relative_to(root).as_posix()}: {error}" for error in errors]


def validate(root: Path) -> list[str]:
    issues = []
    required = {
        "AGENTS.md": ["3", "5", "agent-meetings.md", "agents/MEMORY.md"],
        "docs/operations/agent-meetings.md": ["3", "5", "actual", "independent"],
        "agents/MEMORY.md": ["LSN-001", "Evidence", "meeting"],
        "docs/traceability.md": ["3", "5", "agent-meetings.md"],
        "GOVERNANCE.md": ["agent-meetings.md", "autonomy"],
        "templates/agent-journal.md": ["Q1", "Q5", "Respondent", "3", "Persona"],
        "agents/PERSONAS.md": ["3", "5", "MEMORY.md", "agent-meetings.md"],
    }
    for role in (root / "agents").glob("*.md"):
        if role.name not in {"MEMORY.md", "PERSONAS.md"}:
            required[role.relative_to(root).as_posix()] = ["3", "5", "MEMORY.md", "agent-meetings.md",
                "## Persona", "Primary professional persona", "Working lens", "Independent judgment", "Communication", "Avoid"]
    for brief in (root / "work").glob("WORK-*/brief.md"):
        required[brief.relative_to(root).as_posix()] = ["3", "5", "agent-meetings.md", "autonomous"]
    for template in ("handoff.md", "department-handoff.md", "review.md", "pull-request.md", "upstream-report.md"):
        required[f"templates/{template}"] = ["Journal meeting and lesson references", "5", "agent-meetings.md"]
    for name, tokens in required.items():
        try:
            text = (root / name).read_text(encoding="utf-8")
            for token in tokens:
                if token.casefold() not in text.casefold():
                    issues.append(f"{name}: missing policy reference {token!r}")
        except OSError:
            issues.append(f"{name}: missing required policy file")
    journals = sorted((root / "work/agent-journals").glob("*.md"))
    if not journals:
        issues.append("no per-agent MD journal is registered")
    for journal in journals:
        issues.extend(journal_errors(journal, root))
    return issues


def read_peers(root: Path, agent: str):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", agent):
        raise ValueError("invalid agent ID")
    for path in sorted((root / "work/agent-journals").glob("*.md")):
        if path.stem != agent:
            data = inventory_bytes(path)
            print(f"\nFILE {path.relative_to(root).as_posix()}\n{data.decode('utf-8')}")
            print(f"- Read: {path.relative_to(root).as_posix()} | bytes: {len(data)} | sha256: {hashlib.sha256(data).hexdigest()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-peers", metavar="AGENT")
    args = parser.parse_args()
    if args.read_peers:
        read_peers(ROOT, args.read_peers)
        return 0
    issues = validate(ROOT)
    print(json.dumps({"status": "failed" if issues else "passed", "issues": issues}, indent=2))
    return int(bool(issues))


if __name__ == "__main__":
    sys.exit(main())
