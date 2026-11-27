/* neural-v2/chunk.js — 把知识库 chunk 原文解析成可排版的块结构。
 *
 * 知识库 chunk 来自 LaTeX 笔记抽取，常见问题：
 *   - 行间公式没有定界符（整行裸 LaTeX）；
 *   - 行内既有 $…$ 也有 \(…\)；
 *   - "(d)/(dt)" 这种抽取残留的分式；
 *   - "式（transverse）" 这种指向原文 label 的交叉引用；
 *   - 拍平成一行的 "### 小标题"、" - 列表项"、" · a | b | c" 表格行。
 *
 * parse(text) → [{t:'h',text} | {t:'p',text} | {t:'math',tex} | {t:'list',items:[text]} | {t:'table',rows:[[cell]]}]
 * 其中 text/cell/item 是“行内串”：普通文本与 $…$ 行内公式混排（已统一为 $ 定界）。
 * splitInline(str) → [{t:'text',v} | {t:'math',v}]，供渲染层逐段排版、逐段兜底。
 *
 * 纯函数、无 DOM 依赖；浏览器挂到 window.TMChunk，node 下 module.exports（供 QA 脚本批量校验）。
 */
(function (root) {
  'use strict';

  var CJK = /[\u3000-\u303f\u3400-\u9fff\uff00-\uffef]/;
  var CJK_G = /[\u3000-\u303f\u3400-\u9fff\uff00-\uffef]/g;
  var CMD = /\\[a-zA-Z]+/;

  /* —— 公式内部修整 —— */
  function fixTex(tex) {
    var s = String(tex).trim();
    // (a)/(b) → \frac{a}{b}（抽取残留；只处理不含括号嵌套的简单情形，重复以覆盖链式）
    for (var i = 0; i < 3; i++) {
      s = s.replace(/\(([^()$]{1,40})\)\s*\/\s*\(([^()$]{1,40})\)/g, '\\frac{$1}{$2}');
    }
    s = s.replace(/\\boldsymbol\b/g, '\\pmb');
    s = s.replace(/\\label\{[^}]*\}/g, '');
    s = s.replace(/\\(eq)?ref\{[^}]*\}/g, '(\\ast)');
    s = s.replace(/\\tag\{[^}]*\}/g, '');
    // 行尾孤立句号/逗号（"= 0 ." 这类）去掉，避免公式尾巴悬空
    s = s.replace(/\s*[.,，。]\s*$/, '');
    return s;
  }

  /* —— 文本内交叉引用 —— */
  function fixRefs(s) {
    return String(s)
      .replace(/(由|见|代入|利用|根据|结合|对比)?\s*式\s*[（(]\s*[A-Za-z][\w:.-]*\s*[）)]/g, function (m, pre) {
        return (pre || '') + '前式';
      })
      .replace(/\s*\\(eq)?ref\{[^}]*\}/g, '')
      .replace(/\\label\{[^}]*\}/g, '');
  }

  /* 统一行内定界：\( … \) → $ … $；\[ … \] 与 $$ … $$ 在块级处理前被替换为占位 */
  function normalizeInlineDelims(s) {
    return s.replace(/\\\(([\s\S]*?)\\\)/g, function (m, x) { return '$' + x.trim() + '$'; });
  }

  /* 文本行里裸露的 LaTeX 片段（含 \cmd，夹在中文之间）补 $…$ */
  function wrapBareInline(s) {
    var parts = splitInline(s);
    return parts.map(function (p) {
      if (p.t === 'math') return '$' + p.v + '$';
      if (!CMD.test(p.v)) return p.v;
      // 按 CJK 切分，含 \cmd 的非 CJK 片段整体当公式
      return p.v.replace(/[^\u3000-\u303f\u3400-\u9fff\uff00-\uffef]+/g, function (run) {
        if (!CMD.test(run)) return run;
        var m = run.match(/^(\s*)([\s\S]*?)(\s*)$/);
        var core = m[2].replace(/\\+$/, '').trim();
        if (!core) return run;
        return m[1] + '$' + core + '$' + m[3];
      });
    }).join('');
  }

  /* —— 行内切分（只识别 $…$；调用前已 normalizeInlineDelims） —— */
  function splitInline(s) {
    var out = [];
    var str = String(s);
    var i = 0, buf = '';
    while (i < str.length) {
      var c = str[i];
      if (c === '\\' && str[i + 1] === '$') { buf += '$'; i += 2; continue; }
      if (c === '$') {
        var j = str.indexOf('$', i + 1);
        while (j > 0 && str[j - 1] === '\\') j = str.indexOf('$', j + 1);
        if (j > i + 1) {
          if (buf) { out.push({ t: 'text', v: buf }); buf = ''; }
          out.push({ t: 'math', v: fixTex(str.slice(i + 1, j)) });
          i = j + 1;
          continue;
        }
        if (j === i + 1) { i += 2; continue; }   // "$$" 空公式
      }
      buf += c;
      i++;
    }
    if (buf) out.push({ t: 'text', v: buf });
    return out;
  }

  /* 一行是否是“裸行间公式” */
  function isBareMathLine(ln) {
    var s = ln.trim();
    if (!s || s.indexOf('$') >= 0) return false;
    var cjk = (s.match(CJK_G) || []).length;
    if (cjk > 2) return false;                      // 允许 "即" 一类的零星连接词
    if (/^[·•\-–]\s/.test(s) || /\|/.test(s)) return false;
    if (CMD.test(s)) return true;
    if (cjk === 0 && /[_^]\{/.test(s)) return true;
    // 纯符号方程（无中文、有等号、有字母，长度适中），如 "u''+u = -F(1/u)/(m h^2 u^2)"
    if (cjk === 0 && /=/.test(s) && /[a-zA-Z]/.test(s) && !/\s[a-zA-Z]{4,}\s/.test(s) && s.length < 160) return true;
    return false;
  }

  /* 拍平文本的预处理：拆出 ### 标题、" - " 列表、" · " 表格行、行间 $$ */
  function unflatten(text) {
    var s = String(text).replace(/\r\n?/g, '\n');
    // \[ … \] → 独立行 $$…$$
    s = s.replace(/\\\[([\s\S]*?)\\\]/g, function (m, x) { return '\n$$' + x.trim().replace(/\n/g, ' ') + '$$\n'; });
    // $$ … $$ 独立成行（原文常拍平在段中）
    s = s.replace(/\$\$([\s\S]*?)\$\$/g, function (m, x) { return '\n$$' + x.trim().replace(/\n/g, ' ') + '$$\n'; });
    // ### 标题：取紧随的短词（≤16 字、单词 ≤10 字、无句读）作为标题
    s = s.replace(/(^|\s)#{2,4}\s+([^\n]*)/g, function (m, lead, rest) {
      var toks = rest.split(/(\s+)/);
      var title = '', k = 0;
      for (; k < toks.length; k++) {
        var tk = toks[k];
        if (/^\s+$/.test(tk)) { if (title) { title += ' '; } continue; }
        if (tk.indexOf('$') >= 0 || /[，。；：、！？,.;:]/.test(tk) || tk.length > 10 || (title + tk).length > 16) break;
        title += tk;
      }
      title = title.trim();
      var tail = toks.slice(k).join('').trim();
      if (!title) return lead + rest;
      return '\n### ' + title + '\n' + tail;
    });
    // 超长单行里的 " - 项" → 换行列表
    s = s.split('\n').map(function (ln) {
      if (ln.length > 160 && / - [\u4e00-\u9fff]/.test(ln)) return ln.replace(/\s+-\s+(?=[\u4e00-\u9fff])/g, '\n- ');
      return ln;
    }).join('\n');
    // 同一行里串起来的 " · a | b" 表格行
    s = s.replace(/\s+·\s+(?=[^\n]*\|)/g, '\n · ');
    return s;
  }

  function parse(text) {
    var src = fixRefs(normalizeInlineDelims(unflatten(text)));
    var lines = src.split('\n');
    var blocks = [];
    var para = [];
    var mathBuf = [];

    function flushPara() {
      if (!para.length) return;
      var t = para.join(' ').replace(/\s+/g, ' ').trim();
      if (t) blocks.push({ t: 'p', text: wrapBareInline(t) });
      para = [];
    }
    function flushMath() {
      if (!mathBuf.length) return;
      // 以 "=" 开头的行接在上一行后面（多行推导）
      var eqs = [];
      mathBuf.forEach(function (m) {
        if (eqs.length && /^[=<>≤≥≈+]|^\\(approx|le|ge|equiv|simeq)\b/.test(m)) eqs[eqs.length - 1] += ' ' + m;
        else if (eqs.length && /[=+\-(,]$|\\\\$/.test(eqs[eqs.length - 1])) eqs[eqs.length - 1] += ' ' + m;
        else eqs.push(m);
      });
      eqs.forEach(function (e) {
        var tex = fixTex(e);
        if (tex) blocks.push({ t: 'math', tex: tex });
      });
      mathBuf = [];
    }
    function last() { return blocks[blocks.length - 1]; }

    for (var i = 0; i < lines.length; i++) {
      var raw = lines[i];
      var ln = raw.trim();
      if (!ln) { flushPara(); flushMath(); continue; }

      var mm = ln.match(/^\$\$([\s\S]*)\$\$$/);
      if (mm) { flushPara(); mathBuf.push(mm[1].trim()); continue; }

      if (/^###\s/.test(ln)) {
        flushPara(); flushMath();
        blocks.push({ t: 'h', text: wrapBareInline(ln.replace(/^###\s+/, '')) });
        continue;
      }

      // 表格行："· a | b | c" 或 "a | b | c"（至少两个竖线分隔、且不在公式里）
      var bare = ln.replace(/^[·•]\s*/, '');
      var noMath = bare.replace(/\$[^$]*\$/g, '');
      if ((noMath.match(/\|/g) || []).length >= 1 && /\s\|\s/.test(noMath)) {
        flushPara(); flushMath();
        var cells = splitCells(bare).map(function (c) {
          if (c && c.indexOf('$') < 0 && !CJK.test(c) && /[=_^\\]/.test(c) && /[A-Za-z]/.test(c)) return '$' + c + '$';
          return wrapBareInline(c);
        });
        var L = last();
        if (L && L.t === 'table') L.rows.push(cells);
        else blocks.push({ t: 'table', rows: [cells] });
        continue;
      }

      // 列表项
      var li = ln.match(/^(?:[·•]\s*|[-–]\s+|\(\w\)\s*|（\w）\s*|\d{1,2}[.)、]\s+)(.+)$/);
      if (li && !isBareMathLine(li[1])) {
        flushPara(); flushMath();
        var item = wrapBareInline(li[1].trim());
        var L2 = last();
        if (L2 && L2.t === 'list') L2.items.push(item);
        else blocks.push({ t: 'list', items: [item] });
        continue;
      }

      if (isBareMathLine(ln)) { flushPara(); mathBuf.push(ln); continue; }

      flushMath();
      para.push(ln);
    }
    flushPara(); flushMath();
    return blocks;
  }

  /* 按顶层 | 切单元格（忽略 $…$ 内的 |） */
  function splitCells(s) {
    var cells = [], buf = '', inM = false;
    for (var i = 0; i < s.length; i++) {
      var c = s[i];
      if (c === '$' && s[i - 1] !== '\\') inM = !inM;
      if (c === '|' && !inM) { cells.push(buf.trim()); buf = ''; continue; }
      buf += c;
    }
    cells.push(buf.trim());
    return cells.filter(function (c, k) { return c || (k > 0 && k < cells.length - 1); });
  }

  /* 纯文本摘要（搜索、tooltip 用）：去掉定界与常见命令 */
  function plain(text) {
    return String(text)
      .replace(/\\\(|\\\)|\\\[|\\\]|\$\$|\$/g, '')
      .replace(/\\(mathbf|mathrm|hat|vec|dot|ddot|bar|tilde|boldsymbol|pmb)\b/g, '')
      .replace(/\\frac\{([^{}]*)\}\{([^{}]*)\}/g, '($1)/($2)')
      .replace(/\\([a-zA-Z]+)/g, '$1')
      .replace(/[{}]/g, '')
      .replace(/^#{2,4}\s*/gm, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  var api = { parse: parse, splitInline: splitInline, fixTex: fixTex, plain: plain, isBareMathLine: isBareMathLine };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.TMChunk = api;
})(typeof window !== 'undefined' ? window : this);
