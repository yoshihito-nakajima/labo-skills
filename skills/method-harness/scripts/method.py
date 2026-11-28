#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""method-harness: read a method paper as cards of claims, code, figures and runs, along several routes.

Cards are canonical; HTML is generated. The source text is not stored, only locators (page, file,
line) and fingerprints. Outputs are private and local.

    python3 <skill>/scripts/method.py --root <project> <command>

commands: check status list show search new closure impact anchor run set-status html graph fingerprints
"""
import argparse
import base64
import datetime
import hashlib
import html as H
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from book_links import BookReferences
from claim_readings import ClaimReadings
from lineage import check_lineage, required as lineage_required
from passages import check_passages, load_writing_fact, writing_namespaces

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEFAULT_ROOT = Path.cwd()
COMMENT_JS = REPO / "src/labo_tools/assets/comment-layer.js"
WRITING_CARDS = REPO / "skills/writing-harness/scripts/cards.py"

STATUS = ["stated", "traced", "reproduced", "checked"]
STATUS_JA = {"stated": "写した", "traced": "原典と合わせた", "reproduced": "動かした", "checked": "独立に確認"}
ORIGINS = {"original", "ai-written", "ai-standin", "reader"}
ORIGIN_JA = {"original": "原著", "ai-written": "AI 作成(未照合)", "ai-standin": "AI 代役", "reader": "読者"}
FACT = ["claim", "step", "figure", "term", "api", "run"]
GLUE = ["ask", "bridge", "preview", "recap", "entrance"]
LEDGER = ["source", "map", "finding"]
# 種類 → 必須の節 / 必須の欄
SPEC = {
    "claim": (["内容"], []), "step": (["説明"], ["code", "lang"]), "figure": (["何を示すか"], ["page"]),
    "term": (["説明"], []), "api": (["説明"], ["sig"]), "run": (["内容"], ["command"]),
    "ask": (["問い"], []), "bridge": (["済んだこと", "足りないこと", "次にすること"], ["between"]),
    "preview": (["後で示すこと"], ["forward"]), "recap": (["確立したこと"], []), "entrance": (["問いと終点"], []),
    "source": (["書誌"], []), "map": (["対応"], []), "finding": (["所見"], ["target"]),
}
FP_SKIP = {"注意"}
REF_FIELDS = ["requires", "references", "realizes", "shows", "produced_by", "evidence", "forward", "between", "answered_by"]
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
MENTION = re.compile(r"\[\[([a-z][a-z0-9-]*)\]\]")


# ---------------------------------------------------------------- 読み書き
class Card:
    def __init__(self, path, fm, secs, raw):
        self.path, self.fm, self.secs, self.raw = path, fm, secs, raw
        self.id = fm.get("id"); self.kind = fm.get("kind")

    def get(self, k, d=None):
        v = self.fm.get(k, d)
        return d if v is None else v

    def refs(self, field):
        v = self.fm.get(field) or []
        if isinstance(v, str):
            v = [v]
        out = []
        for x in v:
            out.append(x.get("card") if isinstance(x, dict) else x)
        return [x for x in out if isinstance(x, str)]


def parse(path):
    raw = Path(path).read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n?(.*)\Z", raw, re.S)
    if not m:
        raise ValueError("前書き(---)が読めない")
    fm = yaml.safe_load(m.group(1)) or {}
    if not isinstance(fm, dict):
        raise ValueError("前書きが辞書でない")
    secs, cur, buf = {}, None, []
    for line in m.group(2).split("\n"):
        h = re.match(r"^## (.+?)\s*$", line)
        if h:
            if cur is not None:
                secs[cur] = "\n".join(buf).strip()
            cur, buf = h.group(1), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        secs[cur] = "\n".join(buf).strip()
    return Card(Path(path), fm, secs, raw)


class Root:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.cards, self.errors, self.paths = {}, [], {}
        self.routes = {}
        if not (self.root / "harness.toml").exists():
            raise SystemExit(f"harness.toml が無い: {self.root}(init で作る)")
        files = list(self.root.glob("pool/**/*.md")) + list(self.root.glob("src/*.md")) + \
            list(self.root.glob("route/*/card/*.md")) + list(self.root.glob("route/*/map/*.md")) + \
            list(self.root.glob("route/*/finding/*.md"))
        for p in sorted(files):
            try:
                c = parse(p)
            except Exception as e:   # noqa: BLE001
                self.errors.append(("ERR", "PARSE", p.stem, str(e))); continue
            if c.id in self.cards:
                self.errors.append(("ERR", "DUPLICATE-ID", c.id, f"{p} と {self.cards[c.id].path}"))
                continue
            self.cards[c.id] = c
        for rf in sorted(self.root.glob("route/*/route.yaml")):
            try:
                self.routes[rf.parent.name] = yaml.safe_load(rf.read_text(encoding="utf-8")) or {}
            except Exception as e:   # noqa: BLE001
                self.errors.append(("ERR", "PARSE", rf.parent.name, f"route.yaml: {e}"))

    # --- コード(読むだけ)
    def code_root(self, c):
        src = self.cards.get((c.get("code") or {}).get("src"))
        if not src or not src.get("code_root"):
            return None
        return (self.root / src.get("code_root")).resolve()

    def code_lines(self, c):
        cd = c.get("code") or {}
        cr = self.code_root(c)
        if cr is None or "file" not in cd:
            return None, "コードの場所(src の code_root / file)が決まっていない"
        f = cr / cd["file"]
        if not f.is_file():
            return None, f"ファイルが無い: {f}"
        a, b = (cd.get("lines") or [1, 0])[:2]
        L = f.read_text(encoding="utf-8").split("\n")
        if a < 1 or b > len(L) or a > b:
            return None, f"行範囲 {a}-{b} が範囲外(ファイルは {len(L)} 行)"
        return L[a - 1:b], None

    def code_fp(self, c):
        L, err = self.code_lines(c)
        return None if L is None else sha8("\n".join(x.rstrip() for x in L))

    def fingerprint(self, c):
        body = "\0".join(f"{k}\0{norm(v)}" for k, v in c.secs.items() if k not in FP_SKIP)
        extra = self.code_fp(c) if c.kind == "step" else ""
        if c.kind == "run":
            # A run's text depends on its result: re-running with a different outcome makes citing text STALE.
            r = self.run_record(c.id) or {}
            extra = json.dumps([r.get("exit"), r.get("stdout_fp"), r.get("files"), self.record_state(c.id)],
                               sort_keys=True)
        return sha8(f"{c.kind}\0{c.get('variant', '')}\0{body}\0{extra or ''}")

    def runs_dir(self):
        return self.root / "runs"

    def run_record(self, rid):
        p = self.runs_dir() / f"{rid}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def record_state(self, rid):
        """None=記録なし / 'failed' / 'stale' / 'ok'"""
        r = self.run_record(rid)
        if r is None:
            return None
        if r.get("exit") != 0:
            return "failed"
        card = self.cards.get(rid)
        if card is None or (r.get("command"), r.get("cwd")) != (
            card.get("command"), card.get("cwd", ".")
        ) or set(r.get("files") or {}) != set(card.get("files") or []):
            return "stale"
        cr = self.run_code_root(rid)
        for f, fp in (r.get("files") or {}).items():
            p = (cr / f) if cr else None
            if p is None or not p.is_file() or sha8(p.read_text(encoding="utf-8")) != fp:
                return "stale"
        return "ok"

    def run_code_root(self, rid):
        c = self.cards.get(rid)
        if not c:
            return None
        src = self.cards.get(c.get("src"))
        return (self.root / src.get("code_root")).resolve() if src and src.get("code_root") else None


def sha8(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:8]


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip()


# ---------------------------------------------------------------- 検査
def where_ok(root, c):
    p = c.path.relative_to(root.root).parts
    if c.kind in FACT:
        return p[0] == "pool"
    if c.kind in GLUE:
        return p[0] == "route" and p[2] == "card"
    if c.kind == "source":
        return p[0] == "src"
    return p[0] == "route" and p[2] == {"map": "map", "finding": "finding"}[c.kind]


def route_items(rt):
    """route.yaml → [(section title, [(id, show)])]"""
    out = []
    for s in rt.get("sections") or []:
        its = []
        for it in s.get("items") or []:
            if isinstance(it, dict):
                its.append((it["card"], it.get("show")))
            else:
                its.append((it, None))
        out.append((s.get("title", ""), its))
    return out


def route_ids(root, name, seen=None):
    seen = seen or set()
    if name in seen:
        return []
    seen.add(name)
    rt = root.routes.get(name, {})
    ids = []
    for inc in rt.get("includes") or []:
        ids += route_ids(root, inc, seen)
    for _, its in route_items(rt):
        ids += [i for i, _ in its]
    return ids


def check(root, route=None):
    E = list(root.errors)
    C = root.cards
    books = BookReferences(root.root)
    try:
        readings = ClaimReadings(root.root)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        E.append(("ERR", "CLAIM-READING", "harness", str(error)))
    else:
        passages = [(card.id, entry) for card in C.values() if card.kind == "map"
                    for entry in (card.get("passages") if isinstance(card.get("passages"), list) else [])
                    if isinstance(entry, dict) and isinstance(entry.get("id"), str)
                    and isinstance(entry.get("links"), list)
                    and all(isinstance(link, dict) for link in entry["links"])]
        errors = readings.check([entry for _, entry in passages])
        E.extend(("ERR", "CLAIM-READING", identifier, message) for identifier, message in errors)
        walked = {link["card"] for _, entry in passages for link in entry["links"] if "walkthrough" in link}
        need_lineage = lineage_required(root.root)
        for card in C.values():
            if card.kind != "step":
                continue
            problems = check_lineage(card, C)
            if problems is None and need_lineage and card.id in walked:
                problems = ["lineage（提案・意図・コードの素性・違い）が必要"]
            E.extend(("ERR", "LINEAGE", card.id, message) for message in problems or [])
        for identifier, entries in readings.entries.items():
            for entry in entries if isinstance(entries, list) else []:
                origin = entry.get("origin") if isinstance(entry, dict) else None
                if isinstance(origin, dict) and origin.get("src") and getattr(C.get(origin["src"]), "kind", None) != "source":
                    E.append(("ERR", "CLAIM-READING", identifier, f'{entry.get("id")}: origin.src {origin["src"]} は source カードではない'))
        invalid = {identifier for identifier, _ in errors}
        for map_id, passage in passages:
            identifier = passage["id"]
            if identifier in invalid:
                continue
            for link in passage["links"]:
                if "walkthrough" in link:
                    live = readings.walkthrough_fingerprint(identifier, link)
                    if link["walkthrough"].get("fingerprint") != live:
                        E.append(("WARN", "STALE-PASSAGE", map_id,
                                  f"{identifier}: {link.get('key')} のコードと数学の対応を再確認"))
    for c in C.values():
        i = c.id
        if not isinstance(i, str) or not ID_RE.match(i):
            E.append(("ERR", "BAD-ID", str(i), "ID は小文字ケバブ形式")); continue
        if c.path.stem != i:
            E.append(("ERR", "ID-FILE", i, f"ファイル名 {c.path.name} と id が違う"))
        if c.kind not in SPEC:
            E.append(("ERR", "BAD-KIND", i, f"種類 {c.kind!r} は未定義")); continue
        if not where_ok(root, c):
            E.append(("ERR", "WRONG-PLACE", i, f"{c.kind} は置き場所が違う: {c.path.relative_to(root.root)}"))
        if not c.get("title"):
            E.append(("ERR", "NO-TITLE", i, "title が無い"))
        st = c.get("status", "stated")
        if st not in STATUS:
            E.append(("ERR", "BAD-STATUS", i, f"status {st!r}"))
        if c.get("origin") and c.get("origin") not in ORIGINS:
            E.append(("ERR", "BAD-ORIGIN", i, f"origin {c.get('origin')!r}(原著 / ai-written / ai-standin / reader)"))
        secs, need = SPEC[c.kind]
        for s in secs:
            if s not in c.secs:
                E.append(("ERR", "NO-SECTION", i, f"節「{s}」が無い"))
            elif c.secs[s].strip() in ("", "TODO"):
                E.append(("WARN", "PLACEHOLDER", i, f"節「{s}」が空か TODO"))
        for f in need:
            if not c.get(f):
                E.append(("ERR", "NO-FIELD", i, f"欄 {f} が無い"))
        # 参照
        for f in REF_FIELDS:
            rs = c.refs(f)
            if len(rs) != len(set(rs)):
                E.append(("WARN", "DUP-REF", i, f"{f} に重複"))
            for r in rs:
                if r not in C:
                    E.append(("ERR", "UNKNOWN-REF", i, f"{f}: {r}"))
                elif r == i and f == "requires":
                    E.append(("ERR", "SELF-EDGE", i, "自分自身を requires"))
        for r in c.get("relations", []) or []:
            to = r.get("to") if isinstance(r, dict) else None
            if to not in C:
                E.append(("ERR", "UNKNOWN-REF", i, f"relations.to: {to}"))
            elif r.get("type") == "variant" and not r.get("diff"):
                E.append(("ERR", "RELATION-DIFF", i, "variant には diff(何が違うか)が要る"))
        for s in c.get("sources", []) or []:
            if (s.get("src") if isinstance(s, dict) else None) not in C:
                E.append(("ERR", "UNKNOWN-REF", i, f"sources.src: {s}"))
        if c.get("variant_of") and c.get("variant_of") not in C:
            E.append(("ERR", "UNKNOWN-REF", i, f"variant_of: {c.get('variant_of')}"))
        for a in (c.get("anchors") or {}):
            if a not in C:
                E.append(("ERR", "UNKNOWN-REF", i, f"anchors: {a}"))
            elif C[a].kind in SPEC and root.fingerprint(C[a]) != c.fm["anchors"][a]:
                E.append(("WARN", "STALE", i, f"{a} が変わった(読み直して anchor を更新)"))
        if c.kind == "map" and "passages" in c.fm:
            E.extend(check_passages(root, c, WRITING_CARDS, books))
        for t in c.secs.values():
            for m in MENTION.findall(t):
                if m not in C:
                    E.append(("ERR", "UNKNOWN-REF", i, f"[[{m}]]"))
        # 種類ごと
        if c.kind == "step":
            L, err = root.code_lines(c)
            if err:
                E.append(("ERR", "CODE-MISSING", i, err))
            else:
                rec = (c.get("code") or {}).get("fp")
                live = root.code_fp(c)
                if rec and rec != live:
                    E.append(("WARN", "CODE-CHANGED", i, f"コードが変わった(記録 {rec} → 今 {live})。説明を読み直して anchor"))
                if not rec:
                    E.append(("WARN", "NO-CODE-FP", i, "code.fp が未記録(anchor で記録)"))
                a, b = c.get("code")["lines"][:2]
                for ln in (c.secs.get("行説明") or "").split("\n"):
                    m = re.match(r"^\s*-?\s*(\d+)(?:-(\d+))?:\s", ln)
                    if ln.strip() and not m:
                        E.append(("WARN", "BAD-LINE-NOTE", i, f"行説明の形が違う: {ln[:30]}"))
                    elif m and not (a <= int(m.group(1)) <= b):
                        E.append(("ERR", "BAD-LINE-NOTE", i, f"行説明 {m.group(1)} はコード範囲 {a}-{b} の外"))
            if c.get("origin") == "ai-standin" and not c.get("variant_of"):
                E.append(("WARN", "STANDIN-NO-ORIGINAL", i, "AI 代役は、原著のコードがある Step の言語違いにだけ使う(variant_of)"))
        if c.kind == "source" and not (c.get("edition") or c.get("sha256")):
            E.append(("WARN", "NO-EDITION", i, "版か sha256 を記録する"))
        if c.kind == "source" and c.get("code_root") and not (root.root / c.get("code_root")).is_dir():
            E.append(("ERR", "CODE-MISSING", i, f"code_root が無い: {c.get('code_root')}"))
        # 状態の梯子
        if st in ("reproduced", "checked"):
            ev = c.refs("evidence")
            if not ev:
                E.append(("ERR", "NO-EVIDENCE", i, f"{st} には evidence(実行の記録つき run カード)が要る"))
            for r in ev:
                s = root.record_state(r)
                if s is None:
                    E.append(("ERR", "NO-RUN-RECORD", i, f"{r} の実行記録が無い(run で記録)"))
                elif s == "failed":
                    E.append(("ERR", "RUN-FAILED", i, f"{r} の実行が失敗"))
                elif s == "stale":
                    E.append(("WARN", "STALE-RUN", i, f"{r} の記録の後でコードが変わった。もう一度 run"))
        if st in ("traced", "reproduced", "checked") and c.kind in FACT and not c.get("sources") and c.get("origin") != "reader" and c.kind != "run":
            E.append(("WARN", "NO-SOURCE", i, f"{st} だが sources(出典の位置)が無い"))
    # requires の循環
    state = {}

    def dfs(n, path):
        state[n] = 1
        for r in (C[n].refs("requires") if n in C else []):
            if r not in C:
                continue
            if state.get(r) == 1:
                E.append(("ERR", "CYCLE", n, " → ".join(path + [n, r]))); continue
            if r not in state:
                dfs(r, path + [n])
        state[n] = 2
    for n in C:
        if n not in state:
            dfs(n, [])
    if route:
        E += check_route(root, route)
    return E


def check_route(root, name):
    E, C = [], root.cards
    if name not in root.routes:
        return [("ERR", "NO-ROUTE", name, "route.yaml が無い")]
    rt = root.routes[name]
    free = rt.get("order") == "free"
    inc = set()
    for n in rt.get("includes") or []:
        inc |= set(route_ids(root, n))
    seq = [i for _, its in route_items(rt) for i, _ in its]
    pos = {}
    for k, i in enumerate(seq):
        if i not in C:
            E.append(("ERR", "ROUTE-UNKNOWN", name, f"{i}")); continue
        if i in pos:
            E.append(("WARN", "DUPLICATE-IN-ROUTE", i, "route に 2 回出る"))
        pos.setdefault(i, k)
    borrowed = set()
    for i in seq:
        if i in C and C[i].kind == "entrance":
            borrowed |= {b for b in C[i].refs("borrows")}
    for i in seq:
        c = C.get(i)
        if not c:
            continue
        for r in c.refs("requires"):
            if r in pos and pos[r] < pos[i]:
                continue
            if r in inc or r in borrowed:
                continue
            if r in pos:
                E.append(("INFO" if free else "ERR", "FORWARD-OK" if free else "FORWARD", i, f"{r} より前に出る(この route は{'順序が緩い' if free else '厳密'})"))
            else:
                E.append(("ERR", "UNLISTED-BORROW", i, f"{r} が route にも entrance の borrows にも無い"))
        if c.kind == "bridge":
            a, b = (c.refs("between") + [None, None])[:2]
            if a not in pos or b not in pos or not pos[a] < pos[i] < pos[b]:
                E.append(("ERR", "BAD-BETWEEN", i, "between の 2 枚の間に置く"))
            for n in (a, b):
                if n and n in C and n not in (c.get("anchors") or {}):
                    E.append(("WARN", "NO-ANCHOR", i, f"{n} への anchor が無い"))
        if c.kind == "ask" and not any(a in pos and pos[a] > pos[i] for a in c.refs("answered_by")):
            E.append(("WARN", "OPEN-QUESTION", i, "答えるカード(answered_by)がこの route の後ろに無い"))
        if c.kind == "preview":
            for f in c.refs("forward"):
                if f in pos and pos[f] < pos[i]:
                    E.append(("WARN", "PREVIEW-EARLIER", i, f"{f} は先取りより前に出ている"))
        for t in c.secs.values():
            for m in MENTION.findall(t):
                if m in C and m not in pos and m not in inc and m not in borrowed:
                    E.append(("WARN", "REF-OUTSIDE-ROUTE", i, f"[[{m}]] は route の外"))
    for c in C.values():
        if c.kind in GLUE and c.path.parts[-3] == name and c.id not in pos:
            E.append(("WARN", "UNUSED-GLUE", c.id, "この route の つなぎだが置かれていない"))
    return E


# ---------------------------------------------------------------- 書き換え(前書きの 1 行だけ)
def set_status_text(raw, status):
    if re.search(r"^status:.*$", raw, re.M):
        return re.sub(r"^status:.*$", f"status: {status}", raw, count=1, flags=re.M)
    return raw.replace("\n---\n", f"\nstatus: {status}\n---\n", 1)


def set_block(raw, key, value):
    """トップレベルのキー 1 つを置き換える(無ければ前書きの末尾に足す)。value は YAML の辞書か値。"""
    snippet = yaml.dump({key: value}, allow_unicode=True, sort_keys=False, default_flow_style=False, width=10**6)
    rx = re.compile(rf"^{re.escape(key)}:.*(?:\n(?:[ \t]*\n)*(?:[ \t]+.*|- .*|-$))*\n?", re.M)
    if rx.search(raw):
        out = rx.sub(lambda _m: snippet, raw, count=1)
    else:
        m = re.match(r"(---\n.*?\n)(---\n?)", raw, re.S)
        if not m:
            raise ValueError(f"前書きが無い(何も書かなかった): {key}")
        out = m.group(1) + snippet + m.group(2) + raw[m.end():]
    mm = re.match(r"---\n(.*?)\n---\n?", out, re.S)      # 書き換え後も前書きが読めること(壊れたら書かない)
    try:
        fm = yaml.safe_load(mm.group(1)) if mm else None
    except Exception:   # noqa: BLE001
        fm = None
    if not isinstance(fm, dict) or key not in fm:
        raise ValueError(f"前書きの書き換えに失敗(何も書かなかった): {key}")
    return out


def cmd_anchor(root, a):
    """読み直したあとで、現在の指紋を記録する(anchors と、step の code.fp)。"""
    c = root.cards.get(a.id) or sys.exit(f"無い: {a.id}")
    raw = c.raw
    if c.kind == "step" and c.get("code"):
        live = root.code_fp(c)
        if live:
            cd = dict(c.get("code")); cd["fp"] = live
            raw = set_block(raw, "code", cd)
    if c.get("anchors") is not None or a.all or a.to:
        an = dict(c.get("anchors") or {})
        for t in (a.to or []):
            if t not in root.cards:
                sys.exit(f"無い: {t}")
            an.setdefault(t, "")
        for t in list(an):
            if t in root.cards:
                an[t] = root.fingerprint(root.cards[t])
        raw = set_block(raw, "anchors", an)
        c.fm["anchors"] = an
    if c.kind == "map" and c.get("passages"):
        books = BookReferences(root.root)
        errors = [message for level, _, _, message in check_passages(root, c, WRITING_CARDS, books) if level == "ERR"]
        if errors:
            sys.exit("\n".join(errors))
        walkthroughs = [(passage, link) for passage in c.get("passages") for link in passage["links"]
                        if "walkthrough" in link]
        if walkthroughs:
            readings = ClaimReadings(root.root)
            for passage in c.get("passages"):
                errors = readings.check_walkthroughs(passage)
                if errors:
                    sys.exit("\n".join(errors))
            for passage, link in walkthroughs:
                link["walkthrough"]["fingerprint"] = readings.walkthrough_fingerprint(passage["id"], link)
        namespaces = writing_namespaces(root.root)
        for passage in c.get("passages"):
            for link in passage["links"]:
                if link["role"] == "math":
                    fact = load_writing_fact(root.root, WRITING_CARDS, link["card"], namespaces)
                    link["fingerprint"] = fact.fingerprint()
                elif link["role"] == "book":
                    link["version"] = books.resolve(link["card"]).version
        raw = set_block(raw, "passages", c.get("passages"))
    c.path.write_text(raw, encoding="utf-8")
    print(f"anchor 更新: {a.id}")


def cmd_set_status(root, a):
    c = root.cards.get(a.id) or sys.exit(f"無い: {a.id}")
    if a.status not in STATUS:
        sys.exit(f"status は {STATUS}")
    if a.status in ("reproduced", "checked"):
        ev = c.refs("evidence")
        bad = [r for r in ev if root.record_state(r) != "ok"]
        if not ev or bad:
            sys.exit(f"{a.status} にするには、evidence の全 run に有効な実行記録が要る(無効/無し: {bad or 'evidence 欄なし'})")
    c.path.write_text(set_status_text(c.raw, a.status), encoding="utf-8")
    print(f"{a.id}: {c.get('status', 'stated')} → {a.status}")


# ---------------------------------------------------------------- run
def cmd_run(root, a):
    c = root.cards.get(a.id)
    if not c or c.kind != "run":
        sys.exit(f"run カードではない: {a.id}")
    cr = root.run_code_root(a.id)
    if cr is None:
        sys.exit("run カードの src(code_root つきの source)が決まっていない")
    cmd = c.get("command").replace("{python}", sys.executable)
    cwd = cr / c.get("cwd", ".")
    print(f"実行: {cmd}\n  場所: {cwd}")
    t0 = datetime.datetime.now().astimezone()
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=c.get("timeout", 600))
        code, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        code, out, err = -9, (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "timeout"
    files = {}
    for f in c.get("files") or []:
        p_ = cr / f
        files[f] = sha8(p_.read_text(encoding="utf-8")) if p_.is_file() else None
    rec = {"id": a.id, "command": c.get("command"), "cwd": c.get("cwd", "."), "exit": code,
           "stdout_fp": sha8(out), "stdout": out[:4000], "stderr": err[:1000], "date": t0.isoformat(timespec="seconds"),
           "python": sys.version.split()[0], "platform": sys.platform, "files": files}
    root.runs_dir().mkdir(exist_ok=True)
    (root.runs_dir() / f"{a.id}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"終了コード {code}。出力:\n{out[:600]}")
    print(f"記録: runs/{a.id}.json")
    sys.exit(0 if code == 0 else 1)


# ---------------------------------------------------------------- 一覧・検索・影響
def rev_index(root):
    rv = {}
    for c in root.cards.values():
        for f in REF_FIELDS:
            for r in c.refs(f):
                rv.setdefault(r, []).append((c.id, f))
    return rv


def closure(root, ids, field="requires"):
    seen, st = [], list(ids)
    while st:
        n = st.pop()
        for r in (root.cards[n].refs(field) if n in root.cards else []):
            if r not in seen:
                seen.append(r); st.append(r)
    return seen


def impact(root, ids):
    rv = rev_index(root); seen, st = [], list(ids)
    while st:
        n = st.pop()
        for d, f in rv.get(n, []):
            if d not in seen:
                seen.append(d); st.append(d)
    return seen


def tokens(s):
    s = s.lower()
    w = set(re.findall(r"[a-z0-9_]{2,}", s))
    cj = re.findall(r"[ぁ-んァ-ヶ一-龥ー]+", s)
    for x in cj:
        w |= {x[i:i + 2] for i in range(len(x) - 1)} if len(x) > 1 else {x}
    return w


def search(root, q, kind=None, n=8):
    qt = tokens(q); out = []
    for c in root.cards.values():
        if c.kind not in FACT or (kind and c.kind != kind):
            continue
        t = tokens(" ".join([c.id, str(c.get("title", "")), str(c.get("gist", "")), " ".join(c.secs.values())]))
        sc = len(qt & t)
        if sc:
            out.append((sc, c.id, c.get("title", "")))
    return sorted(out, reverse=True)[:n]


def cmd_new(root, a):
    if a.kind not in SPEC:
        sys.exit(f"種類は {list(SPEC)}")
    if a.id in root.cards:
        sys.exit(f"既にある: {a.id}")
    if not ID_RE.match(a.id):
        sys.exit("ID は小文字ケバブ形式")
    rel = ""
    if a.kind in FACT:
        hits = search(root, a.title, a.kind, 3)
        qn = len(tokens(a.title))
        strong = [h for h in hits if h[0] >= 3 or (h[0] >= 2 and h[0] >= 0.6 * qn)]   # 短い題名でも、ほぼ全部が一致すれば似ているとみなす
        if strong and not a.decision:
            print("似たカードがある(--decision reuse | variant:<id> | new --reason ... を付ける):")
            for h in strong:
                print(f"  {h[1]}  {h[2]}  (一致 {h[0]})")
            sys.exit(2)
        if a.decision == "reuse":
            print("再利用。何も書かない。route にそのカードを並べる。"); return
        if a.decision and a.decision.startswith("variant:"):
            to = a.decision.split(":", 1)[1]
            if to not in root.cards:
                sys.exit(f"variant 先が無い: {to}")
            rel = f"relations:\n- {{to: {to}, type: variant, diff: TODO(何が違うか)}}\n"
        elif a.decision == "new" and not a.reason:
            sys.exit("--decision new には --reason が要る")
    secs, need = SPEC[a.kind]
    if a.kind in FACT:
        d = root.root / "pool" / (a.area or "misc")
    elif a.kind in GLUE:
        d = root.root / "route" / (a.route or sys.exit("つなぎには --route")) / "card"
    elif a.kind == "source":
        d = root.root / "src"
    else:
        d = root.root / "route" / (a.route or sys.exit("--route")) / {"map": "map", "finding": "finding"}[a.kind]
    d.mkdir(parents=True, exist_ok=True)
    fm = f"id: {a.id}\nkind: {a.kind}\ntitle: {a.title}\n" + (f"area: {a.area or 'misc'}\n" if a.kind in FACT else "") + \
        "status: stated\norigin: reader\n" + "".join(f"{f}: TODO\n" for f in need) + rel + \
        (f"searched: {a.reason}\n" if a.reason else "")
    body = "".join(f"\n## {s}\nTODO\n" for s in secs)
    p = d / f"{a.id}.md"
    p.write_text(f"---\n{fm}---\n{body}", encoding="utf-8")
    print(f"作成: {p.relative_to(root.root)}")


def summary(root, route=None):
    E = check(root, route)
    n = {"ERR": 0, "WARN": 0, "INFO": 0}
    for s, *_ in E:
        n[s] += 1
    return E, n


def evidence_fingerprints(root):
    """Current fingerprint of every card, for other harnesses that cite code, runs or figures as evidence.

    A run's fingerprint covers its record (see Root.fingerprint), so a different result changes it."""
    out = {}
    for cid, c in sorted(root.cards.items()):
        out[cid] = root.fingerprint(c)
    return out


def cmd_fingerprints(root, a):
    print(json.dumps(evidence_fingerprints(root), ensure_ascii=False, indent=0))


def cmd_check(root, a):
    E, n = summary(root, a.route)
    for s, code, i, msg in E:
        if s == "INFO" and not a.info:
            continue
        print(f"{s:4s} {code} {i}: {msg}")
    print(f"-- エラー {n['ERR']} 件、警告 {n['WARN']} 件、意図的な前方参照など {n['INFO']} 件" + ("" if a.info or not n["INFO"] else "(--info で表示)"))
    sys.exit(1 if n["ERR"] else 0)


def cmd_status(root, a):
    import collections
    t = collections.Counter((c.kind, c.get("status", "stated")) for c in root.cards.values())
    for k in FACT + GLUE + LEDGER:
        row = {s: t[(k, s)] for s in STATUS if t[(k, s)]}
        if sum(row.values()):
            print(f"{k:9s} {sum(row.values()):3d}  " + "  ".join(f"{STATUS_JA[s]}:{v}" for s, v in row.items()))
    E, n = summary(root, a.route)
    print(f"検査: エラー {n['ERR']}、警告 {n['WARN']}、前方参照(意図的) {n['INFO']}")
    print("routes:", ", ".join(f"{k}({len(route_ids(root, k))}枚, {root.routes[k].get('order', 'strict')})" for k in root.routes) or "なし")


def cmd_list(root, a):
    for c in sorted(root.cards.values(), key=lambda c: (c.kind, c.id)):
        if a.kind and c.kind != a.kind:
            continue
        if a.route and c.id not in route_ids(root, a.route):
            continue
        print(f"{c.kind:9s} {c.id:40s} {c.get('status', 'stated'):10s} {c.get('title', '')}")


def cmd_show(root, a):
    rv = rev_index(root)
    for i in a.ids:
        c = root.cards.get(i) or sys.exit(f"無い: {i}")
        print(f"== {c.id} ({c.kind}, {c.get('status', 'stated')}, {ORIGIN_JA.get(c.get('origin'), c.get('origin'))}) {c.get('title', '')}")
        print(f"   指紋 {root.fingerprint(c)}  ファイル {c.path.relative_to(root.root)}")
        for f in REF_FIELDS:
            if c.refs(f):
                print(f"   {f}: {', '.join(c.refs(f))}")
        if rv.get(i):
            print("   参照される: " + ", ".join(f"{d}({f})" for d, f in rv[i]))
        print("   route: " + (", ".join(r for r in root.routes if i in route_ids(root, r)) or "なし"))
        for s, t in c.secs.items():
            print(f"   ## {s}\n      " + t.replace("\n", "\n      ")[:600])


def cmd_graph(root, a):
    ids = route_ids(root, a.route) if a.route else list(root.cards)
    for i in ids:
        c = root.cards.get(i)
        if c:
            for f in ("requires", "realizes", "shows", "produced_by", "evidence", "variant_of"):
                for r in c.refs(f) if f != "variant_of" else ([c.get("variant_of")] if c.get("variant_of") else []):
                    print(f"{i} --{f}--> {r}")


# ---------------------------------------------------------------- HTML
MATH_CACHE = {}


def math_html(tex, display):
    key = ("D" if display else "I") + tex
    if key in MATH_CACHE:
        return MATH_CACHE[key]
    src = f"$${tex}$$" if display else f"${tex}$"
    try:
        r = subprocess.run(["pandoc", "-f", "markdown+tex_math_dollars", "-t", "html", "--mathml"], input=src, capture_output=True, text=True, timeout=30)
        out = re.sub(r"^<p>|</p>\s*$", "", r.stdout.strip()) if r.returncode == 0 and "<math" in r.stdout else H.escape(src)
    except Exception:   # noqa: BLE001
        out = H.escape(src)
    MATH_CACHE[key] = out
    return out


def inline(text, link=lambda i: None):
    parts = re.split(r"(\$\$.+?\$\$|\$[^$\n]+?\$)", text, flags=re.S)
    out = []
    for k, p in enumerate(parts):
        if k % 2:
            d = p.startswith("$$")
            out.append(math_html(p.strip("$"), d))
            continue
        s = H.escape(p)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"\[\[([a-z][a-z0-9-]*)\]\]", lambda m: link(m.group(1)) or f'<span class="ref out">{m.group(1)}</span>', s)
        out.append(s)
    return "".join(out)


def blocks(text, link):
    res = []
    for para in re.split(r"\n\s*\n", text.strip()):
        lines = para.split("\n")
        if all(re.match(r"^\s*[-*] ", ln) for ln in lines):
            items = (re.sub(r'^\s*[-*] ', '', ln) for ln in lines)
            res.append("<ul>" + "".join(f"<li>{inline(item, link)}</li>" for item in items) + "</ul>")
        else:
            res.append(f"<p>{inline(' '.join(lines), link)}</p>")
    return "".join(res)


CSS = """
:root{--bg:#fbfbf8;--fg:#1f2328;--muted:#5d6670;--line:#d8dce0;--panel:#f1f3f5;--accent:#1f6f6b;--warm:#b5651d;--code:#f6f8fa;--bad:#c92a2a;--ok:#2b8a3e}
@media(prefers-color-scheme:dark){:root{--bg:#16181b;--fg:#e6e8ea;--muted:#9aa3ab;--line:#33383d;--panel:#1e2125;--accent:#5fbfb8;--warm:#e0a060;--code:#1b1e22;--bad:#ff8787;--ok:#69db7c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.75 -apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
header.top{position:sticky;top:0;z-index:50;background:var(--panel);border-bottom:1px solid var(--line);padding:.5em 1em;display:flex;gap:.5em;flex-wrap:wrap;align-items:center}
header.top button{font:13px inherit;padding:.25em .7em;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;cursor:pointer}
header.top button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
main{max-width:56em;margin:0 auto;padding:1em 1em 6em}
nav.toc{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:.5em 1em;margin:1em 0}nav.toc a{margin-right:1em}
h2.sec{margin:2em 0 .3em;border-bottom:2px solid var(--accent);padding-bottom:.2em}
article.card{border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:6px;padding:.6em 1em;margin:.9em 0;background:var(--bg)}
article.card.k-ask,article.card.k-bridge,article.card.k-preview,article.card.k-recap,article.card.k-entrance{border-left-color:var(--warm);background:var(--panel)}
article.card.k-step{border-left-color:#4263eb}article.card.k-run{border-left-color:var(--ok)}
.hd{display:flex;gap:.5em;flex-wrap:wrap;align-items:baseline}.hd h3{margin:0;font-size:1.05em}
.chip{font-size:11px;border:1px solid var(--line);border-radius:10px;padding:0 .6em;color:var(--muted);white-space:nowrap}
.chip.stale{border-color:var(--bad);color:var(--bad)}.chip.st-reproduced,.chip.st-checked{border-color:var(--ok);color:var(--ok)}.chip.st-traced{border-color:var(--accent);color:var(--accent)}.chip.ai{border-color:var(--warm);color:var(--warm)}
.gist{color:var(--muted);margin:.2em 0}.cid{font:12px monospace;color:var(--muted)}
.meta{font-size:12.5px;color:var(--muted);margin:.3em 0}.meta a,.ref{color:var(--accent)}.ref.out{opacity:.6}
.sub{font-weight:600;margin:.6em 0 .1em;font-size:.92em;color:var(--muted)}
pre.cb{background:var(--code);border:1px solid var(--line);border-radius:4px;padding:.4em .6em;overflow:auto;font:13px/1.6 ui-monospace,Menlo,monospace;margin:.4em 0}
pre.cb .ln{display:inline-block;width:2.6em;color:var(--muted);user-select:none}
.code-line{display:inline-block;min-width:100%;scroll-margin-top:7rem}
.code-line:target{outline:1px solid var(--accent);outline-offset:-1px}
.note{background:var(--panel);border-left:3px solid #4263eb;padding:.2em .6em;margin:.4em 0;font-size:14px}.note .n{font:11px monospace;color:var(--muted);margin-right:.5em}
.source-figure{margin:1em 0 .3em;background:#fff;padding:.4em;border:1px solid var(--line);border-radius:4px}
.source-figure img{display:block;width:100%;height:auto}
h2.sec,article.card{scroll-margin-top:6rem}
body[data-mode=overview] .full{display:none}body[data-mode=read] article.gist-only .full{display:none}
@media print{header.top,#cl-bar,#cl-add,#cl-box{display:none!important}}
"""

MODE_JS = """<script>
(function(){const b=document.body;function set(m){b.dataset.mode=m;document.querySelectorAll('header.top button[data-m]').forEach(x=>x.classList.toggle('on',x.dataset.m===m))}
document.querySelectorAll('header.top button[data-m]').forEach(x=>x.onclick=()=>set(x.dataset.m));set('read');
function locateLine(){const element=document.getElementById(location.hash.slice(1));
 if(!element?.classList.contains('code-line'))return;
 set('dig');element.scrollIntoView()}
addEventListener('hashchange',locateLine);locateLine()})();
</script>"""

COMMENT_EXTRA = r"""<script>
(function(){'use strict';
 document.querySelectorAll('math').forEach(function(m){m.classList.add('katex');if(m.getAttribute('display')==='block')m.classList.add('katex-display')});
 let timer;function selected(){clearTimeout(timer);timer=setTimeout(function(){const s=getSelection();if(!s||!s.rangeCount||s.isCollapsed){const a=document.getElementById('cl-add');if(a)a.style.display='none';return}
  let n=s.anchorNode.nodeType===1?s.anchorNode:s.anchorNode.parentElement;if(!n||n.closest('#cl-box,#cl-bar,header.top,input,textarea'))return;n.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}))},250)}
 document.addEventListener('selectionchange',selected);document.addEventListener('touchend',selected,{passive:true});
 const bar=document.getElementById('cl-bar');if(!bar)return;const b=document.createElement('button');b.textContent='コメントを書き出す';
 b.onclick=function(){let cs=[];try{cs=JSON.parse(sessionStorage.getItem('comments:'+location.pathname)||'[]')}catch(e){}
  if(!cs.length){alert('コメントはまだありません。文章を選んで追加してください。');return}
  const t=cs.map(function(c){return c.where+'\\n「'+c.quote+'」\\n→ '+(c.text||'(コメントなし)')}).join('\\n\\n');
  const u=URL.createObjectURL(new Blob([t+'\\n'],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='method-comments.txt';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(u)},60000)};
 bar.appendChild(b)})();
</script>"""


def render_card(root, c, rname, in_route, rv, show):
    link = lambda i: (f'<a class="ref" href="#c-{i}">{inline(str(root.cards[i].get("title", i)))}</a>' if i in in_route and i in root.cards else None)   # noqa: E731
    live = root.fingerprint(c)
    stale = [a for a, f in (c.get("anchors") or {}).items() if a in root.cards and root.fingerprint(root.cards[a]) != f]
    codechg = c.kind == "step" and (c.get("code") or {}).get("fp") and (c.get("code") or {}).get("fp") != root.code_fp(c)
    st = c.get("status", "stated")
    chips = [f'<span class="chip">{c.kind}</span>']
    if c.kind != "run":
        chips.append(f'<span class="chip st-{st}">{STATUS_JA[st]}</span>')
    if c.get("origin") in ("ai-written", "ai-standin"):
        chips.append(f'<span class="chip ai">{ORIGIN_JA[c.get("origin")]}</span>')
    if stale or codechg:
        chips.append('<span class="chip stale">STALE: 読み直し</span>')
    lab = f"[{rname}/{c.id}] {c.get('title', c.id)}"
    h = [f'<article class="card k-{c.kind} {"gist-only" if show == "gist" else ""}" id="c-{c.id}" data-card-id="{c.id}" data-comment-label="{H.escape(lab, quote=True)}">']
    h.append(f'<div class="hd"><h3>{inline(str(c.get("title", c.id)))}</h3>{"".join(chips)}<span class="cid">{c.id}</span></div>')
    if c.get("gist"):
        h.append(f'<div class="gist">{inline(str(c.get("gist")), link)}</div>')
    full = []
    if c.kind == "figure" and c.get("image"):
        asset = root.root / c.get("image")
        if asset.is_file() and asset.suffix.lower() == ".png":
            encoded = base64.b64encode(asset.read_bytes()).decode("ascii")
            alt = H.escape(c.get("alt") or c.get("title", ""), quote=True)
            full.append(f'<figure class="source-figure"><img src="data:image/png;base64,{encoded}" alt="{alt}"></figure>')
        else:
            full.append('<p class="meta">図の画像を開けません。下の出典から確認できます。</p>')
    if c.kind == "step":
        L, err = root.code_lines(c)
        cd = c.get("code") or {}
        a0 = cd.get("lines", [1, 1])[0]
        notes = {}
        for ln in (c.secs.get("行説明") or "").split("\n"):
            m = re.match(r"^\s*-?\s*(\d+)(?:-(\d+))?:\s*(.*)$", ln)
            if m:
                notes.setdefault(int(m.group(1)), []).append((m.group(2), m.group(3)))
        if L is None:
            full.append(f'<p class="meta">コードを読めない: {H.escape(err)}</p>')
        else:
            body = []
            for k, line in enumerate(L):
                n = a0 + k
                for end, t in notes.get(n, []):
                    body.append(None); full_note = f'<div class="note"><span class="n">{n}{"–" + end if end else ""} 行</span>{inline(t, link)}</div>'
                    body[-1] = full_note
                body.append(f'<span class="code-line" id="c-{c.id}-L{n}">'
                            f'<span class="ln">{n}</span> {H.escape(line)}</span>')
            code_html = ""
            buf = []
            for x in body:
                if x.startswith("<div"):
                    if buf:
                        code_html += '<pre class="cb">' + "\n".join(buf) + "</pre>"; buf = []
                    code_html += x
                else:
                    buf.append(x)
            if buf:
                code_html += '<pre class="cb">' + "\n".join(buf) + "</pre>"
            code_url = H.escape((root.code_root(c) / cd["file"]).resolve().as_uri(), quote=True)
            full.append(f'<p class="meta"><a href="{code_url}">参照ファイルを開く</a></p><div class="code">{code_html}</div><div class="meta">{H.escape(cd.get("file", ""))} {cd.get("lines", [""])[0]}–{cd.get("lines", ["", ""])[1]} · {H.escape(str(c.get("lang", "")))}'
                        + (f' · <a href="#c-{c.get("variant_of")}">{H.escape(c.get("variant_of"))} の言語違い</a>' if c.get("variant_of") and c.get("variant_of") in in_route else "") + "</div>")
    for sname, text in c.secs.items():
        if c.kind == "step" and sname == "行説明":
            continue
        full.append(f'<div class="sub">{H.escape(sname)}</div>{blocks(text, link)}')
    if c.kind == "run":
        code_root = root.run_code_root(c.id)
        if code_root:
            for filename in c.get("files") or []:
                code_file = (code_root / filename).resolve()
                if code_file.is_file():
                    url = H.escape(code_file.as_uri(), quote=True)
                    full.append(f'<p class="meta"><a href="{url}">実行に使ったファイル · {H.escape(filename)}</a></p>')
        rec = root.run_record(c.id)
        s = root.record_state(c.id)
        if rec:
            full.append(f'<div class="meta">実行記録 {rec["date"]} · 終了コード {rec["exit"]} · {"有効" if s == "ok" else {"stale": "コードが変わった後(古い)", "failed": "失敗"}.get(s, s)}</div><pre class="cb">{H.escape(rec["stdout"][:800])}</pre>')
        else:
            full.append('<div class="meta">実行記録なし</div>')
    meta = []
    for f, ja in (("requires", "前提"), ("realizes", "実現する"), ("shows", "示す"), ("evidence", "根拠の実行"), ("produced_by", "生成元"), ("references", "参照")):
        rs = c.refs(f)
        if rs:
            related = []
            for ref in rs:
                if ref not in root.cards:
                    continue
                title = inline(str(root.cards[ref].get("title", ref)))
                if ref in in_route:
                    related.append(f'<a href="#c-{ref}">{title}</a>')
                else:
                    related.append(f'<span class="ref out" title="この route の外">{title}</span>')
            if related:
                meta.append(f"{ja}: " + "、".join(related))
    used = [d for d, f in rv.get(c.id, []) if d in in_route and f in ("requires", "realizes", "shows", "references")]
    if used:
        meta.append("使われる所: " + "、".join(f'<a href="#c-{d}">{inline(str(root.cards[d].get("title", d)))}</a>' for d in dict.fromkeys(used)))
    srcs = [s for s in (c.get("sources") or []) if isinstance(s, dict)]
    if srcs:
        citations = []
        for source in srcs:
            entry = root.cards.get(source.get("src"))
            if not entry:
                continue
            citation = H.escape(f'{entry.get("title", entry.id)} {source.get("loc", "")}')
            pdf_page = source.get("pdf_page")
            if entry.get("file") and type(pdf_page) is int and pdf_page > 0:
                pdf = (root.root / entry.get("file")).resolve()
                if pdf.is_file() and pdf.suffix.lower() == ".pdf":
                    url = H.escape(f"{pdf.as_uri()}#page={pdf_page}", quote=True)
                    citation = f'<a href="{url}">{citation}</a>'
            citations.append(citation)
        if citations:
            meta.append("出典: " + "、".join(citations))
    h.append('<div class="full">' + "".join(full) + "</div>")
    if meta:
        h.append('<div class="meta full">' + "<br>".join(meta) + "</div>")
    h.append("</article>")
    return "".join(h)


def build_html(root, rname, title=None):
    rt = root.routes[rname]
    secs = route_items(rt)
    in_route = set(route_ids(root, rname))
    rv = rev_index(root)
    E, n = summary(root, rname)
    has_comments = COMMENT_JS.is_file()
    route_show = rt.get("show", "full")
    has_deeper = any((show or route_show) == "gist" for _, items in secs for _, show in items)
    deeper_button = '<button data-m="dig">掘る</button>' if has_deeper else ""
    read_help = '「通読」は一部のカードを要点だけ表示し、「掘る」は全部を表示する。' if has_deeper else '「通読」は説明やコードも表示する。'
    parts = [f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H.escape(title or rt.get("title", rname))}</title><style>{CSS}</style></head><body data-mode="read">']
    parts.append('<header class="top"><b>' + H.escape(rt.get("title", rname)) + '</b><span class="chip">route: ' + H.escape(rname) + ("・順序は緩い" if rt.get("order") == "free" else "") + '</span>'
                 f'<button data-m="overview">俯瞰</button><button data-m="read">通読</button>{deeper_button}</header><main>')
    parts.append('<nav class="toc">' + "".join(f'<a href="#s{k}">{H.escape(t)}</a>' for k, (t, _) in enumerate(secs)) + "</nav>")
    comment_help = "文章を選ぶとカード ID つきでコメントできる。" if has_comments else ""
    parts.append(f'<p class="meta">生成物(読む用)。直すのはカード。検査:エラー {n["ERR"]}・警告 {n["WARN"]}・意図的な前方参照 {n["INFO"]}。'
                 f'「俯瞰」は要点だけ表示する。{read_help}{comment_help}</p>')
    for k, (t, its) in enumerate(secs):
        parts.append(f'<h2 class="sec" id="s{k}">{inline(t)}</h2>')
        for i, show in its:
            if i in root.cards:
                parts.append(render_card(root, root.cards[i], rname, in_route, rv, show or route_show))
    parts.append("</main>" + MODE_JS)
    if has_comments:
        parts.append('<script>window.CommentLayer={lang:"ja"};</script><script>\n' + COMMENT_JS.read_text(encoding="utf-8") + "</script>" + COMMENT_EXTRA)
    parts.append("</body></html>")
    return "".join(parts)


def cmd_html(root, a):
    if a.route not in root.routes:
        sys.exit(f"route が無い: {a.route}")
    cache = root.root / ".cache" / "math.json"
    if cache.exists():
        MATH_CACHE.update(json.loads(cache.read_text(encoding="utf-8")))
    out = Path(a.out) if a.out else root.root / "out" / f"{a.name or a.route}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(root, a.route), encoding="utf-8")
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(json.dumps(MATH_CACHE, ensure_ascii=False), encoding="utf-8")
    print(f"-> {out}  ({out.stat().st_size / 1e3:.0f} KB)。ローカルのファイル。")


def cmd_init(root_path):
    r = Path(root_path)
    if (r / "harness.toml").exists():
        sys.exit("既にある")
    for d in ("pool", "src", "route", "runs"):
        (r / d).mkdir(parents=True, exist_ok=True)
    (r / "harness.toml").write_text('language = "ja"\n# 私用・ローカル。公開しない。原文は持たず、位置(頁・ファイル・行)と指紋だけを持つ。\n', encoding="utf-8")
    print(f"作成: {r}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    sp = ap.add_subparsers(dest="cmd", required=True)

    def add(name, **kw):
        p = sp.add_parser(name); p.set_defaults(fn=name)
        return p
    add("init")
    p = add("check"); p.add_argument("--route"); p.add_argument("--info", action="store_true")
    p = add("status"); p.add_argument("--route")
    p = add("list"); p.add_argument("--kind"); p.add_argument("--route")
    p = add("show"); p.add_argument("ids", nargs="+")
    p = add("search"); p.add_argument("q"); p.add_argument("--kind")
    p = add("new"); p.add_argument("kind"); p.add_argument("id"); p.add_argument("--title", required=True); p.add_argument("--area"); p.add_argument("--route"); p.add_argument("--decision"); p.add_argument("--reason")
    p = add("closure"); p.add_argument("ids", nargs="+")
    p = add("impact"); p.add_argument("ids", nargs="+")
    p = add("anchor"); p.add_argument("id"); p.add_argument("--all", action="store_true", help="anchors を全部、今の指紋に更新"); p.add_argument("--to", nargs="+", help="anchor を足す相手")
    p = add("run"); p.add_argument("id")
    p = add("set-status"); p.add_argument("id"); p.add_argument("status")
    p = add("html"); p.add_argument("--route", required=True); p.add_argument("--name"); p.add_argument("--out")
    p = add("graph"); p.add_argument("--route")
    add("fingerprints")
    a = ap.parse_args(argv)
    if a.cmd == "init":
        return cmd_init(a.root)
    root = Root(a.root)
    {"check": cmd_check, "status": cmd_status, "list": cmd_list, "show": cmd_show, "new": cmd_new,
     "anchor": cmd_anchor, "run": cmd_run, "set-status": cmd_set_status, "html": cmd_html, "graph": cmd_graph,
     "fingerprints": cmd_fingerprints}.get(a.cmd, lambda r, x: None)(root, a) \
        if a.cmd not in ("search", "closure", "impact") else None
    if a.cmd == "search":
        for sc, i, t in search(root, a.q, a.kind):
            print(f"{sc:3d}  {i}  {t}")
    elif a.cmd == "closure":
        print("\n".join(closure(root, a.ids)))
    elif a.cmd == "impact":
        print("\n".join(impact(root, a.ids)))


if __name__ == "__main__":
    main()
