#!/usr/bin/env python3
"""List what changed between two versions of a TeX file, by label and section rather than by line.

  python3 label_diff.py <old.tex> <new.tex> [--title TEXT] [--name NAME] > changes.md

The file is cut into segments at every line containing \\label{...}; a segment is keyed by its first
label and runs to the next label. Segments are compared by content: added, changed, removed. Each label
is reported under its enclosing \\section (the section's own label and title), with the size of the
change (whitespace-only changes are ignored). Line numbers in the new
file are given as hints only; labels are the stable locator for reviews and bookmarks.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import pathlib
import re
import sys

LABEL = re.compile(r"\\label\{([^}]*)\}")
SECTION = re.compile(r"\\section\*?(?:\[[^\]]*\])?\{(.*)\}")
ENV = re.compile(r"\\begin\{([A-Za-z*]+)\}")


def segments(text: str) -> tuple[dict[str, dict], list[str]]:
    """Return label -> {hash, section, title, line, env} and the label order."""
    segs: dict[str, dict] = {}
    order: list[str] = []
    section, title, current, buf, start, env = "(before first section)", "", None, [], 1, ""
    lines = text.splitlines()

    def close():
        if current is not None and current not in segs:
            norm = [" ".join(x.split()) for x in buf if x.strip()]
            segs[current] = {"hash": hashlib.sha1("\n".join(norm).encode()).hexdigest(), "lines": norm, "section": sec_of,
                             "title": title_of, "line": start, "env": env}
            order.append(current)

    sec_of, title_of = section, title
    for i, line in enumerate(lines, 1):
        m_sec = SECTION.search(line)
        if m_sec:
            title = m_sec.group(1).split("}\\label")[0].strip()
        labels = LABEL.findall(line)
        if labels:
            close()
            if m_sec or (i > 1 and SECTION.search(lines[i - 2]) and not LABEL.search(lines[i - 2])):
                section = labels[0]
            current, buf, start = labels[0], [], i
            m_env = ENV.search(line) or (ENV.search(lines[i - 2]) if i > 1 else None)
            env = m_env.group(1) if m_env else ""
            sec_of, title_of = section, title
        buf.append(line)
    close()
    return segs, order


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("old", type=pathlib.Path)
    ap.add_argument("new", type=pathlib.Path)
    ap.add_argument("--title", default="ラベル単位の変更一覧")
    ap.add_argument("--name", help="file name to show (default: the new file's name)")
    a = ap.parse_args(argv)
    old, _ = segments(a.old.read_text(errors="ignore"))
    new, order = segments(a.new.read_text(errors="ignore"))
    added = [k for k in order if k not in old]
    changed = [k for k in order if k in old and old[k]["hash"] != new[k]["hash"]]
    removed = [k for k in old if k not in new]
    name = a.name or a.new.name
    out = [f"# {a.title}", "",
           f"`{name}`：旧版 sha256 `{hashlib.sha256(a.old.read_bytes()).hexdigest()[:12]}` → "
           f"新版 `{hashlib.sha256(a.new.read_bytes()).hexdigest()[:12]}`。"
           f"追加 {len(added)}、変更 {len(changed)}、削除 {len(removed)} ラベル。行番号は新版での目安。", ""]
    by_section: dict[str, list[str]] = {}
    for k in order:
        if k in added or k in changed:
            by_section.setdefault(new[k]["section"], []).append(k)
    for sec, keys in by_section.items():
        title = new[sec]["title"] if sec in new else ""
        state = "新しい節" if sec in added else "既存の節"
        out.append(f"## `{sec}` {title}（{state}、L{new[sec]['line'] if sec in new else '?'}〜）")
        out.append("")
        for k in keys:
            if k in added:
                kind = f"追加（{len(new[k]['lines'])} 行）"
            else:
                d = sum(1 for x in difflib.ndiff(old[k]["lines"], new[k]["lines"]) if x[:1] in "+-")
                kind = f"変更（差 {d} 行）"
            env = f" {new[k]['env']}" if new[k]["env"] else ""
            out.append(f"- {kind}：`{k}`{env}（L{new[k]['line']}）")
        out.append("")
    if removed:
        out += ["## 削除されたラベル", ""] + [f"- `{k}`（旧版 L{old[k]['line']}、節 `{old[k]['section']}`）" for k in removed] + [""]
    sys.stdout.write("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
