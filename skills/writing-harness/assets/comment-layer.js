/* Comment layer for reading pages.
 * Select text, add a short comment, and copy all comments to the clipboard as
 *   Where
 *   「quote」
 *   → comment
 * so they can be pasted back to an agent. Formulas are quoted as their TeX source
 * (MathJax 3 or KaTeX). Comments live in sessionStorage of this tab only.
 *
 * Use: inline or load this file at the end of <body>. Optional config before it:
 *   window.CommentLayer = {lang: 'ja'}
 * If the page has buttons #bcom (open list, may contain #ccount) and #bcopy, they are
 * used; otherwise a small floating bar is added. "Where" is the nearest ancestor with
 * data-card (with its .kname text) or data-comment-label, else the nearest preceding
 * heading, else the document title.
 */
(function () {
  'use strict';
  const cfg = window.CommentLayer || {};
  const lang = (cfg.lang || document.documentElement.lang || 'en').slice(0, 2);
  const L = Object.assign({
    ja: {comments: 'コメント', copy: 'クリップボードにコピー', copied: 'コピーしました', add: 'コメントする',
         placeholder: 'コメント', save: '追加', cancel: '取り消し', del: '削除', clear: '全部消す', close: '閉じる',
         none: 'コメントはまだありません．本文を選ぶとボタンが出ます．', confirm: 'コメントを全部消しますか？',
         nocomment: '(コメントなし)'},
    en: {comments: 'Comments', copy: 'Copy to clipboard', copied: 'Copied', add: 'Comment',
         placeholder: 'Comment', save: 'Add', cancel: 'Cancel', del: 'Delete', clear: 'Clear all', close: 'Close',
         none: 'No comments yet. Select text to add one.', confirm: 'Delete all comments?',
         nocomment: '(no comment)'}
  }[lang === 'ja' ? 'ja' : 'en'], cfg.labels || {});

  const css = `
#cl-add{position:absolute;display:none;z-index:2147483600;font:13px system-ui,sans-serif;padding:.25em .7em;border:1px solid #8a5a00;background:#8a5a00;color:#fff;border-radius:4px;cursor:pointer}
#cl-box{display:none;position:fixed;right:1em;bottom:3.2em;z-index:2147483601;width:min(30em,90vw);max-height:60vh;overflow:auto;background:Canvas;color:CanvasText;border:1px solid #bbb;border-radius:6px;padding:.6em .8em;font:14px/1.6 system-ui,sans-serif;box-shadow:0 2px 12px rgba(0,0,0,.2)}
#cl-box textarea{width:100%;box-sizing:border-box;min-height:4em;font:14px system-ui,sans-serif;background:Canvas;color:CanvasText;border:1px solid #bbb}
#cl-box button,#cl-bar button{font:13px system-ui,sans-serif;padding:.2em .6em;border:1px solid #bbb;background:ButtonFace;color:ButtonText;border-radius:4px;cursor:pointer}
#cl-list .c{border-top:1px solid #ddd;padding:.3em 0}
#cl-box .q{opacity:.7}
#cl-bar{position:fixed;right:1em;bottom:1em;z-index:2147483601;display:flex;gap:.4em}
mjx-container.cl-msel,.katex.cl-msel{background:Highlight;color:HighlightText;border-radius:2px}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  const el = (tag, attrs, html) => { const e = document.createElement(tag); Object.assign(e, attrs || {}); if (html) e.innerHTML = html; return e; };
  let bOpen = document.getElementById('bcom'), bCopy = document.getElementById('bcopy'), count = document.getElementById('ccount');
  if (!bOpen || !bCopy) {
    const bar = el('div', {id: 'cl-bar'});
    bOpen = el('button', {}, `${L.comments} <span id="cl-count">0</span>`); bCopy = el('button', {textContent: L.copy});
    bar.append(bOpen, bCopy); document.body.appendChild(bar); count = bar.querySelector('#cl-count');
  }
  const add = el('button', {id: 'cl-add', textContent: L.add});
  const box = el('div', {id: 'cl-box'}, `<div id="cl-edit" style="display:none"><div class="q" id="cl-quote"></div>
<textarea id="cl-text" placeholder="${L.placeholder}"></textarea><button id="cl-save">${L.save}</button> <button id="cl-cancel">${L.cancel}</button></div>
<div id="cl-list"></div><p><button id="cl-clear">${L.clear}</button> <button id="cl-close">${L.close}</button></p>`);
  document.body.append(add, box);
  const $ = id => document.getElementById(id);

  const key = 'comments:' + location.pathname;
  let comments = []; try { comments = JSON.parse(sessionStorage.getItem(key) || '[]'); } catch (e) {}
  const save = () => { try { sessionStorage.setItem(key, JSON.stringify(comments)); } catch (e) {} };
  let pending = null;

  // TeX source of a rendered formula.
  function mathjaxTex(m) {
    if (m.dataset.tex) return m.dataset.tex;
    try {
      for (const it of MathJax.startup.document.math) {
        if (!it.typesetRoot) continue;
        const t = it.math;
        it.typesetRoot.dataset.tex = !it.display ? '$' + t + '$' : (t.startsWith('\\begin') ? t : '\\[' + t + '\\]');
      }
    } catch (e) {}
    return m.dataset.tex || '';
  }
  function katexTex(k) {
    const a = k.querySelector('annotation[encoding="application/x-tex"]'); if (!a) return '';
    return k.closest('.katex-display') ? '\\[' + a.textContent + '\\]' : '$' + a.textContent + '$';
  }
  const MATH = 'mjx-container,.katex';
  function selText(s) {
    if (!s.rangeCount) return '';
    const d = document.createElement('div');
    for (let i = 0; i < s.rangeCount; i++) d.appendChild(s.getRangeAt(i).cloneContents());
    if (!d.querySelector(MATH)) return s.toString();
    // match clones to originals by order, since clones lose MathJax's bookkeeping
    const orig = []; for (let i = 0; i < s.rangeCount; i++) {
      let a = s.getRangeAt(i).commonAncestorContainer; if (a.nodeType !== 1) a = a.parentNode;
      const own = a.closest(MATH); orig.push(...(own ? [own] : [...a.querySelectorAll(MATH)].filter(m => s.containsNode(m, true))));
    }
    const top = [...d.querySelectorAll(MATH)].filter(m => !m.parentElement.closest(MATH));
    const origTop = orig.filter(m => !m.parentElement.closest(MATH));
    top.forEach((m, i) => { const o = origTop[i] || m; m.replaceWith(o.matches('mjx-container') ? mathjaxTex(o) : katexTex(o)); });
    return d.textContent;
  }
  // Formula glyphs are drawn outside the text, so mark selected formulas ourselves.
  let marked = [];
  document.addEventListener('selectionchange', () => {
    marked.forEach(m => m.classList.remove('cl-msel')); marked = [];
    const s = getSelection(); if (!s.rangeCount || s.isCollapsed) return;
    for (let i = 0; i < s.rangeCount; i++) {
      let a = s.getRangeAt(i).commonAncestorContainer; if (a.nodeType !== 1) a = a.parentNode;
      const own = a.closest(MATH);
      for (const m of own ? [own] : a.querySelectorAll(MATH)) if (s.containsNode(m, true)) { m.classList.add('cl-msel'); marked.push(m); }
    }
  });
  document.addEventListener('copy', e => {
    const s = getSelection(); if (!s.rangeCount) return;
    const t = selText(s); if (t === s.toString()) return;
    e.clipboardData.setData('text/plain', t); e.preventDefault();
  });

  function where(node) {
    let n = node && node.nodeType === 1 ? node : node && node.parentNode;
    for (let x = n; x && x !== document.body; x = x.parentNode) {
      if (x.dataset && x.dataset.card) { const h = x.querySelector('.kname'); return (h ? h.textContent + ' ' : '') + '[' + x.dataset.card + ']'; }
      if (x.dataset && x.dataset.commentLabel) return x.dataset.commentLabel;
    }
    let last = null;
    for (const h of document.querySelectorAll('h1,h2,h3,h4')) {
      if (h.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING || h.contains(n)) last = h; else break;
    }
    return last ? last.textContent.trim() : document.title;
  }
  const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  function render() {
    if (count) count.textContent = comments.length;
    $('cl-list').innerHTML = comments.map((c, i) => `<div class="c"><b>${esc(c.where)}</b><div class="q">「${esc(c.quote)}」</div><div>${esc(c.text)}</div><button data-i="${i}">${L.del}</button></div>`).join('') || `<p class="q">${L.none}</p>`;
    $('cl-list').querySelectorAll('button').forEach(b => b.onclick = () => { comments.splice(+b.dataset.i, 1); save(); render(); });
  }
  document.addEventListener('mouseup', e => {
    if (e.target.closest('#cl-box,#cl-bar,#cl-add,#bar')) return;
    const s = getSelection(); const txt = selText(s).trim();
    if (!txt) { add.style.display = 'none'; return; }
    pending = {where: where(s.anchorNode), quote: txt.replace(/\s+/g, ' ')};
    const r = s.getRangeAt(0).getBoundingClientRect();
    add.style.left = (scrollX + r.right + 6) + 'px'; add.style.top = (scrollY + r.top - 4) + 'px'; add.style.display = 'block';
  });
  add.onclick = () => { add.style.display = 'none'; box.style.display = 'block'; $('cl-edit').style.display = 'block';
    $('cl-quote').textContent = pending.where + '「' + pending.quote + '」'; $('cl-text').value = ''; $('cl-text').focus(); };
  $('cl-save').onclick = () => { if (!pending) return; comments.push({...pending, text: $('cl-text').value.trim()}); pending = null; save(); $('cl-edit').style.display = 'none'; render(); };
  $('cl-cancel').onclick = () => { pending = null; $('cl-edit').style.display = 'none'; };
  bOpen.onclick = () => { box.style.display = box.style.display === 'block' ? 'none' : 'block'; render(); };
  $('cl-close').onclick = () => { box.style.display = 'none'; };
  $('cl-clear').onclick = () => { if (confirm(L.confirm)) { comments = []; save(); render(); } };
  bCopy.onclick = async () => {
    const text = comments.map(c => c.where + '\n「' + c.quote + '」\n→ ' + (c.text || L.nocomment)).join('\n\n');
    try { await navigator.clipboard.writeText(text); } catch (e) { const t = el('textarea', {value: text}); document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove(); }
    const old = bCopy.textContent; bCopy.textContent = L.copied; setTimeout(() => bCopy.textContent = old, 1500);
  };
  render();
})();
