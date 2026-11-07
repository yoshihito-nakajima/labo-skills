#!/usr/bin/env python3
"""Offline PDF navigation audit. Reads raw qpdf JSON, never follows actions."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

SCHEMA = 1


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint(value) -> str:
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())


def text(value) -> str:
    if not isinstance(value, str):
        raise ValueError("expected PDF string or name")
    if value.startswith("u:"):
        return value[2:]
    if value.startswith("b:"):
        data = bytes.fromhex(value[2:])
        if data.startswith((b"\xfe\xff", b"\xff\xfe")):
            return data.decode("utf-16")
        return data.decode("latin-1")
    if value.startswith("/"):
        return re.sub(r"#([0-9a-fA-F]{2})", lambda m: chr(int(m[1], 16)), value[1:])
    raise ValueError("not an encoded PDF string or name")


def finite(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


class Audit:
    def __init__(self, data: dict):
        self.objects = data["qpdf"][1]
        self.pages = data["pages"]
        self.page_numbers = {p["object"]: i + 1 for i, p in enumerate(self.pages)}
        self.names = {}
        self.destinations = {}
        self.links = []
        self.outlines = []
        self.findings = []
        self.labels = {}
        self.aux_files = []

    def finding(self, severity, code, location, detail):
        self.findings.append(dict(severity=severity, code=code, location=location, detail=str(detail)))

    def resolve(self, value):
        seen = set()
        while isinstance(value, str) and re.fullmatch(r"\d+ \d+ R", value):
            if value in seen:
                raise ValueError(f"indirect reference cycle: {value}")
            seen.add(value)
            entry = self.objects.get("obj:" + value)
            if not entry or "value" not in entry:
                raise ValueError(f"missing or non-value object: {value}")
            value = entry["value"]
        return value

    def guarded(self, location, function, *args):
        try:
            return function(*args)
        except (ValueError, KeyError, IndexError, TypeError, AttributeError, RecursionError) as exc:
            self.finding("error", "malformed_object", location, exc)
            return None

    def add_name(self, name, dest):
        name = text(name)
        if name in self.names:
            self.finding("error", "duplicate_destination", name, "duplicate name in destination tables")
        self.names[name] = dest

    def name_tree(self, node, seen):
        if isinstance(node, str):
            if node in seen:
                raise ValueError("cycle or repeated node in destination name tree")
            seen.add(node)
        node = self.resolve(node)
        pairs = self.resolve(node.get("/Names", []))
        if len(pairs) % 2:
            raise ValueError("odd length destination name table")
        for i in range(0, len(pairs), 2):
            self.add_name(pairs[i], pairs[i + 1])
        for child in self.resolve(node.get("/Kids", [])):
            self.name_tree(child, seen)

    def destination(self, dest):
        visited = set()
        name = None
        while True:
            dest = self.resolve(dest)
            if isinstance(dest, dict):
                dest = dest.get("/D")
            elif isinstance(dest, str):
                key = text(dest)
                name = name or key
                if key in visited or key not in self.names:
                    raise ValueError(f"unresolved or cyclic named destination: {key}")
                visited.add(key)
                dest = self.names[key]
            else:
                break
        if not isinstance(dest, list) or len(dest) < 2:
            raise ValueError("destination is not an explicit destination array")
        page = self.page_numbers.get(dest[0])
        if page is None:
            raise ValueError("destination page is not in this PDF's page tree")
        lengths = {"/XYZ": 5, "/Fit": 2, "/FitH": 3, "/FitV": 3,
                   "/FitR": 6, "/FitB": 2, "/FitBH": 3, "/FitBV": 3}
        kind = dest[1]
        if kind not in lengths:
            raise ValueError(f"unknown destination fit type: {kind}")
        if len(dest) != lengths[kind] or any(v is not None and not finite(v) for v in dest[2:]):
            raise ValueError("invalid destination coordinate array")
        if kind == "/FitR" and (None in dest[2:] or dest[2] >= dest[4] or dest[3] >= dest[5]):
            raise ValueError("empty destination fit rectangle")
        if kind == "/XYZ" and dest[4] is not None and dest[4] < 0:
            raise ValueError("negative destination zoom")
        # Null /XYZ coordinates preserve viewer state; they are legal, not a failure.
        return dict(name=name, page=page, fit=kind, coordinates=dest[2:])

    def action(self, owner, location):
        if "/AA" in owner:
            self.finding("unknown", "additional_actions", location, "additional actions are not executed or verified")
        if "/Dest" in owner:
            if "/A" in owner:
                self.finding("error", "conflicting_action", location, "both /Dest and /A")
            return dict(kind="internal", target=self.destination(owner["/Dest"]))
        action = self.resolve(owner.get("/A"))
        if not isinstance(action, dict):
            raise ValueError("link has no destination or action dictionary")
        kind = action.get("/S")
        if "/Next" in action:
            self.finding("unknown", "action_chain", location, "chained actions are not executed or verified")
        if kind == "/GoTo":
            return dict(kind="internal", target=self.destination(action.get("/D")))
        if kind == "/URI":
            uri = text(self.resolve(action.get("/URI")))
            parts = urlsplit(uri)
            if not parts.scheme or (parts.scheme.lower() in {"http", "https"} and not parts.netloc):
                raise ValueError("URI lacks a scheme or HTTP host")
            return dict(kind="uri", uri=uri, reachability="not_checked")
        if kind in {"/GoToR", "/Launch"}:
            spec = self.resolve(action.get("/F"))
            if isinstance(spec, dict):
                spec = spec.get("/UF", spec.get("/F"))
            filename = text(spec) if spec is not None else None
            if kind == "/GoToR" and (not filename or "/D" not in action):
                raise ValueError("remote destination lacks filename or /D")
            self.finding("unknown", "external_file_action", location,
                         "file/remote action inventoried only; check delivered bundle and destination separately")
            return dict(kind=kind[1:], file=filename, destination=action.get("/D"), reachability="not_checked")
        self.finding("unknown", "unsupported_action", location, f"unsupported action {kind}; never executed")
        return dict(kind="unsupported", action=kind)

    def page_box(self, obj):
        seen = set()
        crop = media = None
        while isinstance(obj, dict):
            crop = crop if crop is not None else obj.get("/CropBox")
            media = media if media is not None else obj.get("/MediaBox")
            parent = obj.get("/Parent")
            if not parent:
                break
            if parent in seen:
                raise ValueError("page inheritance cycle")
            seen.add(parent)
            obj = self.resolve(parent)
        return self.resolve(crop if crop is not None else media)

    def link(self, annotation, page_number, box, ordinal):
        location = f"page {page_number}, link {ordinal}"
        # Append before resolving the action, so broken links remain in the inventory.
        item = dict(page=page_number, ordinal=ordinal, kind="unresolved")
        self.links.append(item)
        rect = self.resolve(annotation.get("/Rect"))
        item["rect"] = rect
        if not isinstance(rect, list) or len(rect) != 4 or not all(finite(x) for x in rect):
            self.finding("error", "invalid_rectangle", location, "invalid link rectangle")
        elif rect[0] >= rect[2] or rect[1] >= rect[3]:
            self.finding("error", "empty_rectangle", location, "link rectangle has no positive area")
        elif isinstance(box, list) and len(box) == 4 and all(finite(x) for x in box):
            # Rect and CropBox are both in default user space, even on rotated pages.
            if rect[2] <= box[0] or rect[0] >= box[2] or rect[3] <= box[1] or rect[1] >= box[3]:
                self.finding("error", "off_page_rectangle", location, "link lies wholly outside CropBox")
            elif rect[0] < box[0] or rect[1] < box[1] or rect[2] > box[2] or rect[3] > box[3]:
                self.finding("warning", "clipped_rectangle", location, "link partly outside CropBox; inspect rendering")
        else:
            self.finding("unknown", "page_box", location, "could not verify visible page bounds")
        if annotation.get("/F", 0) & (1 | 2 | 32):
            self.finding("warning", "hidden_link", location, "link has invisible/hidden/no-view flags")
        result = self.guarded(location, self.action, annotation, location)
        if result:
            item.update(result)

    def outline_chain(self, ref, depth=0, visited=None):
        visited = set() if visited is None else visited
        while ref:
            if not isinstance(ref, str) or ref in visited:
                raise ValueError("cycle or invalid reference in outline tree")
            visited.add(ref)
            node = self.resolve(ref)
            item = dict(depth=depth, title="", kind="container")
            self.outlines.append(item)
            title = self.guarded(f"outline {ref}", lambda: text(self.resolve(node.get("/Title"))))
            item["title"] = title or "(unreadable title)"
            location = "outline " + item["title"]
            if "/Dest" in node or "/A" in node:
                item["kind"] = "unresolved"
                action = self.guarded(location, self.action, node, location)
                if action:
                    item.update(action)
            elif not node.get("/First"):
                self.finding("warning", "outline_without_target", location, "leaf bookmark has no destination")
            if node.get("/First"):
                self.guarded(location, self.outline_chain, node["/First"], depth + 1, visited)
            ref = node.get("/Next")

    def run(self):
        root = self.resolve(self.objects["trailer"]["value"]["/Root"])
        tree = self.resolve(root.get("/Names", {}))
        if "/Dests" in tree:
            self.guarded("destination name tree", self.name_tree, tree["/Dests"], set())
        legacy = self.resolve(root.get("/Dests", {}))
        for key, value in legacy.items():
            self.guarded("legacy destinations", self.add_name, key, value)
        for name, value in self.names.items():
            result = self.guarded("destination " + name, self.destination, value)
            if result:
                self.destinations[name] = result
        for number, page in enumerate(self.pages, 1):
            obj = self.resolve(page["object"])
            box = self.guarded(f"page {number}", self.page_box, obj)
            annotations = self.resolve(obj.get("/Annots", []))
            for ordinal, ref in enumerate(annotations, 1):
                annotation = self.guarded(f"page {number}, annotation {ordinal}", self.resolve, ref)
                if isinstance(annotation, dict) and annotation.get("/Subtype") == "/Link":
                    self.guarded(f"page {number}, link {ordinal}", self.link, annotation, number, box, ordinal)
        if "/Outlines" in root:
            outline = self.resolve(root["/Outlines"])
            self.guarded("outline tree", self.outline_chain, outline.get("/First"))
        return self


def groups(line):
    """Read brace groups from common emitted aux syntax, without executing TeX."""
    result = []
    pos = 0
    while pos < len(line):
        if line[pos].isspace():
            pos += 1
            continue
        if line[pos] != "{":
            raise ValueError("unsupported aux group syntax")
        start = pos + 1
        level = 1
        pos += 1
        while pos < len(line) and level:
            if line[pos] == "\\":
                pos += 2
                continue
            if line[pos] == "{":
                level += 1
            elif line[pos] == "}":
                level -= 1
            pos += 1
        if level:
            raise ValueError("unbalanced aux braces")
        result.append(line[start:pos - 1])
    return result


def inspect_aux(audit, path, visited=None, root=None):
    visited = set() if visited is None else visited
    path = path.resolve()
    root = path.parent if root is None else root
    if path in visited:
        return
    visited.add(path)
    if not path.is_relative_to(root):
        audit.finding("unknown", "aux_include_outside_root", str(path), "not followed outside supplied aux directory")
        return
    data = path.read_bytes()
    audit.aux_files.append(dict(path=str(path), sha256=digest(data)))
    for number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
        location = f"{path.name}:{number}"
        try:
            if line.startswith(r"\@input{"):
                includes = groups(line[len(r"\@input"):])
                inspect_aux(audit, path.parent / includes[0], visited, root)
            elif line.startswith(r"\newlabel{"):
                key, body = groups(line[len(r"\newlabel"):])
                fields = groups(body)
                if key.endswith("@cref") or len(fields) < 4 or not fields[3]:
                    continue  # non-hyperref labels do not assert a PDF destination
                if len(fields) > 4 and fields[4]:
                    audit.finding("unknown", "external_aux_label", location, key)
                    continue
                if key in audit.labels:
                    audit.finding("error", "duplicate_label", location, key)
                audit.labels[key] = fields[3]
                if fields[3] not in audit.destinations:
                    audit.finding("error", "aux_destination_missing", location, f"{key} -> {fields[3]}")
        except (OSError, ValueError) as exc:
            audit.finding("unknown", "aux_not_parsed", location, exc)


def inspect_expectations(audit, expected):
    allowed = {"destinations", "routes", "min_links", "min_outlines"}
    if not isinstance(expected, dict) or set(expected) - allowed:
        raise ValueError("expectations must use destinations, routes, min_links, min_outlines only")
    for key, actual in (("min_links", len(audit.links)), ("min_outlines", len(audit.outlines))):
        if key in expected:
            minimum = expected[key]
            if type(minimum) is not int or minimum < 0:
                raise ValueError(f"{key} must be a nonnegative integer")
            if actual < minimum:
                audit.finding("error", "missing_expected_items", key, f"expected >= {minimum}, found {actual}")
    for spec in expected.get("destinations", []):
        spec = {"name": spec} if isinstance(spec, str) else spec
        if not isinstance(spec, dict) or set(spec) - {"name", "page"} or not isinstance(spec.get("name"), str):
            raise ValueError("invalid expected destination")
        actual = audit.destinations.get(spec["name"])
        if actual is None or ("page" in spec and actual["page"] != spec["page"]):
            audit.finding("error", "expected_destination", spec["name"], "missing or on unexpected physical page")
    for spec in expected.get("routes", []):
        if not isinstance(spec, dict) or set(spec) - {"to", "label", "from_page", "min_count"}:
            raise ValueError("invalid expected route")
        if ("to" in spec) == ("label" in spec):
            raise ValueError("route needs exactly one of to (destination name) and label (aux label)")
        target_name = spec.get("to") if "to" in spec else audit.labels.get(spec["label"])
        target = audit.destinations.get(target_name)
        count = spec.get("min_count", 1)
        if type(count) is not int or count < 1:
            raise ValueError("route min_count must be a positive integer")
        matched = 0
        for link in audit.links:
            landed = link.get("target")
            if link["kind"] != "internal" or not target:
                continue
            same = landed.get("name") == target_name or all(landed[k] == target[k] for k in ("page", "fit", "coordinates"))
            if same and ("from_page" not in spec or spec["from_page"] == link["page"]):
                matched += 1
        if matched < count:
            audit.finding("error", "expected_route_missing", str(spec), f"matched {matched}, expected >= {count}")


def render_pages(pdf, directory, dpi, previous):
    version = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True, check=True, timeout=10)
    config = dict(renderer=(version.stdout + version.stderr).splitlines()[0], dpi=dpi, format="png")
    key = fingerprint(config)[:12]
    pdf_hash = digest(pdf.read_bytes())
    directory = directory / (pdf_hash + "-" + key)
    directory.mkdir(parents=True, exist_ok=True)
    old = (previous or {}).get("rendering", {})
    comparable = old.get("status") == "rendered" and old.get("config") == config
    old_pages = old.get("pages", {}) if comparable else {}
    if old_pages and (previous or {}).get("pdf", {}).get("sha256") == pdf_hash:
        reusable = True
        for item in old_pages.values():
            path = Path(item["path"])
            if (path.parent.resolve() != directory.resolve() or not path.is_file()
                    or digest(path.read_bytes()) != item["sha256"]):
                reusable = False
                break
        if reusable:
            return dict(status="rendered", config=config, pages=old_pages, changed_pages=[], removed_pages=[],
                        comparison="same_renderer_config", cache_reused=True, visual_review="not_performed")
    # Render into a fresh subdirectory; never mix images from different PDF versions.
    with tempfile.TemporaryDirectory(prefix="render-", dir=directory) as staging:
        prefix = Path(staging) / "page"
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(prefix)],
                       capture_output=True, check=True, timeout=300)
        pages = {}
        for path in sorted(Path(staging).glob("page-*.png")):
            number = int(path.stem.rsplit("-", 1)[1])
            output = directory / path.name
            path.replace(output)
            pages[str(number)] = dict(sha256=digest(output.read_bytes()), path=str(output))
    changed = [int(n) for n, item in pages.items() if item["sha256"] != old_pages.get(n, {}).get("sha256")]
    return dict(status="rendered", config=config, pages=pages, changed_pages=sorted(changed),
                removed_pages=sorted(int(n) for n in old_pages if n not in pages),
                comparison="same_renderer_config" if comparable else "no_comparable_baseline",
                cache_reused=False, visual_review="not_performed")


def check(pdf: Path, *, aux=None, expect=None, previous=None, render_dir=None, dpi=96,
          render_previous=None, source=None):
    started = time.perf_counter()
    pdf = pdf.resolve()
    report = dict(schema=SCHEMA, pdf=dict(path=str(pdf), sha256=digest(pdf.read_bytes())),
                  checker_sha256=digest(Path(__file__).read_bytes()), findings=[],
                  scope="offline PDF structure; not mathematical, visual, GUI or external reachability certification",
                  rendering=dict(status="not_requested"), gui=dict(status="not_performed"),
                  external_reachability=dict(status="not_checked"))
    report["document_source"] = str(Path(source).resolve()) if source is not None else None
    report["expectations"] = dict(status="not_supplied")
    if expect is not None:
        report["expectations"] = dict(status="pending", path=str(Path(expect).resolve()))
    audit = None
    try:
        version = subprocess.run(["qpdf", "--version"], capture_output=True, text=True, check=True, timeout=10)
        report["qpdf_version"] = version.stdout.strip().splitlines()[0]
        result = subprocess.run(["qpdf", "--json", str(pdf)], capture_output=True, text=True, timeout=60)
        if result.returncode not in {0, 3}:
            raise ValueError("qpdf could not read PDF: " + result.stderr.strip()[:2000])
        audit = Audit(json.loads(result.stdout))
        report["findings"] = audit.findings
        if result.returncode == 3 or result.stderr.strip():
            audit.finding("unknown", "qpdf_diagnostic", "PDF", result.stderr.strip()[:2000])
        audit.run()
        if aux is not None:
            inspect_aux(audit, Path(aux))
        if expect is not None:
            data = Path(expect).read_bytes()
            report["expectations"].update(sha256=digest(data))
            inspect_expectations(audit, json.loads(data))
            report["expectations"]["status"] = "checked"
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        report["findings"].append(dict(severity="unknown", code="tool_or_input_unavailable", location="audit", detail=str(exc)))
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, RecursionError, subprocess.CalledProcessError) as exc:
        report["findings"].append(dict(severity="error", code="audit_failed", location="audit", detail=str(exc)))
    if audit is not None:
        report.update(counts=dict(pages=len(audit.pages), links=len(audit.links), outlines=len(audit.outlines),
                                  named_destinations=len(audit.names), aux_labels=len(audit.labels),
                                  link_kinds=dict(Counter(x["kind"] for x in audit.links))),
                      links=audit.links, outlines=audit.outlines, destinations=audit.destinations,
                      aux_files=audit.aux_files)
        report["navigation_fingerprints"] = {
            str(p): fingerprint(dict(links=[x for x in audit.links if x["page"] == p],
                                     destinations={k: v for k, v in audit.destinations.items() if v["page"] == p},
                                     outlines=[x for x in audit.outlines if x.get("target", {}).get("page") == p]))
            for p in range(1, len(audit.pages) + 1)
        }
    if previous:
        comparable = (isinstance(previous, dict) and previous.get("schema") == SCHEMA
                      and previous.get("document_source") == report["document_source"]
                      and previous.get("checker_sha256") == report["checker_sha256"]
                      and previous.get("qpdf_version") == report.get("qpdf_version"))
        old = previous.get("navigation_fingerprints", {}) if comparable else {}
        current = report.get("navigation_fingerprints", {})
        report["navigation_diff"] = dict(
            comparison="same_checker" if comparable else "no_comparable_baseline",
            changed_pages=sorted(int(p) for p in current if current[p] != old.get(p)),
            removed_pages=sorted(int(p) for p in old if p not in current),
            previous_pdf_sha256=previous.get("pdf", {}).get("sha256"),
            scope="navigation only; unchanged fingerprints do not prove unchanged page appearance")
    if render_dir is not None:
        try:
            render_reference = render_previous if render_previous is not None else previous
            if render_reference and render_reference.get("document_source") != report["document_source"]:
                render_reference = None
            report["rendering"] = render_pages(pdf, Path(render_dir), dpi,
                                               render_reference)
            if audit is not None and len(report["rendering"]["pages"]) != len(audit.pages):
                raise ValueError("rendered page count differs from PDF")
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            report["rendering"] = dict(status="failed", detail=str(exc))
            report["findings"].append(dict(severity="unknown", code="render_failed", location="rendering", detail=str(exc)))
    # Detect a concurrent rebuild rather than attaching results to different bytes.
    if digest(pdf.read_bytes()) != report["pdf"]["sha256"]:
        report["findings"].append(dict(severity="error", code="pdf_changed_during_check", location="PDF", detail="rerun on a stable artifact"))
    severities = Counter(x["severity"] for x in report["findings"])
    report["status"] = "fail" if severities["error"] else "incomplete" if severities["unknown"] else "pass"
    report["finding_counts"] = dict(severities)
    report["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    return report


def save_report(path, report):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("report must not be a symlink")
    inputs = [report.get("pdf", {}).get("path"), report.get("expectations", {}).get("path"),
              report.get("document_source")]
    inputs += [entry["path"] for entry in report.get("aux_files", [])]
    if path.resolve() in {Path(p).resolve() for p in inputs if p}:
        raise ValueError("report must not overwrite any input, including an included aux file")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, prefix=".navigation-", delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def render_baseline_path(report_path):
    path = Path(report_path)
    return path.with_name(path.stem + ".render.json")


def save_render_baseline(report_path, report):
    """Preserve rendered bytes independently of the latest structural audit."""
    if report.get("rendering", {}).get("status") != "rendered":
        return
    if any(f.get("code") == "pdf_changed_during_check" for f in report.get("findings", [])):
        return
    baseline = {k: report[k] for k in ("schema", "pdf")}
    baseline["document_source"] = report.get("document_source")
    baseline["rendering"] = {k: report["rendering"][k] for k in ("status", "config", "pages")}
    # Use all consumed inputs for the write guard, but keep only rendering evidence.
    baseline["aux_files"] = report.get("aux_files", [])
    baseline["expectations"] = report.get("expectations", {})
    save_report(render_baseline_path(report_path), baseline)


def load_render_baseline(report_path):
    path = render_baseline_path(report_path)
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(value, dict) or value.get("schema") != SCHEMA
                or not isinstance(value.get("pdf", {}).get("sha256"), str)
                or value.get("rendering", {}).get("status") != "rendered"
                or not isinstance(value["rendering"].get("config"), dict)
                or not isinstance(value["rendering"].get("pages"), dict)):
            raise ValueError("invalid rendering baseline")
        for number, item in value["rendering"]["pages"].items():
            if not number.isdigit() or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
                raise ValueError("invalid rendering page evidence")
        return value
    except (OSError, ValueError, AttributeError, TypeError) as exc:
        print(f"Rendering baseline unavailable; compare afresh: {path}: {exc}", file=sys.stderr)
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Expectations JSON (physical PDF pages are 1-based):
  {"min_links": 1, "min_outlines": 1,
   "destinations": ["theorem.1", {"name": "equation.1", "page": 2}],
   "routes": [{"from_page": 1, "to": "theorem.1", "min_count": 1},
              {"label": "eq:example"}]}
Use exactly one of "to" and "label" for each route; "label" requires --aux.
Omit from_page to search all pages. Derive expectations from the source's
required routes, not from links already present in the PDF.
Exit status: 0 = structural pass, 1 = defects, 2 = incomplete/unavailable.
No status certifies visual quality, GUI operation or external reachability.''')
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--aux", type=Path)
    parser.add_argument("--source", type=Path, help="TeX entry identity; prevents reuse across different document roots")
    parser.add_argument("--expect", type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--dpi", type=int, default=96)
    args = parser.parse_args(argv)
    if not 36 <= args.dpi <= 300:
        parser.error("dpi must be between 36 and 300")
    inputs = [p.resolve() for p in (args.pdf, args.aux, args.expect, args.source) if p is not None]
    if args.report.resolve() in inputs:
        parser.error("report must not overwrite an input")
    if args.render_dir is not None and render_baseline_path(args.report).resolve() in inputs:
        parser.error("rendering baseline must not overwrite an input")
    try:
        stored = None
        if args.report.is_file():
            try:
                stored = json.loads(args.report.read_text(encoding="utf-8"))
                if not isinstance(stored, dict) or not isinstance(stored.get("pdf", {}), dict):
                    stored = None
            except (OSError, ValueError):
                pass
        previous = json.loads(args.previous.read_text()) if args.previous and args.previous.exists() else stored
        if previous is not None and not isinstance(previous, dict):
            raise ValueError("previous report must be a JSON object")
        source = args.source
        if source is None and stored and stored.get("pdf", {}).get("sha256") == digest(args.pdf.read_bytes()):
            source = stored.get("document_source")
        expected = args.expect
        if expected is None and source is not None:
            candidate = Path(source).with_suffix(".navigation.json")
            if candidate.exists() or candidate.is_symlink():
                expected = candidate
        # Reuse only the auxiliary paths of the same PDF's latest build, and
        # read them afresh. Rendering must not silently drop required routes.
        aux = args.aux
        if aux is None and stored and stored.get("pdf", {}).get("sha256") == digest(args.pdf.read_bytes()):
            files = stored.get("aux_files", [])
            if files:
                aux = Path(files[0]["path"])
        result = check(args.pdf, aux=aux, expect=expected, previous=previous,
                       render_dir=args.render_dir, dpi=args.dpi,
                       render_previous=load_render_baseline(args.report) if args.render_dir else None,
                       source=source)
        save_render_baseline(args.report, result)
        save_report(args.report, result)
    except (OSError, ValueError) as exc:
        print(f"navigation: incomplete: {exc}", file=sys.stderr)
        return 2
    print(f"navigation: {result['status']}; {result.get('counts', {})}; {args.report}")
    return {"pass": 0, "fail": 1, "incomplete": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
