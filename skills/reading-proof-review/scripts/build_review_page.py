#!/usr/bin/env python3
"""Build the single-file proof-review page from a spec directory.

Usage:
  build_review_page.py SPEC_DIR --out PAGE.html [--lang en|ja] [--katex-dir DIR] [--fetch-katex] [--template FILE]

SPEC_DIR holds steps.json (the ledger), bodies.json (per-step l1/l2/l3 HTML), review.json (panel,
findings, prior-art table, indicator, summary) and, optionally, demo.html (a self-contained snippet
that may carry its own <script>). Fields ending in _html, the step bodies and finding "detail"
are inserted as HTML (math is written as <span class="m">TeX</span> or <div class="d">TeX</div>);
every other text field is escaped. The page is a local file; nothing is published.
"""
import argparse
import base64
import datetime
import html
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_ledger  # noqa: E402
import indicator  # noqa: E402

E = html.escape

LABELS = {
 "en": dict(
  toc="Contents", display="Display", btn_all="Open all", btn_none="Close all", btn_key="Open key steps only",
  caution="This is a reading aid for work under review. 'No gap found' means none was found within the stated scope; it is not a proof of correctness. Novelty is judged only against the sources actually read. Nothing here is a formal proof or a journal's opinion.",
  local="A single local file; it is not published anywhere.",
  h_summary="Summary", h_intro="The result", h_spine="Proof spine", h_compare="Key versus non-key steps", h_demo="Try it",
  h_review="Review", h_prior="Relation to prior work", h_indicator="Viability indicator", h_glossary="Glossary",
  spine_lead="Each step shows one line (always visible), the key reasoning (folded) and the line-by-line proof (folded again). Key steps are open to the key reasoning.",
  h_diagram="Dependency diagram", diagram_hint="An arrow means 'uses'. Orange is key, purple semi-key, grey standard. Click a box to jump to the step.",
  legend_key="key", legend_semi="semi-key", legend_standard="standard",
  compare_lead="Key = necessary for the theorem and not in the literature as such (by the work's own claim). Semi-key = necessary but a combination of known methods. Standard = in the literature as such.",
  th_class="Class / id", th_content="Content", th_role="Role", th_origin="Origin", th_risk="Remaining risk", th_evidence="Evidence of checking",
  tier_key="key", tier_semi="semi-key", tier_standard="standard",
  origin_inherited="inherited from prior work", origin_standard="standard", origin_adapted="known method, adapted", origin_new="new (as claimed)",
  meta_loc="Source", meta_origin="Origin", meta_deps="Uses", none="none", why_tier="Why this class",
  l2="Key reasoning", l3="Line-by-line proof", step_findings="Findings on this step (%d)",
  sev_fatal="fatal", sev_major="major", sev_minor="minor", sev_form="form",
  st_confirmed="confirmed", st_suspected="suspected", st_unchecked="unchecked",
  review_conclusion="Conclusion of the review", n_findings="%d findings: fatal %d, major %d, minor %d, form %d.",
  review_reading="How to read this", review_reading_text="'No gap found' means none was found within the scope in the table. An adversarial reader can only report holes it finds; it cannot show that none exist. Reviews by language models are not an expert's check or a formal proof.",
  h_panel="Panel and scope", th_view="Viewpoint", th_who="Who", th_scope="Scope checked", th_result="Result",
  h_mychecks="Checks I ran myself", h_findings="Findings, most serious first", findings_hint="'Confirmed' means a counterexample or a reproducible calculation exists; 'suspected' means reasoning only.",
  f_target="Target", f_from="Raised by", f_ruling="Ruling", f_all="whole work", f_evidence="Evidence",
  th_prior="Prior work", th_op="Operator placement", th_hyp="Assumptions and conclusions", th_overlap="Overlap with the key steps", th_state="What was checked",
  prior_hole="Largest unchecked gap", prior_uncited="Candidates raised by reviewers (outside the source list, bibliographic details unchecked)",
  prior_admitted="What the work itself already concedes",
  verdict="Verdict", axes_h="Axes", rules_h="Rules for the verdict", changers_h="What would change this verdict",
  indicator_note="This is an aid to judgment, not a prediction of acceptance and not a certificate of correctness. Read the reason for each axis.",
  lvl_strong="strong", lvl_mid="mid", lvl_weak="weak", lvl_unknown="unknown",
  ax_correctness="Evidence of correctness", ax_novelty="Novelty of the key part", ax_delta="Difference from the closest prior work",
  ax_strength="Strength of the theorem", ax_significance="Significance and applications", ax_literature="Completeness of the literature check",
  v_none="no verdict", v_needs_work="needs work before submission", v_short_or_preprint="short paper or preprint", v_journal="journal candidate",
  generated="Generated",
 ),
 "ja": dict(
  toc="目次", display="表示", btn_all="すべて開く", btn_none="すべて閉じる", btn_key="キーだけ開く（既定）",
  caution="これは査読中の研究の読解資料です。「穴が見つからなかった」は、記した範囲で見つからなかったという意味で、正しさの証明ではありません。新規性は、実際に読んだ資料の範囲でしか判断していません。形式証明でも、雑誌の判断でもありません。",
  local="手元で開く単一ファイルです。ネット上には公開されていません。",
  h_summary="結論の要約", h_intro="何を示した研究か", h_spine="証明の骨格", h_compare="キーと標準の比較", h_demo="手を動かす",
  h_review="査読", h_prior="先行研究との違い", h_indicator="論文になりそうかの指標", h_glossary="用語メモ",
  spine_lead="各ステップは「1 行説明（常に表示）→ 要点（畳み）→ 全行の証明（さらに畳み）」の 3 段です。キーは要点まで開いてあります。",
  h_diagram="依存関係図", diagram_hint="矢印は「使う」。オレンジ＝キー、紫＝準キー、灰＝標準。クリックでそのステップへ飛びます。",
  legend_key="キー", legend_semi="準キー", legend_standard="標準",
  compare_lead="キー＝定理に必要で、かつ先行研究にそのままは無い（その研究自身の主張による）。準キー＝必要だが既知の手法の組み合わせ。標準＝文献にそのまま載る。",
  th_class="分類・id", th_content="内容", th_role="役割", th_origin="由来", th_risk="残るリスク", th_evidence="確認の証拠",
  tier_key="キー", tier_semi="準キー", tier_standard="標準",
  origin_inherited="先行研究から継承", origin_standard="標準", origin_adapted="既知の手法の改変", origin_new="新規（その研究の主張）",
  meta_loc="原稿", meta_origin="由来", meta_deps="使うもの", none="なし", why_tier="分類の理由",
  l2="要点", l3="全行の証明", step_findings="このステップへの査読の指摘（%d 件）",
  sev_fatal="致命的", sev_major="要修正", sev_minor="軽微", sev_form="表現",
  st_confirmed="確定", st_suspected="疑い", st_unchecked="未確認",
  review_conclusion="査読の結論", n_findings="指摘は全 %d 件：致命的 %d、要修正 %d、軽微 %d、表現 %d。",
  review_reading="この結果の読み方", review_reading_text="「穴が見つからなかった」は、表の範囲で見つからなかったという意味です。敵対的な視点が出せるのは見つけた穴だけで、穴が無いことの証明にはなりません。言語モデルによる査読は、専門家の点検でも形式証明でもありません。",
  h_panel="査読の体制と範囲", th_view="視点", th_who="担当", th_scope="検査の範囲", th_result="結果",
  h_mychecks="私が自分で行った確認", h_findings="指摘の一覧（重大な順）", findings_hint="「確定」は反例か再現できる計算があるもの、「疑い」は推論のみのものです。",
  f_target="対象", f_from="出した視点", f_ruling="私の裁定", f_all="全体", f_evidence="根拠",
  th_prior="先行研究", th_op="方程式・対象の置き方", th_hyp="仮定と結論", th_overlap="キーとの重なり", th_state="確認の状態",
  prior_hole="未確認の最大の穴", prior_uncited="査読者が挙げた候補（出典の範囲外・書誌は未確認）",
  prior_admitted="その研究自身が既に認めていること",
  verdict="判定", axes_h="軸", rules_h="判定の規則", changers_h="この判定を変える項目",
  indicator_note="これは判断の補助で、採否の予測でも正しさの認証でもありません。軸ごとの根拠を読んで判断してください。",
  lvl_strong="強", lvl_mid="中", lvl_weak="弱", lvl_unknown="未確認",
  ax_correctness="正しさの証拠", ax_novelty="キー部分の新規性", ax_delta="最も近い先行研究との差分",
  ax_strength="定理の強さ", ax_significance="意義・応用", ax_literature="文献調査の完全性",
  v_none="判定なし", v_needs_work="投稿前に要作業", v_short_or_preprint="短報または arXiv まで", v_journal="ジャーナル候補",
  generated="生成日",
 ),
}

SEV_CLASS = {"fatal": "sev-c", "major": "sev-m", "minor": "sev-n", "form": "sev-e"}
SEV_ORDER = {"fatal": 0, "major": 1, "minor": 2, "form": 3}
LVL_CLASS = {"strong": "l-strong", "mid": "l-mid", "weak": "l-weak", "unknown": "l-unk"}
TIER_COLOR = {"key": "#c2410c", "semi": "#6b4fbb", "standard": "#5b6677"}


def find_katex(explicit=None):
    import os
    from fetch_katex import default_dest
    cands = []
    if explicit:
        cands.append(pathlib.Path(explicit))
    if os.environ.get("KATEX_DIR"):
        cands.append(pathlib.Path(os.environ["KATEX_DIR"]))
    cands.append(default_dest())
    try:
        dist = subprocess.run(["kpsewhich", "-var-value", "TEXMFDIST"], capture_output=True, text=True, timeout=10).stdout.strip()
        if dist:
            cands += sorted(pathlib.Path(dist).glob("doc/support/*/*/katex"))
    except (OSError, subprocess.SubprocessError):
        pass
    for c in cands:
        if (c / "katex.min.js").exists() and (c / "katex.min.css").exists():
            return c
    return None


def katex_assets(kdir):
    if not kdir:
        return "", "", []
    css = (kdir / "katex.min.css").read_text(encoding="utf-8")
    present = {p.stem for p in (kdir / "fonts").glob("*.woff2")}

    def font(m):
        p = kdir / "fonts" / (m.group(1) + ".woff2")
        return "url(data:font/woff2;base64,%s)" % (base64.b64encode(p.read_bytes()).decode() if p.exists() else "")
    css = re.sub(r"url\(fonts/([A-Za-z0-9_-]+)\.woff2\)", font, css)
    css = re.sub(r",url\(fonts/[^)]*\)\s*format\('woff'\)", "", css)
    css = re.sub(r",url\(fonts/[^)]*\)\s*format\('truetype'\)", "", css)
    css = re.sub(r"src:url\(fonts/[^)]*\.eot\);src:url\(fonts/[^)]*#iefix\)\s*format\('embedded-opentype'\),", "src:", css)
    wanted = ["KaTeX_Main-Regular", "KaTeX_Math-Italic", "KaTeX_Main-Bold", "KaTeX_AMS-Regular", "KaTeX_Caligraphic-Regular", "KaTeX_Main-Italic"]
    missing = [w for w in wanted if w not in present]
    return css, (kdir / "katex.min.js").read_text(encoding="utf-8"), missing


def diagram(steps, target, by_step_findings):
    S = {s["id"]: s for s in steps}
    depth = {}

    def dp(i):
        if i not in depth:
            ds = [dp(x) for x in S[i]["deps"] if x != target]
            depth[i] = (max(ds) + 1) if ds else 0
        return depth[i]
    for i in S:
        if i != target:
            dp(i)
    depth[target] = max([d for d in depth.values()] or [0]) + 1
    cols = {}
    for i, d in depth.items():
        cols.setdefault(d, []).append(i)
    BW, BH, GX, GY = 112, 34, 52, 14
    pos = {i: (20 + d * (BW + GX), 16 + r * (BH + GY)) for d, ids in cols.items() for r, i in enumerate(ids)}
    W = 40 + (max(cols) + 1) * (BW + GX)
    H = 30 + max(len(v) for v in cols.values()) * (BH + GY)
    out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#9aa4b5"/></marker></defs>' % (W, H)]
    for i in S:
        for x in S[i]["deps"]:
            x1, y1 = pos[x]
            x2, y2 = pos[i]
            out.append('<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="#c3cad6" stroke-width="1.2" marker-end="url(#ar)"/>' % (
                x1 + BW, y1 + BH / 2, x1 + BW + GX / 2, y1 + BH / 2, x2 - GX / 2, y2 + BH / 2, x2, y2 + BH / 2))
    for i, (x, y) in pos.items():
        fill = "#1d2430" if i == target else TIER_COLOR[S[i]["tier"]]
        out.append('<a href="#%s"><rect x="%d" y="%d" width="%d" height="%d" rx="7" fill="%s"/><text x="%d" y="%d" fill="#fff" font-size="12.5" font-weight="700" text-anchor="middle">%s</text><text x="%d" y="%d" fill="#fff" font-size="10" text-anchor="middle" opacity=".9">%s</text></a>' % (
            "intro" if i == target else "step-" + E(i), x, y, BW, BH, fill, x + BW / 2, y + 14, E(i), x + BW / 2, y + 27, E(S[i]["title"][:11])))
        n = len(by_step_findings.get(i, []))
        if n:
            out.append('<circle cx="%d" cy="%d" r="8" fill="#fff" stroke="#a32020"/><text x="%d" y="%.1f" font-size="10" text-anchor="middle" fill="#a32020" font-weight="700">%d</text>' % (x + BW - 4, y + 2, x + BW - 4, y + 5.5, n))
    out.append("</svg>")
    return "".join(out)


def build(spec_dir, lang, katex_dir, template_path):
    L = LABELS[lang]
    spec = pathlib.Path(spec_dir)
    meta, steps = check_ledger.load(spec / "steps.json")
    target = meta.get("target", "T")
    errors, _ = check_ledger.check(meta, steps)
    if errors:
        raise SystemExit("ledger errors:\n" + "\n".join(errors))
    bodies = json.load(open(spec / "bodies.json", encoding="utf-8"))
    R = json.load(open(spec / "review.json", encoding="utf-8"))
    S = {s["id"]: s for s in steps}
    F = {f["id"]: f for f in R["findings"]}
    by_step = {}
    for f in R["findings"]:
        for st in f.get("steps", []):
            if st not in S:
                raise SystemExit(f"finding {f['id']} refers to unknown step {st}")
            by_step.setdefault(st, []).append(f["id"])

    def link(i):
        return '<a href="#%s">%s</a>' % ("intro" if i == target else "step-" + E(i), E(i))

    tier_name = {k: L["tier_" + k] for k in TIER_COLOR}
    origin_name = {k: L["origin_" + k] for k in check_ledger.ORIGINS}

    def sev_tag(sev):
        return '<span class="tag %s">%s</span>' % (SEV_CLASS[sev], L["sev_" + sev])

    def status_text(f):
        return f.get("status_note") or L["st_" + f["status"]]

    # steps
    groups = R.get("groups") or [["", [s["id"] for s in steps if s["id"] != target]]]
    grouped = {i for _, ids in groups for i in ids}
    rest = [s["id"] for s in steps if s["id"] != target and s["id"] not in grouped]
    if rest:
        groups = groups + [["", rest]]
    cards = []
    for title, ids in groups:
        if title:
            cards.append("<h3>%s</h3>" % E(title))
        for i in ids:
            s = S[i]
            b = bodies.get(i, {})
            t = s["tier"]
            cls = {"key": "t-keyc", "semi": "t-semic", "standard": ""}[t]
            fl = "".join(' <a class="tag %s" href="#find-%s">%s</a>' % (SEV_CLASS[F[x]["sev"]], x, x) for x in by_step.get(i, []))
            cards.append('<details class="step %s" id="step-%s"><summary><span class="tag t-%s">%s</span><b>%s</b>　%s%s</summary>' % (cls, E(i), t, tier_name[t], E(i), E(s["title"]), fl))
            deps = "、".join(link(x) for x in s["deps"]) or L["none"]
            cards.append('<div class="meta">%s: %s　/　%s: %s　/　%s: %s</div>' % (L["meta_loc"], E(s["loc"]), L["meta_origin"], origin_name[s["origin"]], L["meta_deps"], deps))
            cards.append('<div class="l1">%s</div>' % b.get("l1", E(s["statement"])))
            if s.get("why_tier"):
                cards.append('<div class="meta">%s: %s</div>' % (L["why_tier"], E(s["why_tier"])))
            if b.get("l2"):
                cards.append('<details class="l2"><summary>%s</summary>%s</details>' % (L["l2"], b["l2"]))
            if b.get("l3"):
                cards.append('<details class="l3"><summary>%s</summary>%s</details>' % (L["l3"], b["l3"]))
            if by_step.get(i):
                cards.append('<details class="l3"><summary>%s</summary><ul>%s</ul></details>' % (L["step_findings"] % len(by_step[i]), "".join('<li><a href="#find-%s">%s</a>　%s</li>' % (x, x, E(F[x]["short"])) for x in by_step[i])))
            cards.append("</details>")

    # compare
    rows = []
    sr = R.get("step_review", {})
    for t in ("key", "semi", "standard"):
        for s in steps:
            if s["id"] == target or s["tier"] != t:
                continue
            r = sr.get(s["id"], {})
            cl = {"key": "k", "semi": "s", "standard": ""}[t]
            rows.append('<tr class="%s"><td><span class="tag t-%s">%s</span>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                cl, t, tier_name[t], link(s["id"]), E(s["title"]), E(s.get("role", "")), origin_name[s["origin"]], E(r.get("risk", "—")), E(r.get("evidence", "—"))))
    compare = "<p>%s</p><table><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>%s</table>" % (
        L["compare_lead"], L["th_class"], L["th_content"], L["th_role"], L["th_origin"], L["th_risk"], L["th_evidence"], "".join(rows))
    if R.get("compare_note_html"):
        compare += '<div class="card">%s</div>' % R["compare_note_html"]

    # review
    cnt = {k: sum(1 for f in R["findings"] if f["sev"] == k) for k in SEV_ORDER}
    panel = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (E(p["name"]), E(p["who"]), E(p["scope"]), E(p["result"])) for p in R["panel"])
    fl = []
    for f in sorted(R["findings"], key=lambda f: (SEV_ORDER[f["sev"]], f["id"])):
        st = "、".join(link(x) for x in f.get("steps", [])) or L["f_all"]
        fl.append('<details class="step" id="find-%s"><summary>%s<span class="tag t-info">%s</span><b>%s</b>　%s</summary><div class="meta">%s: %s　/　%s: %s</div><div class="l1">%s</div>%s</details>' % (
            E(f["id"]), sev_tag(f["sev"]), E(status_text(f)), E(f["id"]), E(f["short"]), L["f_target"], st, L["f_from"], E("、".join(f["from"])), f["detail"],
            "".join(('<div class="meta">%s: %s</div>' % (L[k2], E(f[k1]))) for k1, k2 in (("evidence", "f_evidence"), ("ruling", "f_ruling")) if f.get(k1))))
    review = ('<div class="card %s"><p><b>%s</b>　%s</p><p>%s</p></div><div class="card warn"><p><b>%s</b>　%s</p></div>'
              '<h3>%s</h3><table><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>%s</table>') % (
        "good" if cnt["fatal"] == 0 else "bad", L["review_conclusion"], E(R["review_conclusion"]),
        L["n_findings"] % (len(R["findings"]), cnt["fatal"], cnt["major"], cnt["minor"], cnt["form"]),
        L["review_reading"], L["review_reading_text"], L["h_panel"], L["th_view"], L["th_who"], L["th_scope"], L["th_result"], panel)
    if R.get("my_checks"):
        review += "<h3>%s</h3><ul>%s</ul>" % (L["h_mychecks"], "".join("<li>%s</li>" % E(x) for x in R["my_checks"]))
    review += '<h3>%s</h3><p class="lab">%s</p>%s' % (L["h_findings"], L["findings_hint"], "\n".join(fl))

    # prior
    pr = "".join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (E(p["name"]), E(p["op"]), E(p["hyp"]), E(p["overlap"]), E(p["state"])) for p in R["prior"])
    prior = "<table><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>%s</table>" % (L["th_prior"], L["th_op"], L["th_hyp"], L["th_overlap"], L["th_state"], pr)
    if R.get("prior_hole"):
        prior += '<div class="card warn"><p><b>%s</b>　%s</p></div>' % (L["prior_hole"], E(R["prior_hole"]))
    if R.get("uncited"):
        prior += "<h3>%s</h3><ul>%s</ul>" % (L["prior_uncited"], "".join("<li>%s</li>" % E(x) for x in R["uncited"]))
    if R.get("admitted"):
        prior += "<h3>%s</h3><ul>%s</ul>" % (L["prior_admitted"], "".join("<li>%s</li>" % E(x) for x in R["admitted"]))

    # indicator
    ind = R["indicator"]
    verrs = indicator.violations(ind)
    if verrs:
        raise SystemExit("indicator violates the rules:\n" + "\n".join(verrs))
    ax = "".join('<div class="axis"><div><b>%s</b></div><div><span class="lvl %s">%s</span></div><div>%s</div></div>' % (
        L["ax_" + a["key"]], LVL_CLASS[a["level"]], L["lvl_" + a["level"]], E(a["why"])) for a in ind["axes"])
    indicator_html = ('<div class="card key"><p class="verdict">%s: %s</p><p>%s</p></div><h3>%s</h3>%s<h3>%s</h3><ul>%s</ul><h3>%s</h3><ol>%s</ol><div class="card warn"><p>%s</p></div>') % (
        L["verdict"], L["v_" + ind["verdict"]], E(ind["verdict_why"]), L["axes_h"], ax, L["rules_h"],
        "".join("<li>%s</li>" % E(r) for r in indicator.RULES[lang]), L["changers_h"], "".join("<li>%s</li>" % E(c) for c in ind["changers"]), L["indicator_note"])

    # body
    sections = [("summary", L["h_summary"], R["summary_html"]), ("intro", L["h_intro"], R.get("intro_html", ""))]
    spine = ""
    if R.get("key_ideas_html"):
        spine += '<div class="card key">%s</div>' % R["key_ideas_html"]
    spine += "<h3>%s</h3><p class=\"lab\">%s</p><div class=\"flow2\">%s</div><div class=\"legend\"><i style=\"background:#c2410c\"></i>%s<i style=\"background:#6b4fbb\"></i>%s<i style=\"background:#5b6677\"></i>%s</div>" % (
        L["h_diagram"], L["diagram_hint"], diagram(steps, target, by_step), L["legend_key"], L["legend_semi"], L["legend_standard"])
    spine += "<p class=\"lab\">%s</p>%s" % (L["spine_lead"], "\n".join(cards))
    sections.append(("spine", L["h_spine"], spine))
    sections.append(("compare", L["h_compare"], compare))
    extra_script = ""
    demo = spec / "demo.html"
    if demo.exists():
        d = demo.read_text(encoding="utf-8")
        scripts = re.findall(r"<script>[\s\S]*?</script>", d)
        extra_script = "\n".join(scripts)
        sections.append(("demo", L["h_demo"], re.sub(r"<script>[\s\S]*?</script>", "", d)))
    sections += [("review", L["h_review"], review), ("prior", L["h_prior"], prior), ("indicator", L["h_indicator"], indicator_html)]
    if R.get("glossary"):
        sections.append(("glossary", L["h_glossary"], "<dl>%s</dl>" % "".join("<dt>%s</dt><dd>%s</dd>" % (g[0], g[1]) for g in R["glossary"])))
    body = ['<h1>%s</h1><p class="sub">%s<br><span class="lab">%s　%s %s</span></p>' % (
        E(R["title"]), E(R.get("subtitle", "")), L["local"], L["generated"], datetime.date.today().isoformat()),
        '<div class="card warn"><p>%s</p></div>' % L["caution"]]
    for n, (sid, head, content) in enumerate(sections):
        body.append('<h2 id="%s">%d. %s</h2>%s' % (sid, n, E(head), content))

    tpl = pathlib.Path(template_path).read_text(encoding="utf-8")
    css, js, missing = katex_assets(katex_dir)
    page = (tpl.replace("{{BODY}}", "\n".join(body)).replace("{{TITLE}}", E(R["title"])).replace("{{LANG}}", lang)
            .replace("{{EXTRA_SCRIPT}}", extra_script).replace("/*KATEX_CSS*/", css).replace("/*KATEX_JS*/", js))
    page = re.sub(r"\{\{L:([a-z_]+)\}\}", lambda m: E(L[m.group(1)]), page)
    return page, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--lang", default="en", choices=sorted(LABELS))
    ap.add_argument("--katex-dir")
    ap.add_argument("--fetch-katex", action="store_true", help="download the pinned KaTeX (MIT) into the cache when none is found")
    ap.add_argument("--template", default=str(HERE.parent / "assets/review-page-template.html"))
    a = ap.parse_args(argv)
    kdir = find_katex(a.katex_dir)
    if not kdir and a.fetch_katex:
        from fetch_katex import fetch
        kdir = fetch()
    page, missing = build(a.spec_dir, a.lang, kdir, a.template)
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
