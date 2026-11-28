"""`labo book ...`: command line for the book card system (see book.py, book_ops.py, book_review.py)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from . import book as bk
from . import book_ops as ops
from . import book_review as rev
from . import book_receipt as receipts
from . import book_rounds as rounds
from .book import Book, BookError
from .book_borrows import BorrowSnapshots

DEFAULT_ROOT = "local/materials/book"
LOCAL_MATHJAX = "local/cache/mathjax/3.2.2/tex-svg-full.js"
ACTIONS = ("check", "status", "search", "new", "anchor", "borrow", "closure", "impact", "graph", "outline", "render", "read", "html",
           "show", "list", "merge", "rename", "retire", "restructure", "deps", "promote", "reject",
           "review-input", "record-review", "review-receipt", "leak-check", "next", "release", "place")


def register(areas, add_workspace) -> None:
    parser = areas.add_parser("book", help="card system for books: shared pool, routes, graph views, intake review")
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ACTIONS:
        sub = actions.add_parser(name)
        add_workspace(sub)
        sub.add_argument("--root", default=DEFAULT_ROOT, help=f"book root, workspace-relative (default {DEFAULT_ROOT})")
        sub.add_argument("--format", choices=("text", "json"), default="text")
        if name in ("check", "status", "borrow", "graph", "outline", "render", "read", "html", "deps", "review-input", "leak-check", "list", "next"):
            sub.add_argument("--route", required=name in ("borrow", "graph", "outline", "render", "read", "html", "review-input", "next"),
                             help="route slug")
        if name in ("closure", "impact", "graph", "html"):
            sub.add_argument("--candidates", action="store_true",
                             help="also follow requires_candidates (unconfirmed dependency candidates)")
        if name == "search":
            sub.add_argument("query")
            sub.add_argument("--limit", type=int, default=8)
            sub.add_argument("--kind", action="append", help="restrict to a card kind (repeatable)")
        if name == "new":
            sub.add_argument("kind")
            sub.add_argument("id")
            sub.add_argument("--title", default="")
            sub.add_argument("--variant")
            sub.add_argument("--area", dest="pool_area", help="pool directory for a fact card")
            sub.add_argument("--route")
            sub.add_argument("--decision", help="after the pool search: reuse | variant:<id> | new")
            sub.add_argument("--reason")
            sub.add_argument("--proves", help="proof (A3): the claim it proves")
            sub.add_argument("--target", help="finding (D1): the card it is about")
            sub.add_argument("--severity", choices=bk.SEVERITY)
            sub.add_argument("--summary", help="finding (D1): one-line statement")
        if name == "borrow":
            sub.add_argument("id", help="prerequisite card in the owning route")
        if name in ("anchor", "closure", "impact", "show", "restructure"):
            sub.add_argument("ids", nargs="+")
        if name == "list":
            sub.add_argument("--kind")
            sub.add_argument("--area", dest="list_area")
            sub.add_argument("--status")
            sub.add_argument("--stale", action="store_true")
            sub.add_argument("--legacy", action="store_true")
            sub.add_argument("--limit", type=int, default=0)
        if name in ("merge", "rename", "retire"):
            sub.add_argument("--apply", action="store_true", help="do it (default: print the plan)")
        if name == "merge":
            sub.add_argument("keep")
            sub.add_argument("drop")
        if name == "rename":
            sub.add_argument("old")
            sub.add_argument("new")
        if name == "retire":
            sub.add_argument("id")
            sub.add_argument("--reason", required=True)
            sub.add_argument("--force", action="store_true")
        if name == "deps":
            sub.add_argument("--write", action="store_true", help="store candidates as requires_candidates")
        if name in ("promote", "reject"):
            sub.add_argument("id")
            sub.add_argument("--only", help="comma-separated candidates (default: all)")
        if name == "graph":
            sub.add_argument("--out", help="workspace-relative YAML path (default: route/<slug>/dependencies.yaml)")
        if name == "render":
            sub.add_argument("--level", default="L3", choices=sorted(bk.LEVELS))
            sub.add_argument("--out", help="output .tex path (default: print to stdout)")
            sub.add_argument("--standalone", action="store_true", help="a complete document with preamble")
            sub.add_argument("--language", default="ja", choices=sorted(bk.HEADS))
            sub.add_argument("--preamble", help="file with the whole preamble (replaces the built-in one)")
            sub.add_argument("--title")
            sub.add_argument("--term-macro", help="project macro for index terms, e.g. termat -> \\termat{label}{reading}{term}")
            sub.add_argument("--formula-macro", help="project macro for formula index entries, e.g. formulaat")
        if name == "html":
            sub.add_argument("--slice", dest="slice_", help="closure:<id> | impact:<id> | section:<n> | area:<name> "
                                                              "| kinds:A1,A2")
        if name in ("read", "html"):
            sub.add_argument("--name", help="write output/<name>.html (the page is regenerable, so output/ is fine)")
            sub.add_argument("--out", help="write to this path instead")
        if name == "read":
            sub.add_argument("--language", default="ja", choices=("ja", "en"))
            sub.add_argument("--mathjax-bundle", help=f"MathJax SVG bundle to embed (uses {LOCAL_MATHJAX} if present)")
        if name == "review-input":
            sub.add_argument("--out", required=True, help="new folder for the frozen packets (workspace-relative)")
            sub.add_argument("--kind", default="math", choices=("math", "output"))
            sub.add_argument("--max-chars", type=int, default=60000, help="split packets above this size")
            sub.add_argument("--cards", help="comma-separated card ids (their proofs follow)")
            sub.add_argument("--cards-file", help="file with one card id per line")
            sub.add_argument("--section", help="stable route section id or zero-based index")
            sub.add_argument("--closure", help="a card and everything it needs")
            sub.add_argument("--unreviewed", choices=("math", "output"), help="cards without a current review of this kind")
        if name == "record-review":
            sub.add_argument("--packet", help="a packet folder whose reviewer wrote result/<packet>.md ending in a RESULT line "
                                              "(then no other option is needed)")
            sub.add_argument("--manifest")
            sub.add_argument("--report", help="the returned report (stored by hash only)")
            sub.add_argument("--result", choices=("pass", "findings"))
            sub.add_argument("--kind", choices=("math", "output"))
            sub.add_argument("--ids", help="comma-separated ids actually checked (default: the whole packet)")
        if name == "review-receipt":
            sub.add_argument("mode", choices=("prepare", "check", "apply"))
            sub.add_argument("--case", required=True, help="frozen review case directory")
            sub.add_argument("--reviewer", required=True, help="reviewer run ID from host assignment or completion")
            sub.add_argument("--producer", help="producer run ID from the host (prepare)")
            sub.add_argument("--packet", default="packet-01", help="case packet name (prepare)")
            sub.add_argument("--report", default="result/math-review.md", help="case-relative report path (prepare)")
            sub.add_argument("--next-request", help="request file to hand off after a clean receipt (prepare)")
        if name == "next":
            sub.add_argument("--compact", action="store_true", help="one action line for the coordinator (text output)")
            sub.add_argument("--role", default="all", choices=rounds.ROLES, help="the coordinator's role")
            sub.add_argument("--review-dir", help="folder for review packets and their results")
            sub.add_argument("--work-dir", help="folder where worker prompt files are written")
            sub.add_argument("--source-text", action="append", help="local source text for the verbatim check (repeatable)")
            sub.add_argument("--claim", help="claim a dispatched unit for this holder (always pass it when running for real)")
            sub.add_argument("--ttl-hours", type=float, default=12.0, help="claims and unanswered packets expire after this")
            sub.add_argument("--batch-chars", type=int, default=30000)
            sub.add_argument("--skip-legacy", action="store_true",
                             help="carry imported (legacy) cards over as they are: no restructure or dependency units for them")
        if name == "place":
            sub.add_argument("route_name", metavar="ROUTE")
            sub.add_argument("ids", nargs="+")
            sub.add_argument("--section", help="section id, title or index; declare missing sections in chaptered routes")
            sub.add_argument("--after", help="put the cards right after this listed card")
        if name == "release":
            sub.add_argument("unit")
            sub.add_argument("--done", action="store_true", help="mark the unit finished (for units not derived from state)")
        if name == "leak-check":
            sub.add_argument("--source-text", action="append", required=True,
                             help="directory (or file) of local source text, repeatable; never reported or copied")
            sub.add_argument("--ngram", type=int, default=8)
            sub.add_argument("--min-run", type=int, default=12, help="report runs of at least this many words")


def _root(args) -> Path:
    root = Path(args.root)
    return (root if root.is_absolute() else args.workspace / root).resolve()


def _path(args, value: str) -> Path:
    p = Path(value)
    return (p if p.is_absolute() else args.workspace / p).resolve()


def _rel(args, path: Path) -> str:
    """Workspace-relative text; both sides resolved so a symlinked workspace (/tmp on macOS) works."""
    try:
        return str(Path(path).resolve().relative_to(args.workspace.resolve()))
    except ValueError:
        return str(path)


def _emit(args, data, lines) -> None:
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for line in lines:
            print(line)


def _csv(value: str | None) -> list | None:
    return [x.strip() for x in value.split(",") if x.strip()] if value else None


def run(args) -> int:
    root = _root(args)
    act = args.action
    # operations that rewrite cards read fresh under the lock themselves
    if act == "merge":
        lines = ops.merge(root, args.keep, args.drop, args.apply)
        _emit(args, lines, lines + ([] if args.apply else ["(dry run; pass --apply)"]))
        return 0
    if act == "review-receipt":
        case = _path(args, args.case)
        if args.mode == "prepare":
            out = receipts.prepare(case, args.packet, args.report, args.producer, args.reviewer,
                                   _path(args, args.next_request) if args.next_request else None)
            line = f"DISPATCH reviewer={out['reviewer']} assignment={out['assignment']}"
        else:
            if args.producer or args.next_request:
                raise BookError("--producer and --next-request are prepare options")
            out = receipts.receive(root, case, args.reviewer, apply=args.mode == "apply")
            line = f"{out['action']} checked={out['checked']}"
            if out["action"] == "NEXT":
                line += f" request={out['next_request']}"
        _emit(args, out, [line])
        return 0
    book = Book(root)
    if act == "check":
        res = bk.check(book, args.route)
        _emit(args, res, [f"ERROR {e}" for e in res["errors"]] + [f"warning {w}" for w in res["warnings"]]
              + [f"{len(book.cards)} cards: {len(res['errors'])} errors, {len(res['warnings'])} warnings"])
        return int(bool(res["errors"]))
    if act == "status":
        st = bk.status(book, args.route)
        lines = [f"cards: {st['cards']}  errors: {st['errors']}  warnings: {st['warnings']}  legacy: {st['legacy']}  "
                 f"unconfirmed dependency candidates: {st['candidates_pending']}  "
                 f"carried-over legacy cards in the route (not reviewed here): {st['carried_over_legacy']}"]
        lines += [f"  {k}: " + ", ".join(f"{s} {n}" for s, n in sorted(v.items())) for k, v in sorted(st["by_kind"].items())]
        r = st["review"]
        lines += [f"math review of fact cards: current {r['reviewed_current']}, stale {r['reviewed_stale']}, "
                  f"never {r['never_reviewed']} (of {r['math_cards']})",
                  "STALE: " + (", ".join(st["stale"]) or "none"),
                  "open major findings: " + (", ".join(st["open_major_findings"]) or "none"),
                  "scope audit: " + ", ".join(f"{k} {v}" for k, v in st["scope_audit"].items()),
                  "source mappings complete (every C2 OK or OUT, no open major finding, no error): " + str(st["complete"]),
                  "taken in (complete, and every fact card has a current math review): " + str(st["taken_in"])]
        _emit(args, st, lines)
        return 0
    if act == "search":
        hits = bk.search(book, args.query, args.limit, tuple(args.kind) if args.kind else None)
        _emit(args, [{"score": s, "id": c.id, "kind": c.kind, "variant": c.meta.get("variant"), "title": c.meta.get("title"),
                      "status": c.meta.get("status"), "summary": c.summary(100)} for s, c in hits],
              [f"{s:.2f} {c.id} [{c.kind}{'/' + c.meta['variant'] if c.meta.get('variant') else ''}] "
               f"{c.meta.get('title', '')}: {c.summary(80)}" for s, c in hits] or ["no similar card in the pool"])
        return 0
    if act == "new":
        path = bk.new_card(book, args.kind, args.id, title=args.title, variant=args.variant, area=args.pool_area,
                           route=args.route, decision=args.decision, reason=args.reason, target=args.target, proves=args.proves,
                           severity=args.severity, summary=args.summary)
        print("reuse the existing card; nothing written" if path is None else f"wrote {_rel(args, path)}")
        return 0
    if act == "borrow":
        try:
            version = BorrowSnapshots(book).version(args.route, args.id)
        except ValueError as exc:
            raise BookError(str(exc)) from exc
        data = {"card": args.id, "owner": args.route, "version": version}
        _emit(args, data, yaml.safe_dump([data], sort_keys=False).splitlines())
        return 0
    if act == "anchor":
        for cid in args.ids:
            if cid not in book.cards:
                raise BookError(f"unknown card {cid}")
            with bk.book_lock(book.root):
                anchors = bk.set_anchors(book.cards[cid], book)
            print(f"{cid}: " + ", ".join(f"{k}={v}" for k, v in anchors.items()))
        return 0
    if act in ("closure", "impact"):
        book.use_candidates = args.candidates
        for cid in args.ids:
            if cid not in book.cards:
                raise BookError(f"unknown card {cid}")
        if act == "closure":
            ids = book.closure(args.ids)
            lines = ["closure (selected cards and all hard prerequisites): " + ", ".join(ids)]
        else:
            ids = book.impact(args.ids)
            lines = ["impact (changed cards and everything depending on them): " + ", ".join(ids),
                     "reread (anchored prose): " + (", ".join(book.stale_prose(ids)) or "none")]
        _emit(args, {"ids": ids}, lines)
        return 0
    if act == "graph":
        book.use_candidates = args.candidates
        graph = bk.build_graph(book, args.route, args.workspace)
        out = Path(args.out) if args.out else Path(Path(_rel(args, root))) / "route" / args.route / "dependencies.yaml"
        target = _path(args, str(out))
        target.write_text(yaml.safe_dump(graph, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
        print(f"wrote {_rel(args, target)} ({len(graph['nodes'])} nodes); check it with "
              f"`labo dependencies check --graph {_rel(args, target)}`")
        return 0
    if act == "outline":
        data = book.load_route(args.route)
        seq = book.sequence(data)
        outline = bk.route_outline(data, (entry["section"] for entry in seq))
        lines = [f"# {data['title']}", ""]
        for index, heading in outline.items():
            if chapter := heading.get("chapter"):
                title = chapter["title"] or "付録"
                lines.extend((f"## {chapter['number']}　{title} 〔{chapter['id']}〕", ""))
            title = heading["title"] or "付録"
            lines.extend((f"### {heading['number']}　{title} 〔{heading['id']}〕", "",
                          "| カード | 種類・題名 | 直接前提・証明対象 |", "|---|---|---|"))
            heading["cards"] = []
            for entry in (row for row in seq if row["section"] == index):
                card = book.cards.get(entry["id"])
                if card is None:
                    raise BookError(f"missing card in outline: {entry['id']}")
                title = str(card.meta.get("title") or card.id).replace("|", r"\|").replace("\n", " ")
                deps = list(dict.fromkeys(card.requires + ([card.meta["proves"]] if card.meta.get("proves") else [])))
                heading["cards"].append({"id": card.id, "kind": card.kind, "title": title, "requires": deps})
                links = "、".join(f"`{cid}`" for cid in deps) or "—"
                lines.append(f"| `{card.id}` | {card.kind} {title} | {links} |")
            lines.append("")
        _emit(args, list(outline.values()), lines)
        return 0
    if act == "render":
        pre = _path(args, args.preamble).read_text(encoding="utf-8") if args.preamble else None
        text = bk.render_tex(book, args.route, args.level, standalone=args.standalone, language=args.language,
                             preamble=pre, title=args.title,
                             index_macros={k: v for k, v in (("term", args.term_macro), ("formula", args.formula_macro)) if v})
        if args.out:
            target = _path(args, args.out)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            print(f"wrote {target}")
        else:
            print(text)
        return 0
    if act in ("read", "html"):
        from .book_html import build_page, write_page
        name = args.name
        if act == "read":
            from .book_reader import build_reader
            bundle_path = _path(args, args.mathjax_bundle or LOCAL_MATHJAX)
            bundle = bundle_path.read_text(encoding="utf-8") if args.mathjax_bundle or bundle_path.is_file() else None
            page = build_reader(book, args.route, language=args.language, mathjax_bundle=bundle)
            name = name or f"book-{args.route}"
        else:
            book.use_candidates = args.candidates
            page = build_page(book, args.route, args.slice_)
        print(f"wrote {write_page(args.workspace, page, name, str(_path(args, args.out)) if args.out else None)}")
        return 0
    if act == "show":
        infos = [ops.show(book, cid) for cid in args.ids]
        _emit(args, infos, [line for info in infos for line in ops.render_show(info) + ["=" * 60]])
        return 0
    if act == "list":
        cards = ops.list_cards(book, route=args.route, kind=args.kind, area=args.list_area, status=args.status,
                               stale=args.stale, legacy=args.legacy, limit=args.limit)
        _emit(args, [{"id": c.id, "kind": c.kind, "status": c.meta.get("status"), "title": c.meta.get("title")}
                     for c in cards],
              [f"{c.id}  [{c.kind}] {c.meta.get('status', '')}  {c.meta.get('title', '')}" for c in cards]
              + [f"{len(cards)} cards"])
        return 0
    if act == "rename":
        lines = ops.rename(root, args.old, args.new, args.apply)
        _emit(args, lines, lines + ([] if args.apply else ["(dry run; pass --apply)"]))
        return 0
    if act == "retire":
        lines = ops.retire(root, args.id, args.reason, args.apply, args.force)
        _emit(args, lines, lines + ([] if args.apply else ["(dry run; pass --apply)"]))
        return 0
    if act == "restructure":
        for cid in args.ids:
            print(f"rewrote {ops.restructure(root, cid)}: fill the sections, delete '本文', set legacy: false, "
                  f"choose the variant")
        return 0
    if act == "deps":
        result = ops.deps_candidates(root, args.route, args.write)
        lines = [f"{result['cards_with_candidates']} cards cite {result['edges']} cards they do not yet require"
                 + (f"; wrote requires_candidates on {result['written']}" if args.write else " (dry run; --write stores them)")]
        lines += [f"  {k} <- {', '.join(v)}" for k, v in list(result["candidates"].items())[:40]]
        _emit(args, result, lines)
        return 0
    if act in ("promote", "reject"):
        fn = ops.promote if act == "promote" else ops.reject
        moved = fn(root, args.id, _csv(args.only))
        print(f"{act}: {', '.join(moved) or 'nothing'}"
              + ("" if moved else " (candidates exist only after `book deps --write`)"))
        return 0
    if act == "review-input":
        cards = _csv(args.cards)
        if args.cards_file:
            cards = [x.strip() for x in _path(args, args.cards_file).read_text(encoding="utf-8").splitlines() if x.strip()]
        sel = {"cards": cards, "section": args.section, "closure": args.closure, "unreviewed": args.unreviewed}
        dirs = rev.review_input(book, args.route, _path(args, args.out), args.kind, args.max_chars, **sel)
        for d in dirs:
            print(f"wrote {_rel(args, d)}")
        return 0
    if act == "next":
        out = rounds.decide(book, args.route, workspace=args.workspace, root=root, role=args.role,
                            review_dir=_path(args, args.review_dir) if args.review_dir else None,
                            work_dir=_path(args, args.work_dir) if args.work_dir else None,
                            source_text=[str(_path(args, p)) for p in args.source_text or []] or None,
                            ttl_hours=args.ttl_hours, batch_chars=args.batch_chars, claim=args.claim,
                            skip_legacy=args.skip_legacy)
        if args.format == "json":
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            head = f"{out['action']} tier={out['tier']}"
            if args.compact:
                head += f" FINGERPRINT={out['fingerprint']}"
            if out["action"] == "DISPATCH":
                head += f" worker_role={out['worker_role']} unit={out['unit']} prompt={out.get('prompt_file') or '(inline)'}"
            if out["action"] == "RUN":
                head += f" command: {out['command']}"
            if args.compact:
                if out["action"] in ("WAIT", "BLOCKED"):
                    head += f" {out['reason']}"
                print(head)
                return 0
            print(head)
            print(f"reason: {out['reason']}")
            print(f"FINGERPRINT={out['fingerprint']}")
            s = out["summary"]
            print(f"state: cards {s['cards']} errors {s['errors']} legacy {s['legacy']} stale {s['stale']} "
                  f"audit {s['scope_audit']} review never {s['review']['never_reviewed']} stale {s['review']['reviewed_stale']} "
                  f"open packets {s['open_packets']} returned {s['returned_packets']} complete {s['complete']} "
                  f"taken_in {s['taken_in']} leak_checked {s['leak_checked']}")
        return 0
    if act == "place":
        placed = ops.place(root, args.route_name, args.ids, args.section, args.after)
        print("placed: " + (", ".join(placed) or "nothing (already in the route)"))
        return 0
    if act == "release":
        print(rounds.release(root, args.unit, args.done))
        return 0
    if act == "record-review":
        if args.packet:
            res = rounds.record_from_packet(root, _path(args, args.packet))
            _emit(args, res, [f"recorded {len(res['recorded'])} cards as {res['result']}", "changed since the packet (not reviewed): "
                              + (", ".join(res["changed_since_packet"]) or "none")])
            return 0
        if not (args.manifest and args.report and args.result):
            raise BookError("record-review needs --packet, or all of --manifest, --report and --result")
        res = rev.record_review(root, _path(args, args.manifest), _path(args, args.report), args.result, args.kind,
                                _csv(args.ids))
        _emit(args, res, [f"recorded {len(res['recorded'])} cards", "changed since the packet (not reviewed): "
                          + (", ".join(res["changed_since_packet"]) or "none"),
                          "not in --ids: " + (", ".join(res["not_listed"]) or "none")])
        return 0
    if act == "leak-check":
        stats: dict = {}
        hits = rev.leak_check(book, [_path(args, p) for p in args.source_text], route=args.route, ngram=args.ngram,
                              min_run=args.min_run, stats=stats)
        if not stats.get("words"):
            raise BookError("no source words were read: check the --source-text paths (an empty scan proves nothing)")
        if args.format == "text":
            print(f"scanned {stats['files']} files, {stats['words']} source words (not reported)")
        _emit(args, hits, [f"VERBATIM {h['id']}: {h['run_words']} consecutive words also in a source text: "
                           f"\"{h['card_words']}\"" for h in hits]
              + [f"{len(hits)} cards share a run of at least {args.min_run} words with the given source text"])
        return int(bool(hits))
    raise BookError(f"unknown action {act}")
