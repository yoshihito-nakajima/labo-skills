"""Collect and validate the mathematical statements in each detailed passage."""

from hashlib import sha256
import json
from pathlib import Path
import re
import tomllib

import yaml

from closed_formula import closed_tex


KINDS = {
    "definition": "定義",
    "math": "主張",
    "cost": "計算量",
    "observation": "観察",
    "cited": "引用",
    "code": "コードの主張",
}
# How the source's wording relates to the work it rests on (the original, 原典).
ORIGIN_RELATIONS = {
    "agrees": "原典と一致",
    "hypotheses": "前提を補えば原典と一致",
    "stronger": "原典より強い言い方",
    "weaker": "原典より弱い言い方",
    "differs": "原典と食い違う",
    "unchecked": "原典は未照合",
}
REALIZATION_KINDS = {
    "equality": "等式",
    "approximation": "誤差つき近似",
    "numerical": "数値計算",
    "choice": "選択",
}
REALIZATION_FIELDS = ("math", "code", "kind", "holds", "outside", "error")
POINT_KINDS = ("definition", "math", "cost")
ID = re.compile(r"[a-z][a-z0-9-]*")
TEXT_FIELDS = ("title", "statement", "reason")
CHECK_NOTATION = re.compile(r"\\(?:all|some|one|setof|sumover|limto|fn|op|pred)\{")


class ClaimLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in keys:
                raise yaml.constructor.ConstructorError(
                    None, None, f"不正または重複したキー {key!r}", key_node.start_mark)
            keys.add(key)
        return super().construct_mapping(node, deep=deep)


class ClaimReadings:
    def __init__(self, root: Path):
        reader = tomllib.loads((root / "harness.toml").read_text(encoding="utf-8")).get("reader", {})
        manifest = reader.get("claim_readings")
        self.enabled = manifest is not None
        self.require_code_walkthroughs = reader.get("require_code_walkthroughs", False)
        self.require_points = reader.get("require_points", False)
        self.require_realizations = reader.get("require_realizations", False)
        self.max_main = reader.get("max_main_per_section", 2)
        self.entries = {}
        if self.enabled:
            if not isinstance(manifest, str) or not manifest.strip():
                raise ValueError("claim_readings に YAML のパスが必要")
            path = (root / manifest).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError("claim_readings はプロジェクト内に置く")
            self.entries = yaml.load(path.read_text(encoding="utf-8"), Loader=ClaimLoader)
            if not isinstance(self.entries, dict):
                raise ValueError("claim_readings は詳読 ID から言明の配列への対応で指定する")

    def check(self, passages):
        """Return located schema, coverage and dependency errors."""
        if not self.enabled:
            return [(passage["id"], error) for passage in passages for error in self.check_walkthroughs(passage)]
        errors = []
        by_id = {passage["id"]: passage for passage in passages}
        for identifier in sorted(by_id.keys() - self.entries.keys()):
            errors.append((identifier, "詳読の言明が未登録"))
        for identifier in sorted(self.entries.keys() - by_id.keys()):
            errors.append((identifier, "対応する詳読がない"))
        for identifier in sorted(by_id.keys() & self.entries.keys()):
            errors.extend((identifier, error) for error in self._check_passage(by_id[identifier]))
        for passage in passages:
            errors.extend((passage["id"], error) for error in self.check_walkthroughs(passage))
        per_section = {}
        for identifier in by_id.keys() & self.entries.keys():
            section = str(by_id[identifier].get("at", {}).get("section"))
            entries = self.entries[identifier] if isinstance(self.entries[identifier], list) else []
            per_section.setdefault(section, []).extend(
                identifier for entry in entries if isinstance(entry, dict) and entry.get("main"))
        for section, owners in sorted(per_section.items()):
            if len(owners) > self.max_main:
                errors.append((owners[0], f"§{section} の本文の主張（main）は{self.max_main}件まで"))
        return errors

    def main_entries(self, passage_id):
        """The statements shown in the main text, in the order of the passage."""
        return [entry for entry in self.entries.get(passage_id, []) if entry.get("main")]

    def check_walkthroughs(self, passage):
        links = [link for link in passage["links"] if "walkthrough" in link]
        errors = [f"{link.get('key')}: コード参照に walkthrough が必要"
                  for link in passage["links"]
                  if self.require_code_walkthroughs and link.get("role") == "code" and "walkthrough" not in link]
        if not links:
            return errors
        if not self.enabled or not passage.get("reading"):
            return errors + ["実装の詳読には claim_readings と reading が必要"]

        entries = self.entries.get(passage["id"], [])
        if not isinstance(entries, list):
            return ["実装の詳読には言明の配列が必要"]
        claims = {entry["id"]: entry for entry in entries
                  if isinstance(entry, dict) and isinstance(entry.get("id"), str)}
        positions = {claim: position for position, claim in enumerate(claims)}
        seen = set()
        for link in links:
            key, walk = link.get("key"), link["walkthrough"]
            if link.get("role") != "code" or not isinstance(walk, dict):
                errors.append(f"{key}: walkthrough はコード参照の辞書として指定する")
                continue
            variant = link.get("design")
            if variant is not None and (not isinstance(variant, str) or not ID.fullmatch(variant)):
                errors.append(f"{key}: 不正な設計の指定")
            if walk.keys() - {"claim", "bridge", "math", "realization", "fingerprint"}:
                errors.append(f"{key}: walkthrough の欄が不正")
            code = walk.get("claim")
            if not isinstance(code, str) or claims.get(code, {}).get("kind") != "code":
                errors.append(f"{key}: walkthrough.claim に同じ詳読のコードの主張が必要")
            else:
                basis = claims[code].get("basis")
                if not isinstance(basis, list) or key not in basis:
                    errors.append(f"{key}: {code} の basis にこのコード参照が必要")
                if code in seen:
                    errors.append(f"{key}: コードの主張 {code} は手順内で重複している")
                seen.add(code)
            bridge = walk.get("bridge")
            if (not isinstance(bridge, str) or not bridge.strip() or CHECK_NOTATION.search(bridge)):
                errors.append(f"{key}: walkthrough.bridge にコードの主張から数学への証明が必要")
            math = walk.get("math")
            if (not isinstance(math, list) or not math or any(
                not isinstance(ref, str) or claims.get(ref, {}).get("kind") != "math" for ref in math
            )):
                errors.append(f"{key}: walkthrough.math に同じ詳読の数学の主張が必要")
            elif [positions[ref] for ref in math] != sorted({positions[ref] for ref in math}):
                errors.append(f"{key}: 数学の主張は重複なく言明の順に置く")
            errors.extend(f"{key}: {error}" for error in self.check_realization(walk.get("realization")))
            if "fingerprint" in walk and (not isinstance(walk["fingerprint"], str)
                                           or not re.fullmatch(r"[a-f0-9]{8}", walk["fingerprint"])):
                errors.append(f"{key}: walkthrough.fingerprint が不正")
        return errors

    def check_realization(self, rows):
        """Check the rows that pair a mathematical quantity with the computed one."""
        if rows is None:
            return ["walkthrough.realization に定理と計算の対応表が必要"] if self.require_realizations else []
        if not isinstance(rows, list) or not rows:
            return ["walkthrough.realization は対応の行の配列で指定する"]
        errors = []
        for number, row in enumerate(rows, 1):
            if not isinstance(row, dict) or row.keys() - set(REALIZATION_FIELDS):
                errors.append(f"realization の{number}行目の欄が不正")
                continue
            for field in ("math", "code", "holds"):
                value = row.get(field)
                if not isinstance(value, str) or not value.strip() or CHECK_NOTATION.search(value):
                    errors.append(f"realization の{number}行目に {field} の本文が必要")
            if row.get("kind") not in REALIZATION_KINDS:
                errors.append(f"realization の{number}行目の kind は " + "、".join(REALIZATION_KINDS))
            if row.get("kind") == "approximation" and not row.get("error"):
                errors.append(f"realization の{number}行目の近似には error が必要")
            for field in ("outside", "error"):
                if field in row and (not isinstance(row[field], str) or not row[field].strip()):
                    errors.append(f"realization の{number}行目の {field} が空")
        return errors

    def walkthrough_fingerprint(self, passage_id, link):
        walk = link["walkthrough"]
        references = {walk["claim"], *walk["math"]}
        claims = [{key: item.get(key) for key in ("id", "kind", "statement", "reason", "formula", "status")}
                  for item in self.entries[passage_id]
                  if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"] in references]
        content = {"line": link.get("line"), "through": link.get("through"), "card": link.get("card"),
                   "bridge": walk["bridge"], "claims": claims}
        if "realization" in walk:
            content["realization"] = walk["realization"]
        return sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8]

    def _check_passage(self, passage):
        entries = self.entries[passage["id"]]
        if not isinstance(entries, list) or not entries:
            return ["言明の配列が空"]
        if not passage.get("reading"):
            return ["言明を載せる詳読に reading が必要"]
        evidence = {item["key"]: item for item in passage["links"] if isinstance(item.get("key"), str)}
        seen = set()
        errors = []
        for entry in entries:
            identifier = entry.get("id") if isinstance(entry, dict) else None
            if not isinstance(identifier, str) or not ID.fullmatch(identifier) or identifier in seen:
                errors.append(f"不正または重複した言明 ID {identifier}")
                continue
            kind = entry.get("kind")
            if not isinstance(kind, str) or kind not in KINDS:
                errors.append(f"{identifier}: 言明の種類が不正")
            if any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in TEXT_FIELDS):
                errors.append(f"{identifier}: 題名・言明本文・根拠が必要")
            elif CHECK_NOTATION.search(entry["statement"]):
                errors.append(f"{identifier}: 言明本文には通常の数学の記法を使う")
            if "point" in entry or (self.require_points and kind in POINT_KINDS):
                point = entry.get("point")
                if not isinstance(point, str) or not point.strip() or CHECK_NOTATION.search(point):
                    errors.append(f"{identifier}: point に通読で示す要点が必要")
            if kind == "cost" and (not isinstance(entry.get("model"), str) or not entry["model"].strip()):
                errors.append(f"{identifier}: 計算量の主張には model（数える操作、入力の大きさ、使う算法）が必要")
            if kind == "cited" and "origin" not in entry:
                errors.append(f"{identifier}: 引用した主張には origin（原典と照合の結果）が必要")
            if "origin" in entry:
                errors.extend(f"{identifier}: {error}" for error in check_origin(entry["origin"]))
            if "main" in entry and (entry["main"] is not True or kind not in ("definition", "math")
                                    or entry.get("status") == "open"):
                errors.append(f"{identifier}: main: true は確認済みの定義・主張にだけ付ける")
            if "setup" in entry:
                errors.append(f"{identifier}: 設定と結論は statement に続けて書く")
            if entry.get("status", "explained") not in ("explained", "open"):
                errors.append(f"{identifier}: status は explained または open")
            if "formula" in entry or kind in ("definition", "math", "code"):
                try:
                    closed_tex(entry.get("formula"))
                except (ValueError, RecursionError) as error:
                    errors.append(f"{identifier}: {error}")
            for field, targets in (("requires", seen), ("basis", evidence)):
                refs = entry.get(field, [])
                if (not isinstance(refs, list)
                        or any(not isinstance(ref, str) or ref not in targets for ref in refs)):
                    errors.append(f"{identifier}: {field} に未登録または後出の参照がある")
            basis = entry.get("basis", [])
            if kind in ("observation", "code") and isinstance(basis, list):
                roles = {"figure", "run"} if kind == "observation" else {"code"}
                if not any(isinstance(ref, str) and evidence.get(ref, {}).get("role") in roles for ref in basis):
                    errors.append(f"{identifier}: 観察・コードの言明には該当図・実行・行への参照が必要")
            seen.add(identifier)
        return errors


def check_origin(origin):
    """`origin`: the work a statement rests on and how the source's wording compares with it."""
    if not isinstance(origin, dict) or set(origin) - {"src", "cite", "loc", "pdf_page", "relation", "note", "substitute"}:
        return ["origin の欄が不正（src または cite、loc、relation、note、substitute）"]
    errors = []
    if "substitute" in origin and (not isinstance(origin["substitute"], str) or not origin["substitute"].strip()
                                   or not origin.get("src")):
        errors.append("代替資料で照合したときは origin.substitute に原典と代えた理由を書き、src に代替資料を置く")
    if not any(isinstance(origin.get(key), str) and origin[key].strip() for key in ("src", "cite")):
        errors.append("origin に src（source カード）か cite（書誌）が必要")
    if origin.get("relation") not in ORIGIN_RELATIONS:
        errors.append("origin.relation は " + "、".join(ORIGIN_RELATIONS))
    if origin.get("relation") not in ("agrees", "unchecked", None) and not origin.get("note"):
        errors.append("原典と一致しない場合は origin.note に違いを書く")
    return errors
