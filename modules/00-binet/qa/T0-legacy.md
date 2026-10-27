# M0（比奈方程样板）— 遗留模块说明

日期：2026-10-27

## 状态

M0 是 P0 阶段的原始样板（`binet.tex` / `binet.pdf` / 原始 `index.html`），
按 **只读基线** 保留，未纳入 M1–M8 的「三件套 + 自测」规范：

- 无 `?selftest=1` 契约（早于 selftest 规范）
- 无 `qa/T1-note.md` / `T2-html.md` / `T3-qa.md` 证据链
- 未改写任何内容（保持 Phase 0 基线，便于对照与回滚）

## 已执行的检查

```
$ ~/.venv-tm/bin/python tools/check_html.py modules/00-binet/index.html
-- 摘要：6/6 项通过，0 项失败
EXIT_CODE=0
```

- 链接可用：根 `binet.html` 兼容跳转保留 query，指向 `modules/00-binet/index.html`
- `binet.pdf` 可打开（5 页，见 `qa/global/baseline.md`）

## 结论

M0 视为**样板/参照模块**，验收标准与 M1–M8 不同；其静态检查通过，
不参与 `?selftest=1` 回归。
