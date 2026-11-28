"""Shared reader layout for mathematical books and papers."""

import html
import json
import re
from pathlib import Path

COMMENT_ASSET = Path(__file__).with_name("assets") / "comment-layer.js"
COMMENT_MARK = "<!-- comment-layer -->"
DEFAULT_MATHJAX = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml-full.js"


def comment_script(lang=None, *, version=None, portable=False, extra=None):
    config = {key: value for key, value in
              (("lang", lang), ("version", version), ("portable", portable)) if value}
    config.update(extra or {})
    safe_config = json.dumps(config).replace("<", r"\u003c")
    cfg = f"<script>window.CommentLayer={safe_config};</script>" if config else ""
    return f'{COMMENT_MARK}{cfg}<script>\n{COMMENT_ASSET.read_text(encoding="utf-8")}</script>{COMMENT_MARK}'


def render_reading_page(title, language, toc, body, *, macros=None, mathjax=DEFAULT_MATHJAX,
                        mathjax_bundle=None, font_px=21, width_em=34, version=None):
    """Insert formatted reader content into the layout shared by the book and paper."""
    lang = "ja" if language == "ja" else "en"
    loader = f'<script defer src="{html.escape(mathjax)}"></script>' if mathjax_bundle is None else ""
    bundle = ""
    if mathjax_bundle is not None:
        bundle = "<script>\n" + re.sub(r"</script", r"<\\/script", mathjax_bundle, flags=re.I) + "\n</script>"
    values = {
        "TITLE": title, "LANG": html.escape(language), "NAV": toc, "BODY": body,
        "MATHJAX_LOADER": loader, "MATHJAX_BUNDLE": bundle,
        "MACROS": json.dumps(macros or {}).replace("<", r"\u003c"),
        "SIZE": str(font_px), "WIDTH": str(width_em),
        "COMMENTS": comment_script(lang, version=version, portable=mathjax_bundle is not None),
    }
    labels = LABELS[lang]
    template = re.sub(r"\{\{(\w+)\}\}", lambda m: html.escape(labels[m[1]]), PAGE)
    body = body.replace("{{appendix}}", html.escape(labels["appendix"])).replace("{{proof}}", html.escape(labels["proof"]))
    toc = toc.replace("{{appendix}}", html.escape(labels["appendix"]))
    values.update(BODY=body, NAV=toc)
    return re.sub(r"%([A-Z_]+)%", lambda m: values[m[1]], template)


LABELS = {'ja': {'toc': '目次', 'smaller': '文字を小さく', 'larger': '文字を大きく', 'narrower': '行を短く', 'wider': '行を長く', 'theme': '明暗', 'comments': 'コメント', 'copy': 'クリップボードにコピー', 'copied': 'コピーしました', 'add': 'コメントする', 'placeholder': 'コメント', 'save': '追加', 'cancel': '取り消し', 'none': 'コメントはまだありません．本文を選ぶとボタンが出ます．', 'delete': '削除', 'clear': '全部消す', 'close': '閉じる', 'confirm': 'コメントを全部消しますか？', 'nocomment': '(コメントなし)', 'proof': '証明', 'appendix': '付録'},
          'en': {'toc': 'Contents', 'smaller': 'Smaller text', 'larger': 'Larger text', 'narrower': 'Shorter lines', 'wider': 'Longer lines', 'theme': 'Light/dark', 'comments': 'Comments', 'copy': 'Copy to clipboard', 'copied': 'Copied', 'add': 'Comment', 'placeholder': 'Comment', 'save': 'Add', 'cancel': 'Cancel', 'none': 'No comments yet. Select text to add one.', 'delete': 'Delete', 'clear': 'Clear all', 'close': 'Close', 'confirm': 'Delete all comments?', 'nocomment': '(no comment)', 'proof': 'Proof', 'appendix': 'Appendix'}}

PAGE = r"""<!doctype html><html lang="%LANG%"><head><meta charset="utf-8"><title>%TITLE%</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>
MathJax = {tex: {inlineMath: [['$','$'],['\\(','\\)']], displayMath: [['\\[','\\]'],['$$','$$']],
  processEnvironments: true, tags: 'ams', macros: %MACROS%},
  options: {skipHtmlTags: ['script','noscript','style','textarea','code']},
  startup: {pageReady() { return MathJax.startup.defaultPageReady().then(() => {
    for (const it of MathJax.startup.document.math) {
      const m = it.math, root = it.typesetRoot; if (!root) continue;
      root.dataset.tex = !it.display ? '$' + m + '$' : (m.startsWith('\\begin') ? m : '\\[' + m + '\\]');
    }});}}};
</script>
%MATHJAX_LOADER%
<style>
:root{--fs:%SIZE%px;--w:%WIDTH%em;--bg:#fbfaf7;--fg:#1d1d1f;--muted:#76736d;--rule:#e2ddd3;--box:#f3f0e8;--accent:#8a5a00;--link:#1f5fa8;--hl:#fff1b8}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1b1b1d;--fg:#e8e6e1;--muted:#9a968e;--rule:#3a3936;--box:#25242a;--accent:#e0b060;--link:#8ab4f8;--hl:#5a4a10}}
:root[data-theme="dark"]{--bg:#1b1b1d;--fg:#e8e6e1;--muted:#9a968e;--rule:#3a3936;--box:#25242a;--accent:#e0b060;--link:#8ab4f8;--hl:#5a4a10}
html{background:var(--bg)}
body{margin:0;color:var(--fg);background:var(--bg);font-family:"Noto Serif","Source Serif 4","Georgia","Times New Roman","Hiragino Mincho ProN","Yu Mincho","Noto Serif JP","Noto Serif CJK JP",serif;font-size:var(--fs);line-height:1.95}
main{max-width:var(--w);margin:0 auto;padding:4.5em 1em 40vh}
h1{font-size:1.5em;line-height:1.5;margin:.5em 0 1.5em}
h2{font-size:1.2em;margin:2.5em 0 1em;padding-bottom:.2em;border-bottom:1px solid var(--rule)}
p{margin:.55em 0}
a{color:var(--link);text-decoration:none} a:hover{text-decoration:underline}
.card{margin:1.6em 0;padding:.6em 1em;border-left:4px solid var(--rule);background:var(--box);border-radius:4px}
.card:target{outline:2px solid var(--accent)}
.k-theorem,.k-proposition,.k-corollary{border-left-color:var(--accent)}
.card header{font-weight:bold;margin-bottom:.2em}
.kname{margin-right:.3em}
.cid{float:right;font:12px/1.6 ui-monospace,monospace;color:var(--muted);font-weight:normal;user-select:none}
.proof summary{cursor:pointer;color:var(--muted);font-size:.9em}
.proof[open] summary{margin-bottom:.4em}
.proof{margin-top:.5em}
.prose{margin:1.2em 0}
.cite{color:var(--muted);font-size:.9em}
ol,ul{padding-left:1.4em}
li.lab{list-style:none}
mjx-container[display="true"]{overflow-x:auto;overflow-y:hidden}
#bar{position:fixed;top:0;left:0;right:0;z-index:5;display:flex;gap:.4em;align-items:center;padding:.4em .8em;background:var(--bg);border-bottom:1px solid var(--rule);font:14px system-ui,sans-serif}
#bar button{font:13px system-ui,sans-serif;padding:.2em .6em;border:1px solid var(--rule);background:var(--box);color:var(--fg);border-radius:4px;cursor:pointer}
#bar .sp{flex:1}
#toc{display:none;position:fixed;top:2.6em;left:.8em;z-index:6;max-height:70vh;overflow:auto;background:var(--bg);border:1px solid var(--rule);padding:.5em .8em;font:14px/1.8 system-ui,sans-serif}
#toc a{display:block}
#toc .toc-chapter{font-weight:650;margin-top:.45em}
#toc .toc-section{padding-inline-start:1em}
[id]{scroll-margin-top:4em}
@media(max-width:600px){#bar{flex-wrap:wrap}#bar button{min-height:36px}#toc{top:5em;max-width:90vw}main{padding:7em .75em 40vh}.card{padding:.5em .65em}[id]{scroll-margin-top:7em}}
@media print{#bar,#toc,#cl-add,#cl-box{display:none!important}main{padding-top:0;max-width:none}.cid{display:none}}
mark.cm{background:var(--hl);color:inherit}
</style></head><body>
<div id="bar"><button id="btoc">{{toc}}</button><button id="bsm" title="{{smaller}}">A−</button><button id="blg" title="{{larger}}">A＋</button>
<button id="bnr" title="{{narrower}}">⇤⇥−</button><button id="bwd" title="{{wider}}">⇤⇥＋</button><button id="bth">{{theme}}</button>
<span class="sp"></span><button id="bcom">{{comments}} <span id="ccount">0</span></button><button id="bcopy">{{copy}}</button></div>
<nav id="toc">%NAV%</nav>
<main><h1>%TITLE%</h1>
%BODY%
</main>
<script>
(function(){
  const root=document.documentElement, store={get(k){try{return localStorage.getItem(k)}catch(e){return null}},set(k,v){try{localStorage.setItem(k,v)}catch(e){}}};
  const key='reader:'+location.pathname;
  let fs=parseFloat(store.get(key+':fs'))||%SIZE%, w=parseFloat(store.get(key+':w'))||%WIDTH%;
  const th=store.get(key+':theme'); if(th) root.dataset.theme=th;
  function apply(){root.style.setProperty('--fs',fs+'px');root.style.setProperty('--w',w+'em');store.set(key+':fs',fs);store.set(key+':w',w);}
  apply();
  const $=id=>document.getElementById(id);
  $('bsm').onclick=()=>{fs=Math.max(14,fs-1);apply()}; $('blg').onclick=()=>{fs=Math.min(34,fs+1);apply()};
  $('bnr').onclick=()=>{w=Math.max(20,w-2);apply()}; $('bwd').onclick=()=>{w=Math.min(60,w+2);apply()};
  $('bth').onclick=()=>{const d=root.dataset.theme==='dark'||(!root.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);root.dataset.theme=d?'light':'dark';store.set(key+':theme',root.dataset.theme)};
  $('btoc').onclick=()=>{const t=$('toc');t.style.display=t.style.display==='block'?'none':'block'};
  $('toc').onclick=()=>{$('toc').style.display='none'};
})();
</script>%COMMENTS%%MATHJAX_BUNDLE%</body></html>"""
