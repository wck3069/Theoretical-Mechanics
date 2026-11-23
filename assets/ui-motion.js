/* ============================================================
   ui-motion.js · 共享动效层（配合 ui-liquid.css）
   · IntersectionObserver：滚动揭示（.ui-reveal → .ui-in），
     目标 .card/.cat-row/.ch/.panel/.detail/.tmai-panel/.ms-toc，
     同一容器内交错，延迟由 --ui-delay 控制，上限 240ms。
   · rAF 视差：[data-ui-parallax] 与 .hero/.ms-hero 的直接子元素，
     位移上限 24px；跳过减少动态偏好、不可见元素与画布。
   幂等；不触碰模拟画布逻辑与任何数据/交互代码。
   ============================================================ */
(function () {
  'use strict';
  if (window.__uiMotionInit) return;
  window.__uiMotionInit = true;

  var REDUCE = typeof matchMedia === 'function' &&
    matchMedia('(prefers-reduced-motion: reduce)').matches;
  var MAX_PARALLAX = 24;      // px，硬上限
  var MAX_DELAY = 240;        // ms，交错上限
  var REVEAL_SEL = '.card, .cat-row, .ch, .panel, .detail, .tmai-panel, .ms-toc';

  function visible(el) {
    return el && el.offsetParent !== null ||
      (el && getComputedStyle(el).position === 'fixed');
  }

  /* ---------- 1. 滚动揭示 ---------- */
  function initReveal() {
    var els = Array.prototype.slice.call(document.querySelectorAll(REVEAL_SEL));
    if (!els.length) return;
    if (REDUCE || !('IntersectionObserver' in window)) return; // CSS 已保证可见
    els.forEach(function (el) {
      el.classList.add('ui-reveal');
    });
    // 按“最近的共享祖先”分组交错：同一网格/列表内的兄弟依次延迟
    var order = new Map();
    els.forEach(function (el) {
      var key = el.parentElement || document.body;
      var n = order.get(key) || 0;
      order.set(key, n + 1);
      el.style.setProperty('--ui-delay', Math.min(n * 60, MAX_DELAY) + 'ms');
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('ui-in');
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 2. 视差（<=24px） ---------- */
  function initParallax() {
    if (REDUCE || !('requestAnimationFrame' in window)) return;
    var targets = [];
    function collect() {
      targets = [];
      Array.prototype.forEach.call(
        document.querySelectorAll('[data-ui-parallax]'),
        function (el) { targets.push({ el: el, depth: parseFloat(el.getAttribute('data-ui-parallax')) || 12 }); });
      Array.prototype.forEach.call(
        document.querySelectorAll('.hero > *, .ms-hero > *'),
        function (el) {
          if (el.tagName === 'CANVAS') return;               // 不干扰画布
          if (getComputedStyle(el).animationName !== 'none') return; // 不与关键帧动画打架
          var i = targets.filter(function (t) { return t.el.parentElement === el.parentElement; }).length;
          targets.push({ el: el, depth: Math.min(8 + i * 6, MAX_PARALLAX) });
        });
      targets = targets.filter(function (t) { return t.el && !t.el.hasAttribute('data-ui-no-parallax'); });
    }
    collect();
    var raf = 0, lastY = -1;
    function apply() {
      raf = 0;
      if (document.hidden) return;
      var vh = window.innerHeight || document.documentElement.clientHeight;
      for (var i = 0; i < targets.length; i++) {
        var t = targets[i], el = t.el;
        if (!visible(el)) continue;
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) continue;   // 远离视口：跳过
        var center = r.top + r.height / 2 - vh / 2;
        var y = Math.max(-MAX_PARALLAX, Math.min(MAX_PARALLAX,
          -(center / vh) * t.depth));
        el.style.transform = 'translate3d(0,' + y.toFixed(1) + 'px,0)';
      }
    }
    function schedule() {
      if (lastY === window.scrollY) return;
      lastY = window.scrollY;
      if (!raf) raf = requestAnimationFrame(apply);
    }
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) schedule();
    });
    schedule();
  }

  function boot() { initReveal(); initParallax(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
