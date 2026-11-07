#!/usr/bin/env python3
"""Rules for the paper-viability indicator, and a check that a stated verdict respects them.

The indicator is a judgment aid, not a score. Six axes carry a level (strong/mid/weak/unknown);
the verdict is capped by explicit rules. This module is the single authority for those rules:
the page builder prints them and the checker enforces them.

Usage: indicator.py REVIEW.json   (reads review["indicator"]; exit 1 on a violated rule)
"""
import json
import sys

AXES = ("correctness", "novelty", "delta", "strength", "significance", "literature")
LEVELS = ("unknown", "weak", "mid", "strong")
VERDICTS = ("none", "needs_work", "short_or_preprint", "journal")

RULES = {
    "en": [
        "Without a completed review, no verdict is issued and correctness is 'unknown'.",
        "One confirmed fatal finding caps the verdict at 'needs work'.",
        "Correctness cannot exceed 'mid' without an expert's check or a formal proof.",
        "If the closest prior work was not read, novelty cannot exceed 'mid'.",
        "'Short paper or preprint' needs correctness at least 'mid' and a concretely stated difference from the closest prior work.",
        "'Journal candidate' needs novelty 'strong', theorem strength at least 'mid', and that the prior-art attack did not break the claim.",
        "With a limited source list, the literature axis cannot exceed 'mid'.",
    ],
    "ja": [
        "査読が完了していなければ判定を出さず、正しさは「未確認」とする。",
        "確定した致命的な指摘が 1 つでもあれば、判定は「投稿前に要作業」までとする。",
        "専門家の点検か形式証明がなければ、正しさは「中」を超えない。",
        "最も近い先行研究を読んでいなければ、新規性は「中」を超えない。",
        "「短報または arXiv まで」には、正しさが「中」以上で、最も近い先行研究との差分が具体的に書けることを要する。",
        "「ジャーナル候補」には、新規性が「強」、定理の強さが「中」以上、先行研究への攻撃が破れなかったことを要する。",
        "出典を限定した調査では、文献調査の軸は「中」を超えない。",
    ],
}


def rank(level):
    return LEVELS.index(level)


def allowed_verdict(axes, facts):
    """Highest verdict the rules permit. axes: {axis: level}; facts: booleans/ints."""
    if not facts.get("review_done"):
        return "none"
    if facts.get("fatal_confirmed", 0) > 0:
        return "needs_work"
    best = "needs_work"
    if rank(axes["correctness"]) >= rank("mid") and facts.get("delta_stated"):
        best = "short_or_preprint"
    if (axes["novelty"] == "strong" and rank(axes["strength"]) >= rank("mid")
            and facts.get("attack_survived") and best == "short_or_preprint"):
        best = "journal"
    return best


def violations(ind):
    axes = {a["key"]: a["level"] for a in ind["axes"]}
    facts = ind.get("facts", {})
    errs = []
    for k in AXES:
        if k not in axes:
            errs.append(f"axis {k} missing")
        elif axes[k] not in LEVELS:
            errs.append(f"axis {k}: level must be one of {LEVELS}")
    if errs:
        return errs
    if not facts.get("review_done") and axes["correctness"] != "unknown":
        errs.append("correctness must be 'unknown' when the review is not done")
    if not facts.get("expert_or_formal_check") and rank(axes["correctness"]) > rank("mid"):
        errs.append("correctness above 'mid' needs an expert check or formal proof")
    if facts.get("closest_prior_unread") and rank(axes["novelty"]) > rank("mid"):
        errs.append("novelty above 'mid' while the closest prior work is unread")
    if facts.get("sources_limited", True) and rank(axes["literature"]) > rank("mid"):
        errs.append("literature above 'mid' with a limited source list")
    verdict = ind.get("verdict")
    if verdict not in VERDICTS:
        errs.append(f"verdict must be one of {VERDICTS}")
    elif rank_v(verdict) > rank_v(allowed_verdict(axes, facts)):
        errs.append(f"verdict {verdict!r} exceeds what the rules allow ({allowed_verdict(axes, facts)!r})")
    if not ind.get("changers"):
        errs.append("list what would change the verdict (changers)")
    return errs


def rank_v(v):
    return VERDICTS.index(v)


def main(argv=None):
    path = (argv or sys.argv[1:])[0]
    errs = violations(json.load(open(path, encoding="utf-8"))["indicator"])
    for e in errs:
        print("ERROR", e)
    if not errs:
        print("indicator consistent with the rules")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
