--{abstract}--
思考路径：
1. 读研报不是读章节，是读结论与结论之间的支撑关系。先把全文切成"结论句 / 论据句 / 数据句 / 限定句"四类，其余内容（行业科普、公司沿革）降为背景。
2. 从结论句反推论证链：每条核心结论必须能找到若干前提（premise），每个前提必须能找到证据（evidence）。找不到证据的前提是"断链"，必须显式标记为断链，而不是补齐想象。
3. 论证链上的每条证据，按"缺了会不会崩"（execution_required）和"缺了结论成不成立"（thesis_required）两个维度分别打分。这两件事在旧模板里被混成一个 required，直接导致核心论据被降级。
4. 所有"高位/中位/低位""强/弱"必须落到 bands，所有公式必须落到生效期。研报里没给阈值就写 UNDEFINED_THRESHOLD，不给形容词留后门。
5. 把论证链映射成 Step/动作：一条论证链对应一个 Step，一个前提对应一个动作，一个证据对应一条数据依赖。映射完成后做两件事——数据能不能拿到（dry_run），结论能不能反推出来（反向复现）。
6. 反向复现是唯一有效的验收测试。结构完整但复现不出研报结论的 FLOW，判 PARTIAL，不判 PASS。
--{/abstract}--

# Step 0：研报解析与证据抽取

#1 --{动作}-- [数据]
**切分研报全文并标注句类**
* 数据依赖：研报正文全文
- 按页/段切分，保留 `文件简称 p页码` 锚点
- 逐段标注句类：`conclusion`（结论）/ `premise`（前提）/ `data`（含数值的陈述）/ `qualifier`（限定与条件）/ `background`（背景）
- 统计各类句子的数量与分布，`conclusion` 占比超过 30% 的报告说明论证密度低，后续需加密抽取
[输出]：句类标注表 `sentence_map.csv`
[输出示例]：
| id | 页 | 句类 | 原文摘要 | 关键数值 |
|---|---|---|---|---|
| S031 | p4 | conclusion | 煤炭板块正从周期波动定价转向战略安全资源定价 | — |
| S048 | p6 | premise | 长协机制使煤价波动率下降，盈利可预测性提升 | 波动率 22%→9% |
| S112 | p14 | data | 西方石油 PE_TTM 为 12.4 倍 | 12.4 |
| S047 | p5 | qualifier | 该结论成立的前提是长协履约率维持 90% 以上 | 90% |

#2 --{动作}-- [数据]
**抽取表格与图表数据点**
* 数据依赖：研报内表格与图表数据
- 逐表记录：表名、页、行列结构、单位、口径、时间范围
- 图表只记录可读出的数据点与坐标轴定义；示意图不入库
- 对同一指标在不同表出现且数值不一致的，标记 `CALIBER_CONFLICT` 并保留两个口径
[输出]：表格登记表 `table_registry.csv`
[输出示例]：
| table_id | 表名 | 页 | 指标 | 单位 | 口径 | 期间 | 取值 |
|---|---|---|---|---|---|---|---|
| T03 | 长协公式分段 | p8 | 长协价公式 | 元/吨 | 港口下水 | 2017-2021 | (基准+浮动)×比例 |
| T07 | 可比公司估值 | p14 | PE_TTM | 倍 | 2025E | 2025-08 | 中国神华 11.2 / 兖矿 8.9 |

#3 --{动作}-- [非数据]
**建立口径与术语对照**
* 信息来源：研报正文与脚注
- 列出全文出现的口径分歧：含税/不含税、期末/平均、累计/单季、港口/坑口、并表/权益
- 每个分歧项记录研报采用的口径与另一口径的换算关系（若有）
- 无法换算的，后续涉及该指标的公式必须标 `NOT_COMPARABLE`
[输出]：口径对照表 `caliber_map.md`
[输出示例]：
| 指标 | 口径A | 口径B | 研报采用 | 可换算 | 说明 |
|---|---|---|---|---|---|
| 煤价 | 港口 5500 大卡平仓价 | 坑口含税价 | A | 否 | 差价含运费与热值差，不可直接相减 |
| 收入 | 累计 | 单季 | 单季 | 是 | 累计差分 |

# Step 1：核心结论与论证链

#4 --{动作}-- [非数据]
**识别核心结论并排序**
* 信息来源：`sentence_map.csv` 中 conclusion 类句子
- 按"是否决定投资动作"排序，取前 3–7 条为核心结论（claim），其余为次级观察
- 每条 claim 写成可裁决的陈述句：含主语、指标、方向、阈值或时间条件
- 纯描述性句子（"行业空间广阔"）不得作为 claim，降为 background
[输出]：claim 清单 `claims.yaml` 的 claim_id 与 statement 部分
[输出示例]：
| claim_id | statement | 类型 | 是否可裁决 |
|---|---|---|---|
| C1 | 长协机制使行业盈利波动率较上一周期下降一半以上 | 机制型 | 是 |
| C2 | 煤炭板块估值锚由周期 PE 切换为资源重置价值 | 估值型 | 是 |
| C3 | 行业空间广阔 | 描述型 | 否（降 background） |

#5 --{动作}-- [非数据]
**构建论证链（claim → premise → evidence）**
* 信息来源：`sentence_map.csv`、`table_registry.csv`
- 每条 claim 向下拆 2–5 个 premise；每个 premise 向下挂 1–n 条 evidence
- evidence 必须可定位：`文件 p页码` 或 `table_id 行号`
- 找不到 evidence 的 premise 标 `BROKEN_CHAIN`，不得用常识补
- 记录 premise 之间的逻辑关系：`AND`（全部成立才成立）/ `OR`（任一成立即可）/ `WEIGHTED`
[输出]：论证链图 `argument_chain.yaml`
[输出示例]：
```yaml
C1:
  statement: 长协机制使行业盈利波动率较上一周期下降一半以上
  premises:
    - id: P1.1
      text: 长协覆盖率提升至 80% 以上
      logic: AND
      evidence: [E1.1.1]
    - id: P1.2
      text: 长协价与现货价价差收敛
      logic: AND
      evidence: [E1.2.1, E1.2.2]
  broken_chain: []
E1.2.1:
  desc: 长协价与现货价月度序列
  anchor: T03 p8
```

#6 --{动作}-- [非数据]
**抽取反向因素与失效条件**
* 信息来源：研报风险章节、qualifier 句
- 每条 claim 必须配至少 1 条反向因素（什么情况下结论不成立）
- 反向因素同样需要证据或明确的监测指标，否则标 `UNVERIFIABLE_RISK`
- 反向因素进入 FLOW 时，必须落在独立动作上，不得塞进"风险提示"段落了事
[输出]：反向因素表 `counter_factors.csv`
[输出示例]：
| claim_id | 失效条件 | 监测指标 | 证据 | 是否可验证 |
|---|---|---|---|---|
| C1 | 长协履约率跌破 90% | 月度履约率 | 政策文件 | 是 |
| C2 | 板块 PB 回升至 2 倍以上而 ROE 未改善 | 板块 PB、ROE | T07 | 是 |

# Step 2：证据权重与数据源

#7 --{动作}-- [数据]
**证据分级：execution_required / thesis_required / importance**
* 数据依赖：`argument_chain.yaml`、`counter_factors.csv`
- 对每条 evidence 分别回答两个问题：
  - 缺了它，流程还能不能跑完 → `execution_required`
  - 缺了它，这条 claim 还能不能成立 → `thesis_required`
- 两问皆为否 → 该证据不该进 data_requirements
- `thesis_required=true` → `importance ∈ {critical, high}`
- 标 `evidence_role`：core（直接支撑 claim）/ supporting（支撑 premise 的一个侧面）/ background（仅提供量级感）
- 写 `missing_data_impact`：缺了会怎样，具体到"哪条 claim 变成 INDETERMINATE"
[输出]：证据权重表 `evidence_weights.csv`
[输出示例]：
| evidence_id | 指标 | execution_required | thesis_required | importance | evidence_role | missing_data_impact |
|---|---|---|---|---|---|---|
| E2.3.1 | 西方石油 PE_TTM | false | true | critical | core | C2 的海外对标锚缺失，C2 降为 PARTIALLY_SUPPORTED |
| E2.3.2 | 板块股息率 | true | true | high | core | 无法判断"资源重估"是否已被股息定价 |
| E2.9.1 | 进口分国别月度 | false | false | medium | supporting | 仅影响供给结构的解释力 |

#8 --{动作}-- [非数据]
**降级复核（防止核心论据被静默降级）**
* 信息来源：`evidence_weights.csv`
- 逐条检查 `evidence_role=core` 且 `thesis_required=false` 的条目，要求写明降级理由
- 逐条检查出现在 claim statement 里的指标，其 `importance` 不得低于 high
- 输出降级清单；理由不成立的回退为 `thesis_required=true`
[输出]：降级审计表 `downgrade_audit.csv`
[输出示例]：
| evidence_id | 原判定 | 复核判定 | 理由 | 处理 |
|---|---|---|---|---|
| E2.1.1 | required=false | thesis_required=true | 该指标是 C2 唯一的海外估值锚 | 回退 |
| E2.9.1 | required=false | 维持 false | 仅用于解释供给结构，不进入 claim | 保留 |

#9 --{动作}-- [数据]
**数据源对接与可用性探测**
* 数据依赖：数据源可用性探测结果
- 为每条 `execution_required=true` 的证据指定 `source_id`，禁止留 null
- 实测探测：能否访问、能否取到目标指标、字段是否匹配、频率是否满足、返回是否有效
- 探测失败时按优先级回退：主源 → 备源 → `SOURCE_UNAVAILABLE`
- 记录 `probe_time`，因为数据源可用性是时变的
[输出]：数据源登记表 `source_registry.csv`
[输出示例]：
| source_id | provider | endpoint | access | auth | probe_status | probe_time | fallback |
|---|---|---|---|---|---|---|---|
| SRC_SSE_REIT | 上交所 | query.sse.com.cn | HTTP | 否 | VERIFIED | 2026-11-05 | SRC_EM_ANN |
| SRC_EM_ANN | 东方财富公告 | api.fund.eastmoney.com | HTTP | 否 | VERIFIED | 2026-11-05 | — |
| SRC_WIND_PE | Wind | 终端 | 客户端 | 是 | SOURCE_UNAVAILABLE | 2026-11-05 | SRC_CSINDEX |

# Step 3：阈值与公式

#10 --{动作}-- [数据]
**阈值标定**
* 数据依赖：`table_registry.csv`、历史序列
- 对每个需要判断方向或档位的指标，填齐 `direction / bands / window / calculation_method / applicable_period / threshold_source`
- `threshold_source` 优先级：研报明示 > 历史分位 > 行业惯例 > 监管规则
- 四者皆无 → `UNDEFINED_THRESHOLD`，该指标输出现值不给档位
- bands 必须写成可计算的不等式，禁止写"较高""偏低"
[输出]：阈值表 `thresholds.csv`
[输出示例]：
| 指标 | direction | bands | window | calc | applicable_period | source |
|---|---|---|---|---|---|---|
| 期末出租率 | higher_is_better | high≥95 / mid 90–95 / low<90 | 单期 | 期末值 | 2021-06 起 | 行业惯例 |
| 租金单价同比 | higher_is_better | high≥+3% / mid -3%~+3% / low<-3% | 4 季 | 同比 | 全期 | 研报明示 |
| 长协溢价 | context_dependent | — | — | — | — | UNDEFINED_THRESHOLD |

#11 --{动作}-- [数据]
**公式登记与版本分段**
* 数据依赖：历史制度与口径变更记录
- 每个计算公式登记 `formula_id / expression / variables / unit / freq / valid_from / valid_to / source / caliber_note`
- 制度或口径变更点必须切分版本；单条公式不得跨制度
- 运行期用错版本时，该动作输出 `NOT_COMPARABLE`，不给数值
[输出]：公式登记表 `formula_registry.csv`
[输出示例]：
| formula_id | expression | valid_from | valid_to | source |
|---|---|---|---|---|
| F_COAL_LTC_V1 | (基准价 + 浮动价) × 履约比例 | 2017-01 | 2021-12 | 发改价格〔2016〕 |
| F_COAL_LTC_V2 | 基准价 + 浮动价（区间 570–770） | 2022-01 | — | 发改价格〔2021〕 |

# Step 4：FLOW 生成

#12 --{动作}-- [非数据]
**论证链到 Step/动作的映射**
* 信息来源：`argument_chain.yaml`、`evidence_weights.csv`
- 一条 claim（或一组同源 claim）→ 一个 Step
- 一个 premise → 一个 `#N --{动作}--`
- 一条 evidence → 该动作 `* 数据依赖：` 中的一项，命名与 `data_requirements` 完全一致
- 反向因素 → 独立动作，置于对应 Step 末尾
- 映射完成后统计覆盖率：`thesis_required=true` 的证据必须 100% 有动作承接
[输出]：映射表 `flow_mapping.csv` 与覆盖率统计
[输出示例]：
| claim | premise | 动作 | 承接 evidence | 覆盖率 |
|---|---|---|---|---|
| C1 | P1.1 | #4 | E1.1.1 | 100% |
| C2 | P2.3 | #9 | E2.3.1, E2.3.2 | 100% |
| C2 | P2.4 | — | E2.4.1 | 0%（遗漏，需补） |

#13 --{动作}-- [非数据]
**写入统一 Step 0（数据预处理）**
* 信息来源：本 skill 的 Step 0 规范
- 目标 FLOW 的第一个 Step 固定为 `Step 0: Data Ingestion & Preprocessing`
- 覆盖：数据获取、source_id 验证、字段映射、单位统一、频率统一、时间对齐、缺失值、异常值、去重、数据修订、数据有效性、来源记录、标准化数据集生成
- 明确五种空值语义：`NA`（缺失）/ `0`（真实为零）/ `未披露` / `不适用` / `SOURCE_UNAVAILABLE`
- 后续动作只消费 Step 0 的产物，不得各自回读原始文件
[输出]：Step 0 章节文本 + 数据字典
[输出示例]：
| 字段 | 单位 | 频率 | 空值语义 | 来源 | 处理规则 |
|---|---|---|---|---|---|
| occ_end | % | 季 | NA / 未披露 | 季报 p10 | 不插值，保留 NA |
| revenue_q | 元 | 季 | 0 为真实零 | 季报 p8 | 累计差分，公式 F_REV_Q1 |

#14 --{动作}-- [非数据]
**写入动作输出规格与判定规则**
* 信息来源：`thresholds.csv`、`formula_registry.csv`、`claims.yaml`
- 每个动作必须有 `[输出]` 名称与 `[输出示例]` 表格骨架，示例中不得预填结论
- 每个判断句必须引用 `thresholds.csv` 中的 band 或 `formula_registry` 中的 formula_id
- claim 裁决必须写死 `aggregation`：`each_period` / `mean` / `latest` / `cumulative`
- 每个动作声明允许的输出状态（CONFIRMED 等），以及什么条件下输出 INDETERMINATE
[输出]：动作规格片段（并入 FLOW 正文）
[输出示例]：
| 动作 | 输出 | 裁决聚合 | 允许状态 |
|---|---|---|---|
| #6 | 出租率档位表 | each_period | CONFIRMED / PARTIALLY_SUPPORTED / INDETERMINATE |

# Step 5：可执行性验收

#15 --{动作}-- [数据]
**dry_run：数据可得性试跑**
* 数据依赖：`source_registry.csv`
- 用真实请求验证每条 `execution_required=true` 的指标能否取到至少一期数据
- 记录取到的期数、缺失期、失败原因
- 结论只能是三种：`RUNNABLE` / `RUNNABLE_WITH_GAPS` / `NOT_RUNNABLE`
[输出]：试跑报告 `dry_run_report.md`
[输出示例]：
| 指标 | 需求期数 | 实得期数 | 缺口 | 结论 |
|---|---|---|---|---|
| 季度出租率 | 4 | 4 | 0 | RUNNABLE |
| 评估报告资本化率 | 1 | 0 | 1（扫描件无文字层） | RUNNABLE_WITH_GAPS |

#16 --{动作}-- [数据]
**反向复现测试**
* 数据依赖：`dry_run` 取得的数据
- 在**不看研报结论**的条件下按新 FLOW 跑一遍
- 比对：核心 claim 的裁决方向是否与研报一致；决定性论据是否被省略
- 三种结果：`REPRODUCED`（方向一致且论据完整）/ `PARTIALLY_REPRODUCED`（方向一致但论据缺失）/ `NOT_REPRODUCED`
- 不得用"研报本来就没说清"作为 NOT_REPRODUCED 的免责理由，必须定位到具体断链
[输出]：复现报告 `reproduction_report.md`
[输出示例]：
| claim | 研报结论 | FLOW 裁决 | 关键论据是否齐 | 判定 |
|---|---|---|---|---|
| C1 | 波动率下降一半 | 下降 58%（F_COAL_LTC_V2） | 齐 | REPRODUCED |
| C2 | 估值锚切换 | INDETERMINATE（缺海外对标） | 缺 E2.3.1 | PARTIALLY_REPRODUCED |

#17 --{动作}-- [非数据]
**降级路径测试**
* 信息来源：`evidence_weights.csv`
- 逐条抽掉 `importance=critical` 的证据，重跑受影响动作
- 期望：输出 `INDETERMINATE` 或 `SOURCE_UNAVAILABLE`，并写明缺哪条、影响哪条 claim
- 出现以下任一情况判 FAIL：崩溃、静默补数、用其他指标替身而不声明、仍然输出 CONFIRMED
[输出]：降级测试记录 `degradation_test.md`
[输出示例]：
| 抽掉的证据 | 受影响 claim | 实际输出 | 期望 | 判定 |
|---|---|---|---|---|
| E2.3.1 | C2 | INDETERMINATE + 缺失说明 | INDETERMINATE | PASS |

# Step 6：归档

#18 --{动作}-- [非数据]
**产出归档与版本记录**
* 信息来源：以上全部产出
- 按四件套写出：`SKILL.md`、`FLOW.md`、`METADATA.md`、`_raw_response.txt`
- `_raw_response.txt` 使用逐文件标记：`<<<FILE: x>>> ... <<<END: x>>>`，文末 `<<<END>>>`；三份文件内容必须与拆分后的独立文件逐字节一致
- 同时归档过程件：`research_graph.yaml`（claims + argument_chain + evidence_weights + thresholds + formula_registry 合并）、`downgrade_audit.csv`、`dry_run_report.md`、`reproduction_report.md`
- 版本号规则：结构变更 +0.1.0，阈值/公式变更 +0.0.1，并在 `CHANGELOG.md` 记一行
[输出]：归档清单 `delivery_manifest.md`
[输出示例]：
| 文件 | 用途 | 校验 |
|---|---|---|
| SKILL.md | 触发与约束 | 与 raw 一致 ✓ |
| FLOW.md | 执行主体 | 与 raw 一致 ✓ |
| METADATA.md | 数据契约 | YAML 可解析 ✓ |
| research_graph.yaml | 论证链与证据权重 | 覆盖率 100% ✓ |
