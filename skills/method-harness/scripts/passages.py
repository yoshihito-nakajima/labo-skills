"""Check links from translated passages to evidence and mathematical cards."""

from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
import re
import tomllib
from urllib.parse import urlsplit

from book_links import BOOK_VERSION, BookReferences


LOCAL_KINDS = {"figure": "figure", "code": "step", "run": "run", "claim": "claim", "source": "source"}
ID = re.compile(r"[a-z][a-z0-9-]*")
FINGERPRINT = re.compile(r"[a-f0-9]{8}")


@cache
def writer_api(script):
    spec = spec_from_file_location("method_writing_cards", script)
    writer = module_from_spec(spec)
    spec.loader.exec_module(writer)
    return writer


def load_writing_fact(root, script, ref, namespaces):
    namespace, separator, card_id = ref.partition(":")
    if not separator or not ID.fullmatch(card_id) or namespace not in namespaces:
        raise ValueError(f"未登録の執筆カード参照 {ref}")
    writer = writer_api(script)
    harness = writer.Harness(root / namespaces[namespace])
    matches = list(harness.cards_dir.glob(f"*/{card_id}.md"))
    if len(matches) != 1:
        raise ValueError(f"執筆カード {ref} が一意に見つからない")
    fact = writer.Card(matches[0])
    if fact.id != card_id or not fact.is_fact or not fact.sec("Statement"):
        raise ValueError(f"{ref} は有効な事実カードではない")
    return fact


def writing_namespaces(root):
    return tomllib.loads((root / "harness.toml").read_text(encoding="utf-8")).get("writing_harnesses", {})


def reader_options(root):
    return tomllib.loads((root / "harness.toml").read_text(encoding="utf-8")).get("reader", {})


CODE_REASON_SECTIONS = ("設計の主張", "導出", "コードへの移し方")


def code_reason_section(name, design=None):
    return f"{name}/{design}" if design else name


def check_code_reason(card, design=None):
    if design is not None and (not isinstance(design, str) or not ID.fullmatch(design)):
        raise ValueError(f"{card.id}: 不正な設計の指定")
    sections = [code_reason_section(name, design) for name in CODE_REASON_SECTIONS]
    missing = [name for name in sections if not card.secs.get(name, "").strip()]
    if missing:
        raise ValueError(f"{card.id}: " + "、".join(missing) + "が必要")


def check_reader_fact(root, fact, *, require_goal=True, require_code=False):
    sections = ("Setup", "Goal") if require_goal else ("Setup",)
    for section in sections:
        if not fact.sec(section).strip():
            raise ValueError(f"{fact.id}: ## {section} が必要")
    if fact.kind != "definition" and not fact.sec("Proof").strip():
        raise ValueError(f"{fact.id}: ## Proof が必要")
    code = fact.meta.get("reader_code")
    if code is None and not fact.sec("In code") and not require_code:
        return
    if not isinstance(code, list) or not code:
        raise ValueError(f"{fact.id}: reader_code に対応するコードと行が必要")
    if not fact.sec("In code").strip():
        raise ValueError(f"{fact.id}: ## In code が必要")
    for binding in code:
        if not isinstance(binding, dict) or not isinstance(binding.get("card"), str):
            raise ValueError(f"{fact.id}: reader_code に card と line が必要")
        check_link(root, None, {}, {**binding, "role": "code", "text": fact.id})


def valid_location(where):
    if not isinstance(where, dict) or not re.fullmatch(r"\d+(?:\.\d+)*", str(where.get("section", ""))):
        return False
    keys = set(where) - {"section"}
    if keys == {"heading"}:
        return where["heading"] is True
    return keys in ({"paragraph"}, {"equation"}, {"algorithm", "step"}) and all(
        type(where[key]) is int and where[key] > 0 for key in keys
    )


def reading_blocks(passage):
    """Resolve the author-specified reading order without reordering by evidence type."""
    links = passage["links"]
    keys = [link.get("key") if isinstance(link, dict) else None for link in links]
    if any(not isinstance(key, str) or not ID.fullmatch(key) for key in keys):
        raise ValueError("reading を使う各参照には key が必要")
    if len(keys) != len(set(keys)):
        raise ValueError("参照の key が重複")
    references = dict(zip(keys, links, strict=True))
    entries = passage.get("reading")
    if not isinstance(entries, list) or not entries:
        raise ValueError("reading は本文または参照の配列で指定する")
    seen = set()
    resolved = []
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("reading の要素には text または ref を指定する")
        if item.keys() == {"text"} and isinstance(item["text"], str) and item["text"].strip():
            resolved.append(("text", item["text"]))
            continue
        ref = item.get("ref")
        if item.keys() not in ({"ref"}, {"ref", "part"}) or not isinstance(ref, str) or ref not in references:
            raise ValueError(f"reading の参照先が見つからない {ref}")
        if "part" in item:
            if item["part"] != "code" or references[ref].get("role") != "math" or ref not in seen:
                raise ValueError(f"{ref}: part: code は数学の参照が出た後に指定する")
            if (ref, "code") in seen:
                raise ValueError(f"{ref} のコードが重複")
            seen.add((ref, "code"))
            resolved.append(("fact-code", references[ref]))
        else:
            if ref in seen:
                raise ValueError(f"{ref} が reading 内で重複")
            seen.add(ref)
            resolved.append(("link", references[ref]))
    missing = set(keys) - seen
    if missing:
        raise ValueError("reading に現れない参照 " + ", ".join(sorted(missing)))
    return resolved


def check_passages(root, card, script, books=None):
    """Return diagnostics for the optional passage records on a source map."""
    entries = card.get("passages", [])
    if not isinstance(entries, list):
        return [("ERR", "PASSAGE", card.id, "passages は配列で指定する")]

    issues = []
    namespaces = writing_namespaces(root.root)
    options = reader_options(root.root)
    seen = set()
    for passage in entries:
        if not isinstance(passage, dict):
            issues.append(("ERR", "PASSAGE", card.id, "各 passage は辞書で指定する"))
            continue
        identifier = passage.get("id", "")
        where = passage.get("at")
        if not isinstance(identifier, str) or not ID.fullmatch(identifier) or identifier in seen:
            issues.append(("ERR", "PASSAGE", card.id, f"不正または重複した passage ID {identifier}"))
            continue
        seen.add(identifier)
        if not valid_location(where):
            issues.append(("ERR", "PASSAGE", card.id,
                           f"{identifier}: 節と、見出し・段落・式・Algorithm の手順のいずれかが必要"))
        if not isinstance(passage.get("summary"), str) or not passage["summary"].strip():
            issues.append(("ERR", "PASSAGE", card.id, f"{identifier}: summary が必要"))
        links = passage.get("links")
        if not isinstance(links, list) or not links:
            issues.append(("ERR", "PASSAGE", card.id, f"{identifier}: links が必要"))
            continue
        code_parts = set()
        if options.get("ordered_reading", False) or "reading" in passage:
            try:
                code_parts = {value["key"] for kind, value in reading_blocks(passage) if kind == "fact-code"}
            except ValueError as error:
                issues.append(("ERR", "PASSAGE-ORDER", card.id, f"{identifier}: {error}"))
            if "note" in passage:
                issues.append(("ERR", "PASSAGE-ORDER", card.id, f"{identifier}: note は reading の位置に置く"))
        for link in links:
            try:
                current = check_link(root, script, namespaces, link, books=books)
                if link["role"] == "math" and (options.get("structured_facts", False) or link.get("key") in code_parts):
                    fact = load_writing_fact(root.root, script, link["card"], namespaces)
                    check_reader_fact(root, fact, require_goal=not options.get("ordered_reading", False),
                                      require_code=link.get("key") in code_parts)
                if options.get("code_proofs", False) and link["role"] == "code" and "walkthrough" not in link:
                    check_code_reason(root.cards[link["card"]], link.get("design"))
                if link["role"] not in {"math", "book", "source"} and link["card"] not in (card.get("anchors") or {}):
                    raise ValueError(f"{link['card']} の anchors が必要")
            except ValueError as error:
                issues.append(("ERR", "PASSAGE-REF", card.id, f"{identifier}: {error}"))
            else:
                recorded = link.get("version") if link["role"] == "book" else link.get("fingerprint")
                if current is not None and current != recorded:
                    issues.append(("WARN", "STALE-PASSAGE", card.id,
                                   f"{identifier}: {link['card']} を再確認"))
                if link["role"] == "run" and root.record_state(link["card"]) != "ok":
                    issues.append(("WARN", "STALE-PASSAGE", card.id,
                                   f"{identifier}: {link['card']} の実行記録を再確認"))
    return issues


def check_link(root, script, namespaces, link, *, books=None):
    if not isinstance(link, dict) or not all(
        isinstance(link.get(key), str) and link[key].strip() for key in ("role", "card", "text")
    ):
        raise ValueError("参照には role, card, text が必要")
    ref, role = link["card"], link["role"]
    if role == "math":
        if not isinstance(link.get("fingerprint"), str) or not FINGERPRINT.fullmatch(link["fingerprint"]):
            raise ValueError(f"{ref} の指紋が必要")
        return load_writing_fact(root.root, script, ref, namespaces).fingerprint()
    if role == "book":
        if not isinstance(link.get("version"), str) or not BOOK_VERSION.fullmatch(link["version"]):
            raise ValueError(f"{ref} の book borrow 版が必要")
        return (books if books is not None else BookReferences(root.root)).resolve(ref).version
    target = root.cards.get(ref)
    if role not in LOCAL_KINDS or target is None or target.kind != LOCAL_KINDS[role]:
        raise ValueError(f"{role} に対応するカード {ref} が見つからない")
    if role == "source":
        if target.get("access") != "open" or not all(
            isinstance(target.get(key), str) and target.get(key).strip()
            for key in ("edition", "license", "checked")
        ):
            raise ValueError(f"{ref}: 公開資料の版・利用条件・確認日が必要")
        for key in ("url", "license_url"):
            value = target.get(key)
            url = urlsplit(value) if isinstance(value, str) else None
            if not url or url.scheme != "https" or not url.hostname or url.username or url.password:
                raise ValueError(f"{ref}: {key} に公開元の HTTPS URL が必要")
        if not isinstance(link.get("loc"), str) or not link["loc"].strip():
            raise ValueError(f"{ref}: 参照した節・定理・頁のいずれかが必要")
    if role == "figure" and not (isinstance(link.get("panel"), str) and link["panel"].strip()):
        raise ValueError(f"{ref} のパネルを指定する")
    if role == "figure" and "anchor" in link and (
        not isinstance(link["anchor"], str) or not ID.fullmatch(link["anchor"])
    ):
        raise ValueError(f"{ref} の図のアンカーが不正")
    if role == "figure" and "display" in link and link["display"] not in ("inline", "reading", "link"):
        raise ValueError(f"{ref} の表示は inline、reading、link のいずれか")
    if role == "figure" and "crop" in link:
        box = link["crop"]
        if (not isinstance(box, list) or len(box) != 4
                or not all(type(value) is int and value >= 0 for value in box)
                or not (box[0] < box[2] and box[1] < box[3])):
            raise ValueError(f"{ref} の crop には左・上・右・下の画素座標が必要")
    if role == "code":
        bounds = target.get("code", {}).get("lines", [])
        line = link.get("line")
        through = link.get("through", line)
        if (type(line) is not int or not isinstance(bounds, list) or len(bounds) != 2
                or not all(type(bound) is int for bound in bounds)
                or type(through) is not int or not bounds[0] <= line <= through <= bounds[1]):
            raise ValueError(f"{ref} の行 {line}–{through} はコード範囲外")
