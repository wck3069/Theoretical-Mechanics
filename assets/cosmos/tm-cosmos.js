/* ==========================================================================
 * tm-cosmos.js —— 理论力学教学站 · 「星月夜」星空引擎 (v1.0.0)
 * --------------------------------------------------------------------------
 * 接口契约(与 tm-cosmos.css 头部一致,其他页面按此接入):
 *   <link rel="stylesheet" href="…/assets/cosmos/tm-cosmos.css">
 *   <script defer src="…/assets/cosmos/tm-cosmos.js"></script>
 *   <body data-cosmos="page" data-cosmos-accent="#RRGGBB"(可选,默认金色)
 *         data-cosmos-nebula="pillars|crab|xdf|omega|andromeda"(可选)>
 *
 * 行为:
 *   - 脚本一执行即同步给 <html> 加 .cosmos-ready(defer 预置方案):无 JS 时
 *     .cosmos-reveal 不被隐藏,正文完整可见;JS 就绪后才启用入场动画。
 *   - body 缺少 data-cosmos="page" 时立即干净退出,不产生任何副作用。
 *   - 注入元素(均 position:fixed / pointer-events:none,追加到 body 末尾,
 *     绝不改动页面既有节点):
 *       画布 far  (z-index:-1):~240 远景星(0.5–1.1px,alpha .3–.7),
 *                               慢正弦微闪烁 + ≤2px/min 漂移
 *       画布 near(z-index:-1):~90 近景星(1.2–2.4px),闪烁 + 鼠标(±8px)/
 *                               滚动(±4px)视差(lerp 平滑);流星亦绘于此
 *       画布 swirl(z-index:-1):梵高式涡旋 —— fBm 流函数 ψ 的 curl 噪声
 *                               (速度 = (∂ψ/∂y, −∂ψ/∂x),有限差分),叠加
 *                               3 个固定涡核的切向高斯旋涡;~800 条笔触
 *                               一次性预渲染到离屏画布,再以 ±0.3° 旋转 /
 *                               ±6px 平移极慢合成(20fps 节流),alpha ~.9;
 *                               仅 resize(250ms 去抖)时重新生成。
 *       <img class="cosmos-nebula">:星云照片,径向遮罩,opacity .22,位于
 *                               画布之下(z-index -2),90s ken-burns(CSS)。
 *       <div class="cosmos-moon">:弯月占位;月亮样式全部由 CSS 实现。
 *   - .cosmos-reveal 由 IntersectionObserver(rootMargin "0px 0px -8% 0px")
 *     添加 .is-visible,显现后即 unobserve。
 *   - 流星:每 9–15s 随机一颗,400ms 金白渐变拖尾;reduced-motion 下不出现。
 *   - prefers-reduced-motion:星与涡旋各绘制一次静态画面,无闪烁/漂移/
 *     月亮动画/流星;document.hidden 时暂停 rAF,恢复可见时继续。
 *   - DPR 上限 1.5;页面高于视口时背景固定、滚动不重绘(仅视差插值)。
 *   - 全局变量仅一个:window.TMCosmos = { version: "1.0.0" };含双初始化
 *     守卫;零外部请求;不用 eval;不用 innerHTML 写入动态数据。
 *   - 噪声/星场/流场为对 josephg/noisejs(ISC)及若干 MIT 星场示例思路的
 *     自行重写(Perlin 改进噪声 + fBm + curl),未复制任何未授权代码。
 * ========================================================================== */

(function () {
  "use strict";

  /* 渐进增强预置一行:脚本运行到此即刻声明 JS 可用(先于一切其他逻辑) */
  document.documentElement.classList.add("cosmos-ready");

  /* 单一全局 + 双初始化守卫 */
  if (window.TMCosmos && window.TMCosmos.version) {
    return;
  }
  window.TMCosmos = { version: "1.0.0" };

  var body = document.body || document.getElementsByTagName("body")[0];
  if (!body || body.getAttribute("data-cosmos") !== "page") {
    return; /* 未启用:干净退出 */
  }

  var reducedMotion = false;
  if (window.matchMedia) {
    reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  /* 主题色 accent:仅接受 6 位十六进制,写入 CSS 变量 --cosmos-accent */
  var accent = "#ffd27a";
  var accentAttr = body.getAttribute("data-cosmos-accent");
  if (accentAttr && /^#?[0-9a-fA-F]{6}$/.test(accentAttr)) {
    accent = accentAttr.charAt(0) === "#" ? accentAttr : "#" + accentAttr;
  }
  document.documentElement.style.setProperty("--cosmos-accent", accent);

  /* ---------------- 工具 ---------------- */
  var DPR_CAP = 1.5;
  function dpr() {
    var d = window.devicePixelRatio || 1;
    return d > DPR_CAP ? DPR_CAP : d;
  }
  function rand(min, max) { return min + Math.random() * (max - min); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function clamp(v, lo, hi) { return v < lo ? lo : (v > hi ? hi : v); }

  /* 确定性 PRNG(mulberry32):涡旋构图稳定、可复现 */
  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ---------------- Perlin 改进噪声(2D)+ 4 阶 fBm 流函数 ψ ----------------
     算法思路重写自 josephg/noisejs(ISC) */
  var Noise = (function () {
    var p = new Uint8Array(512);
    var perm = [
      151,160,137,91,90,15,131,13,201,9,110,98,126,108,106,213,
      8,80,245,96,71,218,237,182,158,142,228,244,235,194,76,64,
      176,169,43,143,17,61,118,136,251,243,101,224,199,234,7,95,
      205,193,74,196,41,183,153,197,161,45,55,105,252,146,104,87,
      129,216,138,167,147,170,198,49,24,68,52,66,139,181,180,79,
      94,83,187,242,23,63,70,168,6,33,219,230,65,163,188,15,121,
      89,114,174,226,24,59,54,31,227,43,133,190,141,229,190,239,
      13,247,165,177,88,53,157,184,80,202,30,191,125,252,99,241,
      128,145,35,212,103,166,210,156,135,162,36,246,232,149,140,
      178,221,124,26,209,86,148,60,107,215,10,46,78,69,171,207
    ];
    var i;
    for (i = 0; i < 256; i++) {
      p[i] = perm[i] & 255;
      p[i + 256] = p[i];
    }
    function fade(t) { return t * t * t * (t * (t * 6 - 15) + 10); }
    function grad(hash, x, y) {
      switch (hash & 7) {
        case 0: return x + y;
        case 1: return -x + y;
        case 2: return x - y;
        case 3: return -x - y;
        case 4: return x;
        case 5: return -x;
        case 6: return y;
        default: return -y;
      }
    }
    /* 返回约 [-1, 1] */
    function noise2(x, y) {
      var X = Math.floor(x) & 255;
      var Y = Math.floor(y) & 255;
      x -= Math.floor(x);
      y -= Math.floor(y);
      var u = fade(x);
      var v = fade(y);
      var aa = p[p[X] + Y];
      var ab = p[p[X] + Y + 1];
      var ba = p[p[X + 1] + Y];
      var bb = p[p[X + 1] + Y + 1];
      var x1 = lerp(grad(aa, x, y), grad(ba, x - 1, y), u);
      var x2 = lerp(grad(ab, x, y - 1), grad(bb, x - 1, y - 1), u);
      return lerp(x1, x2, v);
    }
    /* 4 阶 fBm:小振幅高频叠加,构成平滑的流函数场 */
    function psi(x, y) {
      return (
        noise2(x, y) * 1.0 +
        noise2(x * 2.03 + 5.2, y * 2.03 - 3.7) * 0.5 +
        noise2(x * 4.07 - 9.1, y * 4.07 + 2.4) * 0.25 +
        noise2(x * 8.11 + 13.3, y * 8.11 - 7.9) * 0.125
      );
    }
    return { noise2: noise2, psi: psi };
  })();

  /* ---------------- 画布工厂:全屏 fixed、不拦截交互、位于内容之下 ---------------- */
  function makeLayer(id) {
    var c = document.createElement("canvas");
    c.id = id;
    c.setAttribute("aria-hidden", "true");
    c.style.cssText =
      "position:fixed;top:0;left:0;width:100vw;height:100vh;" +
      "pointer-events:none;z-index:-1;";
    return c;
  }

  var canvasFar = makeLayer("tm-cosmos-far");
  var canvasNear = makeLayer("tm-cosmos-near");
  var canvasSwirl = makeLayer("tm-cosmos-swirl");

  /* 星云照片(opt-in),位于画布之下;z-index(-2)由 .cosmos-nebula 提供 */
  var nebulaName = body.getAttribute("data-cosmos-nebula");
  if (nebulaName === "pillars" || nebulaName === "crab" || nebulaName === "xdf" ||
      nebulaName === "omega" || nebulaName === "andromeda") {
    /* 由本脚本自身 src 推导资源目录(webp 与脚本同目录),零外链 */
    var baseDir = "";
    var selfScript = document.querySelector('script[src*="tm-cosmos.js"]');
    if (selfScript && selfScript.getAttribute("src")) {
      baseDir = selfScript.getAttribute("src").replace(/[^/]*$/, "");
    }
    var nebulaImg = document.createElement("img");
    nebulaImg.className = "cosmos-nebula";
    nebulaImg.setAttribute("alt", "");
    nebulaImg.setAttribute("aria-hidden", "true");
    nebulaImg.src = baseDir + nebulaName + ".webp";
    body.appendChild(nebulaImg);
  }

  /* 弯月占位:金月 + 双层光晕 + 涡卷环,样式全部在 CSS(纯 CSS 月亮) */
  var moon = document.createElement("div");
  moon.className = "cosmos-moon";
  moon.setAttribute("aria-hidden", "true");
  var moonSwirl = document.createElement("div");
  moonSwirl.className = "cosmos-moon__swirl";
  var moonDisc = document.createElement("div");
  moonDisc.className = "cosmos-moon__disc";
  moon.appendChild(moonSwirl);
  moon.appendChild(moonDisc);
  body.appendChild(moon);

  body.appendChild(canvasFar);
  body.appendChild(canvasNear);
  body.appendChild(canvasSwirl);

  var farCtx = canvasFar.getContext("2d");
  var nearCtx = canvasNear.getContext("2d");
  var swirlCtx = canvasSwirl.getContext("2d");
  if (!farCtx || !nearCtx || !swirlCtx) {
    return; /* 无 2d 上下文的环境:干净退出 */
  }

  var W = 0;    /* CSS 像素宽 */
  var H = 0;    /* CSS 像素高 */
  var scale = 1;

  /* ---------------- 星场 ---------------- */
  var FAR_COUNT = 240;
  var NEAR_COUNT = 90;
  var farStars = [];
  var nearStars = [];

  function seedStars() {
    var i;
    farStars.length = 0;
    nearStars.length = 0;
    /* 远景:直径 0.5–1.1px,alpha .3–.7;漂移 ≤2px/min ≈ 0.00034px/ms */
    for (i = 0; i < FAR_COUNT; i++) {
      farStars.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: rand(0.25, 0.55),
        base: rand(0.3, 0.7),
        tw: rand(0.00012, 0.00045), /* 慢正弦闪烁频率(1/ms) */
        ph: rand(0, Math.PI * 2),
        dx: rand(-0.00034, 0.00034),
        dy: rand(-0.00034, 0.00034)
      });
    }
    /* 近景:直径 1.2–2.4px;depth 决定视差权重 */
    for (i = 0; i < NEAR_COUNT; i++) {
      nearStars.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: rand(0.6, 1.2),
        base: rand(0.45, 0.85),
        depth: rand(0.5, 1.0),
        tw: rand(0.0006, 0.0016),
        ph: rand(0, Math.PI * 2)
      });
    }
  }

  function drawFar(t) {
    var i, s, x, y, alpha;
    farCtx.clearRect(0, 0, W, H);
    for (i = 0; i < farStars.length; i++) {
      s = farStars[i];
      if (reducedMotion) {
        x = s.x; y = s.y;
        alpha = s.base;
      } else {
        /* 漂移取模回绕,永不越界(背景固定,滚动不影响) */
        x = ((s.x + s.dx * t) % W + W) % W;
        y = ((s.y + s.dy * t) % H + H) % H;
        alpha = s.base + 0.12 * Math.sin(t * s.tw + s.ph);
      }
      farCtx.globalAlpha = clamp(alpha, 0.05, 0.85);
      farCtx.fillStyle = "#f5e6b8";
      farCtx.beginPath();
      farCtx.arc(x, y, s.r, 0, 6.2832);
      farCtx.fill();
    }
    farCtx.globalAlpha = 1;
  }

  /* 视差状态(鼠标 ±8px / 滚动 ±4px,lerp 平滑) */
  var mouseTX = 0, mouseTY = 0, curX = 0, curY = 0;
  var scrollTX = 0, scrollCur = 0;
  var parX = 0, parY = 0;

  function drawNear(t) {
    var i, s, alpha;
    nearCtx.clearRect(0, 0, W, H);
    for (i = 0; i < nearStars.length; i++) {
      s = nearStars[i];
      alpha = reducedMotion
        ? s.base
        : s.base + 0.18 * Math.sin(t * s.tw + s.ph);
      nearCtx.globalAlpha = clamp(alpha, 0.05, 1);
      nearCtx.fillStyle = "#eef2ff";
      nearCtx.beginPath();
      nearCtx.arc(
        s.x + parX * s.depth,
        s.y + parY * s.depth,
        s.r, 0, 6.2832
      );
      nearCtx.fill();
    }
    nearCtx.globalAlpha = 1;
    drawShooting(nearCtx, t);
  }

  function onPointerMove(e) {
    if (reducedMotion) { return; }
    mouseTX = clamp((e.clientX / W) * 2 - 1, -1, 1) * 8;
    mouseTY = clamp((e.clientY / H) * 2 - 1, -1, 1) * 8;
  }
  function onScroll() {
    var max = Math.max(1, document.documentElement.scrollHeight - H);
    scrollTX = clamp((window.pageYOffset / max) * 8, 0, 4);
  }
  /* ---------------- 梵高涡旋:curl(fBm 流函数 ψ) + 固定涡核 ----------------
     速度场 v = ( ∂ψ/∂y , −∂ψ/∂x )(中心差分);叠加 3 个涡核的切向高斯旋涡。
     笔触沿场方向欧拉积分,逐段变宽形成锥形收梢。一次预渲染,极慢变换合成。 */
  var SWIRL_COLORS = ["#0b1d51", "#1a3a6e", "#2c5aa0", "#0e2a66"];
  var SWIRL_GOLD = "#e8c15a";
  var STROKE_COUNT = 800;
  var NOISE_SCALE = 0.0021; /* 每 CSS 像素的噪声坐标增量 */
  var swirlOff = null;      /* 离屏预渲染画布 */
  var swirlAngle = 0, swirlTX = 0, swirlTY = 0;

  function fieldVelocity(x, y, vortices, out) {
    var e = 1.5; /* 中心差分步长(CSS px) */
    var dpsidy = Noise.psi(x * NOISE_SCALE, (y + e) * NOISE_SCALE) -
                 Noise.psi(x * NOISE_SCALE, (y - e) * NOISE_SCALE);
    var dpsidx = Noise.psi((x + e) * NOISE_SCALE, y * NOISE_SCALE) -
                 Noise.psi((x - e) * NOISE_SCALE, y * NOISE_SCALE);
    var vx = dpsidy;
    var vy = -dpsidx;
    var i, vort, dx, dy, r2, gauss, inv;
    for (i = 0; i < vortices.length; i++) {
      vort = vortices[i];
      dx = x - vort.cx;
      dy = y - vort.cy;
      r2 = dx * dx + dy * dy;
      gauss = Math.exp(-r2 / (vort.sigma * vort.sigma));
      inv = 1 / (Math.sqrt(r2) + 0.0001);
      vx += (-dy * inv) * vort.strength * gauss;
      vy += (dx * inv) * vort.strength * gauss;
    }
    out.x = vx;
    out.y = vy;
  }

  function buildSwirl() {
    var rnd = mulberry32(0x574152); /* 固定种子:构图稳定、可复现 */
    var d = dpr();
    swirlOff = document.createElement("canvas");
    swirlOff.width = Math.max(1, Math.round(W * d));
    swirlOff.height = Math.max(1, Math.round(H * d));
    var octx = swirlOff.getContext("2d");
    if (!octx) { return; }
    octx.setTransform(d, 0, 0, d, 0, 0);
    octx.lineCap = "round";
    octx.lineJoin = "round";

    /* 星月夜式涡核:主漩涡居中偏左上,次涡旋两枚(其一反向) */
    var short = Math.min(W, H);
    var vortices = [
      { cx: W * 0.34, cy: H * 0.38, sigma: short * 0.16, strength: 2.6 },
      { cx: W * 0.66, cy: H * 0.22, sigma: short * 0.10, strength: 1.9 },
      { cx: W * 0.52, cy: H * 0.64, sigma: short * 0.12, strength: -2.1 }
    ];

    var vel = { x: 0, y: 0 };
    var i, k, sx, sy, px, py, len, steps, w0, alpha, color, jitter, mag, stepX, stepY;
    for (i = 0; i < STROKE_COUNT; i++) {
      /* 约半数起点绕涡核采样(更聚拢成漩涡),其余均匀铺满画面 */
      if (i % 2 === 0) {
        var v = vortices[Math.floor(rnd() * vortices.length)];
        sx = v.cx + (rnd() + rnd() + rnd() - 1.5) * v.sigma * 2.2;
        sy = v.cy + (rnd() + rnd() + rnd() - 1.5) * v.sigma * 2.2;
      } else {
        sx = rnd() * W;
        sy = rnd() * H;
      }
      len = 20 + rnd() * 40;        /* 笔触总长 20–60px */
      steps = Math.max(4, Math.round(len / 3.2));
      w0 = 1.2 + rnd() * 1.6;       /* 线宽 1.2–2.8px */
      alpha = 0.05 + rnd() * 0.05;  /* 每笔 globalAlpha .05–.10 */
      color = rnd() < 0.08
        ? SWIRL_GOLD /* ~8% 金色高光 */
        : SWIRL_COLORS[Math.floor(rnd() * SWIRL_COLORS.length)];

      octx.strokeStyle = color;
      px = sx;
      py = sy;
      for (k = 0; k < steps; k++) {
        fieldVelocity(px, py, vortices, vel);
        mag = Math.sqrt(vel.x * vel.x + vel.y * vel.y) + 0.0001;
        stepX = (vel.x / mag) * 3.2 + (rnd() - 0.5) * 0.6;
        stepY = (vel.y / mag) * 3.2 + (rnd() - 0.5) * 0.6;
        /* 逐段降低 alpha 与线宽(叠加宽度抖动)= 锥形收梢笔触 */
        octx.globalAlpha = alpha * (0.55 + 0.45 * (1 - k / steps));
        jitter = w0 * (1 - 0.5 * (k / steps)) * (0.75 + rnd() * 0.35);
        octx.lineWidth = jitter < 0.4 ? 0.4 : jitter;
        octx.beginPath();
        octx.moveTo(px, py);
        px += stepX;
        py += stepY;
        octx.lineTo(px, py);
        octx.stroke();
        if (px < -80 || px > W + 80 || py < -80 || py > H + 80) { break; }
      }
    }
    octx.globalAlpha = 1;
  }

  function compositeSwirl(t) {
    if (!swirlOff) { return; }
    if (!reducedMotion) {
      /* ±0.3° 旋转、±6px 平移,周期 ~90–140s 的极慢漂移 */
      swirlAngle = 0.3 * Math.PI / 180 * Math.sin(t * 0.0000702);
      swirlTX = 6 * Math.sin(t * 0.0000517 + 1.3);
      swirlTY = 6 * Math.cos(t * 0.0000431);
    }
    swirlCtx.clearRect(0, 0, W, H);
    swirlCtx.save();
    swirlCtx.globalAlpha = 0.9;
    swirlCtx.translate(W / 2 + swirlTX, H / 2 + swirlTY);
    swirlCtx.rotate(swirlAngle);
    swirlCtx.translate(-W / 2, -H / 2);
    swirlCtx.drawImage(swirlOff, 0, 0, W, H);
    swirlCtx.restore();
    swirlCtx.globalAlpha = 1;
  }

  /* ---------------- 流星:每 9–15s 随机一颗,400ms 金白渐变拖尾 ---------------- */
  var shooting = null;

  function scheduleShooting() {
    if (reducedMotion) { return; }
    window.setTimeout(function () {
      fireShooting();
      scheduleShooting();
    }, 9000 + Math.random() * 6000);
  }

  function fireShooting() {
    if (document.hidden) { return; }
    var margin = W * 0.15;
    var ang = rand(18, 62) * Math.PI / 180; /* 向右下坠落 */
    shooting = {
      x0: rand(margin, W - margin),
      y0: rand(H * 0.05, H * 0.45),
      ux: Math.cos(ang),
      uy: Math.sin(ang),
      len: rand(120, 220),
      t0: performance.now()
    };
  }

  function drawShooting(ctx, t) {
    if (!shooting) { return; }
    var age = t - shooting.t0;
    if (age > 400) { shooting = null; return; }
    var prog = age / 400;
    var travel = 120 + prog * 260;
    var tipX = shooting.x0 + shooting.ux * travel;
    var tipY = shooting.y0 + shooting.uy * travel;
    var tailX = tipX - shooting.ux * shooting.len;
    var tailY = tipY - shooting.uy * shooting.len;
    var fade = prog < 0.25 ? prog / 0.25 : (1 - prog) / 0.75;
    var g = ctx.createLinearGradient(tailX, tailY, tipX, tipY);
    g.addColorStop(0, "rgba(255,255,255,0)");
    g.addColorStop(0.75, "rgba(255,255,255," + (0.55 * fade).toFixed(3) + ")");
    g.addColorStop(1, accent);
    ctx.save();
    ctx.globalAlpha = 1;
    ctx.strokeStyle = g;
    ctx.lineWidth = 1.6;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(tailX, tailY);
    ctx.lineTo(tipX, tipY);
    ctx.stroke();
    ctx.restore();
  }

  /* ---------------- 入场显现:IntersectionObserver,显现后 unobserve ---------------- */
  function revealAll() {
    var nodes = document.querySelectorAll(".cosmos-reveal");
    var i;
    for (i = 0; i < nodes.length; i++) {
      nodes[i].classList.add("is-visible");
    }
  }
  if ("IntersectionObserver" in window) {
    var revealObserver = new IntersectionObserver(function (entries) {
      var i;
      for (i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          entries[i].target.classList.add("is-visible");
          revealObserver.unobserve(entries[i].target);
        }
      }
    }, { root: null, rootMargin: "0px 0px -8% 0px", threshold: 0 });
    var revealNodes = document.querySelectorAll(".cosmos-reveal");
    var ri;
    for (ri = 0; ri < revealNodes.length; ri++) {
      revealObserver.observe(revealNodes[ri]);
    }
  } else {
    revealAll(); /* 极旧浏览器:直接显现,保证内容可见 */
  }

  /* ---------------- 尺寸:初始化与 resize(250ms 去抖)重排画布并重新生成 ---------------- */
  function setupCanvases() {
    W = window.innerWidth;
    H = window.innerHeight;
    scale = dpr();
    var layers = [canvasFar, canvasNear, canvasSwirl];
    var i;
    for (i = 0; i < layers.length; i++) {
      layers[i].width = Math.max(1, Math.round(W * scale));
      layers[i].height = Math.max(1, Math.round(H * scale));
    }
    farCtx.setTransform(scale, 0, 0, scale, 0, 0);
    nearCtx.setTransform(scale, 0, 0, scale, 0, 0);
    swirlCtx.setTransform(scale, 0, 0, scale, 0, 0);
    seedStars();
    buildSwirl();
  }

  function drawStatic() {
    parX = 0; parY = 0;
    drawFar(0);
    drawNear(0);
    compositeSwirl(0);
  }

  var resizeTimer = null;
  function onResize() {
    if (resizeTimer !== null) { window.clearTimeout(resizeTimer); }
    resizeTimer = window.setTimeout(function () {
      resizeTimer = null;
      setupCanvases();
      drawStatic(); /* 先落一张静态帧,动画模式下随后由 rAF 接管 */
    }, 250);
  }

  /* ---------------- 主循环:far ~12fps / near ~30fps / swirl 20fps 节流 ----------------
     document.hidden 时暂停 rAF(取消并退出),恢复可见时无缝重启;
     页面高于视口时背景固定,滚动不触发重绘(仅视差插值)。 */
  var rafId = null;
  var lastFar = 0, lastNear = 0, lastSwirl = 0;

  function frame(now) {
    rafId = window.requestAnimationFrame(frame);

    /* 视差插值(lerp 平滑) */
    curX = lerp(curX, mouseTX, 0.06);
    curY = lerp(curY, mouseTY, 0.06);
    scrollCur = lerp(scrollCur, scrollTX, 0.08);
    parX = curX;
    parY = curY - scrollCur;

    if (now - lastFar >= 83) {
      lastFar = now;
      drawFar(now);
    }
    if (now - lastNear >= 33) {
      lastNear = now;
      drawNear(now);
    }
    if (now - lastSwirl >= 50) { /* 20fps */
      lastSwirl = now;
      compositeSwirl(now);
    }
  }

  function startLoop() {
    if (rafId === null) {
      lastFar = lastNear = lastSwirl = 0;
      rafId = window.requestAnimationFrame(frame);
    }
  }
  function stopLoop() {
    if (rafId !== null) {
      window.cancelAnimationFrame(rafId);
      rafId = null;
    }
  }

  function onVisibility() {
    if (reducedMotion) { return; }
    if (document.hidden) {
      stopLoop();
    } else {
      startLoop();
    }
  }

  /* ---------------- 启动 ---------------- */
  setupCanvases();
  if (reducedMotion) {
    drawStatic(); /* 只画一次静态星空与涡旋;无闪烁/漂移/流星/月亮动画 */
  } else {
    window.addEventListener("mousemove", onPointerMove, { passive: true });
    window.addEventListener("scroll", onScroll, { passive: true });
    document.addEventListener("visibilitychange", onVisibility);
    startLoop();
    scheduleShooting();
  }
  window.addEventListener("resize", onResize);
})();
