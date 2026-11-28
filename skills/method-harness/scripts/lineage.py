"""Lineage of code cards: which prior work proposed the step, what its authors meant, and whose code this is."""

import tomllib

CODE_KINDS = {
    "author": "提案者のコード",
    "library": "公開ライブラリ",
    "reader": "読解側の既存計算",
    "ai": "AI 作成の読解用コード",
}
STATUS = {"checked": "一次資料で照合済み", "open": "未確認"}
FIELDS = {"proposal", "intent", "code", "follows", "differences", "status", "substitute"}


def required(root):
    reader = tomllib.loads((root / "harness.toml").read_text(encoding="utf-8")).get("reader", {})
    return bool(reader.get("require_lineage", False))


def check_lineage(card, cards):
    """Return error messages for a step card's `lineage` record (None when the card has none)."""
    lineage = card.get("lineage")
    if lineage is None:
        return None
    if not isinstance(lineage, dict) or set(lineage) - FIELDS:
        return ["lineage の欄が不正（proposal, intent, code, follows, differences, status）"]
    errors = []
    proposal = lineage.get("proposal")
    if (not isinstance(proposal, dict) or set(proposal) - {"src", "loc", "pdf_page"}
            or not isinstance(proposal.get("loc"), str) or not proposal["loc"].strip()):
        errors.append("lineage.proposal に src と loc が必要")
    elif getattr(cards.get(proposal.get("src")), "kind", None) not in ("source", "src"):
        errors.append(f"lineage.proposal.src {proposal.get('src')} は source カードではない")
    for field in ("intent", "differences"):
        if not isinstance(lineage.get(field), str) or not lineage[field].strip():
            errors.append(f"lineage.{field} に本文が必要")
    if lineage.get("code") not in CODE_KINDS:
        errors.append("lineage.code は " + "、".join(CODE_KINDS))
    if lineage.get("status") not in STATUS:
        errors.append("lineage.status は checked または open")
    if "substitute" in lineage and (not isinstance(lineage["substitute"], str) or not lineage["substitute"].strip()):
        errors.append("lineage.substitute に原典と代えた理由が必要")
    if "follows" in lineage and (not isinstance(lineage["follows"], str) or not lineage["follows"].strip()):
        errors.append("lineage.follows が空")
    return errors
