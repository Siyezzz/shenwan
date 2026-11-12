# reits-research-skills

公募 REITs 投研 Skills 仓库：**研报方法论迁移 + 四个业务 Skill（投后跟踪 / 投前分析 / 研报撰写 / 横向基准）+ 四个真实案例验证**。

核心命题：**一份 REITs 研究报告该长什么样，才能让投资研究员拿它做决策**——而不是让读者看见流程跑了多少步。

## 这个仓库解决什么问题

卖方研报的研究逻辑很难复用：结论留在 PDF 里，方法留在分析师脑子里。已有的"研报转 Skill"做法（见 `template/template_convention_audit.md` 审计的 11 个样本）能把研报变成结构完整的 FLOW，但存在三个系统性缺陷：

1. **数据层空转**——645 条数据需求的 `source_id` 全为 `null`，流程一条都跑不通；
2. **判断层无标尺**——"高/中/低"出现 35 次却没有任何区间定义；
3. **时间层无版本**——公式不记适用期，制度变化后被跨期套用。

本项目不重写模板，而是在**保留原 10 个 METADATA 字段与 FLOW 四段骨架**的前提下，补上数据探针、标尺、公式有效期和"不可判定"四件事，然后用真实披露文件跑三个 REITs 案例来证明它跑得通。

## 目录

```
reits-research-skills/
├── README.md
├── skills/
│   ├── reits-post-investment-monitor/    # Skill A 投后定期跟踪（FLOW #1–#22）
│   ├── reits-pre-investment-analysis/    # Skill B 投前深度分析（FLOW #1–#26）
│   ├── research-report-to-flow/          # Skill C 研报转 FLOW 方法论（FLOW #1–#18）
│   ├── reits-report-writing/             # Skill D 研报撰写（FLOW #1–#14，记者腔；三套骨架 pre/post/comparison）
│   └── reits-peer-benchmarking/          # Skill E 横向基准（FLOW #1–#22，只交论证底稿 findings.csv，成文交 Skill D）
├── template/
│   ├── template_convention_audit.md      # 继承规范（写作约束 + 机器校验清单）
│   ├── report_style_analysis.md          # 11 份卖方研报的文风统计（规则出处）
│   ├── investment_report_template.md     # 投前十章模板
│   └── post_investment_report_template.md # 投后八节模板
├── source_documents/                     # 来源索引；原始 PDF 需按索引下载，不入库
├── outputs/
│   ├── research_flow_audit/              # 附件学习与 FLOW 审计
│   ├── report_quality_audit.md           # 项目审计（31 条问题清单 + 不修改清单）
│   ├── source_data_audit.md              # 来源与数据真实性十项全量核验
│   ├── case_01_glp_reit/
│   ├── case_02_huaxia_shen_international/
│   ├── case_03_sinofarm_reit/
│   └── case_04_peer_benchmarking/        # 6 只仓储物流横向基准（报告 + 5 图 + 自包含 HTML）
├── models/                               # 现金流模型、数据矩阵
├── tests/                                # 数据质量 / 计算 / 执行 / 回归测试记录
├── iteration_log/                       # 六轮迭代留痕 + 提交记录
└── presentation/                         # 两版汇报材料
    ├── management_briefing.md            # 面向管理层（提纲+口述稿+追问应答）
    └── teacher_briefing.md               # 面向老师（纯口语：流程/思路/亮点/疑惑）
```

**两个 skill 的分工（横向基准）**：`reits-peer-benchmarking` 只做取数与判断，交出 `findings.csv`（判断＋用词档位＋锚点＋反例）与图；`reits-report-writing` 按 `outline_schema.comparison` 成文并做记者腔清洗。判断档位在取数层定稿，成文层不得升格、不得新造数字——这条边界是报告不写成"运行日志"的前提。

## 当前进度

| 阶段 | 状态 | 产出 |
|---|---|---|
| 一、附件审计与模板研究 | **完成** | `outputs/research_flow_audit/attachment_study.md`、`research_flow_audit.xlsx`、`template/template_convention_audit.md` |
| 二、研报转 FLOW 方法论 Skill | **完成** | `skills/research-report-to-flow/`（SKILL + METADATA + FLOW #1–#18 + raw，可逆一致） |
| 三、REITs 业务 Skill | **完成** | `skills/reits-post-investment-monitor/`（FLOW #1–#22）、`skills/reits-pre-investment-analysis/`（FLOW #1–#26） |
| 四、真实资料获取 | **部分** | `source_documents/` 共 **60 份 PDF**（305MB）+ `source_index.csv`（**62 条记录 = 60 条实体 + 2 条缺口登记**）。上交所公告接口需内部 `channelId`，公开请求不可用；改用东方财富基金公告接口 `type=3`（定期报告）分类后，季报/半年报/年报/年度评估/年度审计可完整枚举。**60 份页数已逐份回填并复核（60/60 一致），52 份有可用文字层，8 份为扫描件（已标 `OCR_NEEDED`，未冒充已识别）。** 首农资产评估报告原件确为不可得（`SOURCE_UNAVAILABLE`）；基金合同已补（此前误记为不可得）。详见 `outputs/source_data_audit.md` |
| 五、三案例实跑 | **完成** | 三份报告（**6,210 / 6,839 / 24,488** 中文字符，正文口径）+ `run_log.md` + `claims_verdict.csv` + `source_index.csv`；案例三另有 `assumptions.csv`（30 条）与 `figures/` |
| 五之二、研报撰写 Skill | **完成（第六轮新增）** | `skills/reits-report-writing/`（FLOW #1–#14）+ `template/investment_report_template.md` + `template/post_investment_report_template.md` + `template/report_style_analysis.md`（11 份卖方研报文风统计）+ `tools/count_report_words.py` + `tools/check_voice.py`（自指语／读者语／裸数字可机检）。三份报告按新体例重写，正文 FLOW 编号 0 处、状态码 0 处 |
| 六、三轮以上迭代 | **完成（6 轮）** | `iteration_log/ITERATION_LOG.md`（667 行）：1 可执行性 / 2 研究质量 / 3 鲁棒性 / 4 自检可信度 / 5 材料完备性 / 6 **产品形态（报告重构，含两轮审稿记录）**，每轮含修改前后数值对比 |
| 七、GitHub | **完成** | 已推送至 `github.com/Siyezzz/shenwan`（`main` 分支，首次提交 47 文件 / 10,419 行）。经代理报 502，清除 `HTTP(S)_PROXY` 后直连成功。**原始 PDF（60 份 / 305MB）按 `.gitignore` 不入库**，仅入库 `source_index.csv`——与「许可与边界」中「不再分发」一致 |
| 八、最终目录 | **完成** | 见上节目录结构 |
| 九、汇报材料 | **完成（两版）** | `presentation/management_briefing.md`（管理层版：5 页提纲 + 1,342 字口述稿 + 数据卡 + 12 条追问 + 边界声明）；`presentation/teacher_briefing.md`（老师版：纯口语 3,204 字，按「流程/思路/亮点/疑惑」四段，约 14 分钟，含 3 档时长裁剪 + 7 条追问备用） |
| 十、最终验收 | **完成** | `outputs/final_acceptance_report.md`（**25 项：22 PASS / 3 PARTIAL / 0 FAIL**）；来源真实性另有 `outputs/source_data_audit.md` 十项全量核验 |
| 十一、横向基准（第七轮新增） | **完成** | `skills/reits-peer-benchmarking/`（FLOW #1–#22）＋ `outputs/case_04_peer_benchmarking/`：6 只仓储物流 REIT 同口径对比，报告正文 **14,862** 中文字符（不设字数下限；v1.2 补比较标准后较 v1.1 增 2,286，全部是新增论证）、5 张图、自包含 HTML。核心动作是**选样可复现**（10 只候选池全量枚举 → 6 只纳入的逐条理由 → 顺丰 180305 边界检验）、**三口径排名 + 极差**（六只极差均 3–4 位，无一只稳定）、**定价残差**（`CFO/㎡ = 0.0269×市值/㎡ + 78.97`，唯二离群的 −10.9% 与 +13.3% 恰为本项目两只）。v2.1.0 另把原 `reits-peer-comparison` 的四项做法并入（目的→样本口径的四种映射、`proxy` 指标单列不入排名、面板证据等级 A/B/C/D、反推市值交叉校验阈值），旧 skill 已退役归档。**v2.2.0 补「对比标准」**：位置由三层参照定义（组内位次与幅度／国债 1.85% 与健康线等绝对锚／OLS 残差隐含值），判定用词分「组内排序→相对位置→确认了位置」三档；商业模式优劣落成五轴（可预测性／分派自给度／增长来源／利益一致性／周期弹性），可改进项与独特优势改为三连判定（挂坐标＋轴＋下期字段；组内唯一＋可核对＋消失条件）。**v2.3.0 拆成两个 skill**：本 skill 只做取数与判断，交 `findings.csv`（判断＋用词档位＋锚点＋反例），正文由 `reits-report-writing` 按新增的 `comparison` 骨架写；问法升级为「市场在这几只身上定出了什么价」（定价函数斜率＋残差，可给隐含应有市值，明确不是目标价）、「风险留在谁的表上」（风险归属表 → 五轴 → 可迁移性三分：可复制／可购买／不可复制）；新增 `reits-report-writing` 的记者腔规则（六种模型腔改写法＋换标测试／删首段／删尾句） |

## 自检

```bash
python tools/build_raw.py      # 重建并校验 _raw_response.txt 可逆性（期望 ALL_MATCH）
python tools/count_report_words.py outputs/case_03_sinofarm_reit/report_508601.md --min 15000
python tests/run_tests.py      # 153 条断言（当前基线 PASS 151 / FAIL 0 / SKIP 2；两项投后报告未使用 IRR 的检查不适用）

# 横向基准可复跑（case_04）
cd outputs/case_04_peer_benchmarking
python build_panel.py    # 4 个 csv：panel / matrix_yield / matrix_quality / sample_funnel
python make_figs.py      # 5 张 SVG（坐标由数据计算）
python build_html.py     # 单文件 HTML，SVG 内联
```

| 测试组 | 条数 | 说明文档 |
|---|---|---|
| T-CALC 计算与对账 | 22 | `tests/test_calculations.md` |
| T-DQ 数据质量 | 24 | `tests/test_data_quality.md` |
| T-SKILL Skill 结构 | 31 | `tests/test_skill_execution.md` |
| T-REG 回归 | 17 | `tests/regression_tests.md` |
| **T-REPORT 报告形态** | **58** | 新增：正文口径字数与封面声明一致性、FLOW 编号残留、运行日志混入、来源锚点、未登记假设、可供分配 vs 实际分派、分派率 vs IRR、IRR 可重算、EBITDA 桥闭合、来源可追溯、缺失披露、估值敏感性 |

> 当前交付不生成独立 review 文件，也不要求固定审稿轮次；来源、计算和论证核验并入写作流程，未解决的实质问题进入报告。历史审稿版本由 Git 保留。

> **测试通过不代表结论正确。** 153 条断言拦的是"计算错、口径混、报告像运行日志"这三类可机检问题；"这个判断对不对"只能靠人工复核，记录见 `iteration_log/ITERATION_LOG.md` Iteration 6 的两轮审稿。

## 数据来源

全部案例文件通过**东方财富基金公告接口**（`api.fund.eastmoney.com/f10/JJGG`，`type=3` 定期报告分类）获取**公告原文 PDF**，逐份 URL 记录在 `source_documents/source_index.csv`。**获取渠道是第三方平台，不是交易所直连**——上交所公告查询接口需内部 `channelId`，公开请求不可用。文件为原样披露件、未改写，但不引用搜索引擎摘要。

**可复现性边界**：原始 PDF 按 `.gitignore` 不入库（305MB 且受版权约束），因此 **clone 后不能直接复现原始文件**；能复现的是①计算过程（`models/`、`tools/` 可从披露数值重算全部结论）、②报告结构（`template/` + `skills/*/FLOW.md`）、③数值溯源路径（文件 + 页码）。原始文件需按索引 URL 自行下载。

## 许可与边界

- 原始披露文件版权归发行人/管理人，仅作研究留档，不再分发。
- 本仓库不含任何非公开信息。
