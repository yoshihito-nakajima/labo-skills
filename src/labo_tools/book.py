"""Card system for books: a shared pool of fact cards and per-book routes.

A *book root* holds

    pool/<area>/<id>.md          fact cards shared by every book (A1-A6)
    src/<id>.md                  source records (C1), shared
    route/<slug>/route.yaml      the book's route: sections, order, what is shown
    route/<slug>/card/<id>.md    glue cards of that book (B1-B5)
    route/<slug>/map/<id>.md     source mapping, i.e. scope audit (C2)
    route/<slug>/finding/<id>.md review findings (D1)

A card is Markdown with YAML front matter and fixed `## ` sections.  Nothing here
reads, stores or fetches original sources: cards carry locators only.  The tool never
certifies mathematics; it keeps identifiers, dependencies, fingerprints and states.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import yaml

from .locking import exclusive_lock


class BookError(ValueError):
    """A book root, card or route cannot be used as requested."""


STATUS = ("stated", "drafted", "self-checked", "independent", "lean")
RELATIONS = ("same", "implies", "special-case", "variant", "alt-proof", "equivalent", "supplied")
ADOPTION = ("adopted", "partial", "not-adopted", "outlook")
AUDIT = ("TODO", "OK", "PARTIAL", "MISSING", "OUT")
FINDING_STATUS = ("fixed", "resolved-with-reason", "open")
SEVERITY = ("major", "minor")
ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
BY_RE = re.compile(r"\[by:\s*([^\]]+)\]")
FRONT_RE = re.compile(r"\A---\n(.*?)\n---[ \t]*\n?(.*)\Z", re.S)
HEAD_RE = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.M)
# sections that explain but do not state mathematics; they do not enter the fingerprint
VOLATILE = {"remarks", "caution", "why"}
# an imported card whose structure has not been split into the template's sections yet
UNCLASSIFIED = "unclassified"
BODY = ("body", "本文", "Body (imported text)")


def _s(key, ja, en):
    return (key, ja, en)


@dataclass(frozen=True)
class Template:
    code: str
    name: str
    scope: str  # pool | src | card | map | finding
    required: tuple
    optional: tuple = ()
    variants: tuple = ()
    fields: tuple = ()
    dep: str | None = None  # kind in a knowledge-dependencies graph, if a node
    ladder: bool = True  # carries `status`
    titled: bool = True


TEMPLATES = {t.code: t for t in (
    Template("A1", "definition / notation", "pool",
             (_s("definition", "定義", "Definition"),),
             (_s("premise", "前提", "Premises"), _s("notation", "記法", "Notation"), _s("caution", "注意", "Caution")),
             ("structure", "predicate", "recursive", "quotient-choice", "notation-only"), dep="definition"),
    Template("A2", "claim", "pool",
             (_s("hypotheses", "仮定", "Hypotheses"), _s("conclusion", "結論", "Conclusion"),
              _s("quantifiers", "量化子", "Quantifiers")),
             (_s("boundary", "境界の場合", "Boundary cases"), _s("remarks", "備考", "Remarks")),
             ("equation-inclusion", "equivalence", "existence", "unique-existence", "estimate", "construction-correct"),
             dep="theorem"),
    Template("A3", "proof", "pool",
             (_s("plan", "方針", "Plan"), _s("steps", "段階", "Steps")),
             (_s("boundary-check", "境界の場合の確認", "Boundary check"),
              _s("used-hyps", "使った仮定", "Hypotheses used")),
             ("direct", "contrapositive-contradiction", "induction", "double-inclusion", "equivalence-both",
              "construction-uniqueness", "cases", "computation"), ("proves",)),
    Template("A4", "example / counterexample", "pool",
             (_s("setting", "設定", "Setting"), _s("verification", "確認", "Verification")),
             (_s("lesson", "何が分かるか", "What it shows"),),
             ("concrete", "counterexample", "computation", "motivating"), ("illustrates",), dep="lemma"),
    Template("A5", "exercise / solution", "pool",
             (_s("question", "問", "Question"), _s("solution", "解答", "Solution")),
             (_s("uses", "使う主張", "Claims used"),), dep="lemma"),
    Template("A6", "convention", "pool",
             (_s("convention", "規約", "Convention"), _s("scope", "適用範囲", "Scope")),
             (_s("exceptions", "例外の宣言のしかた", "Declaring exceptions"),), dep="assumption"),
    Template("B1", "motivation / question", "card",
             (_s("question", "問い", "Question"),),
             (_s("why", "なぜ自然か", "Why natural"), _s("leads", "次に導くもの", "Leads to")),
             fields=("answered_by",), titled=False),
    Template("B2", "transition", "card",
             (_s("done", "済んだこと", "Done"), _s("missing", "足りないこと", "Missing"),
              _s("next", "次にすること", "Next")),
             variants=("forward", "supplement", "turn", "bridge-to-example", "need-for-definition"),
             fields=("between",), titled=False),
    Template("B3", "preview", "card",
             (_s("later", "後で示すこと", "To be shown later"),),
             (_s("no-use", "今は使わない旨", "Not used yet"),), fields=("forward",), titled=False),
    Template("B4", "recap", "card",
             (_s("established", "確立したこと", "Established"),),
             (_s("left", "残ったこと", "Left open"),), titled=False),
    Template("B5", "entrance", "card",
             (_s("endpoint", "問いと終点", "Question and endpoint"),
              _s("known", "前提とする既知事実", "Assumed known results"),
              _s("conventions", "規約", "Conventions")),
             (_s("reader", "想定する読者", "Intended reader"),), fields=("borrows",)),
    Template("C1", "source record", "src",
             (_s("biblio", "書誌", "Bibliography"), _s("edition", "版・ハッシュ", "Edition and hash"),
              _s("pages", "頁対応", "Page map")), ladder=False),
    Template("C2", "source mapping", "map",
             (_s("difference", "原著との差", "Difference from the source"),),
             (_s("duty", "残る義務", "Remaining obligations"),),
             fields=("sources", "adoption", "scope_audit"), ladder=False, titled=False),
    Template("D1", "finding", "finding",
             (_s("finding", "所見", "Finding"),),
             (_s("repair", "修復", "Repair"), _s("recheck", "再確認の範囲", "Recheck scope")),
             fields=("target", "target_fp", "severity", "status"), ladder=False, titled=False),
)}

SCOPE_DIR = {"pool": "pool", "src": "src", "card": "card", "map": "map", "finding": "finding"}
LEVELS = {"L0": ("A1", "A2", "A6"), "L1": ("A1", "A2", "A6", "A4"),
          "L2": ("A1", "A2", "A6", "A4", "A3"),
          "L3": ("A1", "A2", "A6", "A4", "A3", "B1", "B2", "B3", "B4", "B5"),
          "L4": tuple(TEMPLATES)}


MENTION_RE = re.compile(r"\[\[([a-z][a-z0-9-]*)\]\]")
# labels, index registrations and navigation macros are not reading text
NOISE_MACROS = re.compile(r"\\(?:label|termat|formulaat|index|phantomsection|cref|Cref|ref|eqref)(?:\{[^{}]*\})+")
TEX_COMMAND = re.compile(r"\\[A-Za-z]+\*?")


def clean_tex(text: str) -> str:
    """Reading text of a TeX fragment: drop labels, index and reference macros."""
    return NOISE_MACROS.sub(" ", text)


class Card:
    def __init__(self, path: Path, meta: dict, body: str):
        self.path, self.meta, self.body = path, meta, body
        self.id = str(meta.get("id", path.stem))
        self.kind = str(meta.get("kind", ""))
        self.template = TEMPLATES.get(self.kind)
        self.route = None
        self.sections, self.unknown_sections = self._split()

    def _split(self):
        sections, unknown = {}, []
        marks = list(HEAD_RE.finditer(self.body))
        names = {}
        if self.template:
            for key, ja, en in self.template.required + self.template.optional + (BODY,):
                names[ja] = key
                names[en.lower()] = key
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(self.body)
            title = m.group(1).strip()
            key = names.get(title) or names.get(title.lower())
            text = self.body[m.end():end].strip()
            if key:
                sections[key] = text
            else:
                unknown.append(title)
        return sections, unknown

    @property
    def legacy(self) -> bool:
        return bool(self.meta.get("legacy"))

    @property
    def requires(self) -> list:
        return list(self.meta.get("requires") or [])

    @property
    def references(self) -> list:
        return list(self.meta.get("references") or [])

    def fingerprint(self) -> str:
        parts = [self.kind, str(self.meta.get("variant", ""))]
        for key, text in sorted(self.sections.items()):
            if key not in VOLATILE:
                parts.append(key + ":" + " ".join(text.split()))
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:8]

    def summary(self, limit: int = 160) -> str:
        t = self.template
        keys = [k for k in ("definition", "hypotheses", "conclusion", "convention", "setting", "question", "later", "body")
                if k in self.sections]
        text = " ".join(" ".join(clean_tex(self.sections[k]).split()) for k in keys[:2])
        return text[:limit]

    def ref_ids(self) -> list:
        """Every card id this card points at, by any field."""
        m, out = self.meta, []
        for key in ("requires", "requires_candidates", "references", "between", "forward", "answered_by",
                    "conventions", "well_defined"):
            out += list(m.get(key) or [])
        for key in ("proves", "illustrates", "target"):
            if m.get(key):
                out.append(m[key])
        out += [x.get("src") for x in m.get("sources") or [] if isinstance(x, dict)]
        out += [x.get("card") for x in m.get("maps_to") or [] if isinstance(x, dict)]
        out += [x.get("card") for x in m.get("borrows") or [] if isinstance(x, dict)]
        out += [x.get("to") for x in m.get("relations") or [] if isinstance(x, dict)]
        out += self.mentions()
        return [x for x in out if x]

    def mentions(self) -> list:
        """Cards named in the text as [[card-id]] (rendered as cross references)."""
        return list(dict.fromkeys(MENTION_RE.findall(self.body)))

    def reviewed_current(self, kind: str | None = None) -> bool:
        fp = self.fingerprint()
        return any(r.get("fp") == fp and (kind is None or r.get("kind") == kind)
                   for r in self.meta.get("reviews") or [] if isinstance(r, dict))


def parse_card(path: Path) -> Card:
    text = path.read_text(encoding="utf-8")
    m = FRONT_RE.match(text)
    if not m:
        raise BookError(f"{path}: missing YAML front matter")
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        raise BookError(f"{path}: bad YAML front matter: {exc}") from exc
    if not isinstance(meta, dict):
        raise BookError(f"{path}: front matter must be a mapping")
    return Card(path, meta, m.group(2))


def dump_card(meta: dict, body: str) -> str:
    return "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=100) + "---\n" + body


LIST_OF_TEXT = ("requires", "requires_candidates", "references", "between", "forward", "answered_by", "conventions",
                "well_defined", "aliases", "symbols", "index", "not_requires")
LIST_OF_MAPS = ("maps_to", "borrows", "relations", "sources", "reviews")
MAPS = ("anchors", "searched")
TEXT = ("proves", "illustrates", "target", "variant", "status", "title", "area", "label")


def sanitize(meta: dict) -> list:
    """Coerce wrongly typed front matter to an empty value; return what was wrong, so `check` reports it
    instead of a later step failing on it."""
    wrong = []
    for key in LIST_OF_TEXT:
        if key in meta and not (isinstance(meta[key], list) and all(isinstance(x, str) for x in meta[key])):
            wrong.append(f"{key} must be a list of ids")
            meta[key] = [x for x in meta[key] if isinstance(x, str)] if isinstance(meta[key], list) else []
    for key in LIST_OF_MAPS:
        if key in meta and not (isinstance(meta[key], list) and all(isinstance(x, dict) for x in meta[key])):
            wrong.append(f"{key} must be a list of mappings")
            meta[key] = [x for x in meta[key] if isinstance(x, dict)] if isinstance(meta[key], list) else []
    for key in MAPS:
        if key in meta and not isinstance(meta[key], dict):
            wrong.append(f"{key} must be a mapping")
            meta[key] = {}
    for key in TEXT:
        if key in meta and meta[key] is not None and not isinstance(meta[key], str):
            wrong.append(f"{key} must be text")
            meta[key] = str(meta[key])
    return wrong


INDEX_DIR = ".index"  # generated parse cache and lock; keep it out of every Git


@contextmanager
def book_lock(root: Path):
    """Serialize operations that create or rewrite cards, across processes."""
    d = Path(root) / INDEX_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitignore").write_text("*\n", encoding="utf-8") if not (d / ".gitignore").exists() else None
    with (d / "lock").open("a+b") as handle:
        with exclusive_lock(handle):
            yield


def _jsonable(meta):
    return json.loads(json.dumps(meta, default=str, ensure_ascii=False))


class Book:
    """All cards of one book root, loaded once; parsed cards are cached by path, size and mtime."""

    def __init__(self, root: Path, use_cache: bool = True):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise BookError(f"book root not found: {root}")
        self.cards: dict[str, Card] = {}
        self.problems: list[tuple] = []  # (level, code, id, message) found while loading
        self.use_candidates = False  # count requires_candidates as hard edges in graph views
        cache_path = self.root / INDEX_DIR / "cards.json"
        cache: dict = {}
        if use_cache and cache_path.is_file():
            try:
                cache = json.loads(cache_path.read_text(encoding="utf-8")).get("files", {})
            except (OSError, ValueError):
                cache = {}
        fresh: dict = {}
        for path in sorted(self.root.rglob("*.md")):
            rel = path.relative_to(self.root).parts
            slot = self._slot(rel)
            if slot is None:
                continue
            key = "/".join(rel)
            st = path.stat()
            hit = cache.get(key)
            try:
                if hit and hit[0] == st.st_mtime_ns and hit[1] == st.st_size:
                    card = Card(path, hit[2], hit[3])
                else:
                    card = parse_card(path)
                    card.meta = _jsonable(card.meta)
                    card.id = str(card.meta.get("id", path.stem))
                    card.kind = str(card.meta.get("kind", ""))
                    card.template = TEMPLATES.get(card.kind)
                    card.sections, card.unknown_sections = card._split()
            except (BookError, OSError, UnicodeDecodeError) as exc:
                self.problems.append(("error", "PARSE", path.stem, str(exc)))
                continue
            raw = json.loads(json.dumps(card.meta))  # the cache keeps what the file says, not the coerced copy
            for msg in sanitize(card.meta):
                self.problems.append(("error", "BAD-FIELD", card.id, msg))
            fresh[key] = [st.st_mtime_ns, st.st_size, raw, card.body]
            card.route = slot[1]
            card.slot = slot[0]
            if card.id in self.cards:
                self.problems.append(("error", "DUPLICATE-ID", card.id, f"also in {self.cards[card.id].path}"))
                continue
            self.cards[card.id] = card
        if use_cache and fresh != cache:
            try:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                (cache_path.parent / ".gitignore").write_text("*\n", encoding="utf-8")
                tmp = cache_path.with_suffix(f".{os.getpid()}.tmp")
                tmp.write_text(json.dumps({"version": 1, "files": fresh}, ensure_ascii=False), encoding="utf-8")
                tmp.replace(cache_path)
            except OSError:
                pass

    @staticmethod
    def _slot(rel):
        if rel[0] == "pool" and len(rel) >= 3 and rel[-1] != "README.md":
            return ("pool", None)
        if rel[0] == "src" and len(rel) == 2 and rel[-1] != "README.md":
            return ("src", None)
        if rel[0] == "route" and len(rel) == 4 and rel[2] in ("card", "map", "finding"):
            return (rel[2], rel[1])
        return None

    def routes(self) -> list:
        base = self.root / "route"
        return sorted(p.name for p in base.iterdir() if (p / "route.yaml").is_file()) if base.is_dir() else []

    # ---- routes
    def load_route(self, slug: str, _chain: tuple = ()) -> dict:
        if slug in _chain:
            raise BookError("route includes form a cycle: " + " -> ".join(_chain + (slug,)))
        path = self.root / "route" / slug / "route.yaml"
        if not path.is_file():
            raise BookError(f"route not found: {slug}")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            raise BookError(f"route {slug}: route.yaml cannot be read: {exc}") from exc
        if not isinstance(data, dict):
            raise BookError(f"route {slug}: route.yaml must be a mapping")
        sections = []
        for inc in data.get("includes") or []:
            sections += self.load_route(inc, _chain + (slug,))["sections"]
        for s in data.get("sections") or []:
            items = []
            for it in s.get("items") or []:
                if isinstance(it, str):
                    it = {"card": it}
                if not isinstance(it, dict) or not ({"card", "proof_of"} & set(it)):
                    raise BookError(f"route {slug}: bad item {it!r}")
                items.append(it)
            sections.append({"title": str(s.get("title", "")), "items": items})
        appendix = [{"card": x} if isinstance(x, str) else x for x in data.get("appendix") or []]
        return {"slug": slug, "title": data.get("title", slug), "sections": sections, "appendix": appendix}

    def sequence(self, route: dict) -> list:
        """Reading order: dicts {id, section, role}; role is item | proof | appendix."""
        seq, later, appendix = [], {}, []
        for si, sec in enumerate(route["sections"]):
            for it in sec["items"]:
                if "proof_of" in it:
                    pid = later.get(it["proof_of"]) or self.chosen_proof(it["proof_of"])
                    if pid:
                        seq.append({"id": pid, "section": si, "role": "proof"})
                    continue
                cid = it["card"]
                seq.append({"id": cid, "section": si, "role": "item"})
                card = self.cards.get(cid)
                if not card or card.kind not in ("A1", "A2", "A5"):
                    continue
                mode = it.get("proof", "owner")
                if mode in ("later", "omit"):
                    if mode == "later":
                        later[cid] = self.chosen_proof(cid)
                elif mode == "appendix":
                    appendix.append(self.chosen_proof(cid))
                else:
                    pid = self.chosen_proof(cid) if mode == "owner" else mode
                    if pid:
                        seq.append({"id": pid, "section": si, "role": "proof"})
        for it in route["appendix"]:
            for cid in (it.get("card"), self.chosen_proof(it["card"]) if it.get("card") in self.cards
                        and self.cards[it["card"]].kind in ("A1", "A2", "A5") else None):
                if cid:
                    appendix.append(cid)
        seq += [{"id": cid, "section": len(route["sections"]), "role": "appendix"} for cid in appendix if cid]
        return seq

    def proofs_of(self, claim: str) -> list:
        return [c for c in self.cards.values() if c.kind == "A3" and c.meta.get("proves") == claim]

    def chosen_proof(self, claim: str, override: str | None = None):
        if override:
            return override
        proofs = self.proofs_of(claim)
        owners = [c for c in proofs if c.meta.get("owner")]
        pick = (owners or proofs or [None])[0]
        return pick.id if pick else None

    # ---- dependency view at claim level
    def node_requires(self, cid: str, proof_for: dict | None = None) -> list:
        card = self.cards[cid]
        out = list(card.requires)
        if self.use_candidates:
            out += list(card.meta.get("requires_candidates") or [])
        if card.kind in ("A1", "A2", "A5"):
            pid = (proof_for or {}).get(cid) or self.chosen_proof(cid)
            if pid in self.cards:
                out += self.cards[pid].requires
                if self.use_candidates:
                    out += list(self.cards[pid].meta.get("requires_candidates") or [])
        seen, res = set(), []
        for x in out:
            if x not in seen and x != cid:
                seen.add(x)
                res.append(x)
        return res

    def nodes(self) -> list:
        return [c.id for c in self.cards.values() if c.kind in ("A1", "A2", "A4", "A5", "A6")]

    def closure(self, targets: list, proof_for: dict | None = None) -> list:
        out, stack = [], list(targets)
        while stack:
            x = stack.pop()
            if x in out or x not in self.cards:
                continue
            out.append(x)
            stack += self.node_requires(x, proof_for)
        return out

    def impact(self, changed: list, proof_for: dict | None = None) -> list:
        rev: dict = {}
        for cid in self.nodes():
            for r in self.node_requires(cid, proof_for):
                rev.setdefault(r, []).append(cid)
        out, stack = [], list(changed)
        while stack:
            x = stack.pop()
            if x in out:
                continue
            out.append(x)
            stack += rev.get(x, [])
        return out

    def stale_prose(self, changed: list) -> list:
        """Cards whose anchors point at a changed card (glue, claims, mappings, findings)."""
        return sorted(c.id for c in self.cards.values()
                      if any(a in changed for a in (c.meta.get("anchors") or {})))


def _cycle(edges: dict):
    state, stack = {}, []

    def visit(n):
        state[n] = 1
        stack.append(n)
        for m in edges.get(n, ()):
            if state.get(m) == 1:
                return stack[stack.index(m):] + [m]
            if m not in state:
                found = visit(m)
                if found:
                    return found
        state[n] = 2
        stack.pop()
        return None

    for n in list(edges):
        if n not in state:
            found = visit(n)
            if found:
                return found
    return None


def anchor_targets(card: Card) -> list:
    m = card.meta
    out = list(card.requires) + list(m.get("between") or [])
    for key in ("proves", "illustrates"):
        if m.get(key):
            out.append(m[key])
    out += [x.get("card") for x in m.get("maps_to") or [] if isinstance(x, dict)]
    return [x for x in dict.fromkeys(out) if x]


def check(book: Book, route: str | None = None) -> dict:
    """Return {'errors': [...], 'warnings': [...]}; each entry is 'CODE id: message'."""
    errors, warnings = [], []

    def add(level, code, cid, msg):
        (errors if level == "error" else warnings).append(f"{code} {cid}: {msg}")

    for level, code, cid, msg in book.problems:
        add(level, code, cid, msg)
    cards = book.cards
    for card in cards.values():
        cid, m, t = card.id, card.meta, card.template
        if not ID_RE.match(cid):
            add("error", "BAD-ID", cid, "ids are lowercase kebab-case")
        if cid != card.path.stem:
            add("error", "ID-FILE", cid, f"id differs from file name {card.path.name}")
        if t is None:
            add("error", "BAD-KIND", cid, f"unknown kind {card.kind!r}")
            continue
        if getattr(card, "slot", None) != t.scope:
            add("error", "WRONG-PLACE", cid, f"{card.kind} cards live under {SCOPE_DIR[t.scope]}/")
        if t.titled and not m.get("title"):
            add("error", "NO-TITLE", cid, "title is required")
        if t.variants:
            if m.get("variant") not in t.variants + (UNCLASSIFIED,):
                add("error", "BAD-VARIANT", cid, f"variant must be one of {', '.join(t.variants)}")
        if t.ladder and m.get("status") not in STATUS:
            add("error", "BAD-STATUS", cid, f"status must be one of {', '.join(STATUS)}")
        if not card.legacy and card.sections.get("body"):
            add("warning", "BODY-LEFT", cid, "the imported '本文' section is still there; finish splitting it into the "
                                              "template's sections and delete it")
        if not card.legacy and m.get("variant") == UNCLASSIFIED:
            add("warning", "UNCLASSIFIED-VARIANT", cid, "choose the variant that fits this card")
        if m.get("status") == "independent" and not card.reviewed_current():
            add("warning", "STALE-REVIEW", cid, "marked independent but no review matches the current fingerprint")
        for f in () if card.legacy and t.scope == "pool" else t.fields:
            if m.get(f) in (None, "", []):
                add("error", "NO-FIELD", cid, f"{f} is required for {card.kind}")
        if card.legacy:
            if not card.sections.get("body"):
                add("error", "NO-SECTION", cid, "an imported (legacy) card needs a '本文' (Body) section")
            add("warning", "LEGACY", cid, "imported text; split it into the template's sections when the card is next edited")
        for key, ja, en in () if card.legacy else t.required:
            if not card.sections.get(key):
                add("error", "NO-SECTION", cid, f"section '{ja}' ({en}) is required")
            elif card.sections[key].strip() in ("TODO", "（未記入）"):
                add("warning", "PLACEHOLDER", cid, f"section '{ja}' is a placeholder")
        for title in card.unknown_sections:
            add("warning", "UNKNOWN-SECTION", cid, f"section '{title}' is not part of {card.kind}")
        for r in card.ref_ids():
            if r not in cards:
                add("error", "UNKNOWN-REF", cid, f"refers to unknown card {r}")
        for f in ("requires", "references"):
            if len(set(m.get(f) or [])) != len(m.get(f) or []):
                add("error", "DUP-REF", cid, f"duplicate entries in {f}")
        if set(card.requires) & set(card.references):
            add("error", "REQ-AND-REF", cid, "a card cannot be both required and merely referenced")
        if cid in card.requires:
            add("error", "SELF-EDGE", cid, "requires itself")
        for rel in m.get("relations") or []:
            if rel.get("type") not in RELATIONS:
                add("error", "BAD-RELATION", cid, f"relation type must be one of {', '.join(RELATIONS)}")
            if rel.get("type") == "variant" and not rel.get("diff"):
                add("error", "RELATION-DIFF", cid, "a variant relation must say what differs")
        for conv in m.get("conventions") or []:
            if conv in cards and cards[conv].kind != "A6":
                add("error", "NOT-CONVENTION", cid, f"{conv} is not an A6 convention card")
        for fp_id, fp in (m.get("anchors") or {}).items():
            if fp_id not in cards:
                add("error", "UNKNOWN-REF", cid, f"anchor on unknown card {fp_id}")
            elif cards[fp_id].fingerprint() != fp:
                add("warning", "STALE", cid, f"{fp_id} changed after this card was read (anchored {fp})")
        _kind_checks(book, card, add)

    owners: dict = {}
    for c in cards.values():
        if c.kind == "A3" and c.meta.get("owner"):
            owners.setdefault(c.meta.get("proves"), []).append(c.id)
    for claim, ids in owners.items():
        if len(ids) > 1:
            add("error", "TWO-OWNERS", claim, f"more than one owning proof: {', '.join(ids)}")
    for c in cards.values():
        if c.kind == "A2" and c.meta.get("status") not in (None, "stated"):
            proofs = book.proofs_of(c.id)
            if not proofs:
                add("warning", "NO-PROOF", c.id, f"status {c.meta.get('status')} but no proof card")
            elif len(proofs) > 1 and c.id not in owners:
                add("warning", "NO-OWNER", c.id, "several proofs and none marked owner")
            else:
                want = {"equivalence": "equivalence-both", "unique-existence": "construction-uniqueness"}.get(
                    c.meta.get("variant"))
                pid = book.chosen_proof(c.id)
                if want and pid and cards[pid].meta.get("variant") != want:
                    add("warning", "PROOF-SHAPE", c.id, f"a {c.meta.get('variant')} claim expects a {want} proof")

    cyc = _cycle({cid: [r for r in book.node_requires(cid) if r in cards] for cid in book.nodes()})
    if cyc:
        add("error", "CYCLE", cyc[0], "hard prerequisites form a cycle: " + " -> ".join(cyc))
    if route:
        _route_checks(book, route, add)
    return {"errors": errors, "warnings": warnings}


def _kind_checks(book: Book, card: Card, add):
    cards, m, cid = book.cards, card.meta, card.id
    if card.kind == "A1" and m.get("variant") in ("recursive", "quotient-choice") and not m.get("well_defined"):
        add("error", "NO-WELL-DEFINED", cid, "recursive and quotient/choice definitions need well_defined: [claim]")
    if card.kind == "A3":
        target = cards.get(m.get("proves"))
        if target is not None and target.kind not in ("A1", "A2", "A5"):
            add("error", "PROVES-NON-CLAIM", cid, f"{m.get('proves')} is not an A2 claim (nor an A1 definition "
                                                  f"or A5 exercise it supports)")
        steps = card.sections.get("steps", "")
        if card.legacy:
            return
        cites = [x.strip() for g in BY_RE.findall(steps) for x in g.split(",") if x.strip()]
        for x in cites:
            if x not in cards:
                add("error", "UNKNOWN-REF", cid, f"step cites unknown card {x}")
            elif x not in card.requires:
                add("error", "CITE-NOT-REQUIRED", cid, f"step cites {x} but it is not in requires")
        for r in card.requires:
            if r in cards and r not in cites:
                add("warning", "UNUSED-REQUIRES", cid, f"requires {r} but no step cites it")
        _shape(card, steps, add)
    if card.kind == "B2":
        between = m.get("between") or []
        if len(between) != 2:
            add("error", "BAD-BETWEEN", cid, "between must name exactly two cards")
        elif not all(x in (m.get("anchors") or {}) for x in between):
            add("warning", "NO-ANCHOR", cid, "anchor both neighbours so a change makes this card STALE")
    if card.kind == "B3":
        if set(m.get("forward") or []) & set(card.requires):
            add("error", "PREVIEW-REQUIRED", cid, "a previewed result cannot be a prerequisite")
    if card.kind == "C2":
        if m.get("adoption") not in ADOPTION:
            add("error", "BAD-ADOPTION", cid, f"adoption must be one of {', '.join(ADOPTION)}")
        if m.get("scope_audit") not in AUDIT:
            add("error", "BAD-AUDIT", cid, f"scope_audit must be one of {', '.join(AUDIT)}")
        if m.get("adoption") in ("partial", "not-adopted", "outlook") and not m.get("reason"):
            add("error", "NO-REASON", cid, "partial or missing adoption needs reason (and remaining obligations)")
        if m.get("scope_audit") == "OK" and not m.get("maps_to"):
            add("error", "NO-MAP", cid, "marked OK but maps to no card")
        for x in m.get("maps_to") or []:
            if isinstance(x, dict) and x.get("relation") not in RELATIONS:
                add("error", "BAD-RELATION", cid, f"relation must be one of {', '.join(RELATIONS)}")
            if isinstance(x, dict) and x.get("relation") == "variant" and not x.get("diff"):
                add("error", "RELATION-DIFF", cid, "a variant mapping must say what differs")
        for x in m.get("sources") or []:
            if isinstance(x, dict) and x.get("src") in cards and cards[x["src"]].kind != "C1":
                add("error", "NOT-SOURCE", cid, f"{x['src']} is not a C1 source record")
        if m.get("scope_audit") == "OUT" and not m.get("reason"):
            add("error", "NO-REASON", cid, "an OUT row names the book or reason that owns it")
        if m.get("scope_audit") == "OK":
            for x in anchor_targets(card):
                if x in cards and (m.get("anchors") or {}).get(x) not in (None, cards[x].fingerprint()):
                    add("warning", "AUDIT-STALE", cid, f"marked OK but {x} changed since")
                if x in cards and cards[x].meta.get("status") == "stated":
                    add("warning", "AUDIT-UNPROVED", cid, f"marked OK but {x} is only stated")
    if card.kind == "D1":
        t = cards.get(m.get("target"))
        if t is not None and m.get("target_fp") != t.fingerprint():
            add("warning", "FINDING-TARGET-CHANGED", cid, f"{t.id} changed since this finding; recheck")
        if m.get("severity") not in SEVERITY:
            add("error", "BAD-SEVERITY", cid, f"severity must be one of {', '.join(SEVERITY)}")
        if m.get("status") not in FINDING_STATUS:
            add("error", "BAD-FINDING-STATUS", cid, f"status must be one of {', '.join(FINDING_STATUS)}")
        if m.get("status") == "resolved-with-reason" and not m.get("reason"):
            add("error", "NO-REASON", cid, "a resolved finding needs the reason it is not a defect")
    if card.kind == "C1" and not (m.get("sha256") or m.get("edition")):
        add("warning", "NO-EDITION", cid, "record the edition or hash so a changed edition is noticed")


def _shape(card: Card, steps: str, add):
    v, cid = card.meta.get("variant"), card.id
    if v == "equivalence-both":
        fwd = re.search(r"⇒|\\Rightarrow|\\implies|\(only if\)|必要", steps)
        bwd = re.search(r"⇐|\\Leftarrow|\\impliedby|\(if\)|十分", steps)
        if not (fwd and bwd):
            add("error", "SHAPE", cid, "an equivalence proof must treat both directions")
    elif v == "induction":
        if not (re.search(r"基底|base", steps, re.I) and re.search(r"帰納|inductive|induction step", steps, re.I)):
            add("error", "SHAPE", cid, "an induction proof needs a base case and an inductive step")
    elif v == "construction-uniqueness":
        if not (re.search(r"存在|existence", steps, re.I) and re.search(r"一意|uniqueness|unique", steps, re.I)):
            add("error", "SHAPE", cid, "show existence and uniqueness separately")
    elif v == "double-inclusion":
        if len(re.findall(r"\\subseteq|\\subset|⊆|⊂|\\supseteq|⊇", steps)) < 2:
            add("error", "SHAPE", cid, "a double-inclusion proof must show both inclusions")


def _route_checks(book: Book, slug: str, add):
    cards = book.cards
    route = book.load_route(slug)
    seq = book.sequence(route)
    pos, shown = {}, set()
    for i, e in enumerate(seq):
        if e["id"] not in cards:
            add("error", "ROUTE-UNKNOWN", slug, f"route lists unknown card {e['id']}")
            continue
        if e["id"] in pos:
            add("warning", "DUPLICATE-IN-ROUTE", e["id"],
                f"appears twice in route {slug}; a claim already shows its proof (use `proof_of` only with `proof: later`)")
        pos.setdefault(e["id"], i)
        shown.add(e["id"])
    borrows = {}
    for cid in shown:
        c = cards[cid]
        if c.kind == "B5":
            for b in c.meta.get("borrows") or []:
                if isinstance(b, dict) and b.get("card"):
                    borrows[b["card"]] = b
    for b in borrows:
        if b in pos:
            add("warning", "BORROW-IN-ROUTE", slug, f"{b} is borrowed but also appears in the route")
    for e in seq:
        c = cards.get(e["id"])
        if not c:
            continue
        deps = list(c.requires)
        for conv in c.meta.get("conventions") or []:
            deps.append(conv)
        for r in deps:
            if r not in cards:
                continue
            if r not in pos:
                if r not in borrows:
                    add("error", "UNLISTED-BORROW", c.id,
                        f"needs {r}, which is neither in route {slug} nor listed in an entrance card's borrows")
            elif pos[r] > pos[c.id]:
                add("error", "FORWARD", c.id, f"needs {r}, which comes later in route {slug}")
        for mention in c.mentions():
            if mention in cards and mention not in pos and mention not in borrows:
                add("warning", "REF-OUTSIDE-ROUTE", c.id,
                    f"cites [[{mention}]], which is neither in route {slug} nor borrowed")
        if c.kind == "B3":
            for f in c.meta.get("forward") or []:
                if f in pos and pos[f] < pos[c.id]:
                    add("warning", "PREVIEW-EARLIER", c.id, f"{f} already appeared before this preview")
                if f not in pos:
                    add("warning", "PREVIEW-MISSING", c.id, f"{f} never appears in route {slug}")
        if c.kind == "B2":
            b = c.meta.get("between") or []
            if len(b) == 2 and all(x in pos for x in b) and not pos[b[0]] < pos[c.id] < pos[b[1]]:
                add("warning", "TRANSITION-PLACE", c.id, "does not sit between its two neighbours in this route")
        if c.kind == "B1":
            for a in c.meta.get("answered_by") or []:
                if a not in pos:
                    add("warning", "OPEN-QUESTION", c.id, f"answering card {a} is not in route {slug}")
            if not c.meta.get("answered_by"):
                add("warning", "OPEN-QUESTION", c.id, "no answered_by recorded")
    for cid, c in cards.items():
        if c.route == slug and c.kind in ("B1", "B2", "B3", "B4", "B5") and cid not in pos:
            add("warning", "UNUSED-GLUE", cid, f"glue card of route {slug} is not placed in it")


# ---------------------------------------------------------------- search


# words that carry no identity: id prefixes, connectives and the most generic mathematical nouns
ID_NOISE = {"def", "claim", "proof", "lem", "thm", "prop", "cor", "ex", "exer", "conv", "the", "and", "for", "of",
            "number", "integer", "set", "function", "map", "definition", "theorem", "lemma", "proposition",
            "corollary", "example", "exercise"}


def _tokens(text: str) -> set:
    text = text.lower()
    out = set(re.findall(r"[a-z0-9]{2,}", text)) - ID_NOISE
    for run in re.findall(r"[぀-ヿ㐀-鿿]+", text):
        out |= {run[i:i + 2] for i in range(len(run) - 1)} or {run}
    return out


def search(book: Book, query: str, limit: int = 8, kinds: tuple | None = None, min_overlap: int = 1) -> list:
    q = _tokens(query)
    if not q:
        return []
    hits = []
    for c in book.cards.values():
        if c.kind not in ("A1", "A2", "A3", "A4", "A5", "A6") or (kinds and c.kind not in kinds):
            continue
        doc = " ".join([c.id.replace("-", " "), str(c.meta.get("title", "")), " ".join(c.meta.get("aliases") or []),
                        " ".join(map(str, c.meta.get("symbols") or [])),
                        TEX_COMMAND.sub(" ", c.summary(400))])
        overlap = len(q & _tokens(doc))
        score = overlap / len(q)
        if overlap >= min_overlap:
            hits.append((round(score, 3), c))
    hits.sort(key=lambda h: (-h[0], h[1].id))
    return hits[:limit]


# ---------------------------------------------------------------- creating cards

NEW_MATCH = 0.5


def new_card(book: Book, kind: str, cid: str, **kw) -> Path | None:
    """Scaffold a card under the root lock, on a fresh read, so two writers cannot both create the same
    id or both miss each other's similar card.  Fact cards (A*) must be searched for first: a similar
    card in the pool means the caller states reuse / variant:<id> / new --reason before anything is written."""
    with book_lock(book.root):
        return _new_card(Book(book.root), kind, cid, **kw)


def _new_card(book: Book, kind: str, cid: str, *, title: str = "", variant: str | None = None,
              area: str | None = None, route: str | None = None, decision: str | None = None,
              reason: str | None = None, target: str | None = None, severity: str | None = None,
              summary: str | None = None, proves: str | None = None) -> Path | None:
    t = TEMPLATES.get(kind)
    if t is None:
        raise BookError(f"unknown kind {kind}; choose from {', '.join(TEMPLATES)}")
    if not ID_RE.match(cid):
        raise BookError("id must be lowercase kebab-case")
    if cid in book.cards:
        raise BookError(f"id already exists: {cid}")
    meta: dict = {"id": cid, "kind": kind}
    if t.titled or title:
        meta["title"] = title
    if t.variants:
        meta["variant"] = variant or t.variants[0]
    if kind == "A3":
        if not proves or proves not in book.cards:
            raise BookError("a proof card needs --proves <existing claim id>")
        existing = book.proofs_of(proves)
        if existing and not decision:
            raise BookError(f"{proves} already has a proof ({', '.join(c.id for c in existing)}). Decide: "
                            f"--decision alt (another proof, not the owner; say what it adds with --reason) | reuse")
        if decision == "reuse":
            return None
        meta["proves"], meta["owner"] = proves, not existing
        meta["title"] = title or f"Proof of {book.cards[proves].meta.get('title') or proves}"
        if existing and not reason:
            raise BookError("--decision alt needs --reason (what the second proof adds)")
    if t.scope == "pool" and kind == "A3":
        meta.update(aliases=[], area=area or book.cards[proves].meta.get("area", "misc"), requires=[], references=[],
                    sources=[], status="stated", searched={"candidates": [c.id for c in existing],
                                                          "decision": decision or "first-proof",
                                                          **({"reason": reason} if reason else {})})
        path = book.root / "pool" / meta["area"] / f"{cid}.md"
    elif t.scope == "pool":
        query = f"{cid.replace('-', ' ')} {title}"
        hits = [(s, c) for s, c in search(book, query, kinds=(kind,)) if s >= NEW_MATCH]
        listing = "; ".join(f"{c.id} ({c.kind}, {s})" for s, c in hits)
        if hits and not decision:
            raise BookError(f"similar cards in the pool: {listing}. Decide first: --decision reuse | variant:<id> "
                            f"| new --reason '<why none fits>'")
        if decision == "reuse":
            return None
        if decision and decision.startswith("variant:"):
            meta["relations"] = [{"to": decision.split(":", 1)[1], "type": "variant", "diff": ""}]
        elif decision == "new" and not reason and hits:
            raise BookError("--decision new needs --reason when similar cards exist")
        meta["searched"] = {"candidates": [c.id for _, c in hits], "decision": decision or "new",
                            **({"reason": reason} if reason else {})}
        meta.update(aliases=[], area=area or "misc", requires=[], references=[], symbols=[], index=[],
                    sources=[], status="stated")
        path = book.root / "pool" / (area or "misc") / f"{cid}.md"
    else:
        if t.scope != "src" and not route:
            raise BookError(f"{kind} cards belong to a route; pass --route")
        if t.ladder:
            meta["status"] = "stated"
        for f in t.fields:
            meta.setdefault(f, [] if f in ("between", "forward", "maps_to", "borrows", "answered_by", "sources") else "")
        if kind == "C2":
            meta.update(adoption="adopted", scope_audit="TODO")
        if kind == "C1":
            meta.update(edition="", sha256="", role="primary")
        if kind == "B2":
            meta["anchors"] = {}
        if kind == "D1":
            if target:
                if target not in book.cards:
                    raise BookError(f"unknown target card {target}")
                meta["target"], meta["target_fp"] = target, book.cards[target].fingerprint()
            meta.update(severity=severity or "minor", status="open")
        path = book.root / ("src" if t.scope == "src" else f"route/{route}/{SCOPE_DIR[t.scope]}") / f"{cid}.md"
        if t.scope in ("card", "map") and kind != "C2":
            meta.setdefault("requires", [])
    if path.exists():
        raise BookError(f"file exists: {path}")
    body = "".join(f"## {ja}\n\n{summary if kind == 'D1' and summary else 'TODO'}\n\n" for _, ja, _en in t.required)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_card(meta, body), encoding="utf-8")
    return path


def set_anchors(card: Card, book: Book) -> dict:
    anchors = {x: book.cards[x].fingerprint() for x in anchor_targets(card) if x in book.cards}
    meta = dict(card.meta)
    meta["anchors"] = anchors
    card.path.write_text(dump_card(meta, card.body), encoding="utf-8")
    return anchors


# ---------------------------------------------------------------- dependency graph


def build_graph(book: Book, route: str, workspace: Path) -> dict:
    """Schema v1 of knowledge-dependencies for one route: one explicitly scoped choice of proofs."""
    data = book.load_route(route)
    seq = book.sequence(data)
    proof_for = {}
    for it in [i for s in data["sections"] for i in s["items"]]:
        if it.get("card") and it.get("proof") not in (None, "owner", "later", "omit", "appendix"):
            proof_for[it["card"]] = it["proof"]
    in_route = [e["id"] for e in seq if book.cards.get(e["id"]) and book.cards[e["id"]].template
                and book.cards[e["id"]].template.dep]
    borrowed = []
    for e in seq:
        c = book.cards.get(e["id"])
        if c and c.kind == "B5":
            borrowed += [b["card"] for b in c.meta.get("borrows") or [] if isinstance(b, dict)]
    ids = list(dict.fromkeys(in_route))
    ext = [b for b in dict.fromkeys(borrowed) if b in book.cards and b not in ids]
    nodes = []
    for cid in ids + ext:
        c = book.cards[cid]
        deps = [r for r in book.node_requires(cid, proof_for) if r in ids or r in ext] if cid in ids else []
        kind = c.template.dep if cid in ids else "external"
        if c.kind == "A2" and c.meta.get("env") in ("lemma",):
            kind = "lemma"
        nodes.append({"id": cid, "kind": kind, "statement": c.summary(300) or c.meta.get("title") or cid,
                      "source": {"path": c.path.resolve().relative_to(Path(workspace).resolve()).as_posix(),
                                 "locator": f"card {cid}"},
                      "requires": deps})
    return {"schema_version": 1, "scope": f"Route {route}: the proofs chosen by the route.",
            "coverage": {"status": "partial", "note": "Generated from cards; edges are the declared requires of the "
                                                       "statement and its chosen proof."},
            "nodes": nodes}


# ---------------------------------------------------------------- TeX output

ENV = {"A1": "definition", "A2": "theorem", "A4": "example"}
THEOREMS = {
    "en": ("\\theoremstyle{plain}\n\\newtheorem{theorem}{Theorem}[section]\n\\newtheorem{lemma}[theorem]{Lemma}\n"
           "\\newtheorem{proposition}[theorem]{Proposition}\n\\newtheorem{corollary}[theorem]{Corollary}\n"
           "\\newtheorem{axiom}[theorem]{Axiom}\n\\theoremstyle{definition}\n\\newtheorem{definition}[theorem]{Definition}\n"
           "\\newtheorem{example}[theorem]{Example}\n\\newtheorem{exercise}[theorem]{Exercise}\n"
           "\\newenvironment{solution}{\\begin{proof}[Solution]}{\\end{proof}}\n"),
    "ja": ("\\theoremstyle{plain}\n\\newtheorem{theorem}{定理}[section]\n\\newtheorem{lemma}[theorem]{補題}\n"
           "\\newtheorem{proposition}[theorem]{命題}\n\\newtheorem{corollary}[theorem]{系}\n"
           "\\newtheorem{axiom}[theorem]{公理}\n\\theoremstyle{definition}\n\\newtheorem{definition}[theorem]{定義}\n"
           "\\newtheorem{example}[theorem]{例}\n\\newtheorem{exercise}[theorem]{演習}\n"
           "\\newenvironment{solution}{\\begin{proof}[解答]}{\\end{proof}}\n"),
}
HEADS = {
    "en": "% !TeX program = xelatex\n\\documentclass[11pt]{article}\n\\usepackage{amsmath,amssymb,amsthm,mathtools}\n"
          "\\usepackage{enumitem}\n\\usepackage[hidelinks]{hyperref}\n\\usepackage{cleveref}\n",
    "ja": "% !TeX program = uplatex\n\\documentclass[uplatex,dvipdfmx,11pt]{jsarticle}\n"
          "\\usepackage{amsmath,amssymb,amsthm,mathtools}\n\\usepackage{enumitem}\n"
          "\\usepackage[dvipdfmx,hidelinks]{hyperref}\n\\usepackage{cleveref}\n",
}


def card_label(card: Card) -> str:
    return card.meta.get("label") or f"card:{card.id}"


def render_tex(book: Book, route: str, level: str = "L3", *, standalone: bool = False, language: str = "ja",
               preamble: str | None = None, title: str | None = None) -> str:
    """TeX of a route at a show level.  `[[card-id]]` in card text becomes `\\cref` of that card's label
    (the card's own `label`, else `card:<id>`), so references survive moving cards between books."""
    if level not in LEVELS:
        raise BookError(f"level must be one of {', '.join(LEVELS)}")
    show = set(LEVELS[level])
    data = book.load_route(route)
    seq = book.sequence(data)
    out, last_section = [], None
    for e in seq:
        c = book.cards.get(e["id"])
        if c is None or c.kind not in show:
            continue
        if e["section"] != last_section:
            last_section = e["section"]
            if last_section < len(data["sections"]):
                out.append(f"\\section{{{data['sections'][last_section]['title']}}}\n")
            else:
                out.append("\\appendix\n\\section{Appendix}\n")
        out.append(_tex_card(book, c, language))
    body = "\n".join(out)
    if not standalone:
        return body
    if preamble is not None:
        head = preamble.rstrip() + "\n"
    elif language in HEADS:
        head = HEADS[language] + "\n" + THEOREMS[language]
    else:
        raise BookError(f"no built-in preamble for language {language!r}; pass a preamble file")
    heading = title or str(data["title"]).replace("_", "\\_")
    return (head + f"\n\\title{{{heading}}}\n\\date{{}}\n\\begin{{document}}\n\\maketitle\n\n{body}\n\\end{{document}}\n")


def _resolve(book: Book, text: str) -> str:
    return MENTION_RE.sub(lambda m: f"\\cref{{{card_label(book.cards[m.group(1)])}}}"
                          if m.group(1) in book.cards else m.group(0), text)


def _tex_card(book: Book, c: Card, language: str = "ja") -> str:
    m = c.meta
    s = {k: _resolve(book, v) for k, v in c.sections.items()}
    own_label = c.legacy and m.get("label")  # an imported body already carries its label
    label = "" if own_label else f"\\label{{{card_label(c)}}}\n"
    index = "".join(f"\\index{{{x}}}\n" for x in m.get("index") or [])
    if c.legacy and s.get("body") and c.kind in ("A1", "A2", "A3", "A4", "A5", "A6"):
        env = {"A1": "definition", "A2": m.get("env", "theorem"), "A3": "proof", "A4": "example",
               "A5": "exercise", "A6": m.get("env", "axiom")}[c.kind]
        mark = "" if c.kind == "A3" else label
        return f"\\begin{{{env}}}\n{mark}{s['body']}\n\\end{{{env}}}\n"
    title = f"[{m['title']}]" if m.get("title") and c.kind in ("A1", "A2") else ""
    if c.kind == "A1":
        return f"\\begin{{definition}}{title}\n{label}{index}{s.get('definition', '')}\n" \
               f"{s.get('notation', '')}\n\\end{{definition}}\n"
    if c.kind == "A2":
        env = m.get("env", "theorem")
        body = "\n".join(x for x in (s.get("hypotheses"), s.get("conclusion")) if x)
        return f"\\begin{{{env}}}{title}\n{label}{index}{body}\n\\end{{{env}}}\n"
    if c.kind == "A3":
        return f"\\begin{{proof}}\n{s.get('steps', '')}\n\\end{{proof}}\n"
    if c.kind == "A4":
        return f"\\begin{{example}}\n{label}{index}{s.get('setting', '')}\n{s.get('verification', '')}\n\\end{{example}}\n"
    if c.kind == "A5":
        return (f"\\begin{{exercise}}\n{label}{s.get('question', '')}\n\\end{{exercise}}\n"
                f"\\begin{{solution}}\n{s.get('solution', '')}\n\\end{{solution}}\n")
    if c.kind == "A6":
        return f"\\paragraph{{{'規約' if language == 'ja' else 'Convention'}}}\n{label}{s.get('convention', '')}\n"
    if c.kind == "B5":
        return "\n".join(s[k] for k in ("endpoint", "known", "conventions", "reader") if s.get(k)) + "\n"
    return "\n".join(v for v in s.values() if v) + "\n"


# ---------------------------------------------------------------- status


def _route_ids(book: Book, route: str) -> set:
    return {e["id"] for e in book.sequence(book.load_route(route))}


def status(book: Book, route: str | None = None) -> dict:
    result = check(book, route)
    by_kind: dict = {}
    for c in book.cards.values():
        d = by_kind.setdefault(c.kind, {})
        key = c.meta.get("status") or c.meta.get("scope_audit") or c.meta.get("adoption") or "-"
        d[key] = d.get(key, 0) + 1
    open_major = [c.id for c in book.cards.values() if c.kind == "D1" and c.meta.get("severity") == "major"
                  and c.meta.get("status") == "open"]
    audit = [c for c in book.cards.values() if c.kind == "C2" and (route is None or c.route == route)]
    complete = bool(audit) and all(c.meta.get("scope_audit") in ("OK", "OUT") for c in audit) \
        and not open_major and not result["errors"]
    math = [c for c in book.cards.values() if c.kind in ("A1", "A2", "A3", "A4", "A5", "A6")
            and (route is None or c.id in _route_ids(book, route))]
    review = {"math_cards": len(math), "reviewed_current": sum(1 for c in math if c.reviewed_current("math")),
              "reviewed_stale": sum(1 for c in math if not c.reviewed_current("math")
                                    and any(r.get("kind") == "math" for r in c.meta.get("reviews") or [])),
              "never_reviewed": sum(1 for c in math if not any(r.get("kind") == "math"
                                                               for r in c.meta.get("reviews") or []))}
    return {"cards": len(book.cards), "review": review,
            "legacy": sum(1 for c in book.cards.values() if c.legacy),
            "candidates_pending": sum(1 for c in book.cards.values() if c.meta.get("requires_candidates")),
            "by_kind": by_kind, "errors": len(result["errors"]),
            "warnings": len(result["warnings"]),
            "stale": sorted(w.split()[1].rstrip(":") for w in result["warnings"] if w.startswith("STALE")),
            "open_major_findings": open_major,
            "scope_audit": {k: sum(1 for c in audit if c.meta.get("scope_audit") == k) for k in AUDIT},
            "complete": complete,
            "taken_in": complete and review["math_cards"] > 0 and review["never_reviewed"] == 0
            and review["reviewed_stale"] == 0}
