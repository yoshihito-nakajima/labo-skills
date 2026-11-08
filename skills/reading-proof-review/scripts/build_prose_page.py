#!/usr/bin/env python3
"""Build a single-file HTML page (KaTeX embedded) from authored Markdown.

Usage:
  build_prose_page.py PAGE.md --out PAGE.html [--lang ja|en] [--katex-dir DIR] [--fetch-katex]

This is the standalone route for a prose explanation (see references/routes.md). The input is the
Markdown dialect of the site generator, so one authored page can take either route:

  +++ frontmatter: title, slug, language +++
  headings, paragraphs, bullet and numbered lists, pipe tables, block quotes, fenced code,
  inline `code`, **bold**, *italic*, [links](https://...) and [anchors](#id),
  $inline$ and $$display$$ mathematics (also over several lines),
  ::: details Summary {#anchor} ... ::: (blocks nest),
  a figure on its own line: ![alt](asset:name.svg), read from figures/<slug>/name.svg next to the page.

Everything else is escaped; raw HTML is shown as text. The page is a local file, not a publication.
"""
import argparse
import html
import pathlib
import re
import sys

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_review_page import LABELS, find_katex, katex_assets  # noqa: E402

ANCHOR = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")


class PageError(SystemExit):
    pass


def split_front(text):
    m = re.match(r"\+\+\+\n(.*?)\n\+\+\+\n?", text, re.S)
    if not m:
        raise PageError("missing +++ frontmatter (title, slug, language)")
    meta = tomllib.loads(m.group(1)) if tomllib else dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', m.group(1)))
    return meta, text[m.end():]


class Converter:
    def __init__(self, base, slug):
        self.base, self.slug, self.h2 = pathlib.Path(base), slug, 0

    # ---- inline
    def inline(self, text):
        keep = []

        def hold(value):
            keep.append(value)
            return "\x00%d\x00" % (len(keep) - 1)

        text = re.sub(r"\\([\\*_`|$\[\]#<>])", lambda m: hold(html.escape(m.group(1))), text)
        text = re.sub(r"`([^`]+)`", lambda m: hold("<code>%s</code>" % html.escape(m.group(1))), text)
        text = re.sub(r"(?<!\\)\$([^$\n]+?)\$", lambda m: hold('<span class="m">%s</span>' % html.escape(m.group(1).strip())), text)
        text = html.escape(text, quote=False)

        def link(m):
            label, url = m.group(1), html.unescape(m.group(2))
            if not (url.startswith(("http://", "https://", "#", "mailto:")) or re.fullmatch(r"[\w./-]+(#[\w-]+)?", url)):
                raise PageError("unsupported link target: %s" % url)
            return '<a href="%s">%s</a>' % (html.escape(url), label)
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
        return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)

    # ---- blocks
    def blocks(self, lines):
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if not s:
                i += 1
            elif s.startswith("```"):
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith("```"):
                    j += 1
                out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(lines[i + 1:j])))
                i = j + 1
            elif s.startswith("::: details "):
                head = s[len("::: details "):]
                anchor = None
                m = re.search(r" \{#([^}]+)\}$", head)
                if m:
                    anchor = m.group(1)
                    if not ANCHOR.fullmatch(anchor) or anchor.startswith("section-"):
                        raise PageError("invalid details anchor: %s" % anchor)
                    head = head[:m.start()]
                depth, j = 1, i + 1
                while j < len(lines):
                    t = lines[j].strip()
                    if t.startswith("::: details "):
                        depth += 1
                    elif t == ":::":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                if j == len(lines):
                    raise PageError("unclosed details block: %s" % head)
                attr = ' id="%s"' % anchor if anchor else ""
                out.append('<details class="proof-details"%s><summary>%s</summary>\n%s\n</details>' % (attr, self.inline(head), self.blocks(lines[i + 1:j])))
                i = j + 1
            elif s.startswith("::: "):
                raise PageError("unsupported block: %s" % s)
            elif s.startswith("$$"):
                if s != "$$" and s.endswith("$$") and len(s) > 4:
                    tex, j = s[2:-2], i + 1
                else:
                    j = i + 1
                    body = [s[2:]] if s != "$$" else []
                    while j < len(lines) and not lines[j].strip().endswith("$$"):
                        body.append(lines[j])
                        j += 1
                    if j == len(lines):
                        raise PageError("unclosed display mathematics")
                    last = lines[j].strip()[:-2]
                    if last:
                        body.append(last)
                    tex, j = "\n".join(body), j + 1
                out.append('<div class="d">%s</div>' % html.escape(tex.strip()))
                i = j
            elif re.fullmatch(r"#{1,6}\s+.+", s):
                level = len(s) - len(s.lstrip("#"))
                title = s[level:].strip()
                ident = ""
                if level == 2:
                    self.h2 += 1
                    ident = ' id="section-%d"' % self.h2
                out.append("<h%d%s>%s</h%d>" % (level, ident, self.inline(title), level))
                i += 1
            elif re.fullmatch(r"(-{3,}|\*{3,})", s):
                out.append("<hr>")
                i += 1
            elif s.startswith(">"):
                j = i
                quoted = []
                while j < len(lines) and lines[j].strip().startswith(">"):
                    quoted.append(re.sub(r"^\s*>\s?", "", lines[j]))
                    j += 1
                out.append("<blockquote>%s</blockquote>" % self.blocks(quoted))
                i = j
            elif "|" in s and i + 1 < len(lines) and re.fullmatch(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?", lines[i + 1].strip()):
                rows, j = [], i
                while j < len(lines) and "|" in lines[j]:
                    rows.append(lines[j])
                    j += 1
                out.append(self.table(rows))
                i = j
            elif re.match(r"\s*([-*]|\d+\.)\s+", line):
                j = i
                items = []
                while j < len(lines) and (re.match(r"\s*([-*]|\d+\.)\s+", lines[j]) or (lines[j].startswith("  ") and lines[j].strip())):
                    items.append(lines[j])
                    j += 1
                out.append(self.lists(items))
                i = j
            else:
                j = i
                para = []
                while j < len(lines) and lines[j].strip() and not re.match(r"\s*(#{1,6}\s|```|::: |\$\$|>|([-*]|\d+\.)\s)", lines[j]):
                    para.append(lines[j].strip())
                    j += 1
                text = " ".join(para)
                fig = re.fullmatch(r"!\[([^\]]*)\]\(asset:([A-Za-z0-9._-]+\.svg)\)", text)
                out.append(self.figure(fig.group(1), fig.group(2)) if fig else "<p>%s</p>" % self.inline(text))
                i = max(j, i + 1)
        return "\n".join(out)

    def figure(self, alt, name):
        for cand in (self.base / "figures" / self.slug / name, self.base / "figures" / name):
            if cand.is_file():
                svg = re.sub(r"<\?xml[^>]*\?>", "", cand.read_text(encoding="utf-8")).strip()
                return "<figure>%s<figcaption>%s</figcaption></figure>" % (svg, html.escape(alt))
        raise PageError("figure not found: figures/%s/%s" % (self.slug, name))

    def table(self, rows):
        def cells(row):
            row = row.strip().strip("|")
            return [c.strip() for c in re.split(r"(?<!\\)\|", row)]
        head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
        th = "".join("<th>%s</th>" % self.inline(c) for c in head)
        tr = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % self.inline(c) for c in r) for r in body)
        return "<table><tr>%s</tr>%s</table>" % (th, tr)

    def lists(self, items):
        out, stack = [], []  # stack of (indent, tag)
        for raw in items:
            m = re.match(r"(\s*)([-*]|\d+\.)\s+(.*)", raw)
            if not m:
                out.append(" " + self.inline(raw.strip()))  # continuation of the previous item
                continue
            indent, marker, text = len(m.group(1)), m.group(2), m.group(3)
            tag = "ol" if marker[0].isdigit() else "ul"
            while stack and indent < stack[-1][0]:
                out.append("</li></%s>" % stack.pop()[1])
            if stack and indent == stack[-1][0]:
                out.append("</li>")
            elif not stack or indent > stack[-1][0]:
                out.append("<%s>" % tag)
                stack.append((indent, tag))
            out.append("<li>%s" % self.inline(text))
        while stack:
            out.append("</li></%s>" % stack.pop()[1])
        return "".join(out)


def build(md_path, lang, katex_dir, template_path):
    md_path = pathlib.Path(md_path)
    meta, body = split_front(md_path.read_text(encoding="utf-8"))
    title, slug = meta.get("title"), meta.get("slug")
    if not title or not slug:
        raise PageError("frontmatter needs title and slug")
    L = LABELS[lang]
    conv = Converter(md_path.parent, slug)
    content = conv.blocks(body.splitlines())
    page_body = "<h1>%s</h1>\n%s" % (html.escape(title), content)
    tpl = pathlib.Path(template_path).read_text(encoding="utf-8")
    css, js, missing = katex_assets(katex_dir)
    page = (tpl.replace("{{BODY}}", page_body).replace("{{TITLE}}", html.escape(title)).replace("{{LANG}}", lang)
            .replace("{{EXTRA_SCRIPT}}", "").replace("/*KATEX_CSS*/", css).replace("/*KATEX_JS*/", js))
    page = re.sub(r"\{\{L:([a-z_]+)\}\}", lambda m: html.escape(L[m.group(1)]), page)
    return page, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang")
    ap.add_argument("--katex-dir")
    ap.add_argument("--fetch-katex", action="store_true", help="download the pinned KaTeX (MIT) into the cache when none is found")
    ap.add_argument("--template", default=str(HERE.parent / "assets/prose-page-template.html"))
    a = ap.parse_args(argv)
    meta, _ = split_front(pathlib.Path(a.page).read_text(encoding="utf-8"))
    lang = a.lang or meta.get("language", "ja")
    if lang not in LABELS:
        raise PageError("language must be one of %s" % ", ".join(sorted(LABELS)))
    kdir = find_katex(a.katex_dir)
    if not kdir and a.fetch_katex:
        from fetch_katex import fetch
        kdir = fetch()
    page, missing = build(a.page, lang, kdir, a.template)
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.out).write_text(page, encoding="utf-8")
    print(f"wrote {a.out} ({len(page) // 1024} KB)")
    if not kdir:
        print("WARNING: no KaTeX found (run fetch_katex.py, or pass --fetch-katex, --katex-dir or set KATEX_DIR); math stays as visible TeX source")
    elif missing:
        print("WARNING: KaTeX fonts missing: " + ", ".join(missing) + " (avoid \\mathbb, \\mathbf, \\mathcal, \\mathit where absent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
