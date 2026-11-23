/* tm-seq.js — the ONLY source of simulation order and Mx labels.
   Order = manuscript chapters 1..7, then the Mx number inside each chapter.
   Do NOT edit this order for UI work; add/rename projects by updating SEQ here
   (and the matching chapter-portal card), not by touching navigation code.
   Shared simulation pages: 04-variational carries M8-M10, 08-kinematics carries
   M5/M16/M17, 10-coupled-systems carries M13-M15, 11-rotation-and-field
   carries M20-M21, 18-phase-space carries M22-M23. The mode is selected with the page's query parameter. */
(function () {
  'use strict';

  var SEQ = [
    { slug: '00-binet', mx: 'M0', chap: 'chapter-01-newton', title: '比奈方程（现有样板）' },
    { slug: '01-effective-potential', mx: 'M1', chap: 'chapter-01-newton', title: '有效势与轨道稳定性' },
    { slug: '02-scattering', mx: 'M2', chap: 'chapter-01-newton', title: '散射与俘获' },
    { slug: '03-two-body', mx: 'M3', chap: 'chapter-01-newton', title: '两体问题与系外行星' },
    { slug: '06-collisions', mx: 'M4', chap: 'chapter-01-newton', title: '碰撞与变质量' },
    { slug: '08-kinematics', mx: 'M5', chap: 'chapter-01-newton', title: '圆柱脱离与运动学', param: 'mode', value: 'cylinder' },
    { slug: '14-foucault-rose', mx: 'M6', chap: 'chapter-01-newton', title: '傅科摆与玫瑰线' },
    { slug: '15-lagrange-points', mx: 'M7', chap: 'chapter-01-newton', title: '拉格朗日点' },
    { slug: '04-variational', mx: 'M8', chap: 'chapter-02-variational', title: '等时摆（摆线）', param: 'mode', value: 'cycloid' },
    { slug: '04-variational', mx: 'M9', chap: 'chapter-02-variational', title: '折射定律', param: 'mode', value: 'refraction' },
    { slug: '04-variational', mx: 'M10', chap: 'chapter-02-variational', title: '最短路径', param: 'mode', value: 'shortest' },
    { slug: '05-virtual-work', mx: 'M11', chap: 'chapter-03-lagrangian', title: '虚功原理与静力学' },
    { slug: '09-atwood-pulley', mx: 'M12', chap: 'chapter-03-lagrangian', title: '有转动惯量的 Atwood 机' },
    { slug: '10-coupled-systems', mx: 'M13', chap: 'chapter-04-oscillations', title: '斜面上的滑块', param: 'scene', value: 'wedge' },
    { slug: '10-coupled-systems', mx: 'M14', chap: 'chapter-04-oscillations', title: '弹簧摆', param: 'scene', value: 'spring' },
    { slug: '10-coupled-systems', mx: 'M15', chap: 'chapter-04-oscillations', title: '小车与单摆', param: 'scene', value: 'cart' },
    { slug: '08-kinematics', mx: 'M16', chap: 'chapter-04-oscillations', title: '单摆周期修正', param: 'mode', value: 'pendulum' },
    { slug: '08-kinematics', mx: 'M17', chap: 'chapter-04-oscillations', title: '双摆混沌', param: 'mode', value: 'double' },
    { slug: '07-rigid-body', mx: 'M18', chap: 'chapter-05-rigid-body', title: '刚体几何与角动量' },
    { slug: '17-free-rigid-body', mx: 'M19', chap: 'chapter-05-rigid-body', title: '自由刚体与网球拍效应' },
    { slug: '11-rotation-and-field', mx: 'M20', chap: 'chapter-06-hamiltonian', title: '旋转圆环上的珠子', param: 'scene', value: 'ring' },
    { slug: '11-rotation-and-field', mx: 'M21', chap: 'chapter-06-hamiltonian', title: '磁场中的带电粒子', param: 'scene', value: 'cyclotron' },
    { slug: '18-phase-space', mx: 'M22', chap: 'chapter-06-hamiltonian', title: '相空间与刘维尔', param: 'scene', value: 'phase' },
    { slug: '18-phase-space', mx: 'M23', chap: 'chapter-06-hamiltonian', title: '辛积分器比较', param: 'scene', value: 'integrator' },
    { slug: '13-lightcone-worldlines', mx: 'M24', chap: 'chapter-07-relativity', title: '光锥与世界线' },
    { slug: '16-doppler-beaming', mx: 'M25', chap: 'chapter-07-relativity', title: '相对论多普勒与车头灯效应' },
    { slug: '19-relativistic-collisions', mx: 'M26', chap: 'chapter-07-relativity', title: '相对论碰撞与不变质量' }
  ];
  var ALIAS = { 'M8B': 'M16', 'M12': 'M16' };
  var ALIAS = { 'M8B': 'M12' };

  function currentSlug() {
    var parts = (location.pathname || '').split('/');
    for (var i = parts.length - 1; i >= 0; i--) {
      if (parts[i] && parts[i] !== 'index.html') { return parts[i]; }
    }
    return '';
  }
  function queryValue(name) {
    var q = (location.search || '').replace(/^\?/, '').split('&');
    for (var i = 0; i < q.length; i++) {
      var p = q[i].split('=');
      if (decodeURIComponent(p[0] || '') === name) { return decodeURIComponent(p[1] || ''); }
    }
    return '';
  }
  function hrefOf(entry) {
    if (entry.href) { return entry.href; }
    var href = '../' + entry.slug + '/index.html';
    if (entry.param) { href += '?' + entry.param + '=' + encodeURIComponent(entry.value); }
    return href;
  }
  function setLink(nav, key, href, text) {
    if (!nav) { return; }
    var a = nav.querySelector('[data-tm-nav="' + key + '"]');
    if (!a) { return; }
    if (href !== null) { a.setAttribute('href', href); a.style.display = ''; }
    if (text !== null) { a.textContent = text; }
  }

  function init() {
    var slug = currentSlug();
    var matches = [];
    for (var i = 0; i < SEQ.length; i++) {
      if (SEQ[i].slug === slug) { matches.push(i); }
    }
    if (!matches.length) { return; }
    var idx = matches[0];
    var asked = (queryValue('mx') || '').toUpperCase();
    var byMode = false;
    for (var pm = 0; pm < matches.length; pm++) {
      var e = SEQ[matches[pm]];
      if (e.param && queryValue(e.param) === e.value) { idx = matches[pm]; byMode = true; break; }
    }
    if (!byMode && asked) {
      if (ALIAS[asked]) { asked = ALIAS[asked]; }
      for (var m = 0; m < matches.length; m++) {
        if (SEQ[matches[m]].mx === asked) { idx = matches[m]; break; }
      }
    }
    var cur = SEQ[idx];
    var prev = idx > 0 ? SEQ[idx - 1] : null;
    var next = idx < SEQ.length - 1 ? SEQ[idx + 1] : null;

    var nav = document.querySelector('.tm-orbit-nav');
    setLink(nav, 'prev', prev ? hrefOf(prev) : null, prev ? '\u2039 上一章 \u00b7 ' + prev.mx : null);
    if (!prev) {
      var pa = nav && nav.querySelector('[data-tm-nav="prev"]');
      if (pa) { pa.style.display = 'none'; }
    }
    if (next) { setLink(nav, 'next', hrefOf(next), '下一章 \u00b7 ' + next.mx + ' \u203a'); }
    else { setLink(nav, 'next', '../../manuscript/index.html', '书稿 \u203a'); }

    var exit = nav && nav.querySelector('[data-tm-nav="exit"]');
    if (exit) {
      exit.setAttribute('href', '../../chapters/' + cur.chap.replace(/^chapter-/, '') + '/index.html?ret=' + encodeURIComponent(cur.mx));
    }
    var ask = nav && nav.querySelector('[data-tm-nav="ask"]');
    if (ask) {
      ask.setAttribute('href', '#');
      ask.onclick = function (e) {
        e.preventDefault();
        if (window.TM_AI && typeof window.TM_AI.open === 'function') {
          window.TM_AI.open({ module: cur.mx });
        } else {
          window.location.href = '../../index.html?ask=1&m=' + encodeURIComponent(cur.mx);
        }
      };
    }

    var h1 = document.querySelector('.brand h1') || document.querySelector('header.top h1');
    if (h1) { h1.textContent = cur.title; }
    var dot = document.title.indexOf(' \u00b7 ');
    document.title = cur.title + (dot >= 0 ? document.title.slice(dot) : '');

    var docs = document.querySelectorAll('a.doc');
    for (var d = 0; d < docs.length; d++) {
      var el = docs[d];
      var t = el.textContent || '';
      var role = el.getAttribute('data-tm-doc');
      if (role === 'prev' || (!role && /上一模块/.test(t))) {
        if (prev) { el.setAttribute('href', hrefOf(prev)); el.textContent = '\u2190 上一模块 ' + prev.mx + '\uff1a' + prev.title; }
        else { el.style.display = 'none'; }
      } else if (role === 'next' || (!role && /下一模块|下一章/.test(t))) {
        if (next) { el.setAttribute('href', hrefOf(next)); el.textContent = '下一模块 ' + next.mx + '\uff1a' + next.title + ' \u2192'; }
        else { el.setAttribute('href', '../../manuscript/index.html'); el.textContent = '下一模块：书稿 \u2192'; }
      }
    }

    document.body.setAttribute('data-tm-mx', cur.mx);
    document.body.setAttribute('data-tm-chap', cur.chap);
    try {
      localStorage.setItem('tm-neural-selected', JSON.stringify({
        chap: cur.chap, mx: cur.mx, slug: cur.slug, at: Date.now()
      }));
    } catch (e) {}
  }

  window.TM_SEQ = { refresh: function () { init(); } };
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); }
  else { init(); }
})();
