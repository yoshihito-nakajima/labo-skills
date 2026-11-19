"""`labo book next`: the next unit of work for a light coordinator, decided by rules, not by reading cards.

A coordinator (a small model, or a person) is a *table follower*: it calls `next`, does what the one line says,
and calls it again.  `next` only reads state (cards, source-mapping rows, reviews, the review folder, claims) and
answers one of

  RUN       a mechanical command the coordinator executes itself (record a returned review, make review packets);
  DISPATCH  a unit for a fresh worker of a stated tier, with a self-contained prompt file;
  WAIT      nothing to start now (claimed units or open reviews are outstanding); carries a fingerprint so an
            unchanged WAIT need not start a worker;
  BLOCKED   the run cannot judge completion without configuration or a person;
  DONE      the intake is finished: complete, every fact card has a current review, no verbatim run.

Nothing here names a model, a vendor or a host tool.  Roles are tiers: `coordinator` (reads counts, runs commands,
relays) and `worker` (reads and writes mathematics, judges).  A worker prompt is plain Markdown that any LLM host can
be given.  Claims keep two coordinators from handing out the same unit.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import time
from pathlib import Path

from . import book as bk
from . import book_review as rev
from .book import Book, BookError, book_lock

SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "book-harness"
RESULT_RE = re.compile(r"^RESULT:\s*(pass|findings)\b(.*)$", re.I)
CHECKED_RE = re.compile(r"CHECKED:\s*([A-Za-z0-9,\- ]+?)(?=\s+FINDINGS:|$)", re.I)
FINDINGS_RE = re.compile(r"FINDINGS:\s*([A-Za-z0-9,\- ]+|none)", re.I)
ROLES = ("producer", "reviewer", "all")


# ---------------------------------------------------------------- claims and markers


def _slug(unit: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", unit)[:120]


def claims_dir(root: Path) -> Path:
    return Path(root) / bk.INDEX_DIR / "claims"


def active_claims(root: Path, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    out = {}
    d = claims_dir(root)
    if d.is_dir():
        for f in d.glob("*.json"):
            try:
                c = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if c.get("expires", 0) > now:
                out[c["unit"]] = c
    return out


def done_units(root: Path) -> set:
    d = claims_dir(root) / "done"
    return {json.loads(f.read_text(encoding="utf-8"))["unit"] for f in d.glob("*.json")} if d.is_dir() else set()


def release(root: Path, unit: str, done: bool = False) -> str:
    with book_lock(root):
        f = claims_dir(root) / f"{_slug(unit)}.json"
        existed = f.exists()
        if existed:
            f.unlink()
        if done:
            d = claims_dir(root) / "done"
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{_slug(unit)}.json").write_text(json.dumps({"unit": unit, "at": _dt.datetime.now().isoformat()}),
                                                   encoding="utf-8")
    return ("released " if existed else "no claim on ") + unit + (" (marked done)" if done else "")


# ---------------------------------------------------------------- review folder


def parse_result(text: str) -> dict | None:
    """The machine line a reviewer ends a report with: `RESULT: pass|findings [CHECKED: a,b,c|all]`."""
    for line in reversed([x.strip() for x in text.splitlines() if x.strip()]):
        m = RESULT_RE.match(line)
        if m:
            checked = CHECKED_RE.search(m.group(2) or "")
            ids = None
            if checked and checked.group(1).strip().lower() != "all":
                ids = [x.strip() for x in checked.group(1).split(",") if x.strip()]
            found = FINDINGS_RE.search(m.group(2) or "")
            flagged = None
            if found:
                flagged = [] if found.group(1).strip().lower() == "none" else \
                    [x.strip() for x in found.group(1).split(",") if x.strip()]
            return {"result": m.group(1).lower(), "ids": ids, "findings": flagged}
        break
    return None


def packet_state(book: Book, packet: Path, ttl_hours: float) -> dict:
    manifest = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))
    case = packet.parent.parent
    result = case / "result" / f"{packet.name}.md"
    recorded = case / "result" / f"{packet.name}.recorded.json"
    live = [c["id"] for c in manifest["cards"] if c["id"] in book.cards and book.cards[c["id"]].fingerprint() == c["fp"]]
    age = (time.time() - (packet / "manifest.json").stat().st_mtime) / 3600
    if recorded.is_file():
        state = "recorded"
    elif result.is_file():
        state = "returned"
    elif not live or age > ttl_hours:
        state = "void"  # every card changed since, or no answer within the time limit
    else:
        state = "open"
    return {"packet": packet, "result": result, "recorded": recorded, "state": state, "live": live,
            "ids": [c["id"] for c in manifest["cards"]], "unit": f"review:{case.name}/{packet.name}", "kind": manifest.get("kind", "math")}


def packets(book: Book, review_dir: Path | None, ttl_hours: float) -> list:
    if review_dir is None or not Path(review_dir).is_dir():
        return []
    out = []
    for m in sorted(Path(review_dir).glob("*/input/packet-*/manifest.json")):
        try:
            out.append(packet_state(book, m.parent, ttl_hours))
        except (OSError, ValueError, KeyError):
            continue
    return out


def record_from_packet(root: Path, packet: Path) -> dict:
    """Record the result a reviewer wrote beside a packet (`<case>/result/<packet>.md`, ending in a RESULT line)."""
    packet = Path(packet)
    manifest = packet / "manifest.json"
    case = packet.parent.parent
    report = case / "result" / f"{packet.name}.md"
    if not manifest.is_file() or not report.is_file():
        raise BookError(f"no packet at {packet} or no report at {report}")
    parsed = parse_result(report.read_text(encoding="utf-8"))
    if parsed is None:
        raise BookError(f"{report} does not end with a line `RESULT: pass|findings [CHECKED: ids|all]`; "
                        f"send it back to the reviewer instead of guessing")
    out = rev.record_review(Path(root), manifest, report, parsed["result"], None, parsed["ids"], flagged=parsed["findings"])
    out["result"] = parsed["result"]
    (case / "result" / f"{packet.name}.recorded.json").write_text(json.dumps(out), encoding="utf-8")
    return out


# ---------------------------------------------------------------- deciding


def _errors_by_card(result: dict) -> dict:
    by: dict = {}
    for line in result["errors"]:
        code, _, rest = line.partition(" ")
        by.setdefault(rest.split(":", 1)[0], []).append(code)
    return by


def ready_ids(book: Book, route: str, result: dict | None = None) -> list:
    """Fact cards a reviewer should see: split into sections, variant chosen, not stated-only, fresh, no check error."""
    result = result or bk.check(book, route)
    bad = set(_errors_by_card(result))
    stale = {w.split()[1].rstrip(":") for w in result["warnings"] if w.startswith("STALE ")}
    seq = list(dict.fromkeys(e["id"] for e in book.sequence(book.load_route(route)) if e["id"] in book.cards))
    return [i for i in seq if book.cards[i].kind in ("A1", "A2", "A3", "A4", "A5", "A6") and not book.cards[i].legacy
            and book.cards[i].meta.get("variant") != bk.UNCLASSIFIED and book.cards[i].meta.get("status") != "stated"
            and i not in bad and i not in stale and not book.cards[i].meta.get("requires_candidates")]


def _chunks(ids: list, book: Book, limit: int) -> list:
    out, size = [], 0
    for cid in ids:
        n = len(book.cards[cid].body) + 400
        if out and size + n > limit:
            break
        out.append(cid)
        size += n
    return out


def decide(book: Book, route: str, *, workspace: Path, root: Path, role: str = "all", review_dir: Path | None = None,
           work_dir: Path | None = None, source_text: list | None = None, ttl_hours: float = 12.0,
           batch_chars: int = 30000, claim: str | None = None, skip_legacy: bool = False) -> dict:
    if role not in ROLES:
        raise BookError(f"role must be one of {', '.join(ROLES)}")
    producer, reviewer = role in ("producer", "all"), role in ("reviewer", "all")
    with book_lock(root):
        book = Book(root)  # fresh, under the lock
        result = bk.check(book, route)
        status = bk.status(book, route)
        claims = active_claims(root)
        done = done_units(root)
        pks = packets(book, review_dir, ttl_hours)
        data = book.load_route(route)
        seq_ids = list(dict.fromkeys(e["id"] for e in book.sequence(data) if e["id"] in book.cards))
        stale = sorted(w.split()[1].rstrip(":") for w in result["warnings"] if w.startswith("STALE "))
        leak = []
        leak_configured = bool(source_text)
        if leak_configured:
            stats: dict = {}
            leak = rev.leak_check(book, [Path(p) for p in source_text], route=route, stats=stats)
            if not stats.get("words"):
                leak_configured = False
        summary = {"cards": status["cards"], "errors": status["errors"], "legacy": status["legacy"],
                   "stale": len(stale), "candidates_pending": status["candidates_pending"],
                   "scope_audit": status["scope_audit"], "review": status["review"], "complete": status["complete"],
                   "taken_in": status["taken_in"], "leak_hits": len(leak), "leak_checked": leak_configured,
                   "open_packets": sum(1 for p in pks if p["state"] == "open"),
                   "returned_packets": sum(1 for p in pks if p["state"] == "returned"),
                   "claims": sorted(claims)}
        fp = hashlib.sha256(json.dumps([summary, stale, [(p["unit"], p["state"]) for p in pks],
                                        sorted(done)], sort_keys=True, default=str).encode()).hexdigest()[:10]
        base = {"route": route, "role": role, "fingerprint": fp, "summary": summary}
        lc = f"python3 {Path(__file__).resolve().parents[2] / 'scripts' / 'labo.py'}"
        wsroot = f"--workspace {workspace} --root {Path(root).resolve()}"

        def run(cmd, reason):
            return {**base, "action": "RUN", "tier": "coordinator", "reason": reason, "command": f"{lc} book {cmd} {wsroot}"}

        def dispatch(wrole, unit, reason, inputs, instruction, refs, reply):
            if unit in claims or unit in done:
                return None
            prompt = _prompt(wrole, unit, route, workspace, root, inputs, instruction, refs, reply, lc, source_text)
            pf = None
            if work_dir is not None:
                Path(work_dir).mkdir(parents=True, exist_ok=True)
                pf = str(Path(work_dir) / f"{_slug(unit)}.md")
                Path(pf).write_text(prompt, encoding="utf-8")
            if claim:
                d = claims_dir(root)
                d.mkdir(parents=True, exist_ok=True)
                (d / ".gitignore").write_text("*\n", encoding="utf-8") if not (d / ".gitignore").exists() else None
                (d / f"{_slug(unit)}.json").write_text(json.dumps({
                    "unit": unit, "holder": claim, "role": wrole, "at": _dt.datetime.now().isoformat(),
                    "expires": time.time() + ttl_hours * 3600}), encoding="utf-8")
            return {**base, "action": "DISPATCH", "tier": "worker", "worker_role": wrole, "unit": unit, "reason": reason,
                    "inputs": inputs, "prompt_file": pf, "prompt": None if pf else prompt, "claimed_by": claim}

        out = None
        # 1. returned reviews are recorded mechanically (reviewer parent)
        if reviewer and out is None:
            for p in pks:
                if p["state"] == "returned":
                    out = run(f"record-review --packet {p['packet']}", f"a reviewer returned {p['unit']}")
                    break
        # 2. repair check errors, findings, verbatim runs (producer)
        if producer and out is None and result["errors"]:
            out = dispatch("producer", "repair:" + hashlib.sha256("\n".join(result["errors"]).encode()).hexdigest()[:8],
                           f"{len(result['errors'])} check errors", [f"error: {e}" for e in result["errors"][:25]],
                           "Repair these check errors in the cards named, following the skill. Do not widen scope or weaken a "
                           "statement to make a check pass.", ["check-codes.md", "reading-loop.md"],
                           "DONE <unit> | repaired: <ids> | still failing: <ids or none>")
        if producer and out is None:
            for p in pks:
                if p["state"] == "recorded" and p["unit"].startswith("review:"):
                    rec = json.loads(p["recorded"].read_text(encoding="utf-8"))
                    if rec.get("result") == "findings":
                        unit = "triage:" + p["unit"][len("review:"):]
                        out = dispatch("producer", unit, f"{p['unit']} returned findings",
                                       [f"report: {p['result']}", f"packet cards: {', '.join(p['ids'][:40])}"],
                                       "Triage the review report: for each finding that is real, create a finding card "
                                       "(book new D1 ... --target <card> --severity ... --summary ...), repair the cards, "
                                       "anchor the cards that depend on them, run check, and finish with "
                                       "`book release <unit> --done`. A finding that is not a defect needs a recorded reason.",
                                       ["intake-review.md", "reading-loop.md"],
                                       "DONE <unit> | findings: <n real, n declined> | repaired: <ids>")
                        if out:
                            break
        if producer and out is None:
            majors = [c.id for c in book.cards.values() if c.kind == "D1" and c.meta.get("status") == "open"]
            if majors:
                out = dispatch("producer", "findings:" + hashlib.sha256(",".join(sorted(majors)).encode()).hexdigest()[:8],
                               f"{len(majors)} open findings", [f"finding: {m}" for m in majors[:25]],
                               "Repair the cards the open findings are about, then set each finding fixed, or "
                               "resolved-with-reason, and re-anchor dependants.", ["intake-review.md"],
                               "DONE <unit> | fixed: <ids> | resolved: <ids>")
        if producer and out is None and leak:
            out = dispatch("producer", "rewrite:" + hashlib.sha256(",".join(h["id"] for h in leak).encode()).hexdigest()[:8],
                           f"{len(leak)} cards share a verbatim run with a source",
                           [f"card: {h['id']} ({h['run_words']} words)" for h in leak[:25]],
                           "Rewrite these cards in the book's own words (never copy a run of source sentences), then rerun "
                           "the verbatim check.", ["reading-loop.md"], "DONE <unit> | rewritten: <ids>")
        # 3. unfinished source units, legacy cards, candidates, stale cards (producer)
        if producer and out is None:
            todo = [c for c in book.cards.values() if c.kind == "C2" and c.route == route
                    and c.meta.get("scope_audit") in ("TODO", "MISSING", "PARTIAL")]
            todo.sort(key=lambda c: (["TODO", "MISSING", "PARTIAL"].index(c.meta["scope_audit"]), c.id))
            for c in todo:
                src = "; ".join(f"{s.get('src')}: {s.get('loc')}" for s in c.meta.get("sources") or [] if isinstance(s, dict))
                out = dispatch("producer", f"read:{c.id}", f"source row {c.id} is {c.meta['scope_audit']}",
                               [f"mapping card: {c.path.relative_to(book.root)}", f"sources: {src or '(none listed)'}",
                                f"unit: {c.meta.get('unit', '')}"],
                               "Take this source unit into the pool following the reading loop: read the source, search the "
                               "pool, write or reuse cards in the book's own words, fill the mapping row, self-check, "
                               "anchor, run check.", ["reading-loop.md", "templates.md", "examples.md"],
                               "DONE <unit> | cards: <ids> | row now: <state> | open: <obligations or none>")
                if out:
                    break
        if producer and out is None and not skip_legacy:
            legacy = [i for i in seq_ids if book.cards[i].legacy]
            if legacy:
                batch = _chunks(legacy, book, batch_chars)
                out = dispatch("producer", "legacy:" + batch[0], f"{len(legacy)} imported cards not yet split",
                               [f"cards: {', '.join(batch)}"],
                               "Restructure these imported cards into the template's sections (book restructure), choose the "
                               "variant, delete the old '本文', set legacy false; settle their dependency candidates.",
                               ["pool-operations.md", "templates.md"], "DONE <unit> | restructured: <ids>")
        if producer and out is None and not skip_legacy:
            pend = [i for i in seq_ids if book.cards[i].meta.get("requires_candidates")]
            if pend:
                batch = _chunks(pend, book, batch_chars)
                out = dispatch("producer", "deps:" + batch[0], f"{len(pend)} cards have unconfirmed dependency candidates",
                               [f"cards: {', '.join(batch)}"],
                               "For each card decide which candidates are real prerequisites (promote) and which are mere "
                               "mentions (reject).", ["pool-operations.md"], "DONE <unit> | promoted: <n> | rejected: <n>")
        if producer and out is None and stale:
            batch = stale[:40]
            out = dispatch("producer", "reread:" + hashlib.sha256(",".join(batch).encode()).hexdigest()[:8],
                           f"{len(stale)} cards are stale", [f"cards: {', '.join(batch)}"],
                           "Reread each stale card against what it depends on, repair it if needed, then re-anchor it.",
                           ["templates.md", "reading-loop.md"], "DONE <unit> | reread: <ids> | changed: <ids>")
        # 4. reviews (reviewer): make packets for ready cards, hand open packets to a reviewer
        if reviewer and out is None and review_dir is not None:
            covered = {i for p in pks if p["state"] in ("open", "returned") for i in p["live"]}
            open_findings = {c.meta.get("target") for c in book.cards.values() if c.kind == "D1" and c.meta.get("status") == "open"}
            # a card needs a review unless a passing one is current; one with an open finding waits for its repair
            fresh = [i for i in ready_ids(book, route, result)
                     if not book.cards[i].reviewed_ok(book) and i not in covered and i not in open_findings]
            if fresh:
                Path(work_dir or review_dir).mkdir(parents=True, exist_ok=True)
                listing = Path(work_dir or review_dir) / f"cards-for-review-{fp}.txt"
                listing.write_text("\n".join(fresh), encoding="utf-8")
                case = _dt.datetime.now().strftime("r%Y%m%d-%H%M%S")
                out = run(f"review-input --route {route} --cards-file {listing} --out {Path(review_dir) / case / 'input'}",
                          f"{len(fresh)} ready fact cards have no current math review")
            if out is None:
                for p in pks:
                    if p["state"] == "open":
                        out = dispatch("reviewer", p["unit"], "an open review packet has no result yet",
                                       [f"packet: {p['packet']}", f"write the report to: {p['result']}"],
                                       "Review the cards marked REVIEW in the packet as the skill's math review describes. Judge "
                                       "only those cards. Write the report to the path given. End it with exactly one line "
                                       "`RESULT: pass CHECKED: <ids you checked completely>` if you found no defect in them, or "
                                       "`RESULT: findings CHECKED: <ids> FINDINGS: <the ids that have a finding>` otherwise "
                                       "(checked cards not listed under FINDINGS count as passed). Do not edit cards.",
                                       ["intake-review.md", "templates.md"],
                                       "DONE <unit> | report: <path> | RESULT: <pass|findings>")
                        if out:
                            break
        if out is not None:
            return out
        # 5. nothing to start
        if status["taken_in"] and leak_configured and not leak:
            return {**base, "action": "DONE", "tier": "coordinator", "reason": "complete, every fact card reviewed, no verbatim run"}
        if status["taken_in"] and not leak_configured:
            return {**base, "action": "BLOCKED", "tier": "coordinator",
                    "reason": "taken in, but the verbatim check was not run: pass --source-text <dir of the sources' local text>"}
        waiting = sorted(claims) + [p["unit"] for p in pks if p["state"] == "open"]
        if waiting:
            return {**base, "action": "WAIT", "tier": "coordinator", "reason": "outstanding: " + ", ".join(waiting[:6])}
        if reviewer and review_dir is None and status["review"]["never_reviewed"] + status["review"]["reviewed_stale"]:
            return {**base, "action": "BLOCKED", "tier": "coordinator",
                    "reason": "reviews are missing and no --review-dir is configured to put review packets in"}
        return {**base, "action": "WAIT", "tier": "coordinator",
                "reason": "no unit for this role right now" + ("; waiting for the other role" if role != "all" else "")}


# ---------------------------------------------------------------- worker prompt


def _prompt(role, unit, route, workspace, root, inputs, instruction, refs, reply, lc, source_text) -> str:
    files = [SKILL_DIR / "SKILL.md"] + [SKILL_DIR / "references" / r for r in refs]
    lines = [
        f"# Unit `{unit}` (route `{route}`) — role: {role}",
        "",
        "You are a worker with a fresh context. This unit needs a capable model that reads and writes mathematics and "
        "judges; a light coordinator must not do it. Work alone on this unit and stop when it is done.",
        "",
        "## Read first (use any file-reading tool you have)",
        *[f"- {f}" for f in files],
        "",
        "## The unit",
        instruction,
        "",
        *[f"- {i}" for i in inputs],
        "",
        "## How to run the tools",
        f"`{lc} book <action> ... --workspace {workspace} --root {Path(root).resolve()}` (options go after the action).",
        "Use the skill's commands to create, anchor, merge or review cards; hand-edit a card file only to fill its "
        "sections and front matter, in the shapes the skill's examples show.",
    ]
    if source_text:
        lines += ["", "## Local source text (read-only)", *[f"- {p}" for p in source_text],
                  "Read it if you need it. Never copy a run of it into a card, a finding or a report; write in the "
                  "book's own words and record locators only."]
    lines += [
        "",
        "## Rules",
        "- Write only the cards this unit concerns, through the skill's rules. Do not touch other cards, the route's "
        "unrelated rows, Git, or anything outside the book root and the file named for your report.",
        "- Do not ask the user anything; decide by the skill's rules. If you cannot finish, say exactly what is missing.",
        "- Never send card text or source text anywhere outside this machine.",
        "- Do not record that something was independently reviewed unless the skill's commands did.",
        "",
        "## Reply (at most three lines, nothing else)",
        reply.replace("<unit>", unit),
        "",
        f"When finished run `{lc} book release {unit} --workspace {workspace} --root {Path(root).resolve()}`"
        + (" --done" if unit.startswith("triage:") else "") + " so the unit is no longer claimed.",
    ]
    return "\n".join(lines) + "\n"
