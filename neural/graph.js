(function () {
  'use strict';

  var D = window.TM_NEURAL || { chapters: [], modules: {}, links: [], linkTypes: {} };
  var C = window.TMChunk || {
    parse: function () { return []; },
    splitInline: function (s) { return [{ t: 'text', v: s }]; },
    plain: function (s) { return String(s); }
  };
  var chapters = D.chapters || [];
  var modules = D.modules || {};
  var links = (D.links || []).filter(function (l) { return l && l.from && l.to && modules[l.from] && modules[l.to]; });
  var ltypes = D.linkTypes || {};
  var byChapterSlug = {}, byModuleSlug = {}, ownerOf = {}, unitIds = [];

  chapters.forEach(function (c, ci) {
    byChapterSlug[c.slug] = c;
    (c.modules || []).forEach(function (mid) {
      if (modules[mid] && ownerOf[mid] === undefined) ownerOf[mid] = ci;
    });
  });
  unitIds = Object.keys(modules);
  unitIds.forEach(function (mid) {
    var m = modules[mid];
    if (ownerOf[mid] === undefined) ownerOf[mid] = chapters.length - 1;
    if (m && m.slug) {
      if (!byModuleSlug[m.slug]) byModuleSlug[m.slug] = [];
      if (byModuleSlug[m.slug].indexOf(mid) < 0) byModuleSlug[m.slug].push(mid);
    }
  });

  var $ = function (id) { return document.getElementById(id); };
  var canvas = $('net'), ctx = canvas.getContext('2d');
  var cosmosBg = $('cosmosBg');
  var panel = $('panel'), pTitle = $('pTitle'), pBody = $('pBody'), pKicker = $('pKicker'), pScroll = $('pScroll');
  var tip = $('tip'), qres = $('qres'), q = $('q');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var W = 0, H = 0, dpr = 1;
  var RX = 560, RY = 345;
  var cam = { x: 0, y: 0, k: 1 };
  var camAnim = null; // { x0,y0,k0, x1,y1,k1, t0, dur }
  var nodes = [], byNode = {}, crossLinks = [], memberLinks = [];
  var alpha = 0.02, raf = 0, needsDraw = true, tNow = 0;
  var state = { chapter: null, unit: null, chunk: null, link: null, list: false, hover: null, hoverNode: null, hoverLink: null };
  // 默认开启：同题异法、前置路径、极限对照（32 条），共用工具一键可展开全部 57 条
  var filterTypes = {};
  Object.keys(ltypes).forEach(function (t) { filterTypes[t] = (t !== 'tool'); });

  var textures = {};
  var stars = [];
  var mathPromise = null;
  var stats = { nodes: 0, edges: 0, mathTotal: 0, mathRendered: 0, mathFallback: 0, routes: 0, routeErrors: 0 };
  window.__NV2 = { stats: stats, state: state, cam: cam, go: go, nodes: function () { return nodes; }, fit: fit };

  /* —— 工具函数 —— */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function seeded(n) { var x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
  function chapterOf(mid) { return chapters[ownerOf[mid]] || null; }
  function chapterDir(ch) { return ch.slug.replace(/^chapter-(\d+)-/, function (m, n) { return 'chapters/' + n + '-'; }); }
  function unitCount(ch) { return (ch.modules || []).filter(function (m) { return modules[m]; }).length; }
  function chunksOf(mid) {
    var out = [], m = modules[mid]; if (!m) return out;
    (m.sections || []).forEach(function (s, si) {
      (s.chunks || []).forEach(function (c) { out.push({ section: s, si: si, chunk: c }); });
    });
    return out;
  }
  function chunksOfAll() { var a = []; unitIds.forEach(function (m) { a = a.concat(chunksOf(m)); }); return a; }
  function findChunk(mid, cid) {
    var a = chunksOf(mid);
    for (var k = 0; k < a.length; k++) if (a[k].chunk.id === cid) return a[k];
    return null;
  }
  function linkOf(id) {
    for (var k = 0; k < links.length; k++) if (links[k].id === id) return links[k];
    return null;
  }
  function typeOf(t) { return ltypes[t] || { label: t || '关联', color: '#d7b48a', desc: '' }; }
  function modeOf(mid) {
    var m = modules[mid];
    if (!m || !m.href) return '';
    var parts = String(m.href).split('?');
    var mm = parts.length > 1 ? /(?:^|&)mode=([^&]+)/.exec(parts[1]) : null;
    return mm ? decodeURIComponent(mm[1]) : '';
  }
  // 同一个 slug 可能对应多个里程碑（如 M16/M17 都是 08b-nonlinear）。
  // 默认仍取首个（兼容旧链接），有提示时用 chunk id 前缀或 href 的 mode 消歧。
  function bySlug(slug, hint) {
    var list = byModuleSlug[slug];
    if (!list || !list.length) return null;
    if (hint) {
      var i;
      for (i = 0; i < list.length; i++) if (hint.indexOf(list[i] + '-') === 0) return list[i];
      for (i = 0; i < list.length; i++) if (modeOf(list[i]) === hint) return list[i];
    }
    return list[0];
  }
  function shortTitle(t) {
    return String(t || '').replace(/（[^）]*）/g, '').replace(/\([^)]*\)/g, '').trim();
  }
  function hexA(hex, a) {
    var s = String(hex || '#ffffff').replace('#', '');
    if (s.length === 3) s = s.split('').map(function (c) { return c + c; }).join('');
    var n = parseInt(s, 16);
    return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
  }
  function panelOffset() {
    return (W > 820 && panel.classList.contains('open')) ? Math.min(460, W * 0.92) * 0.5 : 0;
  }

  /* —— 星空初始化 —— */
  function initStars() {
    stars = [];
    var count = W < 700 ? 150 : 260;
    var palette = ['#ffffff', '#cfe4ff', '#9fcaff', '#ffe7bd', '#d6c8ff'];
    for (var i = 0; i < count; i++) {
      var r = seeded(i * 3.1 + 1);
      stars.push({
        x: seeded(i * 7.3 + 2),
        y: seeded(i * 11.7 + 3),
        r: 0.45 + Math.pow(r, 2.4) * 1.65,
        a: 0.25 + seeded(i * 5.9 + 4) * 0.65,
        ph: seeded(i * 13.3 + 5) * Math.PI * 2,
        sp: 0.5 + seeded(i * 17.1 + 6) * 1.4,
        c: palette[Math.floor(seeded(i * 19.7 + 7) * palette.length)]
      });
    }
  }

  /* —— 构建图谱模型（宽椭圆星座 + 外扇形分布 + 预热力导向） —— */
  function addNode(kind, id, label, ci, r, x, y, extra) {
    var n = {
      kind: kind, id: id, label: label, ci: ci, r: r,
      x: x, y: y, vx: 0, vy: 0, fixed: false,
      ax: x, ay: y, // 锚点（章节行星用）
      color: ci >= 0 && chapters[ci] ? chapters[ci].color : '#9fc5ff'
    };
    if (extra) Object.keys(extra).forEach(function (k) { n[k] = extra[k]; });
    nodes.push(n);
    byNode[kind + ':' + id] = n;
    return n;
  }

  function hubAnchor(ci) {
    var a = -Math.PI / 2 + ci * Math.PI * 2 / chapters.length;
    return { x: Math.cos(a) * RX, y: Math.sin(a) * RY, ang: a };
  }

  function buildModel() {
    nodes = []; byNode = {}; crossLinks = []; memberLinks = [];
    chapters.forEach(function (ch, ci) {
      var pos = hubAnchor(ci);
      var isSaturn = ch.slug.indexOf('hamiltonian') >= 0 || (ch.texture && ch.texture.indexOf('saturn') >= 0);
      addNode('chapter', ch.slug, ch.title, ci, 31, pos.x, pos.y, {
        ch: ch, ang: pos.ang, isSaturn: isSaturn, spinSpeed: 0.012 + (ci % 3) * 0.004
      });
      var tex = ch.texture;
      if (tex && !textures[tex]) {
        var im = new Image();
        im.onload = function () { needsDraw = true; };
        im.src = '../' + tex;
        textures[tex] = im;
      }
    });

    chapters.forEach(function (ch, ci) {
      var hub = byNode['chapter:' + ch.slug];
      var list = (ch.modules || []).filter(function (mid) { return modules[mid]; });
      var mCount = list.length;
      // 单元按外向扇区排布，避免挤向画布中心
      var spread = Math.min(Math.PI * 1.48, 0.55 + mCount * 0.19);
      list.forEach(function (mid, idx) {
        var m = modules[mid];
        var t = mCount <= 1 ? 0 : (idx / (mCount - 1) - 0.5);
        var a = hub.ang + t * spread;
        var ring = (idx % 2 === 0 ? 128 : 178) + (mCount > 7 ? 16 : 0);
        var cnt = chunksOf(mid).length;
        var r = clamp(7.5 + Math.sqrt(cnt) * 1.15, 8.5, 13.5);
        addNode('unit', mid, m.title, ci, r,
          hub.x + Math.cos(a) * ring,
          hub.y + Math.sin(a) * ring,
          { mod: m, count: cnt, short: shortTitle(m.title), prefAng: a, prefDist: ring }
        );
      });
    });

    chapters.forEach(function (ch) {
      var hub = byNode['chapter:' + ch.slug];
      (ch.modules || []).forEach(function (mid) {
        if (modules[mid]) memberLinks.push({ a: hub, b: byNode['unit:' + mid], type: 'member' });
      });
    });

    links.forEach(function (l) {
      var a = byNode['unit:' + l.from], b = byNode['unit:' + l.to];
      if (a && b) crossLinks.push({ a: a, b: b, data: l, type: l.type });
    });

    stats.nodes = nodes.length;
    stats.edges = crossLinks.length;

    // 预热力导向，开屏即舒展稳定
    alpha = 0.85;
    for (var step = 0; step < 200; step++) tick(true);
    alpha = 0.02;
    fit(false, true);
  }

  function tick(force) {
    if (!force && alpha <= 0.015) return;
    var a = alpha, i, j, n, o, dx, dy, d2, d, f;
    for (i = 0; i < nodes.length; i++) { nodes[i].fx = 0; nodes[i].fy = 0; }

    // 1. 节点间斥力 + 碰撞分离（预留标签呼吸空间）
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      for (j = i + 1; j < nodes.length; j++) {
        o = nodes[j];
        dx = o.x - n.x; dy = o.y - n.y;
        d2 = dx * dx + dy * dy + 60;
        d = Math.sqrt(d2);
        var sameCh = (n.ci === o.ci);
        var rep = (n.kind === 'chapter' || o.kind === 'chapter') ? 46000 : (sameCh ? 22000 : 18000);
        f = rep / d2;
        n.fx -= dx / d * f; n.fy -= dy / d * f;
        o.fx += dx / d * f; o.fy += dy / d * f;
        var minDist = n.r + o.r + (n.kind === 'chapter' || o.kind === 'chapter' ? 46 : 44);
        if (d < minDist) {
          var push = (minDist - d) * 0.24;
          n.fx -= dx / d * push; n.fy -= dy / d * push;
          o.fx += dx / d * push; o.fy += dy / d * push;
        }
      }
    }

    // 2. 弹簧力
    function spring(edge, len, kk) {
      dx = edge.b.x - edge.a.x; dy = edge.b.y - edge.a.y;
      d = Math.sqrt(dx * dx + dy * dy) || 1;
      f = (d - len) * kk;
      edge.a.fx += dx / d * f; edge.a.fy += dy / d * f;
      edge.b.fx -= dx / d * f; edge.b.fy -= dy / d * f;
    }
    memberLinks.forEach(function (e) { spring(e, e.b.prefDist || 145, 0.026); });
    crossLinks.forEach(function (e) { spring(e, 320, 0.0018); });

    // 3. 章节行星归位到宽椭圆 + 单元微弱外扩偏置
    chapters.forEach(function (ch, ci) {
      var hub = byNode['chapter:' + ch.slug]; if (!hub) return;
      var anc = hubAnchor(ci);
      hub.fx += (anc.x - hub.x) * 0.14;
      hub.fy += (anc.y - hub.y) * 0.14;
    });
    nodes.forEach(function (nn) {
      if (nn.kind === 'unit') {
        var hub = byNode['chapter:' + chapters[nn.ci].slug];
        if (hub) {
          var tx = hub.x + Math.cos(nn.prefAng) * nn.prefDist;
          var ty = hub.y + Math.sin(nn.prefAng) * nn.prefDist;
          nn.fx += (tx - nn.x) * 0.008;
          nn.fy += (ty - nn.y) * 0.008;
        }
      }
      if (nn.fixed) { nn.vx = nn.vy = 0; return; }
      nn.vx = (nn.vx + nn.fx * a) * 0.80;
      nn.vy = (nn.vy + nn.fy * a) * 0.80;
      nn.x += clamp(nn.vx, -16, 16);
      nn.y += clamp(nn.vy, -16, 16);
    });

    if (!force) alpha *= 0.985;
    needsDraw = true;
  }

  /* —— 视口与相机平滑飞行 —— */
  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    initStars();
    needsDraw = true;
  }
  function screen(x, y) { return { x: (x - cam.x) * cam.k + W / 2, y: (y - cam.y) * cam.k + H / 2 }; }
  function world(x, y) { return { x: (x - W / 2) / cam.k + cam.x, y: (y - H / 2) / cam.k + cam.y }; }

  function flyTo(tx, ty, tk, instant) {
    tk = clamp(tk, 0.16, 2.8);
    if (instant || reduce) {
      cam.x = tx; cam.y = ty; cam.k = tk; camAnim = null; needsDraw = true; return;
    }
    camAnim = { x0: cam.x, y0: cam.y, k0: cam.k, x1: tx, y1: ty, k1: tk, t0: performance.now(), dur: 460 };
    needsDraw = true;
  }

  function stepCam(now) {
    if (!camAnim) return;
    var u = clamp((now - camAnim.t0) / camAnim.dur, 0, 1);
    var e = 1 - Math.pow(1 - u, 3);
    cam.x = camAnim.x0 + (camAnim.x1 - camAnim.x0) * e;
    cam.y = camAnim.y0 + (camAnim.y1 - camAnim.y0) * e;
    cam.k = camAnim.k0 + (camAnim.k1 - camAnim.k0) * e;
    if (u >= 1) camAnim = null;
    needsDraw = true;
  }

  function fitNodes(list, instant, maxK) {
    if (!list || !list.length) return;
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    list.forEach(function (n) {
      x0 = Math.min(x0, n.x - n.r - 50); x1 = Math.max(x1, n.x + n.r + 50);
      y0 = Math.min(y0, n.y - n.r - 36); y1 = Math.max(y1, n.y + n.r + 36);
    });
    var pOff = panelOffset();
    var leftPad = W > 820 ? 185 : 52;
    var rightPad = W > 820 ? (pOff ? pOff * 2 + 36 : 56) : 52;
    var topPad = W > 820 ? 84 : 118;
    var botPad = W > 820 ? 44 : 84;
    var availW = Math.max(200, W - leftPad - rightPad);
    var availH = Math.max(200, H - topPad - botPad);
    var k = clamp(Math.min(availW / Math.max(1, x1 - x0), availH / Math.max(1, y1 - y0)), 0.18, maxK || 1.35);
    var cx = (x0 + x1) / 2 - (leftPad - rightPad) / (2 * k);
    var cy = (y0 + y1) / 2 - (topPad - botPad) / (2 * k);
    flyTo(cx, cy, k, instant);
  }

  function fit(reheat, instant) {
    if (reheat) alpha = Math.max(alpha, 0.35);
    fitNodes(nodes, instant, 1.15);
  }

  function focusCameraOn(target) {
    if (!target) return;
    if (target.kind === 'chapter') {
      var list = [target].concat(nodes.filter(function (n) { return n.kind === 'unit' && n.ci === target.ci; }));
      fitNodes(list, false, 1.45);
    } else if (target.kind === 'unit') {
      var pOff = panelOffset();
      var k = Math.max(cam.k, W > 820 ? 1.15 : 1.0);
      flyTo(target.x + pOff / k, target.y, k, false);
    } else if (target.a && target.b) {
      fitNodes([target.a, target.b], false, 1.35);
    }
  }

  /* —— 高亮关系计算（精确到直接邻接，不再误亮无关边） —— */
  function getFocus() {
    if (state.hoverNode) return { kind: 'node', node: state.hoverNode };
    if (state.hoverLink) return { kind: 'link', link: state.hoverLink };
    if (state.unit && byNode['unit:' + state.unit]) return { kind: 'node', node: byNode['unit:' + state.unit] };
    if (state.link) return { kind: 'link', link: state.link };
    if (state.chapter && byNode['chapter:' + state.chapter.slug]) return { kind: 'node', node: byNode['chapter:' + state.chapter.slug] };
    return null;
  }

  function isEdgeHot(e, foc) {
    if (!foc) return false;
    if (foc.kind === 'link') return e.data && e.data.id === foc.link.id;
    var f = foc.node;
    if (e.type === 'member') {
      if (f.kind === 'chapter') return e.a === f;
      if (f.kind === 'unit') return e.b === f;
      return false;
    }
    // 跨章/单元关联边
    if (f.kind === 'unit') return e.a === f || e.b === f;
    if (f.kind === 'chapter') return e.a.ci === f.ci || e.b.ci === f.ci;
    return false;
  }

  function isNodeHot(n, foc) {
    if (!foc) return true;
    if (foc.kind === 'link') return n.kind === 'unit' && (n.id === foc.link.from || n.id === foc.link.to);
    var f = foc.node;
    if (n === f) return true;
    if (f.kind === 'chapter') {
      if (n.kind === 'unit' && n.ci === f.ci) return true;
      return crossLinks.some(function (e) {
        if (!filterTypes[e.type]) return false;
        return (e.a.ci === f.ci && e.b === n) || (e.b.ci === f.ci && e.a === n);
      });
    }
    if (f.kind === 'unit') {
      if (n.kind === 'chapter' && n.ci === f.ci) return true;
      return crossLinks.some(function (e) {
        if (!filterTypes[e.type]) return false;
        return (e.a === f && e.b === n) || (e.b === f && e.a === n);
      });
    }
    return false;
  }

  /* —— 几何与绘制 —— */
  function bezier(e) {
    var ax = e.a.x, ay = e.a.y, bx = e.b.x, by = e.b.y;
    var dx = bx - ax, dy = by - ay, d = Math.hypot(dx, dy) || 1;
    var bend = Math.min(52, d * 0.14) * ((e.a.id < e.b.id) ? 1 : -1);
    return { x0: ax, y0: ay, cx: (ax + bx) / 2 - dy / d * bend, cy: (ay + by) / 2 + dx / d * bend, x1: bx, y1: by };
  }
  function bezPoint(b, t) {
    var u = 1 - t;
    return { x: u * u * b.x0 + 2 * u * t * b.cx + t * t * b.x1, y: u * u * b.y0 + 2 * u * t * b.cy + t * t * b.y1 };
  }

  function drawStars(now) {
    var t = now * 0.001;
    var px = -cam.x * 0.04, py = -cam.y * 0.04;
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      var sx = ((s.x * W + px + (reduce ? 0 : t * 2.2)) % W + W) % W;
      var sy = ((s.y * H + py + (reduce ? 0 : t * 0.6)) % H + H) % H;
      var tw = reduce ? 1 : (0.62 + 0.38 * Math.sin(t * s.sp + s.ph));
      ctx.globalAlpha = s.a * tw;
      ctx.fillStyle = s.c;
      ctx.beginPath();
      ctx.arc(sx, sy, s.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function drawEdge(e, foc, now) {
    var b = bezier(e);
    var s0 = screen(b.x0, b.y0), sc = screen(b.cx, b.cy), s1 = screen(b.x1, b.y1);
    var hot = foc ? isEdgeHot(e, foc) : false;
    var dim = foc && !hot;

    if (e.type === 'member') {
      // 章-单元隶属线：柔和渐变细实线（无虚线）
      var gm = ctx.createLinearGradient(s0.x, s0.y, s1.x, s1.y);
      var ma = dim ? 0.05 : (hot ? 0.48 : 0.22);
      gm.addColorStop(0, hexA(e.a.color, ma * 1.15));
      gm.addColorStop(1, hexA(e.a.color, ma * 0.45));
      ctx.beginPath();
      ctx.moveTo(s0.x, s0.y);
      ctx.quadraticCurveTo(sc.x, sc.y, s1.x, s1.y);
      ctx.lineWidth = (hot ? 1.6 : 1.0) * clamp(cam.k, 0.7, 1.3);
      ctx.strokeStyle = gm;
      ctx.stroke();
      return;
    }

    var ty = typeOf(e.type);
    var kScale = clamp(cam.k, 0.65, 1.35);
    var baseAlpha = dim ? 0.08 : (hot ? 0.94 : 0.54);
    ctx.save();
    if (hot) { ctx.shadowColor = hexA(ty.color, 0.72); ctx.shadowBlur = 10; }

    if (e.type === 'method') {
      // 同题异法：清晰双轨平行弧线（同一问题、两条路线）
      var dx = s1.x - s0.x, dy = s1.y - s0.y, d = Math.hypot(dx, dy) || 1;
      var nx = -dy / d * (hot ? 2.4 : 1.9), ny = dx / d * (hot ? 2.4 : 1.9);
      ctx.lineWidth = (hot ? 1.55 : 1.1) * kScale;
      ctx.strokeStyle = hexA(ty.color, baseAlpha);
      ctx.beginPath();
      ctx.moveTo(s0.x + nx, s0.y + ny); ctx.quadraticCurveTo(sc.x + nx, sc.y + ny, s1.x + nx, s1.y + ny);
      ctx.moveTo(s0.x - nx, s0.y - ny); ctx.quadraticCurveTo(sc.x - nx, sc.y - ny, s1.x - nx, s1.y - ny);
      ctx.stroke();
    } else if (e.type === 'limit') {
      // 极限对照：由粗渐亮实线 + 中点空心菱形标记
      var gl = ctx.createLinearGradient(s0.x, s0.y, s1.x, s1.y);
      gl.addColorStop(0, hexA(ty.color, baseAlpha));
      gl.addColorStop(1, hexA('#e6f6ff', baseAlpha * 0.75));
      ctx.beginPath();
      ctx.moveTo(s0.x, s0.y); ctx.quadraticCurveTo(sc.x, sc.y, s1.x, s1.y);
      ctx.lineWidth = (hot ? 2.3 : 1.5) * kScale;
      ctx.strokeStyle = gl;
      ctx.stroke();
      if (!dim && cam.k > 0.4) {
        var pm = screen(bezPoint(b, 0.5).x, bezPoint(b, 0.5).y);
        var ds = hot ? 5.2 : 4.0;
        ctx.fillStyle = '#060c1c';
        ctx.strokeStyle = hexA(ty.color, hot ? 0.98 : 0.85);
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(pm.x, pm.y - ds); ctx.lineTo(pm.x + ds, pm.y);
        ctx.lineTo(pm.x, pm.y + ds); ctx.lineTo(pm.x - ds, pm.y);
        ctx.closePath(); ctx.fill(); ctx.stroke();
      }
    } else if (e.type === 'tool') {
      // 共用工具：清晰细实线 + 中点实心光珠
      ctx.beginPath();
      ctx.moveTo(s0.x, s0.y); ctx.quadraticCurveTo(sc.x, sc.y, s1.x, s1.y);
      ctx.lineWidth = (hot ? 2.1 : 1.25) * kScale;
      ctx.strokeStyle = hexA(ty.color, baseAlpha * 0.9);
      ctx.stroke();
      if (!dim && cam.k > 0.42) {
        var pt2 = screen(bezPoint(b, 0.5).x, bezPoint(b, 0.5).y);
        ctx.fillStyle = hexA(ty.color, hot ? 1 : 0.85);
        ctx.beginPath(); ctx.arc(pt2.x, pt2.y, hot ? 3.5 : 2.5, 0, Math.PI * 2); ctx.fill();
      }
    } else {
      // 前置路径（prereq）：实线 + 清晰实心方向箭头（from → to）
      ctx.beginPath();
      ctx.moveTo(s0.x, s0.y); ctx.quadraticCurveTo(sc.x, sc.y, s1.x, s1.y);
      ctx.lineWidth = (hot ? 2.5 : 1.65) * kScale;
      ctx.strokeStyle = hexA(ty.color, baseAlpha);
      ctx.stroke();
      if (!dim && cam.k > 0.36) {
        var p1 = bezPoint(b, 0.62), p0 = bezPoint(b, 0.54);
        var sp1 = screen(p1.x, p1.y), sp0 = screen(p0.x, p0.y);
        var ang = Math.atan2(sp1.y - sp0.y, sp1.x - sp0.x), sz = hot ? 9.5 : 7.5;
        ctx.fillStyle = hexA(ty.color, hot ? 1 : 0.92);
        ctx.beginPath();
        ctx.moveTo(sp1.x, sp1.y);
        ctx.lineTo(sp1.x - Math.cos(ang - 0.42) * sz, sp1.y - Math.sin(ang - 0.42) * sz);
        ctx.lineTo(sp1.x - Math.cos(ang + 0.42) * sz, sp1.y - Math.sin(ang + 0.42) * sz);
        ctx.closePath(); ctx.fill();
      }
    }
    ctx.restore();

    // 高亮边上的流动光点
    if (hot && !reduce) {
      var phase = ((now * 0.00042) + seeded(e.a.x + e.b.y)) % 1;
      var pt = bezPoint(b, phase);
      var sp = screen(pt.x, pt.y);
      ctx.save();
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = ty.color; ctx.shadowBlur = 10;
      ctx.beginPath(); ctx.arc(sp.x, sp.y, 2.8, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
  }

  function drawSaturnRing(p, r, alphaMul, front) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(-0.34);
    ctx.scale(1, 0.34);
    ctx.beginPath();
    ctx.arc(0, 0, r * 1.72, front ? 0 : Math.PI, front ? Math.PI : Math.PI * 2);
    ctx.lineWidth = Math.max(2, r * 0.28);
    ctx.strokeStyle = 'rgba(231,211,155,' + (0.48 * alphaMul) + ')';
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, r * 1.44, front ? 0 : Math.PI, front ? Math.PI : Math.PI * 2);
    ctx.lineWidth = Math.max(1.2, r * 0.11);
    ctx.strokeStyle = 'rgba(255,240,200,' + (0.36 * alphaMul) + ')';
    ctx.stroke();
    ctx.restore();
  }

  function drawPlanet(n, p, r, dim, isSelected, now) {
    var im = textures[n.ch.texture];
    var am = dim ? 0.25 : 1;

    // 外圈轨道刻度环
    ctx.save();
    ctx.beginPath();
    ctx.arc(p.x, p.y, r + 7, 0, Math.PI * 2);
    ctx.strokeStyle = hexA(n.color, isSelected ? 0.85 : (dim ? 0.12 : 0.36));
    ctx.lineWidth = isSelected ? 2 : 1.1;
    if (!isSelected) ctx.setLineDash([4, 6]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    if (n.isSaturn) drawSaturnRing(p, r, am, false);

    // 球体 + 纹理自转 + 光照 + 临边昏暗
    ctx.save();
    ctx.globalAlpha = dim ? 0.35 : 1;
    ctx.shadowColor = hexA(n.color, isSelected ? 0.75 : 0.45);
    ctx.shadowBlur = isSelected ? 32 : 22;
    ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2); ctx.fillStyle = '#080c18'; ctx.fill();
    ctx.shadowBlur = 0;

    if (im && im.complete && im.naturalWidth) {
      ctx.save();
      ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2); ctx.clip();
      var shift = reduce ? 0 : ((now * 0.001 * n.spinSpeed) % 1) * (r * 4);
      var dw = r * 4, dh = r * 2;
      ctx.drawImage(im, p.x - r - shift, p.y - r, dw, dh);
      ctx.drawImage(im, p.x - r - shift + dw, p.y - r, dw, dh);
      // 太阳方向高光与暗面
      var gr = ctx.createRadialGradient(p.x - r * 0.38, p.y - r * 0.38, r * 0.12, p.x, p.y, r * 1.12);
      gr.addColorStop(0, 'rgba(255,255,255,.22)');
      gr.addColorStop(0.55, 'rgba(0,0,0,.06)');
      gr.addColorStop(1, 'rgba(2,5,14,.78)');
      ctx.fillStyle = gr;
      ctx.fillRect(p.x - r, p.y - r, r * 2, r * 2);
      ctx.restore();
    } else {
      var g2 = ctx.createRadialGradient(p.x - r * 0.35, p.y - r * 0.35, 1, p.x, p.y, r);
      g2.addColorStop(0, hexA(n.color, 0.95));
      g2.addColorStop(1, hexA(n.color, 0.28));
      ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2); ctx.fill();
    }

    // 大气边缘高光
    ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.strokeStyle = hexA(n.color, isSelected ? 0.95 : 0.6);
    ctx.lineWidth = isSelected ? 2 : 1.2;
    ctx.stroke();
    ctx.restore();

    if (n.isSaturn) drawSaturnRing(p, r, am, true);
  }

  /* —— 标签碰撞系统（8 方位候选 + 暗底微胶囊） —— */
  var labelBoxes = [];
  function reserveCircle(p, r) {
    labelBoxes.push({ l: p.x - r - 2, r: p.x + r + 2, t: p.y - r - 2, b: p.y + r + 2 });
  }
  function boxFree(b) {
    for (var i = 0; i < labelBoxes.length; i++) {
      var o = labelBoxes[i];
      if (!(b.r < o.l - 2 || b.l > o.r + 2 || b.b < o.t - 2 || b.t > o.b + 2)) return false;
    }
    return true;
  }
  function drawPillLabel(x, y, text, size, alphaVal, bold, accent, forcePlace, rNode) {
    var s = String(text).length > 16 ? String(text).slice(0, 15) + '…' : String(text);
    ctx.font = (bold ? '600 ' : '500 ') + size + 'px "Noto Sans CJK SC",system-ui,sans-serif';
    var w = ctx.measureText(s).width;
    var padX = bold ? 7 : 5, padY = bold ? 3 : 2;
    var bw = w + padX * 2, bh = size + padY * 2;
    var off = (rNode || 10) + bh / 2 + 5;

    var cands = bold
      ? [[x, y + off], [x, y - off]]
      : [
          [x, y + off],
          [x, y - off],
          [x + (rNode || 10) + bw / 2 + 6, y],
          [x - (rNode || 10) - bw / 2 - 6, y],
          [x + bw * 0.35, y + off + 4],
          [x - bw * 0.35, y + off + 4],
          [x + bw * 0.35, y - off - 4],
          [x - bw * 0.35, y - off - 4]
        ];

    var chosen = null;
    for (var i = 0; i < cands.length; i++) {
      var cx = cands[i][0], cy = cands[i][1];
      var box = { l: cx - bw / 2, r: cx + bw / 2, t: cy - bh / 2, b: cy + bh / 2, cx: cx, cy: cy };
      if (boxFree(box)) { chosen = box; break; }
    }
    if (!chosen) {
      if (!forcePlace) return;
      chosen = { l: x - bw / 2, r: x + bw / 2, t: y + off - bh / 2, b: y + off + bh / 2, cx: x, cy: y + off };
    }
    labelBoxes.push(chosen);

    // 暗底圆角胶囊（提升可读性，不抢星图）
    ctx.save();
    ctx.globalAlpha = alphaVal;
    ctx.fillStyle = bold ? 'rgba(5,9,22,.78)' : 'rgba(5,9,22,.62)';
    var rad = bh / 2;
    ctx.beginPath();
    ctx.roundRect ? ctx.roundRect(chosen.l, chosen.t, bw, bh, rad) : ctx.rect(chosen.l, chosen.t, bw, bh);
    ctx.fill();
    if (bold && accent) {
      ctx.strokeStyle = hexA(accent, 0.45);
      ctx.lineWidth = 1;
      ctx.stroke();
    }
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = bold ? '#f4f7ff' : '#dce6ff';
    ctx.fillText(s, chosen.cx, chosen.cy + 0.5);
    ctx.restore();
  }

  function draw(now) {
    tNow = now;
    stepCam(now);
    // 背景星云轻微视差
    if (cosmosBg && !reduce) {
      var px = clamp(-cam.x * 0.025, -28, 28);
      var py = clamp(-cam.y * 0.025, -28, 28);
      cosmosBg.style.transform = 'translate3d(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px,0)';
    }

    ctx.clearRect(0, 0, W, H);
    drawStars(now);

    var foc = getFocus();

    // 1. 章节星云光晕
    nodes.forEach(function (n) {
      if (n.kind !== 'chapter') return;
      var p = screen(n.x, n.y), R = 210 * cam.k;
      if (p.x < -R || p.x > W + R || p.y < -R || p.y > H + R) return;
      var hot = isNodeHot(n, foc);
      var halo = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, R);
      halo.addColorStop(0, hexA(n.color, foc ? (hot ? 0.18 : 0.04) : 0.13));
      halo.addColorStop(1, hexA(n.color, 0));
      ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(p.x, p.y, R, 0, Math.PI * 2); ctx.fill();
    });

    // 2. 连线（先暗后亮）
    memberLinks.forEach(function (e) { drawEdge(e, foc, now); });
    var dimEdges = [], hotEdges = [];
    crossLinks.forEach(function (e) {
      if (!filterTypes[e.type]) return;
      if (foc && isEdgeHot(e, foc)) hotEdges.push(e); else dimEdges.push(e);
    });
    dimEdges.forEach(function (e) { drawEdge(e, foc, now); });
    hotEdges.forEach(function (e) { drawEdge(e, foc, now); });

    // 3. 节点本体 + 预留碰撞圆
    labelBoxes = [];
    var visibleUnits = [];
    var visibleChapters = [];

    nodes.forEach(function (n) {
      var p = screen(n.x, n.y), r = Math.max(3, n.r * cam.k);
      if (p.x < -90 || p.x > W + 90 || p.y < -90 || p.y > H + 90) return;
      reserveCircle(p, r + (n.kind === 'chapter' ? 6 : 2));
      var hot = isNodeHot(n, foc);
      var dim = foc && !hot;
      var selected = (state.unit && n.kind === 'unit' && n.id === state.unit) ||
                     (state.chapter && !state.unit && n.kind === 'chapter' && n.id === state.chapter.slug) ||
                     (state.hoverNode === n);

      if (n.kind === 'chapter') {
        drawPlanet(n, p, r, dim, selected, now);
        visibleChapters.push({ n: n, p: p, r: r, dim: dim, selected: selected });
      } else {
        ctx.save();
        if (selected || (foc && hot)) {
          ctx.shadowColor = hexA(n.color, 0.85);
          ctx.shadowBlur = selected ? 18 : 11;
        }
        var g = ctx.createRadialGradient(p.x - r * 0.35, p.y - r * 0.35, 0.5, p.x, p.y, r * 1.15);
        g.addColorStop(0, '#ffffff');
        g.addColorStop(0.28, hexA(n.color, dim ? 0.35 : 0.98));
        g.addColorStop(1, hexA(n.color, dim ? 0.12 : 0.55));
        ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
        ctx.fillStyle = g; ctx.fill();
        ctx.lineWidth = selected ? 2.2 : 1.1;
        ctx.strokeStyle = selected ? '#ffffff' : hexA(n.color, dim ? 0.18 : 0.85);
        ctx.stroke();
        ctx.restore();

        if (n.fixed) {
          ctx.save();
          ctx.strokeStyle = 'rgba(255,255,255,.75)';
          ctx.setLineDash([2.5, 3]);
          ctx.beginPath(); ctx.arc(p.x, p.y, r + 4.5, 0, Math.PI * 2); ctx.stroke();
          ctx.restore();
        }
        visibleUnits.push({ n: n, p: p, r: r, dim: dim, hot: hot, selected: selected });
      }
    });

    // 4. 统一绘制标签（章标题最优先 → 选中/高亮单元 → 其余单元）
    visibleChapters.forEach(function (it) {
      if (W <= 820 && panel.classList.contains('open')) return;
      drawPillLabel(it.p.x, it.p.y, it.n.label, 13, it.dim ? 0.32 : 1, true, it.n.color, true, it.r + 3);
    });
    visibleUnits.sort(function (a, b) {
      return (b.selected ? 100 : 0) + (b.hot ? 10 : 0) - ((a.selected ? 100 : 0) + (a.hot ? 10 : 0));
    });
    visibleUnits.forEach(function (it) {
      var show = it.selected || (foc && it.hot) || cam.k > 0.38;
      if (!show) return;
      var txt = it.n.id + ' ' + it.n.short;
      drawPillLabel(it.p.x, it.p.y, txt, it.selected ? 12 : 11, it.dim ? 0.22 : 0.95, it.selected, it.n.color, it.selected || (foc && it.hot), it.r);
    });
  }

  function loop(now) {
    tick(false);
    // 星空闪烁 / 行星自转 / 流动光点在非 reduced-motion 下持续轻绘
    if (!reduce || needsDraw || camAnim || alpha > 0.015) {
      needsDraw = false;
      draw(now || performance.now());
    }
    raf = requestAnimationFrame(loop);
  }

  /* —— 命中测试与指针交互 —— */
  function hitTest(sx, sy) {
    var w = world(sx, sy), best = null, bd = Infinity;
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      var d = Math.hypot(n.x - w.x, n.y - w.y), lim = n.r + 10 / cam.k;
      if (d < lim && d < bd) { bd = d; best = n; }
    }
    if (best) return { node: best };
    var tol = 10 / cam.k;
    for (var k = 0; k < crossLinks.length; k++) {
      var e = crossLinks[k]; if (!filterTypes[e.type]) continue;
      var b = bezier(e);
      for (var t = 0.08; t <= 0.92; t += 0.07) {
        var p = bezPoint(b, t);
        if (Math.hypot(p.x - w.x, p.y - w.y) < tol) return { link: e.data };
      }
    }
    return null;
  }

  var pointers = {}, drag = null, pinch = null;
  canvas.addEventListener('pointerdown', function (ev) {
    if (ev.button > 0) return;
    canvas.setPointerCapture && canvas.setPointerCapture(ev.pointerId);
    camAnim = null;
    pointers[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
    var keys = Object.keys(pointers);
    if (keys.length === 2) {
      var a = pointers[keys[0]], b = pointers[keys[1]];
      pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), k: cam.k, cx: (a.x + b.x) / 2, cy: (a.y + b.y) / 2 };
      drag = null; return;
    }
    var hit = hitTest(ev.clientX, ev.clientY);
    drag = { id: ev.pointerId, x: ev.clientX, y: ev.clientY, moved: 0, hit: hit, node: hit && hit.node };
    canvas.classList.add('dragging');
  });

  canvas.addEventListener('pointermove', function (ev) {
    if (pointers[ev.pointerId]) { pointers[ev.pointerId].x = ev.clientX; pointers[ev.pointerId].y = ev.clientY; }
    if (pinch && Object.keys(pointers).length >= 2) {
      var ks = Object.keys(pointers), a = pointers[ks[0]], b = pointers[ks[1]];
      var d = Math.hypot(a.x - b.x, a.y - b.y);
      var wx = world(pinch.cx, pinch.cy);
      cam.k = clamp(pinch.k * d / Math.max(1, pinch.d), 0.22, 3.0);
      var nowW = world(pinch.cx, pinch.cy);
      cam.x += wx.x - nowW.x; cam.y += wx.y - nowW.y;
      needsDraw = true; return;
    }
    if (drag && drag.id === ev.pointerId) {
      var dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
      drag.moved += Math.abs(dx) + Math.abs(dy);
      if (drag.node) {
        if (drag.moved >= 6) {
          drag.node.fixed = true;
          var w = world(ev.clientX, ev.clientY);
          drag.node.x = w.x; drag.node.y = w.y; drag.node.vx = drag.node.vy = 0;
          alpha = Math.max(alpha, 0.25);
        }
      } else {
        cam.x -= dx / cam.k; cam.y -= dy / cam.k;
      }
      drag.x = ev.clientX; drag.y = ev.clientY; needsDraw = true; return;
    }

    var h = hitTest(ev.clientX, ev.clientY), n = h && h.node, lk = h && h.link;
    var key = n ? n.kind + ':' + n.id : (lk ? 'link:' + lk.id : '');
    if (key !== state.hover) {
      state.hover = key; state.hoverNode = n || null; state.hoverLink = lk || null; needsDraw = true;
      canvas.classList.toggle('hovering', !!key);
      if (n) {
        var kText = n.kind === 'chapter'
          ? ('第 ' + n.ch.n + ' 章 · ' + unitCount(n.ch) + ' 个交互单元')
          : (n.id + ' · ' + (chapterOf(n.id) ? chapterOf(n.id).title : '') + ' · ' + n.count + ' 个知识节点');
        var desc = n.kind === 'chapter' ? n.ch.summary : C.plain(n.mod.summary || '');
        tip.innerHTML = '<b>' + esc(n.label) + '</b><span class="k">' + esc(kText) + '</span><div class="d">' + esc(String(desc).slice(0, 110)) + '</div>';
        tip.hidden = false;
      } else if (lk) {
        var dirSym = lk.type === 'prereq' ? ' → ' : ' ↔ ';
        tip.innerHTML = '<b>' + esc(C.plain(lk.title)) + '</b><span class="k">' + esc(typeOf(lk.type).label + ' · ' + lk.from + dirSym + lk.to) + '</span><div class="d">' + esc(C.plain(lk.note || '').slice(0, 110)) + '</div>';
        tip.hidden = false;
      } else tip.hidden = true;
    }
    if (!tip.hidden) {
      tip.style.left = clamp(ev.clientX + 16, 12, W - 324) + 'px';
      tip.style.top = clamp(ev.clientY + 14, 70, H - 120) + 'px';
    }
  });

  function endPointer(ev) {
    delete pointers[ev.pointerId];
    if (pinch && Object.keys(pointers).length < 2) pinch = null;
    if (drag && drag.id === ev.pointerId) {
      if (drag.moved < 6) {
        if (drag.node) {
          if (drag.node.kind === 'unit') go('#/u/' + drag.node.id);
          else if (drag.node.kind === 'chapter') go('#/c/' + drag.node.id);
        } else if (drag.hit && drag.hit.link) {
          go('#/l/' + drag.hit.link.id);
        } else if (panel.classList.contains('open')) {
          go('#/');
        }
      }
      drag = null;
    }
    canvas.classList.remove('dragging');
  }
  canvas.addEventListener('pointerup', endPointer);
  canvas.addEventListener('pointercancel', endPointer);
  canvas.addEventListener('pointerleave', function () {
    tip.hidden = true; state.hover = null; state.hoverNode = null; state.hoverLink = null; needsDraw = true;
  });

  canvas.addEventListener('dblclick', function (ev) {
    var h = hitTest(ev.clientX, ev.clientY);
    if (!h || !h.node) { fit(false, false); return; }
    if (h.node.fixed) {
      h.node.fixed = false; alpha = Math.max(alpha, 0.3);
      showNotice('已解除固定', h.node.label);
    } else {
      focusCameraOn(h.node);
    }
  });

  canvas.addEventListener('wheel', function (ev) {
    ev.preventDefault();
    camAnim = null;
    var p = world(ev.clientX, ev.clientY);
    cam.k = clamp(cam.k * Math.exp(-ev.deltaY * 0.0013), 0.22, 3.0);
    var q2 = world(ev.clientX, ev.clientY);
    cam.x += p.x - q2.x; cam.y += p.y - q2.y;
    needsDraw = true;
  }, { passive: false });

  function zoomBy(factor) {
    flyTo(cam.x, cam.y, cam.k * factor, false);
  }

  function syncPlaceholder() {
    q.placeholder = W <= 540 ? '搜索单元、小节或公式' : '搜索单元、小节、概念或公式（按 / 聚焦）';
  }
  window.addEventListener('resize', function () { resize(); syncPlaceholder(); needsDraw = true; });

  /* —— MathJax 懒加载与安全单公式排版 —— */
  function ensureMath() {
    if (!mathPromise) {
      mathPromise = new Promise(function (res) {
        function done() {
          if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
            window.MathJax.startup.promise.then(function () {
              try {
                if (window.MathJax.svgStylesheet && !document.getElementById('mjx-svg-styles')) {
                  var st = window.MathJax.svgStylesheet();
                  if (st) { st.id = 'mjx-svg-styles'; document.head.appendChild(st); }
                }
              } catch (e) {}
              res(window.MathJax);
            }, function () { res(null); });
          } else res(null);
        }
        if (window.MathJax && window.MathJax.tex2svgPromise) { done(); return; }
        var s = document.createElement('script'); s.src = '../assets/mathjax/tex-svg.js'; s.async = true;
        s.onload = done; s.onerror = function () { res(null); }; document.head.appendChild(s);
      });
    }
    return mathPromise;
  }

  function inlineInto(el, str) {
    var parts = C.splitInline(str || '');
    var pending = [];
    parts.forEach(function (p) {
      if (p.t === 'text') {
        el.appendChild(document.createTextNode(p.v));
        return;
      }
      var span = document.createElement('span'); span.className = 'mx'; span.textContent = '$' + p.v + '$';
      el.appendChild(span); stats.mathTotal++; pending.push({ el: span, tex: p.v, display: false });
    });
    return pending;
  }

  function fallback(p) {
    var code = document.createElement('code'); code.className = 'tex-fallback'; code.textContent = p.tex;
    if (p.el.replaceWith) p.el.replaceWith(code);
    stats.mathFallback++;
  }

  function typesetAll(pending) {
    if (!pending.length) return;
    ensureMath().then(function (M) {
      pending.forEach(function (p) {
        if (!M || !M.tex2svgPromise) { fallback(p); return; }
        M.tex2svgPromise(p.tex, { display: !!p.display }).then(function (node) {
          if (node && node.firstChild && !node.querySelector('[data-mml-node="merror"]')) {
            p.el.replaceWith(node); stats.mathRendered++;
          } else fallback(p);
        }).catch(function () { fallback(p); });
      });
    }, function () { pending.forEach(fallback); });
  }

  function blocksInto(host, chunks, hiCid) {
    var pending = [];
    chunks.forEach(function (c) {
      var box = document.createElement('div');
      box.className = 'chunk' + (hiCid && c.id === hiCid ? ' hilite' : '');
      box.dataset.cid = c.id;
      var blocks = C.parse(c.text || '');
      blocks.forEach(function (b) {
        if (b.t === 'h') {
          var h = document.createElement('h4'); pending.push.apply(pending, inlineInto(h, b.text)); box.appendChild(h);
        } else if (b.t === 'math') {
          var d = document.createElement('div'); d.className = 'disp';
          var s = document.createElement('span'); s.className = 'mx'; s.textContent = '$$' + b.tex + '$$';
          d.appendChild(s); box.appendChild(d); stats.mathTotal++; pending.push({ el: s, tex: b.tex, display: true });
        } else if (b.t === 'list') {
          var ul = document.createElement('ul');
          b.items.forEach(function (it) { var li = document.createElement('li'); pending.push.apply(pending, inlineInto(li, it)); ul.appendChild(li); });
          box.appendChild(ul);
        } else if (b.t === 'table') {
          var tb = document.createElement('table');
          b.rows.forEach(function (row, ri) {
            var tr = document.createElement('tr');
            row.forEach(function (cell) {
              var td = document.createElement(ri === 0 ? 'th' : 'td');
              pending.push.apply(pending, inlineInto(td, cell));
              tr.appendChild(td);
            });
            tb.appendChild(tr);
          });
          box.appendChild(tb);
        } else {
          var p = document.createElement('p'); pending.push.apply(pending, inlineInto(p, b.text)); box.appendChild(p);
        }
      });
      if (!blocks.length) { var p2 = document.createElement('p'); p2.textContent = c.text || ''; box.appendChild(p2); }
      host.appendChild(box);
    });
    typesetAll(pending);
  }

  /* —— 面板渲染 —— */
  function btn(label, cls, fn, style) {
    var b = document.createElement('button'); b.type = 'button'; b.className = cls || '';
    b.textContent = label; b.addEventListener('click', fn);
    if (style) Object.keys(style).forEach(function (k) { b.style.setProperty(k, style[k]); });
    return b;
  }
  function linkBtn(label, href, primary) {
    var a = document.createElement('a'); a.href = href; a.textContent = label;
    if (primary) a.className = 'primary';
    return a;
  }
  function acts(host, items) {
    var d = document.createElement('div'); d.className = 'acts';
    items.forEach(function (x) { d.appendChild(x); });
    host.appendChild(d);
  }
  function title3(host, text) { var h = document.createElement('h3'); h.textContent = text; host.appendChild(h); }
  function openPanel(kickerHtml, title) {
    pKicker.innerHTML = kickerHtml;
    pTitle.textContent = title;
    pBody.textContent = '';
    panel.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');
    document.body.classList.add('panel-open');
    pScroll.scrollTop = 0;
  }

  function renderLinkList(host, arr, curMid) {
    var d = document.createElement('div'); d.className = 'xlinks';
    var pending = [];
    arr.forEach(function (l) {
      var b = btn('', 'xlink', function () { go('#/l/' + l.id); });
      var top = document.createElement('div'); top.className = 'x-top';
      var badge = document.createElement('span'); badge.className = 'badge';
      badge.textContent = typeOf(l.type).label; badge.style.setProperty('--tc', typeOf(l.type).color);
      top.appendChild(badge);
      var sym = l.type === 'prereq' ? ' → ' : ' ↔ ';
      var to = document.createElement('span'); to.className = 'to';
      if (curMid) {
        var other = l.from === curMid ? l.to : l.from;
        var om = modules[other];
        to.textContent = (l.type === 'prereq' ? (l.from === curMid ? '后续 ' : '前置 ') : '↔ ') + other + (om ? ' ' + shortTitle(om.title) : '');
      } else {
        to.textContent = l.from + sym + l.to;
      }
      top.appendChild(to); b.appendChild(top);
      var tt = document.createElement('span'); tt.className = 'tt';
      pending.push.apply(pending, inlineInto(tt, l.title));
      b.appendChild(tt);
      if (l.note) {
        var nt = document.createElement('span'); nt.className = 'nt';
        pending.push.apply(pending, inlineInto(nt, l.note));
        b.appendChild(nt);
      }
      d.appendChild(b);
    });
    if (arr.length) {
      host.appendChild(d);
      typesetAll(pending);
    }
  }

  function renderLanding() {
    openPanel('理论力学 · 知识网络', '七章行星星座与跨章脉络');
    var p = document.createElement('p'); p.className = 'summary';
    p.textContent = '共 ' + chapters.length + ' 章、' + unitIds.length + ' 个交互单元、' + chunksOfAll().length + ' 个知识节点与 ' + links.length + ' 条跨章关联。点击任意行星或单元可平滑聚焦并直接阅读带公式的书稿推导；点左下角图例可按关联类型筛选。';
    pBody.appendChild(p);
    title3(pBody, '从章节进入');
    var wrap = document.createElement('div'); wrap.className = 'units';
    chapters.forEach(function (ch) {
      var b = btn('', 'unit-btn', function () { go('#/c/' + ch.slug); }, { '--c': ch.color });
      var bb = document.createElement('b'); bb.textContent = 'C' + ch.n; b.appendChild(bb);
      b.appendChild(document.createTextNode(ch.title));
      var s = document.createElement('small'); s.textContent = unitCount(ch) + ' 单元'; b.appendChild(s);
      wrap.appendChild(b);
    });
    pBody.appendChild(wrap);
    title3(pBody, '精选跨章关联');
    renderLinkList(pBody, links.slice(0, 6));
  }

  function renderChapter(ch) {
    openPanel('<span class="chip" style="--c:' + ch.color + '">第 ' + ch.n + ' 章</span>', ch.title);
    var p = document.createElement('p'); p.className = 'summary'; p.textContent = ch.summary || ''; pBody.appendChild(p);
    acts(pBody, [linkBtn('打开本章讲义 ↗', '../' + chapterDir(ch) + '/index.html', true)]);
    title3(pBody, '本章交互单元 · ' + unitCount(ch));
    var wrap = document.createElement('div'); wrap.className = 'units';
    (ch.modules || []).forEach(function (mid) {
      var m = modules[mid]; if (!m) return;
      var b = btn('', 'unit-btn', function () { go('#/u/' + mid); }, { '--c': ch.color });
      var bb = document.createElement('b'); bb.textContent = mid; b.appendChild(bb);
      b.appendChild(document.createTextNode(m.title));
      var s = document.createElement('small'); s.textContent = chunksOf(mid).length + ' 节'; b.appendChild(s);
      wrap.appendChild(b);
    });
    pBody.appendChild(wrap);
    var chLinks = links.filter(function (l) {
      var c1 = chapterOf(l.from), c2 = chapterOf(l.to);
      return (c1 && c1.slug === ch.slug) || (c2 && c2.slug === ch.slug);
    });
    if (chLinks.length) {
      title3(pBody, '关联脉络 · ' + chLinks.length);
      renderLinkList(pBody, chLinks.slice(0, 10));
    }
  }

  function renderUnit(mid, cid) {
    var m = modules[mid], ch = chapterOf(mid);
    if (!m) { state.unit = null; renderLanding(); return; }
    var cColor = ch ? ch.color : '#9fc5ff';
    var kicker = ch
      ? '<button type="button" class="chip" id="pChBtn" style="--c:' + cColor + '">第 ' + ch.n + ' 章 · ' + esc(ch.title) + '</button><span>/ ' + esc(mid) + '</span>'
      : '<span class="chip" style="--c:' + cColor + '">' + esc(mid) + '</span>';
    openPanel(kicker, m.title);
    var chBtn = $('pChBtn');
    if (chBtn && ch) chBtn.addEventListener('click', function () { go('#/c/' + ch.slug); });

    var p = document.createElement('p'); p.className = 'summary';
    typesetAll(inlineInto(p, m.summary || ''));
    pBody.appendChild(p);

    if ((m.tags || []).length) {
      var tags = document.createElement('div'); tags.className = 'tags';
      m.tags.forEach(function (t) { var s = document.createElement('span'); s.textContent = t; tags.appendChild(s); });
      pBody.appendChild(tags);
    }

    var btns = [];
    if (m.href) btns.push(linkBtn('进入交互模拟 ↗', '../' + m.href, true));
    if (m.pdf) btns.push(linkBtn('讲义 / PDF ↗', '../' + m.pdf));
    if (ch) btns.push(linkBtn('本章页 ↗', '../' + chapterDir(ch) + '/index.html'));
    if (btns.length) acts(pBody, btns);

    var lk = links.filter(function (l) { return l.from === mid || l.to === mid; });
    if (lk.length) {
      title3(pBody, '跨章关联 · ' + lk.length);
      renderLinkList(pBody, lk, mid);
    }

    var secs = m.sections || [];
    var hdRow = document.createElement('div'); hdRow.className = 'sec-hd-row';
    var h3 = document.createElement('h3'); h3.textContent = '知识节点 · ' + secs.length + ' 小节';
    hdRow.appendChild(h3);
    var allExpanded = false;
    var toggleAllBtn = btn('全部展开', 'mini-btn', function () {
      allExpanded = !allExpanded;
      toggleAllBtn.textContent = allExpanded ? '全部折叠' : '全部展开';
      secItems.forEach(function (it) { it.setOpen(allExpanded); });
    });
    if (secs.length > 1) hdRow.appendChild(toggleAllBtn);
    pBody.appendChild(hdRow);

    var secWrap = document.createElement('div'); secWrap.className = 'secs';
    var secItems = [];
    var targetIdx = -1;
    if (cid) {
      secs.forEach(function (sec, si) {
        if ((sec.chunks || []).some(function (c) { return c.id === cid; })) targetIdx = si;
      });
    }
    var defaultOpenIdx = targetIdx >= 0 ? targetIdx : 0;

    secs.forEach(function (sec, si) {
      var box = document.createElement('div'); box.className = 'sec';
      var body = document.createElement('div'); body.className = 'body';
      var rendered = false;

      function setOpen(on) {
        box.classList.toggle('open', on);
        if (on && !rendered) {
          rendered = true;
          blocksInto(body, sec.chunks || [], cid);
        }
      }

      var head = btn('', '', function () { setOpen(!box.classList.contains('open')); });
      var n = document.createElement('span'); n.className = 'n'; n.textContent = String(si + 1).padStart(2, '0'); head.appendChild(n);
      var nm = document.createElement('span'); nm.className = 'sname';
      typesetAll(inlineInto(nm, sec.name));
      head.appendChild(nm);
      if ((sec.chunks || []).length > 1) {
        var sc = document.createElement('span'); sc.className = 'scnt'; sc.textContent = sec.chunks.length + ' 段'; head.appendChild(sc);
      }
      var chv = document.createElement('span'); chv.className = 'chev'; chv.textContent = '›'; head.appendChild(chv);
      box.appendChild(head);
      box.appendChild(body);
      secWrap.appendChild(box);
      secItems.push({ box: box, setOpen: setOpen });

      if (si === defaultOpenIdx) setOpen(true);
    });
    pBody.appendChild(secWrap);

    if (cid) {
      var hi = secWrap.querySelector('.chunk.hilite') || secWrap.querySelector('.sec.open');
      if (hi) setTimeout(function () { hi.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' }); }, 60);
    }
  }

  function renderLink(l) {
    var t = typeOf(l.type);
    openPanel('<span class="chip" style="--c:' + t.color + '">' + esc(t.label) + '</span><span>/ ' + esc(l.id) + '</span>', '');
    typesetAll(inlineInto(pTitle, l.title));
    var p = document.createElement('p'); p.className = 'summary';
    typesetAll(inlineInto(p, l.note || t.desc || ''));
    pBody.appendChild(p);
    title3(pBody, '关联两端');
    var wrap = document.createElement('div'); wrap.className = 'units';
    [l.from, l.to].forEach(function (mid, idx) {
      var m = modules[mid], ch = chapterOf(mid); if (!m) return;
      var b = btn('', 'unit-btn', function () { go('#/u/' + mid); }, { '--c': ch ? ch.color : '#9fc5ff' });
      var bb = document.createElement('b'); bb.textContent = mid; b.appendChild(bb);
      b.appendChild(document.createTextNode(m.title));
      var s = document.createElement('small');
      s.textContent = (l.type === 'prereq' ? (idx === 0 ? '前置 · ' : '后续 · ') : '') + (ch ? ch.title : '');
      b.appendChild(s);
      wrap.appendChild(b);
    });
    pBody.appendChild(wrap);
  }

  function renderList(on) {
    state.list = !!on;
    $('listView').hidden = !on;
    $('btnList').setAttribute('aria-pressed', on ? 'true' : 'false');
    if (!on) return;
    var host = $('lvInner'); host.textContent = '';
    chapters.forEach(function (ch) {
      var d = document.createElement('div'); d.className = 'lv-ch'; d.style.setProperty('--c', ch.color);
      var h = document.createElement('h2'); h.textContent = 'C' + ch.n + ' · ' + ch.title; d.appendChild(h);
      var p = document.createElement('p'); p.textContent = ch.summary || ''; d.appendChild(p);
      (ch.modules || []).forEach(function (mid) {
        var m = modules[mid]; if (!m) return;
        var b = btn('', 'unit-btn', function () { renderList(false); go('#/u/' + mid); }, { '--c': ch.color });
        var bb = document.createElement('b'); bb.textContent = mid; b.appendChild(bb);
        b.appendChild(document.createTextNode(m.title));
        var small = document.createElement('small'); small.textContent = chunksOf(mid).length + ' 节'; b.appendChild(small);
        d.appendChild(b);
      });
      host.appendChild(d);
    });
    var lkSec = document.createElement('div'); lkSec.className = 'lv-full';
    title3(lkSec, '全部跨章关联 · ' + links.length);
    renderLinkList(lkSec, links);
    lkSec.querySelectorAll('.xlink').forEach(function (el) {
      el.addEventListener('click', function () { renderList(false); });
    });
    host.appendChild(lkSec);
  }

  /* —— 多关键词加权搜索（支持直达小节） —— */
  var searchIndex = null;
  function buildIndex() {
    if (searchIndex) return searchIndex;
    searchIndex = [];
    chapters.forEach(function (ch) {
      searchIndex.push({
        kind: 'chapter', id: ch.slug, color: ch.color,
        title: '第 ' + ch.n + ' 章 · ' + ch.title, sub: ch.summary || '',
        hash: '#/c/' + ch.slug,
        head: (ch.title + ' c' + ch.n).toLowerCase(),
        body: (ch.summary || '').toLowerCase()
      });
    });
    unitIds.forEach(function (mid) {
      var m = modules[mid], ch = chapterOf(mid); if (!m) return;
      var col = ch ? ch.color : '#7fe0ff';
      searchIndex.push({
        kind: 'unit', id: mid, color: col,
        title: mid + ' · ' + m.title, sub: C.plain(m.summary || ''),
        hash: '#/u/' + mid,
        head: (mid + ' ' + m.title + ' ' + (m.tags || []).join(' ')).toLowerCase(),
        body: C.plain(m.summary || '').toLowerCase()
      });
      (m.sections || []).forEach(function (sec) {
        var first = (sec.chunks || [])[0];
        if (!first) return;
        var txt = (sec.chunks || []).map(function (c) { return C.plain(c.text); }).join(' ');
        searchIndex.push({
          kind: 'section', id: first.id, color: col,
          title: sec.name, sub: mid + ' ' + shortTitle(m.title) + ' · ' + txt.slice(0, 70),
          hash: '#/u/' + mid + '/' + first.id,
          head: (sec.name + ' ' + mid + ' ' + m.title).toLowerCase(),
          body: txt.toLowerCase()
        });
      });
    });
    links.forEach(function (l) {
      var ty = typeOf(l.type);
      searchIndex.push({
        kind: 'link', id: l.id, color: ty.color,
        title: l.title, sub: l.from + ' ↔ ' + l.to + ' · ' + ty.label,
        hash: '#/l/' + l.id,
        head: (l.title + ' ' + l.id + ' ' + l.from + ' ' + l.to).toLowerCase(),
        body: C.plain(l.note || '').toLowerCase()
      });
    });
    return searchIndex;
  }

  function runSearch() {
    var raw = q.value.trim().toLowerCase();
    qres.textContent = '';
    if (!raw) { qres.hidden = true; return; }
    var toks = raw.split(/\s+/).filter(Boolean);
    var scored = [];
    buildIndex().forEach(function (x) {
      var sc = 0;
      for (var i = 0; i < toks.length; i++) {
        var tk = toks[i];
        var inH = x.head.indexOf(tk) >= 0;
        var inB = x.body.indexOf(tk) >= 0;
        if (!inH && !inB) return;
        sc += inH ? (x.kind === 'unit' ? 12 : x.kind === 'chapter' ? 10 : 8) : 2;
      }
      scored.push({ x: x, sc: sc });
    });
    scored.sort(function (a, b) { return b.sc - a.sc; });
    var hits = scored.slice(0, 14);
    if (!hits.length) {
      qres.hidden = false;
      var e = document.createElement('li'); e.textContent = '没有匹配的知识节点'; qres.appendChild(e); return;
    }
    var kindLabel = { unit: '单元', chapter: '章', section: '小节', link: '关联' };
    hits.forEach(function (it, idx) {
      var x = it.x;
      var li = document.createElement('li');
      li.setAttribute('role', 'option');
      li.setAttribute('aria-selected', idx === 0 ? 'true' : 'false');
      li.dataset.hash = x.hash;
      function markHit(t) {
        var s = esc(t);
        toks.forEach(function (tk) {
          if (!tk) return;
          var re = new RegExp('(' + tk.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig');
          s = s.replace(re, '<mark>$1</mark>');
        });
        return s;
      }
      var a = document.createElement('div'); a.className = 'r-t';
      a.innerHTML = '<span class="r-dot" style="--c:' + esc(x.color) + '"></span><span>' + markHit(x.title) + '</span><i>' + kindLabel[x.kind] + '</i>';
      li.appendChild(a);
      var s = document.createElement('div'); s.className = 'r-s'; s.innerHTML = markHit(x.sub); li.appendChild(s);
      li.addEventListener('click', function () { renderList(false); go(li.dataset.hash); qres.hidden = true; });
      qres.appendChild(li);
    });
    qres.hidden = false;
  }

  q.addEventListener('input', runSearch);
  q.addEventListener('keydown', function (ev) {
    var items = Array.prototype.slice.call(qres.querySelectorAll('li[data-hash]'));
    if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
      if (!items.length) return; ev.preventDefault();
      var cur = items.findIndex(function (x) { return x.getAttribute('aria-selected') === 'true'; });
      var next = clamp(cur + (ev.key === 'ArrowDown' ? 1 : -1), 0, items.length - 1);
      items.forEach(function (x, k) { x.setAttribute('aria-selected', k === next ? 'true' : 'false'); });
      items[next].scrollIntoView({ block: 'nearest' });
    } else if (ev.key === 'Enter' && items.length) {
      ev.preventDefault();
      var sel = items.find(function (x) { return x.getAttribute('aria-selected') === 'true'; }) || items[0];
      renderList(false); go(sel.dataset.hash); qres.hidden = true; q.blur();
    } else if (ev.key === 'Escape') { qres.hidden = true; q.blur(); }
  });
  document.addEventListener('click', function (ev) { if (!ev.target.closest('.search')) qres.hidden = true; });

  /* —— 路由（完全兼容旧版 #/chapter-01-newton/m0） —— */
  var LEGACY = {
    'chapter-01-particle': 'chapter-01-newton', 'chapter-02-system': 'chapter-02-variational',
    'chapter-03-variational': 'chapter-03-lagrangian', 'chapter-04-lagrangian': 'chapter-04-oscillations',
    'chapter-05-oscillations': 'chapter-05-rigid-body', 'chapter-06-rigid-body': 'chapter-06-hamiltonian',
    'chapter-07-hamiltonian': 'chapter-07-relativity'
  };

  function parseHash() {
    var h = (location.hash || '').replace(/^#\/?/, '');
    var p = h.split('/').filter(Boolean);
    var out = { kind: 'landing' };
    if (!p.length) return out;
    if (p[0] === 'c' && byChapterSlug[p[1]]) { out.kind = 'chapter'; out.slug = p[1]; return out; }
    if ((p[0] === 'u' || p[0] === 'l') && p[1]) {
      var up = p[1].toUpperCase();
      if (modules[up]) p[1] = up;
    }
    if (p[0] === 'u' && p[1]) {
      var uk = p[1];
      var umid = modules[uk] ? uk : (modules[uk.toUpperCase()] ? uk.toUpperCase() : bySlug(uk, p[2]));
      if (umid) { out.kind = 'unit'; out.mid = umid; out.cid = p[2] || null; return out; }
    }
    if (p[0] === 'l' && linkOf(p[1])) { out.kind = 'link'; out.id = p[1]; return out; }
    var slug = LEGACY[p[0]] || p[0];
    if (byChapterSlug[slug]) {
      if (p[1]) {
        var up2 = p[1].toUpperCase();
        var mid = modules[p[1]] ? p[1] : (modules[up2] ? up2 : bySlug(p[1], p[2]));
        if (mid) { out.kind = 'unit'; out.mid = mid; out.cid = p[2] || null; return out; }
      }
      out.kind = 'chapter'; out.slug = slug; return out;
    }
    var m2 = modules[p[0]] || modules[p[0].toUpperCase()] || bySlug(p[0]);
    if (m2) { out.kind = 'unit'; out.mid = m2; out.cid = p[1] || null; return out; }
    return { kind: 'unknown' };
  }

  function applyRoute(isInit) {
    var r = parseHash(); stats.routes++;
    state.chapter = state.unit = state.chunk = state.link = null;
    try {
      if (r.kind === 'chapter') {
        state.chapter = byChapterSlug[r.slug];
        renderChapter(state.chapter);
        focusCameraOn(byNode['chapter:' + r.slug]);
      } else if (r.kind === 'unit') {
        state.unit = r.mid; state.chapter = chapterOf(r.mid);
        if (r.cid && findChunk(r.mid, r.cid)) state.chunk = r.cid;
        renderUnit(r.mid, r.cid);
        focusCameraOn(byNode['unit:' + r.mid]);
      } else if (r.kind === 'link') {
        state.link = linkOf(r.id);
        // 若该类型当前被筛选隐藏，自动打开以便在图中看见
        if (state.link && !filterTypes[state.link.type]) {
          filterTypes[state.link.type] = true;
          syncLegendUI();
        }
        renderLink(state.link);
        var eObj = crossLinks.find(function (e) { return e.data.id === r.id; });
        if (eObj) focusCameraOn(eObj);
      } else if (r.kind === 'unknown') {
        closePanel();
        showNotice('找不到这个知识节点', '已回到知识网络全览');
      } else {
        closePanel();
        if (!isInit) fit(false, false);
      }
    } catch (e) {
      stats.routeErrors++; console.error('[neural] route failed', e); closePanel();
    }
    document.querySelectorAll('#chips button').forEach(function (b) {
      b.setAttribute('aria-current', state.chapter && b.dataset.slug === state.chapter.slug ? 'true' : 'false');
    });
    needsDraw = true;
  }

  function go(hash, replace) {
    if (!hash) hash = '#/';
    if (location.hash !== hash) {
      if (replace) history.replaceState(null, '', hash);
      else history.pushState(null, '', hash);
    }
    applyRoute(false);
  }

  function closePanel() {
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('panel-open');
    state.chapter = state.unit = state.chunk = state.link = null;
    needsDraw = true;
  }

  var noticeTimer = 0;
  function showNotice(title, text) {
    var n = $('notice'); n.textContent = title + (text ? ' · ' + text : ''); n.hidden = false;
    clearTimeout(noticeTimer); noticeTimer = setTimeout(function () { n.hidden = true; }, 3800);
  }

  window.addEventListener('hashchange', function () { applyRoute(false); });
  window.addEventListener('popstate', function () { applyRoute(false); });

  /* —— 顶栏、章节胶囊、图例与快捷键 —— */
  function syncLegendUI() {
    var allOn = Object.keys(ltypes).every(function (t) { return filterTypes[t]; });
    var btnAll = $('btnAllLinks');
    if (btnAll) btnAll.textContent = allOn ? '精选' : '全部';
    document.querySelectorAll('#legendItems button').forEach(function (b) {
      b.setAttribute('aria-pressed', filterTypes[b.dataset.type] ? 'true' : 'false');
    });
  }

  function buildChrome() {
    $('stats').textContent = chapters.length + ' 章 · ' + unitIds.length + ' 单元 · ' + links.length + ' 关联';
    var chips = $('chips');
    chapters.forEach(function (ch) {
      var b = btn('', '', function () {
        if (state.chapter && !state.unit && state.chapter.slug === ch.slug) go('#/');
        else go('#/c/' + ch.slug);
      });
      b.style.setProperty('--c', ch.color); b.dataset.slug = ch.slug;
      var d = document.createElement('span'); d.className = 'dot'; b.appendChild(d);
      b.appendChild(document.createTextNode(ch.title));
      var s = document.createElement('small'); s.textContent = unitCount(ch); b.appendChild(s);
      chips.appendChild(b);
    });

    var host = $('legendItems');
    Object.keys(ltypes).forEach(function (t) {
      var ty = ltypes[t];
      var b = btn('', '', function () {
        filterTypes[t] = !filterTypes[t];
        syncLegendUI(); needsDraw = true;
      });
      b.dataset.type = t;
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', '28'); svg.setAttribute('height', '12'); svg.setAttribute('viewBox', '0 0 28 12');
      if (t === 'method') {
        svg.innerHTML = '<line x1="1" y1="4" x2="27" y2="4" stroke="' + ty.color + '" stroke-width="1.4"/><line x1="1" y1="8" x2="27" y2="8" stroke="' + ty.color + '" stroke-width="1.4"/>';
      } else if (t === 'limit') {
        svg.innerHTML = '<line x1="1" y1="6" x2="27" y2="6" stroke="' + ty.color + '" stroke-width="1.6"/><polygon points="14,2 18,6 14,10 10,6" fill="#060c1c" stroke="' + ty.color + '" stroke-width="1.4"/>';
      } else if (t === 'tool') {
        svg.innerHTML = '<line x1="1" y1="6" x2="27" y2="6" stroke="' + ty.color + '" stroke-width="1.4"/><circle cx="14" cy="6" r="2.8" fill="' + ty.color + '"/>';
      } else {
        svg.innerHTML = '<line x1="1" y1="6" x2="21" y2="6" stroke="' + ty.color + '" stroke-width="1.8"/><polygon points="27,6 19,2.5 19,9.5" fill="' + ty.color + '"/>';
      }
      b.appendChild(svg);
      b.appendChild(document.createTextNode(ty.label));
      var c = document.createElement('span'); c.className = 'cnt';
      c.textContent = links.filter(function (l) { return l.type === t; }).length;
      b.appendChild(c); host.appendChild(b);
    });
    syncLegendUI();

    $('btnAllLinks').addEventListener('click', function () {
      var allOn = Object.keys(ltypes).every(function (t) { return filterTypes[t]; });
      Object.keys(ltypes).forEach(function (t) { filterTypes[t] = allOn ? (t !== 'tool') : true; });
      syncLegendUI(); needsDraw = true;
    });

    $('btnFit').addEventListener('click', function () { fit(false, false); });
    $('btnRelayout').addEventListener('click', function () {
      nodes.forEach(function (n) { n.fixed = false; n.vx = n.vy = 0; });
      alpha = 0.8;
      for (var k = 0; k < 120; k++) tick(true);
      alpha = 0.08;
      fit(false, false);
    });
    $('btnList').addEventListener('click', function () { renderList(!state.list); });
    $('btnHelp').addEventListener('click', function () { renderLanding(); });
    $('pClose').addEventListener('click', function () { go('#/'); });
    $('btnZoomIn').addEventListener('click', function () { zoomBy(1.3); });
    $('btnZoomOut').addEventListener('click', function () { zoomBy(1 / 1.3); });
    $('btnZoomFit').addEventListener('click', function () { fit(false, false); });

    document.addEventListener('keydown', function (ev) {
      if (ev.target && /^(INPUT|TEXTAREA)$/.test(ev.target.tagName)) return;
      if (ev.key === '/') { ev.preventDefault(); q.focus(); }
      else if (ev.key === 'f' || ev.key === 'F') fit(false, false);
      else if (ev.key === 'l' || ev.key === 'L') renderList(!state.list);
      else if (ev.key === '?') renderLanding();
      else if (ev.key === '+' || ev.key === '=') zoomBy(1.25);
      else if (ev.key === '-') zoomBy(1 / 1.25);
      else if (ev.key === 'Escape') {
        if (state.list) { renderList(false); return; }
        if (state.unit && state.chunk) go('#/u/' + state.unit);
        else if (state.unit && state.chapter) go('#/c/' + state.chapter.slug);
        else if (panel.classList.contains('open')) go('#/');
      }
    });
  }

  resize(); syncPlaceholder(); buildModel(); buildChrome(); renderList(false); applyRoute(true);
  raf = requestAnimationFrame(loop);
  window.__NV2.ready = true;
})();
