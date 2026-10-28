# P10 修复记录 —— ui-c 组（M7、M8）

## 修改文件
- modules/07-rigid-body/index.html
- modules/08-kinematics/index.html

## M7 刚体

### 文案/符号
- brand p 后新增 `<p class="intro">`：刚体怪事 + 第一步拖 h 盯 d。
- HUD：`d`→`质心高度 d`、`L`→`角动量 L`、`V`→`势能 V`。
- 公式：`d=(R-b)(3R+b)/[4(2R+b)]` → `d=(R-h)(3R+h)/[4(2R+h)]（h＝右侧滑块的球冠高度）`；转环补 Δθ=π 解释；圆盘补角动量 L；球壳补壳内 V 为常数。
- 映射表：`滑块 R/b` → `滑块 R 与球冠高度 h`；`note.tex 推导` → `阅读推导 note.pdf`。
- tag：URL 注明 `URL 中 b 即球冠高度 h`；追加无量纲演示单位说明。

### JS 修复
- `shellV(rho,M,a)`：比较/除以实际 ρ，不再混用 r/a。调用处传实际距离 `r`。验证 R=2,ρ=3 → -0.3333。
- 甲虫世界角：环 `-angle/2`，甲虫 `+angle/2`（trail/body），一圈后甲虫在对侧（世界 π）。
- 重置按钮：`P.b=DEFAULTS.b` → `P.h=DEFAULTS.h`。

## M8 运动学

### 文案/符号
- brand p：`圆柱脱离、单摆周期修正、Lorentz 力` → `圆柱脱离、单摆周期修正、双摆混沌、Lorentz 力与参考系变换`；新增 intro。
- HUD：`θ`→`振幅 θ0`、`T`→`周期 T`、`修正`→`周期修正项（一级近似）`；脱离角槽仅在圆柱模式显示。
- 公式 detach 行补“与质量、半径无关”；滑块 L 标注“本章 L＝长度”。
- 映射表新增双摆混沌行；Lorentz 行改为 `Lorentz 力与参考系变换` + `阅读推导 note.pdf`。
- tag 追加无量纲演示单位说明。

## 验证输出

### check_html.py
```
== check_html.py: modules/07-rigid-body/index.html == 6/6 项通过，0 项失败
== check_html.py: modules/08-kinematics/index.html == 6/6 项通过，0 项失败
```

### verify_selftest.py
```
PASS  07-rigid-body   pass=5 fail=0  SELFTEST 5/5 PASS
PASS  08-kinematics   pass=5 fail=0  SELFTEST 5/5 PASS
-- 2/2 模块通过
```

### shellV 验证
```
shellV(1,1,2)=-0.5  shellV(3,1,2)=-0.3333  shellV(5,1,2)=-0.2
```

## 遗留风险
- M7 note.tex L80 草稿痕迹与 M8 note.tex Lorentz 符号/阈值错误未在本组范围（仅 index.html），由其他组/主控处理。
- h 滑块上限仍为 6（可能进入 h>2R 无效区），audit 建议动态约束，未改动。
- M8 圆柱/单摆模式仍为静态图，audit 建议动画或明确“静态示意”。
