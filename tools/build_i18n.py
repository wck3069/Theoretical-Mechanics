#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract visible Chinese strings, machine-translate them once, and write
assets/tm-i18n-data.js.  The site itself never calls the network at runtime."""
from __future__ import annotations
import ast, html, json, re, sys, time, urllib.parse, urllib.request
try:
    import zhconv
except ImportError:
    zhconv = None
from html.parser import HTMLParser
from pathlib import Path
try:
    import esprima
except ImportError:
    print('esprima missing; use ~/.venv-tm/bin/python', file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tools' / 'i18n_cache.json'
OUT = ROOT / 'assets' / 'tm-i18n-data.js'
SKIP_TAGS = {'script','style','pre','code','noscript','textarea'}
ATTR_OK = {'title','placeholder','aria-label','alt','value'}
ATTR_SKIP = {'href','src','srcset','content','style','class','id','rel','property','name','http-equiv','role','type','data-lang','data-tm-no-i18n'}
CJK = re.compile(r'[\u3400-\u9fff]')
SPACE = re.compile(r'\s+')

def norm(s: str) -> str:
    return SPACE.sub(' ', html.unescape(str(s))).strip()

class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.texts = set()
        self.attrs = set()
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self.skip += 1
        for k, v in attrs:
            if not v or k.lower() in ATTR_SKIP:
                continue
            if (k.lower() in ATTR_OK or k.lower().startswith('data-')) and CJK.search(v):
                self.attrs.add(norm(v))
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
    def handle_endtag(self, tag):
        if tag.lower() in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip and CJK.search(data):
            self.texts.add(norm(data))

SCRIPT_RE = re.compile(r'<script\b([^>]*)>(.*?)</script\s*>', re.I | re.S)
SRC_RE = re.compile(r'\bsrc\s*=', re.I)
TYPE_RE = re.compile(r'''type\s*=\s*["']?([^"'\s>]+)''', re.I)
JS_TYPES = {'', 'text/javascript', 'application/javascript', 'module', 'text/ecmascript', 'application/ecmascript'}

def script_strings(body: str) -> set[str]:
    out = set()
    try:
        toks = esprima.tokenize(body, options={'comment': False})
    except Exception:
        return out
    for tok in toks:
        val = getattr(tok, 'value', '')
        if not val or not isinstance(val, str) or not CJK.search(val):
            continue
        if '${' in val:
            continue
        # esprima.tokenize keeps the surrounding quotes in token.value.
        if len(val) >= 2 and val[0] in ("'", '"', '`') and val[-1] == val[0]:
            try:
                val = ast.literal_eval(val)
            except Exception:
                val = val[1:-1]
        out.add(norm(val))
    # Template literals are not always exposed by esprima's token value.
    for m in re.finditer(r'`([^`\\]*(?:\\.[^`\\]*)*)`', body, re.S):
        v = m.group(1)
        if '${' not in v and CJK.search(v):
            out.add(norm(v))
    return out

def page_strings(path: Path) -> set[str]:
    raw = path.read_text(encoding='utf-8-sig')
    p = Collector(); p.feed(raw)
    out = set(p.texts) | set(p.attrs)
    for m in SCRIPT_RE.finditer(raw):
        attrs, body = m.group(1), m.group(2)
        if SRC_RE.search(attrs):
            continue
        tm = TYPE_RE.search(attrs)
        typ = tm.group(1).lower() if tm else ''
        if typ not in JS_TYPES:
            continue
        out |= script_strings(body)
    return {x for x in out if x and CJK.search(x) and not x.startswith(('http://','https://'))}

def source_files():
    files = [ROOT/'index.html']
    files += sorted((ROOT/'chapters').glob('*/index.html'))
    files += sorted((ROOT/'chapters').glob('*/manuscripts/*.html'))
    files += sorted((ROOT/'modules').glob('*/index.html'))
    files += sorted((ROOT/'modules').glob('*/note.html'))
    files += [ROOT/'modules'/'00-binet'/'binet.html']
    files += [ROOT/'manuscript'/'index.html']
    files += [ROOT/'neural'/'index.html']
    return [f for f in files if f.exists()]

def reader_key(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    m = re.match(r'chapters/([^/]+)/manuscripts/([^/]+)\.html$', rel)
    if m:
        return 'reader-ch-' + m.group(1) + '-' + m.group(2)
    m = re.match(r'modules/([^/]+)/(?:note|binet)\.html$', rel)
    if m:
        return 'reader-' + m.group(1)
    return ''


EN_OVERRIDES = {
    '星表': 'Star Catalog', '学习路径': 'Learning Path', '术语': 'Glossary', '关于': 'About',
    '标签': 'Tags', '全部': 'All', '星图': 'Star Map', '问星': 'Ask Star',
    '搜索章节 / 标签 / 作业来源…': 'Search chapters / tags / assignment sources…',
    '搜索章节': 'Search chapters', '进入模拟': 'Open simulation', '推导 PDF': 'Derivation PDF',
    '阅读网页版': 'Read web edition', '返回星图': 'Back to star map', '七章导航': 'Seven-chapter navigation',
    '本章模块': 'Modules in this chapter', '理论力学 · 交互讲义': 'Theoretical Mechanics · Interactive Notes',
    '理论力学：从质点到哈密顿': 'Theoretical Mechanics: From Particles to Hamiltonian',
    '星表 STAR CATALOG': 'STAR CATALOG', '学习路径 LEARNING PATH': 'LEARNING PATH',
    '术语表 GLOSSARY': 'GLOSSARY', '关于 ABOUT': 'ABOUT',
    '问星 · AI 助教': 'Ask Star · AI Tutor', '更改语言': 'Change language',
    '理论力学': 'Theoretical Mechanics', '从质点到哈密顿': 'From Particles to Hamiltonian',
    '点击星球进入章节': 'Click a planet to open its chapter',
    '理论力学：从质点到哈密顿 — 星图目录': 'Theoretical Mechanics: From Particles to Hamiltonian — Star Map Catalog',
    '星图目录': 'Star Map Catalog', '第1章 质点力学 · 理论力学：从质点到哈密顿': 'Chapter 1 Particle Mechanics · Theoretical Mechanics: From Particles to Hamiltonian',
    '单摆': 'Simple pendulum', '双摆': 'Double pendulum', '刚体力学': 'Rigid Body Mechanics',
    '哈密顿力学': 'Hamiltonian Mechanics', '质点系力学': 'Mechanics of Particle Systems', '变分法': 'Calculus of Variations',
    '拉格朗日力学': 'Lagrangian Mechanics', '小振动': 'Small Oscillations', '哈密顿': 'Hamiltonian',
    '正则方程': 'Canonical equations', '相空间': 'Phase space', '泊松括号': 'Poisson brackets', '约束': 'Constraint',
    '非线性': 'Nonlinear', '有效势': 'Effective potential', '中心力': 'Central force', '散射': 'Scattering',
    '俘获': 'Capture', '刚体': 'Rigid body', '角动量': 'Angular momentum', '阻尼': 'Damping', '甲虫': 'Beetle',
    '什么是有效势？它为什么能判断圆轨道稳定性？': 'What is effective potential? Why can it determine circular-orbit stability?',
    '伯特兰定理说明了什么？': "What does Bertrand's theorem state?",
    '单摆周期为什么随振幅变大？': "Why does a pendulum's period increase with amplitude?",
    '张力': 'Tension', '蓝移': 'Blueshift', '阻尼振动': 'Damped oscillation', '脉冲循环': 'Pulse cycle',
    '● 球壳': '● Spherical shell', '0（守恒）': '0 (conserved)', '脚本错误：': 'Script error:',
    '1 质点力学': '1 Particle Mechanics', '什么是混沌？': 'What is chaos?', '0（离开墙面）': '0 (leaving wall)',
    '● 圆环参考点路线': '● Ring reference-point path', '什么是变质量系统？': 'What is a variable-mass system?',
    '蓝移（靠近观测者）': 'Blueshift (toward observer)', '附录：碰撞公式汇总': 'Appendix: Collision formula summary',
    '雅可比积分 $E$': 'Jacobi integral $E$', '● 实心球（虚线）': '● Solid sphere (dashed)',
    '伯特兰定理是什么？': "What is Bertrand's theorem?", '雨滴为什么越落越快？': 'Why does a raindrop fall faster and faster?',
    '虚功原理为什么能求平衡？': 'Why can virtual work determine equilibrium?', '两体能量与 virial': 'Two-body energy and virial',
    '对根号做一阶近似展开得：': 'Expand the square root to first order:',
    '1 例题：球壳定理的积分证明': '1 Example: Integral proof of the shell theorem',
    '弹性碰撞链（作业-5 Q3）': 'Elastic collision chain (Assignment-5 Q3)',
    '● 甲虫路线（绕质心，不淡化）': '● Beetle path (around COM, not faded)',
    '雅可比积分和机械能有什么区别？': 'What is the difference between the Jacobi integral and mechanical energy?',
    '/r² 单位：m=α=1 无量纲': '/r² units: m=α=1 dimensionless',
    '什么是掠面速度/开普勒第二定律？': "What is areal velocity / Kepler's second law?",
    '伽利略变换和洛伦兹变换有什么区别？': 'What is the difference between Galilean and Lorentz transformations?',
    '质点保持二维圆截面，球半径参数隐藏。': 'The particle keeps a 2D circular cross-section; the sphere radius parameter is hidden.',
    '/部署|离线|单位|学习路径|诺特/': '/deployment|offline|units|learning-path|Noether/',
    '弹簧摆的平衡位置和两个小振动频率是什么？': 'What are the equilibrium position and two small-oscillation frequencies of a spring pendulum?',
    '什么是有效势？为什么能判断圆轨道稳定性？': 'What is effective potential? Why can it determine circular-orbit stability?',
    '圆轨道、稳定性与径向小振动（作业-2 Q4）': 'Circular orbits, stability, and radial small oscillations (Assignment-2 Q4)',
    '虚功原理 · 约束 · 广义力 · 拉格朗日方程': 'Virtual work · constraints · generalized forces · Lagrange equations',
    '质点力学': 'Particle Mechanics', '质点系力学': 'Mechanics of Particle Systems', '变分法': 'Calculus of Variations',
    '拉格朗日力学': 'Lagrangian Mechanics', '小振动': 'Small Oscillations', '刚体力学': 'Rigid Body Mechanics',
    '哈密顿力学': 'Hamiltonian Mechanics', '有效势与轨道稳定性': 'Effective Potential and Orbital Stability',
    '散射与俘获': 'Scattering and Capture', '比奈方程（现有样板）': 'Binet Equation (existing template)',
    '作业一 · 第一章手稿': 'Assignment 1 · Chapter 1 Manuscript', '绪论与第一章笔记': 'Introduction and Chapter 1 Notes',
    '设': 'Let', '，即': ', i.e.', '，拉格朗日为': ', Lagrange is',
    'direction.取指向球心为力的正方向（': 'direction. Take the direction toward the sphere center as the positive force direction (',
    '表示吸引），轴向投影因子为': 'indicates attraction), the axial projection factor is', '，故': ', therefore',
    '红移': 'redshift', '蓝移': 'blueshift',
    'L²/2r² 像一堵「离心墙」（离心势垒）。高斯势 V=−exp(−r²/2) 的势垒只在 L<2√2/2.718≈1.04 时存在；L 超过它，势垒消失，粒子直坠中心。': 'L²/2r² acts as a "centrifugal wall" (centrifugal barrier). The Gaussian potential V=−exp(−r²/2) has a barrier only when L<2√2/2.718≈1.04; above it, the barrier disappears and the particle falls straight to the center.',
    '第一章': 'Chapter 1', '封面': 'Cover', '平时成绩': 'Coursework', '课后作业': 'Homework',
    '期末考试': 'Final exam', '牛顿力学': 'Newtonian mechanics', '分析力学': 'Analytical mechanics',
    '圆柱脱离与运动学': 'Cylinder detachment and kinematics', '单摆周期修正': 'Pendulum period correction',
    '双摆混沌': 'Double-pendulum chaos', '模块页保留 M0–M22 编号；书稿条目用 S7': 'Module pages keep the M0–M22 numbering; the manuscript item uses S7',
    '模式索引': 'Mode index', '等时摆（摆线）': 'Isochronous pendulum (cycloid)',
    '折射定律': 'Law of refraction', '最短路径': 'Shortest path', '圆柱脱离': 'Cylinder detachment',
    '单摆周期（M12 非线性振动）': 'Pendulum period (M12 nonlinear oscillations)', '双摆混沌': 'Double-pendulum chaos',
    '斜面上的滑块': 'Block on an inclined plane', '弹簧摆': 'Spring pendulum', '小车与单摆': 'Cart and pendulum',
    '旋转圆环上的珠子': 'Bead on a rotating ring', '磁场中的带电粒子': 'Charged particle in a magnetic field',
    '单摆周期（共享 M5.2）': 'Pendulum period (shared M5.2)', '单摆周期': 'Pendulum period',
    '作业映射': 'Assignment Map', '模型与假设': 'Model and Assumptions', '推导': 'Derivation',
    '解析结果': 'Analytical Results', '数值验证': 'Numerical Verification', '讨论': 'Discussion',
    '本章小结': 'Chapter Summary', '关键概念与常见误区': 'Key Concepts and Common Misconceptions',
    '分层习题': 'Tiered Exercises', '解题思路与结果': 'Solutions and Results',
    '进一步阅读与来源': 'Further Reading and Sources', '进一步阅读与数据来源': 'Further Reading and Data Sources',
    '本章导读': 'Chapter Overview', '参考文献': 'References', '附录': 'Appendix',
    '目录': 'Contents', '相关': 'Related', '阅读书稿': 'Read chapter', '阅读推导': 'Read derivation',
    '阅读推导（网页版）': 'Read derivation (web)', '网页推导': 'Web derivation',
    '物理图像与理解 · PHYSICAL INSIGHT': 'Physical Insight',
    '核心结论 · KEY RESULT': 'Key Result', '数学注记 · MATH NOTE': 'Math Note',
    '进一步探索 · FURTHER': 'Further Exploration',
    '个月': 'months', '成绩': 'Grade', '分数': 'Score', '随堂测验': 'Quiz',
}
TW_OVERRIDES = {
    '星表': '星表', '学习路径': '學習路徑', '术语': '術語', '关于': '關於', '标签': '標籤', '全部': '全部',
    '星图': '星圖', '问星': '問星', '搜索章节 / 标签 / 作业来源…': '搜尋章節 / 標籤 / 作業來源…',
    '搜索章节': '搜尋章節', '进入模拟': '進入模擬', '推导 PDF': '推導 PDF', '阅读网页版': '閱讀網頁版',
    '返回星图': '返回星圖', '七章导航': '七章導航', '本章模块': '本章模組',
    '理论力学 · 交互讲义': '理論力學 · 互動講義',
    '理论力学：从质点到哈密顿': '理論力學：從質點到哈密頓',
    '星表 STAR CATALOG': '星表 STAR CATALOG', '学习路径 LEARNING PATH': '學習路徑 LEARNING PATH',
    '术语表 GLOSSARY': '術語表 GLOSSARY', '关于 ABOUT': '關於 ABOUT',
    '问星 · AI 助教': '問星 · AI 助教', '更改语言': '更改語言',
    '理论力学': '理論力學', '从质点到哈密顿': '從質點到哈密頓',
    '点击星球进入章节': '點擊星球進入章節',
    '理论力学：从质点到哈密顿 — 星图目录': '理論力學：從質點到哈密頓 — 星圖目錄',
    '星图目录': '星圖目錄', '单摆': '單擺', '双摆': '雙擺', '刚体力学': '剛體力學', '哈密顿力学': '哈密頓力學',
    '质点系力学': '質點系力學', '变分法': '變分法', '拉格朗日力学': '拉格朗日力學', '小振动': '小振動',
    '哈密顿': '哈密頓', '正则方程': '正則方程', '相空间': '相空間', '泊松括号': '泊松括號', '约束': '約束',
    '非线性': '非線性', '有效势': '有效勢', '中心力': '中心力', '散射': '散射', '俘获': '俘獲',
    '刚体': '剛體', '角动量': '角動量', '阻尼': '阻尼', '甲虫': '甲蟲',
    'L²/2r² 像一堵「离心墙」（离心势垒）。高斯势 V=−exp(−r²/2) 的势垒只在 L<2√2/2.718≈1.04 时存在；L 超过它，势垒消失，粒子直坠中心。': 'L²/2r² 像一堵「離心牆」（離心勢壘）。高斯勢 V=−exp(−r²/2) 的勢壘只在 L<2√2/2.718≈1.04 時存在；L 超過它，勢壘消失，粒子直墜中心。',
    '第一章': '第一章', '封面': '封面', '平时成绩': '平時成績', '课后作业': '課後作業',
    '期末考试': '期末考試', '牛顿力学': '牛頓力學', '分析力学': '分析力學',
    '个月': '個月', '成绩': '成績', '分数': '分數', '随堂测验': '隨堂測驗',
}
OVERRIDES = {'en-US': EN_OVERRIDES, 'zh-TW': TW_OVERRIDES}
SEP = '<<<TMSEP>>>'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125 Safari/537.36'

def api(src: str, target: str) -> str:
    url = ('https://translate.googleapis.com/translate_a/single?client=gtx'
           f'&sl=zh-CN&tl={target}&dt=t')
    data = urllib.parse.urlencode({'q': src}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=35) as r:
        body = json.load(r)
    parts = body[0] or []
    return ''.join((p[0] or '') for p in parts).strip()

def translate_one(s: str, target: str) -> str:
    for attempt in range(5):
        try:
            return api(s, target)
        except Exception:
            time.sleep(0.6 * (attempt + 1))
    return s

def translate_batch(items: list[str], target: str, cache: dict[str,str], save=None) -> int:
    todo = [s for s in items if s not in cache]
    if not todo:
        return 0
    # Keep each request comfortably under URL limits.
    chunk = 60
    for i in range(0, len(todo), chunk):
        batch = todo[i:i+chunk]
        while batch and len(SEP.join(batch)) > 1700:
            batch = batch[:-1]
        ok = False
        joined = ('\n' + SEP + '\n').join(batch)
        for attempt in range(4):
            try:
                out = api(joined, target)
                parts = out.split(SEP)
                if len(parts) == len(batch):
                    for s, t in zip(batch, parts):
                        cache[s] = t.strip()
                    ok = True
                    break
            except Exception:
                time.sleep(0.6 * (attempt + 1))
        if not ok:
            for s in batch:
                cache[s] = translate_one(s, target)
        if i % (chunk * 10) == 0:
            print(f'  {target}: {min(i+len(batch),len(todo))}/{len(todo)}', flush=True)
        if save and (i // chunk) % 5 == 4:
            save()
        time.sleep(0.08)
    return len(todo)

def repair_identity(source, target, cache):
    # Google occasionally returns the source when a batched request is throttled.
    bad = [s for s in sorted(source) if cache.get(s, None) == s]
    print(f'  repairing {len(bad)} identity entries for {target}', flush=True)
    for i, s in enumerate(bad):
        try:
            t = api(s, target).strip()
            if t and t != s:
                cache[s] = t
        except Exception:
            time.sleep(0.4)
        if i % 40 == 0:
            time.sleep(0.12)
    return len(bad)

def main():
    per_page: dict[str, set[str]] = {}
    global_set: set[str] = set()
    for f in source_files():
        ss = page_strings(f)
        print(f'{len(ss):4d}  {f.relative_to(ROOT)}')
        key = reader_key(f)
        if key:
            per_page.setdefault(key, set()).update(ss)
        else:
            global_set |= ss
    global_strings = set(global_set)
    for d in OVERRIDES.values():
        global_strings |= set(d)
    all_strings = set(global_strings)
    for ss in per_page.values():
        all_strings |= ss
    print('unique Chinese strings:', len(all_strings), '| global:', len(global_strings), '| reader pages:', len(per_page))
    cache_all = {}
    if CACHE.exists():
        try: cache_all = json.loads(CACHE.read_text())
        except Exception: cache_all = {}
    def save_cache():
        CACHE.write_text(json.dumps(cache_all, ensure_ascii=False, indent=1))

    for target in ('en', 'zh-TW'):
        cache_all.setdefault(target, {})
        if target == 'zh-TW' and zhconv:
            for s in sorted(all_strings):
                cache_all[target].setdefault(s, zhconv.convert(s, 'zh-tw'))
            n = 0
        else:
            n = translate_batch(sorted(all_strings), target, cache_all[target], save_cache)
            repair_identity(all_strings, target, cache_all[target])
        save_cache()
        print(f'{target}: translated {n}; cached {len(cache_all[target])}')
    en = {s: cache_all['en'].get(s, s) for s in all_strings}
    tw = {s: cache_all['zh-TW'].get(s, s) for s in all_strings}
    if zhconv:
        tw = {s: zhconv.convert(v, 'zh-tw') for s, v in tw.items()}
    for s, t in EN_OVERRIDES.items(): en[s] = t
    for s, t in TW_OVERRIDES.items(): tw[s] = t
    data = {'en-US': en, 'zh-TW': tw}
    i18n_dir = ROOT / 'assets' / 'i18n'
    i18n_dir.mkdir(parents=True, exist_ok=True)

    def dump(doc: dict, var: str) -> str:
        payload = json.dumps(doc, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        return '/* generated by tools/build_i18n.py */\nwindow.' + var + '=' + payload + ';\n'

    gdoc = {lang: {s: data[lang][s] for s in global_strings} for lang in ('en-US', 'zh-TW')}
    (i18n_dir / 'global.js').write_text(dump(gdoc, 'TM_I18N_DATA'), encoding='utf-8')
    for key, ss in sorted(per_page.items()):
        page_only = ss - global_strings
        pdoc = {lang: {s: data[lang][s] for s in page_only} for lang in ('en-US', 'zh-TW')}
        (i18n_dir / (key + '.js')).write_text(dump(pdoc, 'TM_I18N_PAGE'), encoding='utf-8')
    loader = '''/* generated by tools/build_i18n.py - lazy loader for translation data */
(function () {
  function lang() { try { return localStorage.getItem('tm-lang') || 'zh-CN'; } catch (e) { return 'zh-CN'; } }
  if (lang() === 'zh-CN') return;
  var s = document.currentScript, all = document.getElementsByTagName('script');
  if (!s) {
    for (var i = all.length - 1; i >= 0; i--) {
      if (/tm-i18n-data\\.js([?#]|$)/.test(all[i].src)) { s = all[i]; break; }
    }
  }
  if (!s) return;
  var base = s.src.replace(/[^/]*$/, ''), p = location.pathname, key = '', m;
  m = p.match(/\\/chapters\\/([^/]+)\\/manuscripts\\/([^/]+)\\.html$/);
  if (m) key = 'reader-ch-' + m[1] + '-' + m[2];
  else {
    m = p.match(/\\/modules\\/([^/]+)\\/(?:note|binet)\\.html$/);
    if (m) key = 'reader-' + m[1];
  }
  var files = ['i18n/global.js'];
  if (key) files.push('i18n/' + key + '.js');
  for (var j = 0; j < files.length; j++) document.write('<script src="' + base + files[j] + '"><\\/script>');
})();
'''
    OUT.write_text(loader, encoding='utf-8')
    sizes = {p.name: p.stat().st_size for p in i18n_dir.glob('*.js')}
    print('wrote', OUT.relative_to(ROOT), OUT.stat().st_size, 'bytes; global', sizes.get('global.js'), 'bytes; page dicts', len(per_page))

if __name__ == '__main__':
    main()
