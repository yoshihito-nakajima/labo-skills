"""Readable and JSON-safe research workflows without an MCP server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import sys

import yaml

from .build import (
    DEFAULT_OUTPUT_MAX_FILES,
    ENGINE_FLAGS,
    open_default_viewer,
    output_transaction,
    prune_output,
    run_build,
    run_source_build,
)
from .evidence import EvidenceError, KINDS, check_evidence, init_catalog, snapshot
from . import exploration
from .layout import LayoutError, init_layout, new_item
from .paper import PaperError, map_openings, read_section
from .plans import PlanError, ResearchPlan, read_workspace
from .reader import ReadingError
from .workspace import WorkspaceError, resolve_workspace


def _filtered(
    plans: list[ResearchPlan], status: str | None, tag: str | None, search: str | None,
) -> list[ResearchPlan]:
    return [
        plan for plan in plans
        if (not status or plan.status == status)
        and (not tag or tag in plan.tags)
        and (not search or search.casefold() in
             f"{plan.slug} {plan.title} {plan.summary}".casefold())
    ]


def _workspace(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", type=Path,
                        help="private labo workspace (repository launcher defaults to its Git superproject)")


def _diagnostic_result(result: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(result["status"].upper())
    if "research" in result:
        print(f"research/{result['research']}: {result['adoption']}")
        for claim in result["claims"]:
            counts = ", ".join(f"{kind}={count}" for kind, count in claim["current_reviews_by_kind"].items())
            print(f"[{claim['evidence_status']}] {claim['id']}: "
                  f"structure={claim['structure']}; current reviews: {counts or 'none'}")
            if claim["attention"]:
                print("  attention: " + ", ".join(claim["attention"]))
        for record in result["records"]:
            print(f"[{record['state']}] {record['path']}")
        if not result["claims"]:
            print("No catalog claims recorded; this is not a statement about the research's completeness.")
    elif "dependencies" in result:
        for dependency in result["dependencies"]:
            print(f"[{dependency['kind']}] {dependency['path']}")
        for path in result["omitted"]:
            print(f"not covered by selected inputs: {path}")
        print("Scope discovery does not expand a snapshot or prove TeX dependency completeness.")
    for issue in result.get("issues", []):
        print(f"{issue['severity']}: {issue['path']}: {issue['message']}")
    limits = result.get("limits", result.get("limitations", []))
    if isinstance(limits, str):
        limits = [limits]
    for limit in limits:
        print(f"limit: {limit}")


def _replay_result(result: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"{result['status'].upper()}: selected-source Lean replay")
    print(f"{result['catalog']}#{result['claim']}: {result['declaration']}")
    print(f"Source: {result['source']}; toolchain: {result['toolchain']['pin']}")
    print(f"Preflight ready: {result['preflight']['ready']}; executed: {result['executed']}")
    for problem in result["preflight"]["problems"]:
        print(f"unavailable: {problem}")
    for index, command in enumerate(result["commands"], 1):
        print(f"{index}. [{command['status']}] exit={command['exit_code']}: "
              + shlex.join(command["argv"]))
        if command["status"] not in {"not-run", "completed"}:
            for stream in ("stdout", "stderr"):
                if command[stream]:
                    print(f"{stream}:\n{command[stream].rstrip()}")
    if result["toolchain"]["version"]:
        print(f"Actual version: {result['toolchain']['version']}")
    if result.get("failure"):
        print(f"failure: {result['failure']}")
    audit = result["axiom_audit"]
    print(f"Axiom audit: {audit['status']}; axioms={audit['axioms']}; "
          f"trust review required={audit['review_required']}")
    if audit["raw_output"] and result["commands"][-1]["status"] == "completed":
        print("Declaration and axiom output:\n" + audit["raw_output"].rstrip())
    print(f"Inputs before: {result['inputs_before']['sha256']}; "
          f"changed during execution: {result['inputs_changed']}")
    print("Full input manifests and command observations are available with --format json.")
    for warning in result["warnings"]:
        print(f"limit: {warning}")
    print("Replay is not informal alignment, owner confirmation, or claim approval.")


def _diagnostic_exit(result: dict, strict: bool) -> int:
    return int(result["status"] == "error" or (strict and result["status"] == "warning"))


def _build_arguments(parser: argparse.ArgumentParser) -> None:
    _workspace(parser)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--paper", help="standard writing/<slug>/main.tex")
    target.add_argument("--source", type=Path,
                        help="explicit TeX document root under writing/ or reading/")
    parser.add_argument("--engine", choices=sorted(ENGINE_FLAGS),
                        help="override engine; source builds detect directives/packages or use workspace config")
    parser.add_argument("--max-files", type=int, default=DEFAULT_OUTPUT_MAX_FILES,
                        help=f"maximum managed output file count after building (default: {DEFAULT_OUTPUT_MAX_FILES})")
    viewer = parser.add_mutually_exclusive_group()
    viewer.add_argument("--open", dest="open_viewer", action="store_true",
                        help="open the PDF with the host system's default viewer after building")
    viewer.add_argument("--no-open", dest="open_viewer", action="store_false",
                        help=argparse.SUPPRESS)
    parser.set_defaults(open_viewer=False)
    parser.add_argument("--dry-run", action="store_true")


def _build(args: argparse.Namespace) -> None:
    if args.max_files < 2:
        raise PaperError("--max-files must be at least 2 to retain a PDF and SyncTeX")
    if args.dry_run:
        if args.source is not None:
            command, stem = run_source_build(args.workspace, args.source, args.engine, True)
        else:
            command = run_build(args.workspace, args.paper, args.engine or "pdflatex", True)
            stem = args.paper
        print(shlex.join(command))
        return

    viewer_error = None
    with output_transaction(args.workspace) as output:
        if args.source is not None:
            command, stem = run_source_build(args.workspace, args.source, args.engine, False)
        else:
            command = run_build(args.workspace, args.paper, args.engine or "pdflatex", False)
            stem = args.paper
        result = prune_output(
            output, args.max_files, protected_stems={stem},
            superseded_prefixes={f"{stem}_"},
        )
        if args.open_viewer:
            viewer_error = open_default_viewer(output / f"{stem}.pdf")

    print(f"Build finished: output/{stem}.pdf + SyncTeX")
    for name in result.removed:
        print(f"Removed old output/{name}")
    print(f"Output files: {result.file_count} (limit {result.max_files})")
    if result.over_limit:
        print("warning: protected or unrecognized files keep output above the limit", file=sys.stderr)
    if args.open_viewer:
        if viewer_error:
            print(f"warning: {viewer_error}", file=sys.stderr)
        else:
            print(f"Opened output/{stem}.pdf in the default viewer")


def main(argv: list[str] | None = None, *, checkout: Path | None = None) -> int:
    # A pipe on native Windows can otherwise use a legacy code page, even
    # when the input files and JSON contract are UTF-8. Also works under -I,
    # which intentionally ignores PYTHONIOENCODING/PYTHONUTF8.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="labo")
    areas = parser.add_subparsers(dest="area", required=True)

    layout = areas.add_parser("layout", help="initialize and use research workspace directories")
    layout_actions = layout.add_subparsers(dest="action", required=True)
    init = layout_actions.add_parser(
        "init", help="add missing workspace directories and writing guides without overwriting files",
    )
    _workspace(init)
    init.add_argument("--dry-run", action="store_true")
    new = layout_actions.add_parser("new", help="create a research, paper, or reference source template")
    kinds = new.add_subparsers(dest="kind", required=True)
    for kind in ("research", "paper", "reference"):
        sub = kinds.add_parser(kind)
        sub.add_argument("slug")
        _workspace(sub)
        sub.add_argument("--dry-run", action="store_true")
        if kind == "research":
            sub.add_argument("--title", required=True)
            sub.add_argument("--summary", required=True)
            sub.add_argument("--next", dest="next_step")

    research = areas.add_parser("research", help="research plan metadata")
    research_actions = research.add_subparsers(dest="action", required=True)
    for name in ("list", "check"):
        sub = research_actions.add_parser(name)
        _workspace(sub)
        if name == "list":
            sub.add_argument("--status", choices=("in_progress", "completed"))
            sub.add_argument("--tag")
            sub.add_argument("--search")
            sub.add_argument("--format", choices=("text", "json"), default="text")

    explore = research_actions.add_parser("exploration", help="opt-in exploration tree and work states")
    explore_actions = explore.add_subparsers(dest="exploration_action", required=True)
    for name in ("init", "configure", "add", "update", "show", "tree", "check"):
        sub = explore_actions.add_parser(name)
        _workspace(sub)
        sub.add_argument("--research", required=True)
        sub.add_argument("--format", choices=("text", "json"), default="text")
        if name == "init":
            sub.add_argument("--if-missing", action="store_true", help="validate and reuse an existing tree without changing its settings")
        if name in {"init", "configure"}:
            sub.add_argument("--mode", choices=("sequential", "parallel"), default="sequential" if name == "init" else None)
            sub.add_argument("--integrator", default="primary" if name == "init" else None)
            sub.add_argument("--max-workers", type=int, default=2 if name == "init" else None)
        if name in {"configure", "add", "update"}:
            sub.add_argument("--actor", required=name == "configure")
        if name in {"configure", "update"}:
            sub.add_argument("--expect-revision", required=True, type=int)
        if name in {"add", "update", "show", "tree"}:
            sub.add_argument("--node", required=name != "tree")
        if name in {"add", "update"}:
            sub.add_argument("--parent", help="parent ID; use '-' to make a root")
            sub.add_argument("--kind", choices=exploration.KINDS, required=name == "add")
            sub.add_argument("--title", required=name == "add")
            sub.add_argument("--summary", required=name == "add")
            sub.add_argument("--next", dest="next_step", required=name == "add")
            sub.add_argument("--state", choices=exploration.STATES)
            sub.add_argument("--owner", help="owner name; '-' clears in sequential mode")
            sub.add_argument("--record", help="workspace-relative detail file; '-' clears")
            sub.add_argument("--claim-ref", action="append", help="replace claim references with repeated path#ID values; '-' clears")
            sub.add_argument("--dependency-ref", action="append", help="replace dependency references; '-' clears")
            sub.add_argument("--proof-required", action=argparse.BooleanOptionalAction, default=None,
                             help="require current formal records before done (always true for theorem/lemma)")
        if name in {"tree", "show"}:
            sub.add_argument("--with-evidence", action="store_true", help="inspect linked formal-evidence input freshness")
        if name == "show":
            sub.add_argument("--details", action="store_true", help="read only this node's detail record")
        if name == "tree":
            sub.add_argument("--depth", type=int, help="visible edge depth from selected root, starting at zero")

    evidence = areas.add_parser("evidence", help="optional evidence structure and review freshness")
    evidence_actions = evidence.add_subparsers(dest="action", required=True)
    evidence_init = evidence_actions.add_parser("init", help="create an empty opt-in claim catalog")
    _workspace(evidence_init)
    evidence_init.add_argument("--catalog", required=True)
    evidence_init.add_argument("--dry-run", action="store_true")
    evidence_snapshot = evidence_actions.add_parser(
        "snapshot", help="print pending review inputs as YAML without writing or approving",
    )
    _workspace(evidence_snapshot)
    evidence_snapshot.add_argument("--kind", choices=KINDS, required=True)
    evidence_snapshot.add_argument("--catalog")
    evidence_snapshot.add_argument("--claim", action="append", default=[])
    evidence_snapshot.add_argument("--file", action="append", default=[])
    evidence_snapshot.add_argument("--tree", action="append", default=[])
    evidence_snapshot.add_argument("--policy-file", action="append", default=[])
    evidence_check = evidence_actions.add_parser("check", help="check selected record structure and freshness")
    _workspace(evidence_check)
    evidence_check.add_argument("--catalog")
    evidence_check.add_argument("--record", action="append", default=[])
    evidence_check.add_argument("--strict", action="store_true")
    evidence_check.add_argument("--format", choices=("text", "json"), default="text")

    evidence_scope = evidence_actions.add_parser("scope", help="inspect literal TeX dependencies and omitted review inputs")
    _workspace(evidence_scope)
    source = evidence_scope.add_mutually_exclusive_group(required=True)
    source.add_argument("--paper", help="writing/<slug>/main.tex")
    source.add_argument("--source", help="workspace-relative TeX entry source")
    evidence_scope.add_argument("--compile-root",
                                help="workspace-relative TeX working directory; '.' means workspace root (default: source parent)")
    evidence_scope.add_argument("--record", help="compare discovered dependencies with one saved snapshot")
    evidence_scope.add_argument("--file", action="append", default=[])
    evidence_scope.add_argument("--tree", action="append", default=[])
    evidence_scope.add_argument("--strict", action="store_true")
    evidence_scope.add_argument("--format", choices=("text", "json"), default="text")

    evidence_inventory = evidence_actions.add_parser("status", help="read one research program's recorded evidence and review coverage")
    _workspace(evidence_inventory)
    evidence_inventory.add_argument("--research", required=True)
    evidence_inventory.add_argument("--catalog", help="catalog within the selected research program (default: claims.yaml)")
    selection = evidence_inventory.add_mutually_exclusive_group()
    selection.add_argument("--reviews", help="review directory within the program (default: reviews/)")
    selection.add_argument("--record", action="append", default=[], help="explicit record selection instead of directory discovery")
    evidence_inventory.add_argument("--strict", action="store_true")
    evidence_inventory.add_argument("--format", choices=("text", "json"), default="text")

    evidence_replay = evidence_actions.add_parser("replay", help="plan or explicitly execute a local selected-source Lean replay")
    _workspace(evidence_replay)
    evidence_replay.add_argument("--catalog", required=True)
    evidence_replay.add_argument("--claim", required=True)
    evidence_replay.add_argument("--execute", action="store_true", help="run the trusted selected Lean project using an already prepared toolchain")
    evidence_replay.add_argument("--timeout", type=float, default=60.0, help="timeout in seconds per command")
    evidence_replay.add_argument("--toolchain-dir", type=Path, help="already installed pinned Lean toolchain directory")
    evidence_replay.add_argument("--format", choices=("text", "json"), default="text")

    dependencies = areas.add_parser("dependencies", help="check an adopted mathematical dependency graph")
    dependency_actions = dependencies.add_subparsers(dest="action", required=True)
    for action in ("check", "sort", "order", "closure", "impact"):
        sub = dependency_actions.add_parser(action)
        _workspace(sub)
        sub.add_argument("--graph", required=True, help="workspace-relative sourced graph YAML")
        sub.add_argument("--format", choices=("text", "json"), default="text")
        if action == "order":
            sub.add_argument("--node", action="append", default=[],
                             help="repeat in the proposed full dependency order")
        elif action in {"closure", "impact"}:
            sub.add_argument("--node", action="append", required=True,
                             help="repeat for selected targets or changed nodes")

    paper = areas.add_parser("paper", help="local section-by-section TeX reading")
    paper_actions = paper.add_subparsers(dest="action", required=True)
    for name in ("map", "section"):
        sub = paper_actions.add_parser(name)
        _workspace(sub)
        sub.add_argument("--paper", required=True)
        if name == "map":
            sub.add_argument("--format", choices=("text", "json"), default="text")
        else:
            sub.add_argument("--name", required=True, help="section file stem")

    reading = paper_actions.add_parser("reading", help="opt-in staged first-reader session; no implicit approval")
    reading_actions = reading.add_subparsers(dest="reading_action", required=True)
    for action in ("start", "next", "observe", "status"):
        sub = reading_actions.add_parser(action)
        _workspace(sub)
        sub.add_argument("--session", required=True, help="private workspace-relative session record")
        sub.add_argument("--format", choices=("text", "json"), default="text")
        if action == "start":
            sub.add_argument("--source", required=True)
            sub.add_argument("--reader", required=True)
            sub.add_argument("--mode", choices=("single-context", "independent"), default="single-context")
        elif action == "next":
            sub.add_argument("--through-line", type=int, required=True)
        elif action == "observe":
            sub.add_argument("--understanding", required=True)
            sub.add_argument("--confusion", required=True)
            sub.add_argument("--rescue", action="store_true", help="append later recovery without replacing the initial observation")

    build = areas.add_parser("build", help="compile TeX and manage PDF/SyncTeX output")
    _build_arguments(build)

    output = areas.add_parser("output", help="build documents and manage files under output/")
    output_actions = output.add_subparsers(dest="action", required=True)
    output_build = output_actions.add_parser(
        "build", help="compile to a slug-named PDF/SyncTeX pair and prune old output",
    )
    _build_arguments(output_build)
    output_prune = output_actions.add_parser("prune", help="remove the oldest managed PDF/SyncTeX outputs")
    _workspace(output_prune)
    output_prune.add_argument("--max-files", type=int, default=DEFAULT_OUTPUT_MAX_FILES,
                              help=f"maximum output file count (default: {DEFAULT_OUTPUT_MAX_FILES})")

    args = parser.parse_args(argv)
    try:
        args.workspace = resolve_workspace(args.workspace, checkout)
        if args.area == "layout":
            if args.action == "init":
                changes = init_layout(args.workspace, dry_run=args.dry_run)
            else:
                changes = new_item(
                    args.workspace, args.kind, args.slug,
                    title=getattr(args, "title", None), summary=getattr(args, "summary", None),
                    next_step=getattr(args, "next_step", None), dry_run=args.dry_run,
                )
            for change in changes:
                print(f"{'would ' if args.dry_run else ''}{change}")
            if not changes:
                print("No layout changes needed")
        elif args.area == "evidence":
            if args.action == "init":
                for change in init_catalog(args.workspace, args.catalog, dry_run=args.dry_run):
                    print(f"{'would ' if args.dry_run else ''}{change}")
            elif args.action == "snapshot":
                record = snapshot(
                    args.workspace, kind=args.kind, catalog=args.catalog,
                    claim_ids=args.claim, files=args.file, trees=args.tree,
                    policy_files=args.policy_file,
                )
                print(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), end="")
            elif args.action == "scope":
                from .evidence_scope import inspect_scope
                result = inspect_scope(args.workspace, source=args.source, paper=args.paper,
                                       record=args.record, files=args.file, trees=args.tree,
                                       compile_root=args.compile_root)
                _diagnostic_result(result, args.format)
                return _diagnostic_exit(result, args.strict)
            elif args.action == "status":
                from .evidence_status import evidence_status
                result = evidence_status(args.workspace, research=args.research, catalog=args.catalog,
                                         reviews=args.reviews, records=args.record)
                _diagnostic_result(result, args.format)
                return _diagnostic_exit(result, args.strict)
            elif args.action == "replay":
                from .formal_replay import replay
                result = replay(args.workspace, catalog=args.catalog, claim=args.claim,
                                execute=args.execute, timeout=args.timeout, toolchain_dir=args.toolchain_dir)
                _replay_result(result, args.format)
                return int(result["status"] in {"failed", "unavailable"})
            elif args.action == "check":
                result = check_evidence(args.workspace, catalog=args.catalog, records=args.record)
                if args.format == "json":
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print(f"{result['status'].upper()}: {result['claim_count']} catalog claim(s), "
                          f"{len(result['records'])} selected review record(s)")
                    for record in result["records"]:
                        print(f"[{record['state']}] {record['path']}")
                    for issue in result["issues"]:
                        print(f"{issue['severity']}: {issue['path']}: {issue['message']}")
                    print("Checks cover recorded structure and input identity, not mathematical correctness.")
                return int(result["status"] == "error" or
                           (args.strict and result["status"] == "warning"))
        elif args.area == "dependencies":
            from .dependencies import inspect_dependencies
            result = inspect_dependencies(args.workspace, graph=args.graph, action=args.action,
                                          nodes=getattr(args, "node", None))
            if args.format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"{result['status'].upper()}: {result['node_count']} nodes, "
                      f"{result['requires_count']} hard dependencies; "
                      f"recorded coverage={result['recorded_coverage']['status']}")
                label = "Topological order" if result["order_complete"] else "Partial topological order"
                print(label + ": " + ", ".join(result["topological_order"]))
                for component, witness in zip(result["cyclic_components"], result["cycle_witnesses"]):
                    print("Cyclic component: " + ", ".join(component))
                    print("Cycle (each node requires the next): " + " -> ".join(witness))
                if result["blocked_nodes"]:
                    print("Blocked downstream: " + ", ".join(result["blocked_nodes"]))
                if "order_check" in result:
                    print("Proposed full order: " + ("valid" if result["order_check"]["valid"] else "invalid"))
                    for field in ("missing", "unknown", "duplicates", "violations"):
                        if result["order_check"][field]:
                            print(field + ": " + json.dumps(result["order_check"][field], ensure_ascii=False))
                if "included" in result:
                    print("Included (selected nodes included): " + ", ".join(result["included"]))
                    print("Selection order complete: " + str(result["selection_order_complete"]))
                    print("Selection order: " + ", ".join(result["selection_order"]))
                for limit in result["limits"]:
                    print("limit: " + limit)
            return int(result["status"] == "error")
        elif args.area == "research":
            if args.action == "exploration":
                action = args.exploration_action
                if action == "init":
                    result = exploration.initialize(args.workspace, args.research, mode=args.mode,
                                                    integrator=args.integrator, max_workers=args.max_workers,
                                                    if_missing=args.if_missing)
                elif action == "configure":
                    changes = {key: getattr(args, key) for key in ("mode", "integrator", "max_workers")
                               if getattr(args, key) is not None}
                    result = exploration.configure(args.workspace, args.research,
                                                   expect_revision=args.expect_revision, actor=args.actor, **changes)
                elif action in {"add", "update"}:
                    changes = {}
                    for arg, key in (("parent", "parent"), ("kind", "kind"), ("title", "title"),
                                     ("summary", "summary"), ("next_step", "next"), ("state", "state"),
                                     ("owner", "owner"), ("record", "record"),
                                     ("proof_required", "proof_required"),
                                     ("claim_ref", "claim_refs"), ("dependency_ref", "dependency_refs")):
                        value = getattr(args, arg)
                        if value is not None:
                            changes[key] = [] if value == ["-"] else None if value == "-" else value
                    if action == "add":
                        result = exploration.add(args.workspace, args.research, id=args.node, actor=args.actor, **changes)
                    else:
                        result = exploration.update(args.workspace, args.research, args.node,
                                                    expect_revision=args.expect_revision, actor=args.actor, **changes)
                else:
                    result = exploration.inspect(args.workspace, args.research, action=action,
                                                node_id=getattr(args, "node", None), depth=getattr(args, "depth", None),
                                                details=getattr(args, "details", False), with_evidence=getattr(args, "with_evidence", False))
                if args.format == "json":
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                elif action in {"init", "configure", "add", "update"}:
                    print(f"OK: {action}; revision={result['revision']}")
                    if "node" in result:
                        print(f"{result['node']['id']}: node revision={result['node']['revision']}")
                else:
                    print(exploration.render(result))
                return int(result.get("status") == "error")
            plans, errors = read_workspace(args.workspace)
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            if args.action == "check":
                print(f"OK: {len(plans)} research plan(s) have valid frontmatter")
            else:
                plans = _filtered(plans, args.status, args.tag, args.search)
                if args.format == "json":
                    print(json.dumps({"schema_version": 1,
                                      "research": [p.to_dict() for p in plans]},
                                     ensure_ascii=False, indent=2))
                else:
                    for plan in plans:
                        print(f"[{plan.status}] {plan.slug} — {plan.title}\n  {plan.summary}")
                        if plan.next:
                            print(f"  Next: {plan.next}")
                    if not plans:
                        print("No matching research plans")
        elif args.area == "paper":
            if args.action == "reading":
                from .reader import start_reading, next_reading, observe_reading, reading_status
                if args.reading_action == "start":
                    result = start_reading(args.workspace, args.source, args.session, args.reader, mode=args.mode)
                elif args.reading_action == "next":
                    result = next_reading(args.workspace, args.session, args.through_line)
                elif args.reading_action == "observe":
                    result = observe_reading(args.workspace, args.session, args.understanding,
                                             args.confusion, rescue=args.rescue)
                else:
                    result = reading_status(args.workspace, args.session)
                if args.format == "json":
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                elif args.reading_action == "next":
                    # Preserve the captured UTF-8 bytes, including CRLF on
                    # Windows; text-mode translation would produce CRCRLF.
                    stream = getattr(sys.stdout, "buffer", None)
                    if stream is None:  # Embedded callers may capture StringIO.
                        sys.stdout.write(result["text"])
                    else:
                        stream.write(result["text"].encode("utf-8"))
                else:
                    print(f"Reader {result['reader']}: through line {result['through_line']}; "
                          f"awaiting observation={result['awaiting_observation']}")
                    print(f"Declared mode: {result['mode']}; context independence is not certified.")
            elif args.action == "section":
                print(read_section(args.workspace, args.paper, args.name), end="")
            else:
                openings = map_openings(args.workspace, args.paper)
                if args.format == "json":
                    print(json.dumps({"schema_version": 1,
                                      "sections": [o.to_dict() for o in openings]},
                                     ensure_ascii=False, indent=2))
                else:
                    for opening in openings:
                        print(f"## {opening.section}\n{opening.opening}\n")
        elif args.area == "build" or (args.area == "output" and args.action == "build"):
            _build(args)
        elif args.area == "output" and args.action == "prune":
            if args.max_files < 2:
                raise PaperError("--max-files must be at least 2 to retain a PDF and SyncTeX")
            with output_transaction(args.workspace) as output_dir:
                result = prune_output(output_dir, args.max_files)
            for name in result.removed:
                print(f"Removed output/{name}")
            print(f"Output files: {result.file_count} (limit {result.max_files})")
            if result.over_limit:
                print("warning: protected or unrecognized files keep output above the limit", file=sys.stderr)
    except (PlanError, PaperError, WorkspaceError, LayoutError, EvidenceError, ReadingError, exploration.ExplorationError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
