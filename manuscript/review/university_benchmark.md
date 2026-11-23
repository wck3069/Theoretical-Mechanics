# 官方课程初步对照

查阅日期：2026-11-05。以下区分官方可核实的课程覆盖和本书的编辑取舍；并未据课程简介推断课堂推导质量。采用用户最新七章结构，非早先附件八章结构。

官方来源：
- [MIT 8.09（2014）教学大纲](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/pages/syllabus/)及[讲义入口](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/download/)：高年级本科，覆盖刚体、正则变换、HJ、作用角与摄动，重视习题中的独立推理。
- [Harvard PHYSICS 151（2026秋）](https://my.harvard.edu/course/PHYSICS151/2026-Fall/Full-Term/001)：官方说明强调守恒量与对称性，以及拉格朗日、哈密顿方法与其他物理领域的关系；不是全套公开讲义证据。
- [Stanford PHYSICS 61、110/210官方目录](https://explorecourses.stanford.edu/m_search?filter-catalognumber-PHYSICS=on&filter-term-Autumn=on&page=1&q=PHYSICS)：61列出相对论测量、间隔、因果性、能动量及不变质量；110列出正则变换、HJ及作用角，并区分本科与研究生注册。
- [UC Berkeley PHYSICS 105官方目录](https://undergraduate.catalog.berkeley.edu/courses/1183571)：覆盖牛顿、分析力学、振动、刚体与张量，并明确习题所需Python基础。
- [David Tong 本人公开讲义现址](https://davidtong.org/teaching/dynamics-and-relativity/)：用于相对论进一步阅读。剑桥旧页已指向现址。

| 本书章节 | 对应官方课程 | 内容对照 | 可借鉴的教学组织（本书取舍） | 当前/后续改进 |
|---|---|---|---|---|
| 1 牛顿力学 | Berkeley 105；Stanford 61 | 质点、中心力、整体守恒 | 用模型与守恒互相检验 | 已补质心系碰撞、截面推导及数值收敛 |
| 2 变分法 | MIT 8.09；Stanford 110 | 分析力学的方法准备 | 边界条件先于形式运算 | 已补端点、横截与二阶判别 |
| 3 拉格朗日 | MIT 8.09；Harvard 151 | 约束、作用量、对称性 | 围绕守恒量组织物理问题 | 已补Noether时间与边界项、驱动能量及非完整模型比较 |
| 4 小振动 | MIT 8.09；Berkeley 105 | 正常模与矩阵方法 | 解析模态与数值比较 | 已补质量加权推导、初值/能量投影、双摆与独立模态验证 |
| 5 刚体 | MIT 8.09；Berkeley 105 | 惯量、旋转系、欧拉方程 | 逐步投影并说明参考点 | 已复审输运与移动矩心、快慢进动/睡眠阈值、姿态和内部轮功率 |
| 6 哈密顿 | MIT 8.09；Stanford 110；Harvard 151 | 正则结构、HJ、作用角 | 从轨道、生成变换到求解 | 已复审局部正则性、HJ分支、作用周期与数值辛结构 |
| 7 相对论 | MIT 8.033（2024）；Stanford 61 | 测量、光锥、四动量与碰撞 | 事件选择与不变量交替验证 | 已重写事件表/校准图/观察者能量/衰变阈值及20组核查 |

局限：本轮完成官方课程范围对照，尚未逐一分析四校原始习题及答案；不宣称已完成全面国际课程质量评估。进阶连续介质、场论等仅作后续参考，不据此扩展本书主要章节。

本轮第1章新增MIT 8.01SC官方碰撞讲义作为具体教学资料；并核对JPL月球参数、NASA电推进与韦布轨道说明，链接均已写入教材。课程对照采用“质心分解—守恒验算—实验室系复算”的组织方法，不据高级课程范围增加额外主章。

第2章本轮补充核实MIT 16.323变分法讲义（研究生层次）与18.086数学方法讲义：只借鉴边界项、参数变化和离散联系，保留本书本科核心范围。具体链接在教材及ch02_revision_report.md。

本轮第3章核对Tong拉格朗日公开讲义与MIT 8.09大纲，采用“约束投影—模型求解—守恒/功率复核”的组织。Lewis与Murray原始研究用于变分约束法的进一步阅读，不把高阶非完整几何加入本科核心要求。详见 ch03_revision_report.md。

第4章本轮进一步核对[MIT 8.09第3章原始讲义](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/aa6e7a8b4e0b5eeef24bce949d4fdb27_MIT8_09F14_Chapter_3.pdf)及[Problem Set 4](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/4ffa078142eca4a96a4bcb7a90bf0a4c_MIT8_09F14_pset4.pdf)，借鉴从广义坐标二次型到模态、由物理系统独立构造T/V并画振型的组织。新增零模漂移、非比例阻尼、近似误差与数值误差分离，不以更广的非线性课程范围替代核心教学。[NIST DLMF §28.17](https://dlmf.nist.gov/28.17)作为精确参数稳定曲线的拓展来源。查阅日期2026-11-05，详见 ch04_revision_report.md。

2026-11-06 第5章进一步核对[MIT 8.09刚体原始讲义](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/6fe39e8d5ce4ce746ca256dfea665eda_MIT8_09F14_Chapter_2.pdf)与[Problem Set 3](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/d5fdb8fec0febc6ba799cc86e67af3ee_MIT8_09F14_pset3.pdf)：借鉴旋转约定先行、对称性/质量分布独立求惯量及旋转坐标训练。Tong原始刚体讲义用于陀螺进一步阅读，NASA Basics of Space Flight第11章用于轮角动量卸载的应用边界。新增的算例和核验按本书坐标重新推导，不把官方课程范围视为全书逐式质量证明。详见 ch05_revision_report.md。

2026-11-06 第6章深化核对[MIT 8.09第4章原始讲义](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/f00f7f68ac7ba346a0868efb7430582c_MIT8_09F14_Chapter_4.pdf)及[Problem Set 5](https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/a55cb49d8706f671ccfdac7c6937cddc_MIT8_09F14_pset5.pdf)：从变换、括号和已知轨道训练HJ重构，补混合Hessian与分支条件。Tong讲义作为结构性进一步阅读；Hairer/Lubich/Wanner综述经Cambridge Core出版页核实，作者主页本轮访问拒绝，未据其不可访问全文声称完成审读。具体公式与数值由本书独立推导和核查，详见 ch06_revision_report.md。

2026-11-06至07 第7章核对[MIT 8.033 Lecture 4](https://ocw.mit.edu/courses/8-033-introduction-to-relativity-and-spacetime-physics-fall-2024/mit8_033_f24_lec04.pdf)与[Lecture 8](https://ocw.mit.edu/courses/8-033-introduction-to-relativity-and-spacetime-physics-fall-2024/mit8_033_f24_lec08.pdf)，借鉴事件先行和四动量不变量求解；明确其-+++与本书+---约定差异。Tong本人原始讲义用于本科覆盖与拓展入口，新增图题独立构造，不引入广义相对论或旋量作为核心。详见 ch07_revision_report.md。
