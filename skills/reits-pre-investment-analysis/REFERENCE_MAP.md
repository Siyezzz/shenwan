# Reference Map — reits-pre-investment-analysis

本文件是本 Skill 的引用地图。它区分仓库内真实存在的文件、仓库内的索引记录、运行时需要用户提供/下载的原始材料，以及外部方法论来源。

## 1. 仓库内已确认存在的文件

| 用途 | 路径 | 可证明什么 | 不能证明什么 |
|---|---|---|---|
| 原始披露材料目录 | `source_documents/source_index.csv` | 已登记的基金、文件名、类型、期间、披露日期、下载 URL、预期本地路径、状态 | 不能证明 PDF 当前已下载到运行环境 |
| 投前流程 | `skills/reits-pre-investment-analysis/FLOW.md` | 分析步骤与输出要求 | 不能代替原始披露材料 |
| Skill 入口 | `skills/reits-pre-investment-analysis/SKILL.md` | 触发条件与执行约束 | 不能代替 METADATA 配置 |
| 配置与公式登记 | `skills/reits-pre-investment-analysis/METADATA.md` | 输入字段、数据要求、情景、公式和数据源登记 | `source_id` 不是某份 PDF 的证据定位 |
| 投前报告模板 | `template/investment_report_template.md` | 报告结构参考 | 不是事实来源 |
| 现金流模型样板 | `models/cash_flow_model.xlsx` | 工作簿结构/公式样板 | 不是当前标的实际模型或数据 |
| 工具脚本 | `tools/ingest_sources.py`、`tools/build_source_index.py`、`tools/build_bottomup.py`、`tools/build_model.py`、`tools/build_matrices.py`、`tools/count_report_words.py` | 对应脚本存在，可检查源码与参数 | 未执行前不能声称脚本已运行或输出已生成 |
| 数据与报告测试 | `tests/test_data_quality.md`、`tests/test_calculations.md`、`tests/test_skill_execution.md`、`tests/regression_tests.md` | 测试标准/回归案例 | 文档存在不等于当前运行已通过测试 |

## 2. 原始披露文件的真实状态

当前 Git 仓库的 `source_documents/` 目录仅有 `source_index.csv`。原始 PDF 未随仓库提交；索引中的 `local_path` 是预期/本地保存路径，必须在运行环境中逐个检查。

索引目前覆盖三个案例：508056（中金普洛斯）、180302（华夏深国际）、508601（中信建投首农）。这些案例材料只能作为对应基金的来源，不能跨基金借用数值。对每个新标的：
1. 按基金代码过滤索引；
2. 检查本地 PDF 是否存在；
3. 缺失时使用该行 URL 下载；
4. 记录 SHA-256、页数、文字层/OCR 状态；
5. 以实际下载文件为证据，不能以索引记录代替文件。

## 3. 正式材料类型与字段映射

| 材料类型 | 主要支持的字段/判断 | 优先引用内容 |
|---|---|---|
| 招募说明书（含更新稿） | 基金概况、募集规模、发行安排、交易结构、资产、预测可供分配、风险因素 | 具体章节、表格、PDF 页码 |
| 基金合同 | 基金期限、分配机制、持有人权利、治理安排 | 条款编号及 PDF 页码 |
| 资产支持专项计划文件 | 专项计划结构、现金流分配顺序、费用与账户安排 | 交易结构/分配条款 |
| 法律意见书 | 权属、合规、许可、重大合同、法律风险 | 法律核查结论及页码 |
| 资产评估报告 | 评估基准日、方法、折现率、资本化率、预测期、终值 | 评估参数表及页码 |
| 审计报告/年度报告 | 历史收入、成本、利润、现金流、资产负债及审计意见 | 报表及附注 |
| 季报/中报/运营公告 | 出租率、租金、收缴率、租户、运营变化 | 运营数据表及披露期间 |
| 外部区域/可比数据 | 区域经济、竞品供给、市场租金、REITs二级市场估值 | 原始发布机构、发布日期、统计口径 |

材料的具体文件名和版本不在本表硬编码，统一以当前基金筛选后的 `source_index.csv` 记录及本次运行的 `source_manifest.csv` 为准。

## 4. 外部方法论与市场数据

METADATA 中的 `SRC_SSE_REIT`、`SRC_EM_ANN`、`SRC_CSINDEX` 是来源渠道/数据提供方标识，不是具体证据。每次引用必须补充实际公告 URL、文件名、披露日期、访问日期、页码或数据字段。

监管规则引用必须记录规则全称、发布机构、文号/版本、生效日期、具体条款及官方链接。不得只写“依据交易所规则”或“依据评估准则”。市场比较数据必须记录观察日期、价格口径、分母口径及样本筛选理由。

## 5. 引用质量规则

任何事实性结论至少满足以下链条：

`Claim → Metric/Value → source_id → exact file → page/table/section → source quote/location`

无法建立完整链条时，结论降级为 `PARTIALLY_SUPPORTED` 或 `INDETERMINATE`。外部数据、研究假设和管理人预测分别标识，不得伪装成历史事实。
