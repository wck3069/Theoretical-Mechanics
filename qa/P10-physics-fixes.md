# P10 物理修正记录（主控接手部分）

> 背景：GPT 额度用尽后，M5–M8 的 LaTeX 修正由主控（DeepSeek V4.1 Flash）直接完成；M0/M2/M3 的修正已在 NOTE-A 会话中完成并被复核。所有修正均重新编译 PDF，且无 `??`。

## M0 `binet.tex`
- GR 最低阶修正：`u³` 归因 → `u''+u=GM/h²+3GM u²/c²`，`λ_GR=3GM/c²`、`μ=0`。
- `μu³` 改标为“唯象的非 GR 进动”，并注明真实水星进动 `5.02e-7 rad/orbit`。
- 页面同步：μ 说明、`G=M=1、h=L/m=1` 量纲说明、底部 tag。
- 重编译：`binet.pdf` 5 页。

## M2 `note.tex`
- 数值表：`Θ=0.920151 rad (52.72°)`，`dσ/dΩ=8k/(9πE)=0.282942`。
- `b<b_c` 措辞改为“不受势垒阻挡而越过”。
- 前向峰 `1/Θ³` 归因改为长程势；删除“短程硬核”说法。
- 重编译：`note.pdf` 6 页。

## M3 `note.tex`
- `r1,max=M2 a(1+e)/(M1+M2)`。
- `K=(M2/(M1+M2))(2πa/P)/√(1−e²)·sin i`；说明 e→1 时 K→∞；一般椭圆 RV 非正弦。
- 重编译：`note.pdf` 6 页。

## M5 `note.tex`
- 直角摆：`V=-2ρg[a²cosφ−b²sinφ]`，`tanφ=-b²/a²`；a=b → φ=-45°。
- 弹簧杆：`V=+Pl/2 sinθ+½k(L−l0)²`，`L=√(h²+l²−2hl sinθ)`，`P/2=k(L−l0)h/L`。
- 圆槽两圆柱：`sinφ=r/(R−r)`；说明 φ 由几何固定，不能用 dV/dφ=0 定；给出等重时的压力 `N=P/cosφ` 与不等重时的联立方法。
- 梯子临界：改为摩擦饱和 `f=μN`，不是 Hessian 奇异。
- 重编译：`note.pdf` 7 页。

## M6 `note.tex`
- `e=0`：改为“法向速度相同、切向保留”，`v1'=(v cosα/2, v sinα)`，`β=arctan(2tanα)−α`；α=45°→18.435°；β_max=19.471°；只有 α=0 才 β=0。
- 数值表：`β_max(e=0.5)=36.8699°`。
- “碰撞分类/讨论”中的“粘连、β=0”同步修正。
- 重编译：`note.pdf` 6 页。

## M7 `note.tex` + `index.html`
- 删除“让我重新计算。”草稿句；补全积分推导。
- 球冠参数统一为 h（球冠高度），公式 `d=h(4R−h)/[4(3R−h)]`；页面公式、tag、映射、README 同步。
- 页面 h 滑块上限 6→3，`capCentroid` 内钳制 `h≤R`。
- `shellV` 单位 bug 与甲虫世界角已在 UI-C 修复。
- 重编译：`note.pdf` 6 页。

## M8 `note.tex`
- Lorentz：`m v̇x=-eB vy`、`m v̇y=-eE+eB vx`；漂移 `v_d=E×B/B²` 方向正确。
- 相空间：`E<mgL` 振荡、`E>mgL` 旋转、`E=mgL` 分界线。
- 渡河：最小漂移 `x_min=(d/v2)√(v1²−v2²)`；v1=2,v2=1 → 1.732d。
- 清理圆周运动推导中的草稿问句。
- 重编译：`note.pdf` 6 页。

## 复核
- `check_html.py`：10 个 HTML 全部 6/6。
- `verify_selftest.py`：8/8 有契约模块 PASS；M0 SKIP。
- `/api/ask` deep（M8 Lorentz）回答与修正后的方程一致。
