(() => {
  function fragmentTarget(hash) {
    if (!hash || hash.includes(':~:')) return null;
    let fragment = hash.slice(1);
    try {
      fragment = decodeURIComponent(fragment);
    } catch {
      // An invalid percent escape can still occur in a literal HTML id.
    }
    return document.getElementById(fragment);
  }

  function reveal(target) {
    for (let ancestor = target.parentElement; ancestor; ancestor = ancestor.parentElement) {
      if (ancestor instanceof HTMLDetailsElement) ancestor.open = true;
    }
  }

  document.addEventListener('click', event => {
    const link = event.target.closest?.('a');
    const href = link?.getAttribute('href');
    if (!href?.startsWith('#')) return;
    const target = fragmentTarget(href);
    if (target) reveal(target);
  });

  window.addEventListener('hashchange', () => {
    const target = fragmentTarget(location.hash);
    if (!target) return;
    const hidden = Boolean(target.closest('details:not([open])'));
    reveal(target);
    if (hidden) target.scrollIntoView({ block: 'start' });
  });

  const initialHash = location.hash;
  const navigation = performance.getEntriesByType('navigation')[0];
  const target = fragmentTarget(initialHash);
  if (!target || navigation?.type === 'back_forward') return;
  reveal(target);

  let interacted = false;
  const interactionEvents = ['pointerdown', 'wheel', 'touchstart', 'keydown'];
  function cancelRestore() {
    interacted = true;
  }
  for (const event of interactionEvents) {
    window.addEventListener(event, cancelRestore, { once: true, passive: true });
  }

  const loaded = document.readyState === 'complete'
    ? Promise.resolve()
    : new Promise(resolve => window.addEventListener('load', resolve, { once: true }));
  const typeset = window.MathJax?.startup?.promise ?? Promise.resolve();
  Promise.allSettled([loaded, typeset, document.fonts?.ready]).then(() => {
    requestAnimationFrame(() => {
      for (const event of interactionEvents) window.removeEventListener(event, cancelRestore);
      if (!interacted && location.hash === initialHash) target.scrollIntoView({ block: 'start' });
    });
  });
})();
