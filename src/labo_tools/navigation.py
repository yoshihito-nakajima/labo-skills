"""Connect build entrypoints to the single skill-owned navigation checker."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


def check_navigation(pdf: Path, cache: Path, stem: str, aux: Path | None = None,
                     *, source: Path | None = None) -> None:
    """Keep artifacts usable; surface failed/incomplete audit separately from TeX."""
    report_path = cache / f"navigation-{stem}.json"
    checker = Path(__file__).resolve().parents[2] / "skills/mathematical-navigation/scripts/check_pdf.py"
    try:
        spec = importlib.util.spec_from_file_location("labo_pdf_navigation", checker)
        if spec is None or spec.loader is None:
            raise ImportError("navigation checker cannot be loaded from this checkout")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        previous = None
        if report_path.is_file():
            try:
                previous = json.loads(report_path.read_text(encoding="utf-8"))
                if not isinstance(previous, dict):
                    raise ValueError("baseline is not a JSON object")
            except (ValueError, OSError):
                previous = None
                print(f"Navigation baseline unreadable; checking afresh: {report_path}", file=sys.stderr)
        # Migrate old combined reports once; structural-only builds never replace
        # the retained rendering baseline or claim a new visual review.
        if previous and not module.render_baseline_path(report_path).exists():
            try:
                module.save_render_baseline(report_path, previous)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                print(f"Old rendering evidence could not be retained: {exc}", file=sys.stderr)
        expected = source.with_suffix(".navigation.json") if source is not None else None
        if expected is not None and not (expected.exists() or expected.is_symlink()):
            expected = None
        result = module.check(pdf, aux=aux if aux and aux.is_file() else None,
                              expect=expected, previous=previous, source=source)
        module.save_report(report_path, result)
        status = result["status"]
        stream = sys.stdout if status == "pass" else sys.stderr
        print(f"Navigation {status}: {result.get('counts', {}).get('links', 0)} links; {report_path}", file=stream)
        if expected is None:
            print("Navigation requirements not supplied; pass covers existing PDF structure only.", file=stream)
        if status != "pass":
            print("PDF/SyncTeX were built; navigation is not cleared. Inspect the report before final delivery.", file=stream)
    except (OSError, ValueError, ImportError) as exc:
        print(f"Navigation incomplete: {exc}; PDF/SyncTeX retained, no navigation success claimed.", file=sys.stderr)
