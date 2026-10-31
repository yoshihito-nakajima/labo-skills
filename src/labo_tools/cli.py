"""Readable and JSON-safe research workflows without an MCP server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import sys

from .build import (
    DEFAULT_OUTPUT_MAX_FILES,
    ENGINE_FLAGS,
    open_default_viewer,
    output_transaction,
    prune_output,
    run_build,
    run_source_build,
)
from .layout import LayoutError, init_layout, new_item
from .paper import PaperError, map_openings, read_section
from .plans import PlanError, ResearchPlan, read_workspace
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
        elif args.area == "research":
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
            if args.action == "section":
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
    except (PlanError, PaperError, WorkspaceError, LayoutError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
