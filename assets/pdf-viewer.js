/* pdf-viewer.js — in-page PDF reader overlay.
   Clicking a same-origin PDF link opens the file inside a modal on the
   current page instead of a standalone browser PDF tab. No dependencies,
   no network access, no PDF.js: the body is a plain <iframe>.
   The overlay carries data-tm-no-i18n, so the site translator never rewrites
   its text; all chrome labels come from the local dictionary below. */
(function () {
  'use strict';

  var doc = document;

  /* Local UI dictionary. Keys: close / tab / download / loading / hint / dialog. */
  var I18N = {
    'zh-CN': { close: '关闭', tab: '新标签打开', download: '下载', loading: '正在载入 PDF…', hint: 'Esc 关闭 · 若空白请用「新标签打开」', dialog: 'PDF 阅读器' },
    'zh-TW': { close: '關閉', tab: '新分頁開啟', download: '下載', loading: '正在載入 PDF…', hint: 'Esc 關閉 · 若空白請用「新分頁開啟」', dialog: 'PDF 閱讀器' },
    'en-US': { close: 'Close', tab: 'Open in new tab', download: 'Download', loading: 'Loading PDF…', hint: 'Esc to close · use "Open in new tab" if blank', dialog: 'PDF reader' },
    'en-GB': { close: 'Close', tab: 'Open in new tab', download: 'Download', loading: 'Loading PDF…', hint: 'Esc to close · use "Open in new tab" if blank', dialog: 'PDF reader' }
  };

  var root = null;         /* .tm-pdfv; built lazily on first open, then reused */
  var els = null;          /* { panel, title, file, tab, dl, close, loading, hint, frame } */
  var isOpen = false;
  var lastTrigger = null;  /* anchor that opened the overlay; focus returns here */
  var prevOverflow = '';   /* documentElement overflow value before scroll-lock */

  /* Read the runtime language from tm-i18n.js when it is loaded. */
  function t(key) {
    var lang = 'zh-CN';
    try {
      if (window.TM_I18N && typeof window.TM_I18N.lang === 'function') { lang = window.TM_I18N.lang(); }
    } catch (e) { /* i18n layer absent on this page */ }
    var d = I18N[lang] || I18N['zh-CN'];
    return d[key] != null ? d[key] : I18N['zh-CN'][key];
  }

  function applyLabels() {
    if (!els) return;
    els.loading.textContent = t('loading');
    els.hint.textContent = t('hint');
    els.tab.textContent = t('tab');
    els.dl.textContent = t('download');
    els.close.setAttribute('aria-label', t('close'));
    els.close.setAttribute('title', t('close'));
    root.setAttribute('aria-label', t('dialog'));
  }

  /* iOS/iPadOS gets a first-class native PDF viewer, so interception is
     skipped there. iPadOS 13+ sends a desktop UA; MacIntel + touch catches it. */
  function isIOS() {
    var ua = navigator.userAgent || '';
    if (/iP(hone|od|ad)/.test(ua)) return true;
    try { return navigator.platform === 'MacIntel' && (navigator.maxTouchPoints || 0) > 1; }
    catch (e) { return false; }
  }

  function injectStyle() {
    if (doc.getElementById('tm-pdfv-style')) return;
    var s = doc.createElement('style');
    s.id = 'tm-pdfv-style';
    s.textContent = [
      /* structure, theme-independent; every rule scoped under .tm-pdfv */
      '.tm-pdfv{position:fixed;inset:0;z-index:2000;display:none;align-items:center;justify-content:center;padding:clamp(8px,2vw,24px)}',
      '.tm-pdfv--open{display:flex}',
      '.tm-pdfv__backdrop{position:absolute;inset:0;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}',
      '.tm-pdfv__panel{position:relative;z-index:1;width:min(1180px,96vw);height:min(92vh,1100px);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 30px 90px rgba(0,0,0,.55)}',
      /* arrival: opacity + translate + scale over 160ms */
      '.tm-pdfv--open .tm-pdfv__panel{animation:tm-pdfv-in .16s ease}',
      '@keyframes tm-pdfv-in{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:none}}',
      '.tm-pdfv__head{flex:0 0 52px;height:52px;display:flex;align-items:center;gap:12px;padding:0 14px;border-bottom:1px solid var(--tm-pdfv-line);white-space:nowrap}',
      '.tm-pdfv__title{flex:0 1 auto;min-width:40px;overflow:hidden;text-overflow:ellipsis;font-size:14px;font-weight:600}',
      '.tm-pdfv__file{flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;font-size:11.5px;color:var(--tm-pdfv-muted)}',
      '.tm-pdfv__spacer{flex:1 0 12px}',
      '.tm-pdfv__act,.tm-pdfv__close{font:inherit;font-size:12px;display:inline-flex;align-items:center;justify-content:center;gap:4px;height:28px;flex:0 0 auto;padding:0 10px;border-radius:8px;border:1px solid transparent;background:var(--tm-pdfv-btn);color:inherit;text-decoration:none;cursor:pointer;box-sizing:border-box;transition:background .12s,border-color .12s}',
      '.tm-pdfv__act:hover,.tm-pdfv__close:hover{background:var(--tm-pdfv-btn-hover);border-color:var(--tm-pdfv-line)}',
      '.tm-pdfv__act:focus-visible,.tm-pdfv__close:focus-visible{outline:2px solid var(--tm-pdfv-accent);outline-offset:2px}',
      '.tm-pdfv__close{width:32px;padding:0;font-size:19px;line-height:1}',
      '.tm-pdfv__stage{flex:1;position:relative;background:var(--tm-pdfv-stage)}',
      '.tm-pdfv__frame{width:100%;height:100%;border:0;display:block}',
      '.tm-pdfv__loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:13px;color:var(--tm-pdfv-muted);background:var(--tm-pdfv-stage)}',
      '.tm-pdfv__hint{flex:0 0 24px;height:24px;line-height:24px;text-align:center;font-size:11.5px;color:var(--tm-pdfv-muted);border-top:1px solid var(--tm-pdfv-line)}',
      /* dark skin: star-field chapter/module pages */
      '.tm-pdfv--dark .tm-pdfv__backdrop{background:rgba(2,4,10,.74)}',
      '.tm-pdfv--dark .tm-pdfv__panel{background:linear-gradient(160deg,rgba(16,24,44,.98),rgba(6,10,20,.99));border:1px solid rgba(146,182,255,.26);color:#e8eeff;--tm-pdfv-muted:#93a4c9;--tm-pdfv-accent:#7fe0ff;--tm-pdfv-stage:#0b1020;--tm-pdfv-line:rgba(146,182,255,.18);--tm-pdfv-btn:rgba(146,182,255,.08);--tm-pdfv-btn-hover:rgba(146,182,255,.16)}',
      /* light skin: paper manuscript pages; panel font stays inherited from the page */
      '.tm-pdfv--light .tm-pdfv__backdrop{background:rgba(30,26,20,.46)}',
      '.tm-pdfv--light .tm-pdfv__panel{background:#fbf9f2;border:1px solid rgba(35,32,26,.22);color:#23201a;--tm-pdfv-muted:#7d7666;--tm-pdfv-accent:#9c3a22;--tm-pdfv-stage:#e8e3d7;--tm-pdfv-line:rgba(35,32,26,.16);--tm-pdfv-btn:rgba(35,32,26,.04);--tm-pdfv-btn-hover:rgba(156,58,34,.08)}',
      /* phones: edge-to-edge sheet, compact actions, hint hidden */
      '@media(max-width:720px){.tm-pdfv{padding:0}.tm-pdfv__panel{width:100%;height:100%;border-radius:0}.tm-pdfv__head{gap:8px;padding:0 10px}.tm-pdfv__act{font-size:11.5px;padding:0 8px}.tm-pdfv__hint{display:none}}',
      /* reduced motion: no transform, plain fade only */
      '@media(prefers-reduced-motion:reduce){.tm-pdfv--open .tm-pdfv__panel{animation:tm-pdfv-fade .16s ease}}',
      '@keyframes tm-pdfv-fade{from{opacity:0}to{opacity:1}}'
    ].join('\n');
    doc.head.appendChild(s);
  }

  function el(tag, cls, text) {
    var n = doc.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function build() {
    if (root) return;
    injectStyle();
    root = el('div', 'tm-pdfv');
    /* the site translator must not touch our own labels */
    root.setAttribute('data-tm-no-i18n', '');
    root.setAttribute('role', 'dialog');
    root.setAttribute('aria-modal', 'true');
    root.setAttribute('aria-labelledby', 'tm-pdfv-title');

    var backdrop = el('div', 'tm-pdfv__backdrop');
    var panel = el('div', 'tm-pdfv__panel');

    var head = el('div', 'tm-pdfv__head');
    var title = el('span', 'tm-pdfv__title');
    title.id = 'tm-pdfv-title';
    var file = el('span', 'tm-pdfv__file');
    var spacer = el('span', 'tm-pdfv__spacer');
    var tab = el('a', 'tm-pdfv__act');
    tab.setAttribute('target', '_blank');
    tab.setAttribute('rel', 'noopener');
    var dl = el('a', 'tm-pdfv__act');
    dl.setAttribute('download', '');
    var close = el('button', 'tm-pdfv__close', '×');
    close.type = 'button';
    head.appendChild(title); head.appendChild(file); head.appendChild(spacer);
    head.appendChild(tab); head.appendChild(dl); head.appendChild(close);

    var stage = el('div', 'tm-pdfv__stage');
    var frame = el('iframe', 'tm-pdfv__frame');
    var loading = el('div', 'tm-pdfv__loading');
    stage.appendChild(frame); stage.appendChild(loading);

    var hint = el('div', 'tm-pdfv__hint');

    panel.appendChild(head); panel.appendChild(stage); panel.appendChild(hint);
    root.appendChild(backdrop); root.appendChild(panel);
    doc.body.appendChild(root);

    /* backdrop click closes; the panel sits above it so inner clicks miss */
    backdrop.addEventListener('click', function () { closeOverlay(); });
    close.addEventListener('click', function () { closeOverlay(); });

    /* loading veil covers the iframe until the document inside has loaded */
    frame.addEventListener('load', function () { loading.style.display = 'none'; });

    els = { panel: panel, title: title, file: file, tab: tab, dl: dl, close: close, loading: loading, hint: hint, frame: frame };
    applyLabels();
  }

  /* Parse the body's computed background-color; WCAG relative luminance
     under 0.5 counts as dark. Transparent body only counts dark on
     data-cosmos pages, whose darkness lives in layered gradients. */
  function bodyIsDark() {
    var raw = '';
    try { raw = getComputedStyle(doc.body).backgroundColor || ''; } catch (e) { return false; }
    var m = raw.match(/rgba?\(([^)]+)\)/);
    if (!m) return false;
    var p = m[1].replace(/\s+/g, '').split(',');
    if (p.length < 3) return false;
    var r = parseFloat(p[0]), g = parseFloat(p[1]), b = parseFloat(p[2]);
    var a = p.length > 3 ? parseFloat(p[3]) : 1;
    if (isNaN(a) || a < 0.05) return false;
    function lin(v) {
      v = Math.max(0, Math.min(255, v)) / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    }
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b) < 0.5;
  }

  function pickTheme() {
    var cosmos = !!(doc.body && doc.body.hasAttribute('data-cosmos'));
    var dark = cosmos || bodyIsDark();
    root.classList.toggle('tm-pdfv--dark', dark);
    root.classList.toggle('tm-pdfv--light', !dark);
  }

  function lastSegment(url) {
    var segs = url.pathname.split('/');
    var name = segs[segs.length - 1] || 'document.pdf';
    try { name = decodeURIComponent(name); } catch (e) { /* keep raw segment */ }
    return name || 'document.pdf';
  }

  function frameSrc(url) {
    /* FitH opens wide enough to be readable; never stack a second fragment */
    return url.href.indexOf('#') === -1 ? url.href + '#view=FitH' : url.href;
  }

  /* Public-ish entry: href is resolved against the current page, so relative
     links from chapters/, modules/, manuscript/ all work. Re-opening while
     open just swaps the document (re-entrant). */
  function openPdf(href, titleText) {
    var url;
    try { url = new URL(href, doc.baseURI || location.href); }
    catch (e) { return; }
    build();
    if (!isOpen) {
      lastTrigger = doc.activeElement;
      prevOverflow = doc.documentElement.style.overflow;
      doc.documentElement.style.overflow = 'hidden';
      root.classList.add('tm-pdfv--open');
      isOpen = true;
    }
    pickTheme();
    var name = lastSegment(url);
    var label = (titleText || '').replace(/\s+/g, ' ').trim() || 'PDF';
    els.title.textContent = label;
    els.file.textContent = name;
    els.tab.setAttribute('href', url.href);
    els.dl.setAttribute('href', url.href);
    els.dl.setAttribute('download', name);
    els.frame.title = label;
    els.loading.style.display = 'flex';
    /* always re-set src so the same file reloads from page one */
    els.frame.src = frameSrc(url);
    applyLabels();
    els.close.focus();
  }

  function closeOverlay() {
    if (!isOpen) return;
    isOpen = false;
    root.classList.remove('tm-pdfv--open');
    doc.documentElement.style.overflow = prevOverflow;
    if (lastTrigger && doc.contains(lastTrigger) && typeof lastTrigger.focus === 'function') {
      lastTrigger.focus();
    }
    lastTrigger = null;
  }

  /* One delegated listener covers static links and anchors created at
     runtime (the neural page builds <a> elements dynamically). */
  doc.addEventListener('click', function (e) {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (e.defaultPrevented) return;
    if (isIOS()) return;
    var a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    /* our own header actions must open real tabs/downloads, not re-open */
    if (a.closest('.tm-pdfv')) return;
    if (a.hasAttribute('download') || a.hasAttribute('data-pdfv-skip')) return;
    var href = a.getAttribute('href');
    if (!href) return;
    var url;
    try { url = new URL(href, location.href); }
    catch (err) { return; }
    /* same-origin only; on file: pages both origins read as 'null' and match */
    if (url.origin !== location.origin) return;
    if (!/\.pdf$/i.test(url.pathname)) return;   /* query/hash already parsed out */
    e.preventDefault();
    openPdf(url.href, a.textContent);
  });

  doc.addEventListener('keydown', function (e) {
    if (isOpen && e.key === 'Escape') { e.preventDefault(); closeOverlay(); }
  });

  /* Chrome labels follow the site language; the root's data-tm-no-i18n keeps
     the MutationObserver translator out of this subtree. */
  doc.addEventListener('tm:langchange', function () {
    if (isOpen) applyLabels();
  });

  window.TMPdfViewer = { open: openPdf, close: closeOverlay };
})();
