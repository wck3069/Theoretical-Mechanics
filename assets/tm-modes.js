/* tm-modes.js — numbered mode index for simulations with several modes.
   Each mode is addressable with the page's native query parameter and the
   index mirrors the <select> used by the simulation. */
(function () {
  'use strict';

  var SETS = {
    '04-variational': {
      select: 'sel-mode', param: 'mode', modes: [
        { id: 'M8', value: 'cycloid', title: '等时摆（摆线）' },
        { id: 'M9', value: 'refraction', title: '折射定律' },
        { id: 'M10', value: 'shortest', title: '最短路径' }
      ]
    },
    '08-kinematics': {
      select: 'sel-mode', param: 'mode', modes: [
        { id: 'M5', value: 'cylinder', title: '圆柱脱离与运动学' },
        { id: 'M16', value: 'pendulum', title: '单摆周期修正' },
        { id: 'M17', value: 'double', title: '双摆混沌' }
      ]
    },
    '10-coupled-systems': {
      select: 'sel-scene', param: 'scene', modes: [
        { id: 'M13', value: 'wedge', title: '斜面上的滑块' },
        { id: 'M14', value: 'spring', title: '弹簧摆' },
        { id: 'M15', value: 'cart', title: '小车与单摆' }
      ]
    },
    '11-rotation-and-field': {
      select: 'sel-scene', param: 'scene', modes: [
        { id: 'M20', value: 'ring', title: '旋转圆环上的珠子' },
        { id: 'M21', value: 'cyclotron', title: '磁场中的带电粒子' }
      ]
    },
    '18-phase-space': {
      select: 'sel-scene', param: 'scene', modes: [
        { id: 'M22', value: 'phase', title: '相空间与刘维尔' },
        { id: 'M23', value: 'integrator', title: '辛积分器比较' }
      ]
    }
  };

  var STYLE = [
    '.tm-mode-index{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}',
    '.tm-mode-index a{display:inline-flex;align-items:center;gap:6px;font-size:11.5px;line-height:1.4;text-decoration:none;',
    'color:#b8c6e6;border:1px solid rgba(146,182,255,.22);background:rgba(10,16,32,.55);border-radius:999px;padding:5px 10px;transition:border-color .15s,color .15s,background .15s}',
    '.tm-mode-index a b{font-family:ui-monospace,monospace;font-size:10.5px;letter-spacing:.06em;color:#7fe0ff;font-weight:600}',
    '.tm-mode-index a:hover{color:#e8eeff;border-color:rgba(255,210,122,.5)}',
    '.tm-mode-index a[aria-current="true"]{color:#ffd27a;border-color:rgba(255,210,122,.6);background:rgba(255,210,122,.10)}',
    '.tm-mode-index a[aria-current="true"] b{color:#ffd27a}',
    '.tm-mode-note{font-size:11px;color:#7f8fb8;margin:-6px 0 12px}'
  ].join('');

  function dirName() {
    var parts = location.pathname.split('/');
    for (var i = parts.length - 1; i >= 0; i--) {
      if (!parts[i] || parts[i] === 'index.html') continue;
      return parts[i];
    }
    return '';
  }

  function currentValue(sel) { return sel ? sel.value : ''; }

  var INIT = (function () {
    try { return new URLSearchParams(location.search); } catch (e) { return null; }
  })();

  function syncUrl(param, value) {
    try {
      var url = new URL(location.href);
      if (value) url.searchParams.set(param, value);
      else url.searchParams.delete(param);
      var mx = INIT && INIT.get('mx');
      if (mx && !url.searchParams.get('mx')) url.searchParams.set('mx', mx);
      history.replaceState(null, '', url.pathname + (url.search ? url.search : '') + url.hash);
    } catch (e) {}
  }

  function build(set) {
    var sel = document.getElementById(set.select);
    if (!sel) return;
    var anchor = sel.closest('.group') || sel.closest('.scene-select') || sel.parentNode;
    var nav = document.createElement('nav');
    nav.className = 'tm-mode-index';
    nav.setAttribute('aria-label', '模式索引');
    var links = [];
    set.modes.forEach(function (m) {
      var a = document.createElement('a');
      var href = '?' + set.param + '=' + encodeURIComponent(m.value);
      var keep = INIT && INIT.get('mx');
      if (keep) href += '&mx=' + encodeURIComponent(keep);
      a.href = href;
      a.setAttribute('data-mode', m.value);
      var b = document.createElement('b'); b.textContent = m.id; a.appendChild(b);
      var t = document.createElement('span'); t.textContent = m.title; a.appendChild(t);
      a.addEventListener('click', function (e) {
        e.preventDefault();
        if (sel.value !== m.value) {
          sel.value = m.value;
          try { sel.dispatchEvent(new Event('change', { bubbles: true })); } catch (err) {
            var ev = document.createEvent('HTMLEvents'); ev.initEvent('change', true, false); sel.dispatchEvent(ev);
          }
        }
        syncUrl(set.param, m.value);
        mark();
        if (window.TM_SEQ && TM_SEQ.refresh) TM_SEQ.refresh();
      });
      nav.appendChild(a); links.push(a);
    });
    anchor.parentNode.insertBefore(nav, anchor);

    if (dirName() === '08-kinematics' && /(?:^|[?&])mx=M12(?:&|$)/.test(location.search) && !/[?&]mode=/.test(location.search)) {
      sel.value = 'pendulum';
      try { sel.dispatchEvent(new Event('change', { bubbles: true })); } catch (err) {}
      syncUrl(set.param, 'pendulum');
    }

    function mark() {
      var v = currentValue(sel);
      links.forEach(function (a) {
        a.setAttribute('aria-current', a.getAttribute('data-mode') === v ? 'true' : 'false');
      });
    }
    sel.addEventListener('change', function () {
      mark(); syncUrl(set.param, sel.value);
      if (window.TM_SEQ && TM_SEQ.refresh) TM_SEQ.refresh();
    });
    mark();
  }

  function init() {
    var style = document.createElement('style');
    style.textContent = STYLE;
    document.head.appendChild(style);
    var key = dirName();
    if (SETS[key]) build(SETS[key]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
