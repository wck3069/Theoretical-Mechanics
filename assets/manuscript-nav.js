/* manuscript-nav.js — progressive enhancement for the manuscript pages.
   Without JS the static TOC (<details open>) works as-is.
   With JS: active-section highlight in the sidebar, drawer auto-collapse on
   narrow screens, and the desktop sidebar stays pinned open. */
(function () {
  "use strict";
  var toc = document.getElementById("ms-toc");
  var body = document.querySelector("article.ms-body");
  if (!toc || !body) return;

  var details = toc.querySelector("details");
  var links = {};
  Array.prototype.forEach.call(toc.querySelectorAll("a[href^='#']"), function (a) {
    links[a.getAttribute("href").slice(1)] = a;
  });

  var mq = window.matchMedia("(max-width: 1100px)");
  function isNarrow() { return mq.matches; }
  function syncOpen() {
    if (!details) return;
    if (isNarrow()) details.removeAttribute("open");
    else details.setAttribute("open", "");
  }
  syncOpen();
  if (mq.addEventListener) mq.addEventListener("change", syncOpen);
  else if (mq.addListener) mq.addListener(syncOpen);

  if (details && details.querySelector("summary")) {
    details.querySelector("summary").addEventListener("click", function (e) {
      if (!isNarrow()) e.preventDefault(); // desktop: sidebar is always open
    });
    Array.prototype.forEach.call(toc.querySelectorAll("a"), function (a) {
      a.addEventListener("click", function () {
        if (isNarrow()) details.removeAttribute("open");
      });
    });
  }

  var targets = [];
  Array.prototype.forEach.call(toc.querySelectorAll("a[href^='#']"), function (a) {
    var el = document.getElementById(a.getAttribute("href").slice(1));
    if (el) targets.push({ link: a, el: el });
  });

  var header = document.querySelector(".ms-header");
  var headerH = 0;
  function measureHeader() {
    if (!header) return;
    headerH = header.getBoundingClientRect().height;
    if (headerH > 0)
      document.documentElement.style.setProperty("--header-h", headerH + "px");
  }
  measureHeader();

  function keepInView(a) {
    if (!(toc.scrollHeight > toc.clientHeight)) return;
    var lr = a.getBoundingClientRect(), tr = toc.getBoundingClientRect();
    if (lr.top < tr.top + 4) toc.scrollTop -= (tr.top + 4) - lr.top;
    else if (lr.bottom > tr.bottom - 4) toc.scrollTop += lr.bottom - (tr.bottom - 4);
  }

  var current = null;
  function spy() {
    var scrollY = window.pageYOffset;
    var probe = scrollY + headerH + 20;
    var cur = null;
    for (var i = 0; i < targets.length; i++) {
      var absTop = targets[i].el.getBoundingClientRect().top + scrollY;
      if (absTop <= probe) cur = targets[i];
      else break;
    }
    var a = cur ? cur.link : null;
    if (a === current) return;
    if (current) { current.classList.remove("active"); current.removeAttribute("aria-current"); }
    current = a;
    if (current) { current.classList.add("active"); current.setAttribute("aria-current", "true"); keepInView(current); }
  }

  var raf = null;
  function schedule() {
    if (raf) return;
    raf = requestAnimationFrame(function () { raf = null; spy(); });
  }
  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", measureHeader);
  window.addEventListener("resize", schedule);
  spy();
})();
