/* Translates UI nodes in place; never replaces React-owned elements. */
(() => {
  'use strict';
  const api = globalThis.DesktopLocalChinese;
  if (!api) return;
  const excluded = 'script,style,pre,code,textarea,input,[contenteditable=true],.side-by-side-diff .content,.CodeMirror,.cm-editor,.monaco-editor,.diff,.diff-view,.diff-table,.diff-line,.blob-code,.commit .summary,.commit .description,.tag-name,.commit-summary,.commit-description,.commit-message,.commit-body,.commit-title,.repository-name,.repository-list-item .name,.branch-name,.branch-list-item .name,.file-path,.path-text,.log-line,.selectable-text';
  const safe = el => el && !el.closest(excluded);
  const attrs = ['aria-label','title','placeholder'];
  function element(el) {
    if (!safe(el) && !el.matches('input,textarea')) return;
    // Only captions, never value, checked, href, data attributes or form contents.
    for (const name of attrs) {
      if (!el.hasAttribute(name)) continue;
      const old = el.getAttribute(name), value = api.translate(old);
      if (old !== value) el.setAttribute(name, value);
    }
  }
  function text(node) {
    if (!safe(node.parentElement)) return;
    const old = node.nodeValue, value = api.translate(old);
    if (old !== value) node.nodeValue = value;
  }
  function scan(root) {
    if (root.nodeType === Node.TEXT_NODE) { text(root); return; }
    if (root.nodeType !== Node.ELEMENT_NODE || !safe(root)) return;
    element(root);
    for (const el of root.querySelectorAll('[aria-label],[title],[placeholder]')) element(el);
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: node => safe(node.parentElement) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
    });
    let node;
    while ((node = walker.nextNode())) text(node);
  }
  function start() {
    document.documentElement.lang = 'zh-CN';
    scan(document.body);
    let queued = false;
    const pending = new Set();
    const observer = new MutationObserver(records => {
      for (const r of records) {
        if (r.type === 'childList') for (const node of r.addedNodes) pending.add(node);
        else pending.add(r.target);
      }
      if (queued) return;
      queued = true;
      queueMicrotask(() => {
        queued = false;
        const nodes = [...pending]; pending.clear();
        for (const node of nodes) if (node.isConnected) scan(node);
      });
    });
    observer.observe(document.body, {subtree:true, childList:true, characterData:true, attributes:true, attributeFilter:attrs});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();
