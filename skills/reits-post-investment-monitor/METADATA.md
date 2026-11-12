type: flow

name: reits-post-investment-monitor

version: 1.0.0

description: "公募REITs存续期定期跟踪：以季报/半年报/年报/运营数据公告为数据源，按运营指标、区域与项目归因、收入与可供分配金额三层展开，处理累计与单季口径，输出数据矩阵、归因表、重点季度复盘与 claim 裁决。"

domain: 公募REITs投后

source_report: "内部方法论（无单一来源研报；口径规则依据《公开募集基础设施证券投资基金指引》与沪深交易所定期报告编制要求）"

script_permission: true

output_dir: ./output

inputs:
  - name: fund_code
    description: 基金代码，如 508056 / 180302。用于定位 doc_root 下子目录与命名产出文件
  - name: start_period
    description: 分析起始期，格式 YYYYQn 或 YYYYHn 或 YYYY，如 2025Q1
  - name: end_period
    description: 分析目标期，如 2025Q4。必须不晚于最后一期已披露定期报告
  - name: focus_period
    description: 重点分析期，如 2025Q4。用于 #18 专题复盘；可为空，为空时跳过 #18
  - name: doc_root
    description: 原始披露文件根目录，目录结构为 <doc_root>/<code>_<简称>/<YYYY-MM-DD>_<tag>_<标题>.pdf
  - name: band_override
    description: 阈值覆盖，键值对形式，如 occupancy.high=93。为空时使用 metric_bands 默认值

data_requirements:
  - name: 期末出租率
    freq: 季
    unit: "%"
    role: "被解释变量：运营质量第一指标"
    period_semantics: 时点
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "无法判断运营是否稳住，区域归因失去分母"
    source_id: SRC_SSE_REIT

  - name: 期末租金单价
    freq: 季
    unit: 元/平方米/月
    role: "被解释变量：价格端"
    period_semantics: 时点
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "无法识别以价换量，租金结论不可判定"
    source_id: SRC_SSE_REIT

  - name: 期末租金收缴率
    freq: 季
    unit: "%"
    role: "解释变量：现金回收质量"
    period_semantics: 时点
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "无法区分账面收入与实收现金"
    source_id: SRC_SSE_REIT

  - name: 期末加权平均剩余租期
    freq: 季
    unit: 天
    role: "解释变量：续租风险前置指标"
    period_semantics: 时点
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "到期结构风险无法量化"
    source_id: SRC_SSE_REIT

  - name: 分项目出租率
    freq: 季
    unit: "%"
    role: "被解释变量：区域归因基础"
    period_semantics: 时点
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "区域归因不可执行，只能给整体结论"
    source_id: SRC_SSE_REIT

  - name: 分项目租金单价
    freq: 季
    unit: 元/平方米/月
    role: "被解释变量：区域价格差异"
    period_semantics: 时点
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "无法判断区域是量的问题还是价的问题"
    source_id: SRC_SSE_REIT

  - name: 分项目剩余租期
    freq: 季
    unit: 天
    role: "解释变量：区域续租压力"
    period_semantics: 时点
    execution_required: false
    thesis_required: false
    importance: medium
    evidence_role: supporting
    missing_data_impact: "区域归因缺少续租维度，不影响主结论"
    source_id: SRC_SSE_REIT

  - name: 营业收入
    freq: 季
    unit: 元
    role: "被解释变量：收入端"
    period_semantics: 期间累计
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "收入分析不可执行"
    source_id: SRC_SSE_REIT

  - name: 可供分配金额
    freq: 季
    unit: 元
    role: "被解释变量：分派能力核心"
    period_semantics: 期间累计
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "核心结论不可判定，报告仅剩运营描述"
    source_id: SRC_SSE_REIT

  - name: 实际分派金额
    freq: 期
    unit: 元
    role: "对照项：分配政策，不作为经营判断"
    period_semantics: 期间累计
    execution_required: false
    thesis_required: false
    importance: medium
    evidence_role: background
    missing_data_impact: "不影响经营结论，仅缺分配政策描述"
    source_id: SRC_SSE_REIT

  - name: 经营活动现金流净额
    freq: 季
    unit: 元
    role: "解释变量：可供分配的现金来源"
    period_semantics: 期间累计
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "无法验证可供分配是否有现金支撑"
    source_id: SRC_SSE_REIT

  - name: 净利润
    freq: 季
    unit: 元
    role: "解释变量：会计利润，受折旧摊销影响"
    period_semantics: 期间累计
    execution_required: false
    thesis_required: false
    importance: medium
    evidence_role: supporting
    missing_data_impact: "不影响主要结论，REITs 以可供分配为准"
    source_id: SRC_SSE_REIT

  - name: 分项目营业收入
    freq: 季
    unit: 元
    role: "被解释变量：收入区域归因"
    period_semantics: 期间累计
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "收入只能给总额，无法归因到项目，区域优势结论缺一半"
    source_id: SRC_SSE_REIT

  - name: 资本性支出
    freq: 期
    unit: 元
    role: "解释变量：可供分配的扣减项"
    period_semantics: 期间累计
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "可供分配变动原因无法闭合"
    source_id: SRC_SSE_REIT

  - name: 租户集中度（前五大占比）
    freq: 期
    unit: "%"
    role: "解释变量：客户结构风险"
    period_semantics: 时点
    execution_required: false
    thesis_required: false
    importance: medium
    evidence_role: supporting
    missing_data_impact: "客户结构分析缺失，不影响当期运营结论"
    source_id: SRC_SSE_REIT

  - name: 租约到期结构（未来各年到期面积占比）
    freq: 期
    unit: "%"
    role: "解释变量：续租风险时间分布"
    period_semantics: 时点
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "下一期观察指标无法给出时间表"
    source_id: SRC_SSE_REIT

period_semantics:
  values: [时点, 期间累计, 单季]
  rules:
    - "时点值在半年/年度口径取期末快照，不取平均"
    - "期间累计值做差分得单季：Q2=H1−Q1，Q3=Q3累计−H1，Q4=FY−Q3累计"
    - "原始已披露单季的直接使用，不得二次差分"
    - "差分结果与年报披露单季值不一致时，以年报为准并记 DATA_QUALITY_WARNING"

metric_naming:
  pattern: "<base>[_<suffix>]"
  bases: [revenue, dist, distributable, distributed, net_profit, cfo, ebitda,
          occ, rent, rent_avg_period, wale, collection, area_leasable, area_leased]
  suffixes:
    "": "本期披露原值（时点值或当期累计值，由 period_semantics 决定）"
    _prev: "上一可比期同口径值，用于算差与算比，不允许直接当结论"
    _yoy: "同比变动，单位 pct，是变动量不是水平值"
    _cum: "本年累计（YTD）口径，与单季值不可混用"
    _q: "单季值。两种来源必须区分：①季报 §3.1「本期」数为披露原值（如收入、净利润、经营现金流）；②由累计值差分得出（如 Q2 = H1 − Q1）。只写 _q 不够，run_log 须注明属哪一种"
  rule: |
    列名必须可解析为 base+suffix，禁止同义异名（occ / occupancy / 出租率 混指同一含义）。
    _q 结尾的列须在 run_log 写明来源（披露原值 or 差分）与相应差分公式。
  validation:
    cum_monotonic: |
      _cum 指标在同一 metric + dim + 年度内必须单调不减（累计值不可能下降）。
      这是可自动化的硬约束：若 _cum 序列出现下降，几乎一定把单季披露原值误标成了累计。
      拦截方式：tools/check_panel.py 的 T-DQ-12（可执行脚本，退出码非 0 即不合格）。
      实例：revenue_cum 曾装 2025Q4 单季收入 2,462 万元，被读成"全年"，实际全年 1.115 亿元（差 4.5 倍）。
    period_sum_identity: |
      Q1+Q2 = 中期报告 H1；Q1+Q2+Q3+Q4 = 年报 FY。不符须记差额并双列并行，不得静默取一。
      实例：某案例四季现金流加总与年报差 0.59%（审计调整，真实差异，须披露）；另一案例 H1 现金流误录为
      58,616,560.98，而原文 37,588,381.33 恰等于 Q1+Q2——前者在任何原始文件中都不存在。
    反例（必须避免）：把年报的"本年累计可供分配"命名为 dist，再与季报单季值并列比较，
    会在 Q1 之后逐季放大偏差（Q4 时差 4 倍）。

source_index_schema:
  file: "<output>/source_index_<code>.csv"
  encoding: utf-8-sig
  primary_key: source_id
  parent_table: "<output>/dataset/doc_index.csv"
  purpose: |
    正文每个数字都能 3 步回到原文：source_id → file + page_from-page_to + section → 原文数值。
    内部标签（q2026Q3 / y2025）不是文件，不能充当来源；它是 tag 列，只用于机器匹配。
  fields:
    source_id:   {required: true,  rule: "S0001 递增"}
    file:        {required: true,  rule: "doc_index.file 原值，完整文件名含 .pdf，外键"}
    local_path:  {required: true,  rule: "相对 doc_root 的路径"}
    url:         {required: true,  rule: "公告 URL；无则 NA(offline)，不得留空；非空须含 fund_code"}
    page_from:   {required: true,  rule: "整数 ≥ 1"}
    page_to:     {required: false, rule: "≤ doc_index.pages；缺省等于 page_from"}
    section:     {required: true,  rule: "原文小节号或表名"}
    metric:      {required: true,  rule: "与 metric_naming 的 base 对齐"}
    value:       {required: true,  rule: "原文数值，不在本步换算"}
    unit:        {required: true,  rule: "原文单位"}
    kind:        {required: true,  rule: "披露原值 | 披露原值（期间均值） | 披露原值（年初至今） | 自算"}
    computed:    {required: true,  rule: "是 / 否"}
    formula:     {required: false, rule: "computed=是 时必填"}
  hard_checks:
    - C1 外键：source_index.file ⊆ doc_index.file
    - C2 页码上界：page_to ≤ doc_index.pages
    - C3 自算必带公式：computed=是 → formula 非空
    - C4 URL 回验：url 非空且非 NA(offline) → 含 fund_code
    - C5 锚点覆盖：正文 <tag> p<page> 锚点可在 source_index 命中 file 且页码落在区间内
  enforcement: |
    tools/validate_output.py 一次完成 C1–C5，退出码非 0 不得交付。
    该脚本只依赖标准库，可对任意 output 目录重复运行——这是"可稳定复现"的最低条件。
    仅有文字规范、没有可执行校验，等于没有校验（历史教训：来源索引只写标签、URL 回验被静默跳过）。

metric_bands:
  occupancy:
    direction: higher_is_better
    high: ">=95"
    medium: "90-95"
    low: "<90"
    window: 单期
    calculation_method: 期末出租率
    applicable_period: "2021-06 起"
    threshold_source: 行业惯例
  rent_yoy:
    direction: higher_is_better
    high: ">=3"
    medium: "-3~3"
    low: "<-3"
    window: 4季
    calculation_method: 同口径期末租金单价同比
    applicable_period: "2022-01 起"
    threshold_source: 行业惯例
  collection:
    direction: higher_is_better
    high: ">=100"
    medium: "95-100"
    low: "<95"
    window: 单期
    calculation_method: 期末租金收缴率
    applicable_period: 全期
    threshold_source: 行业惯例
  wale:
    direction: higher_is_better
    high: ">=540"
    medium: "365-540"
    low: "<365"
    window: 单期
    calculation_method: 期末加权平均剩余租期（天）
    applicable_period: 全期
    threshold_source: 行业惯例
  underdefined_policy: "任一指标无 threshold_source 时输出 UNDEFINED_THRESHOLD，不给档位"

claim_schema:
  version: 2
  purpose: >
    claim 不是"从报告里挑几句有意思的话"，是**可证伪表述的台账**。作用是三条：
    ① 抗选择性叙事——只讲对自己有利的结论时，台账会把没讲的条款和承诺顶出来；
    ② 兑现已记账——管理层在募集书、季报里说过的话，逐期对账，形成可追溯的兑现率；
    ③ 省下一期重复劳动——下期沿用同一张表，只做裁决，不重新发明该盯什么。
  files:
    ledger: claims_<code>.yaml          # 台账：跨期沿用，只增不改，唯一事实来源
    verdict: claims_verdict_<code>.csv  # 本期裁决：由台账 × panel 派生，每次重出
  columns:                              # 14 列固定，顺序一致，两文件同名
    - seq              # 展示序号 C1..Cn，按 origin_page 升序并在同文件内重排
    - claim_id         # 稳定主键 C-<sha1[:6]>，同输入必得同 ID，重跑不变
    - statement        # 陈述原文，≤60 字，只做归一化不得改写语义
    - origin_file      # 必须等于 doc_index.file 原值（完整文件名）
    - origin_page      # 整数页码，须落在 doc_index.pages 内
    - quote            # 原文逐字摘录 ≤40 字，不得转述
    - source_bucket    # S1/S2/S3/S4，见 source_buckets
    - indicator        # 与 metric_naming 的 base 对齐，须能在 panel 找到
    - judgment_rule    # 五枚枚举之一，见 judgment_rules
    - rule_param       # 规则参数，缺失则判 INDETERMINATE
    - aggregation      # each_period / mean / latest
    - periods_covered  # 观测期，分号分隔，如 "2026Q1;2026Q2;2026Q3"
    - observed         # 逐期取值或算式，禁止写"符合预期""基本达标"
    - verdict          # 六态之一，见 verdict_rules

  source_buckets:            # 封闭集，桶外内容一律不入台账
    S1_契约义务:
      describe: 基金合同、招募说明书中含"应当/应/不低于/不少于/%以上/分配比例"的义务条款
      example: 符合分红条件时，应将 90% 以上的年度可供分配金额分配
      priority: 1
    S2_招募书预测:
      describe: 招募书、评估报告中含"预测/预计/目标/拟"的量化指标
      example: 2023/2024 年预测现金分派率 4.52%/4.76%
      priority: 2
    S3_管理层表述:
      describe: 最近四期定期报告正文中含"暂无/已全部/有望/预计/将/保持/不排除"的定性句，且句内出现可核查指标
      example: 望亭物流园 2026 年暂无年内到期面积
      priority: 3
    S4_扩募评估:
      describe: 扩募说明书、资产评估报告中的购入项目预测
      priority: 4

  extraction_rules:           # 规则抽取，不用裁量；给定同一批文件必得同一张表
    - 以「。」「；」切句，逐句匹配 source_buckets 的关键词
    - 句内必须同时命中①桶关键词②可核查项（数字、出租率、租金、分派、面积、期限之一），缺一不入
    - statement 去掉"公司认为""总体来看"等主观前缀，保留主体与谓语
    - quote 取包含可核查项的连续 40 字以内原文，不得跨句拼接
    - 同一 indicator 在同一 origin_file 内只保留最新一条，旧的转 SUPERSEDED
    - 台账上限 12 条；超限按 priority 升序截断，截断项记入 run_log
    - "提升运营效率""优化资产结构"这类无可核查项者，禁止入库

  id_rule:
    formula: "C-" + sha1(normalize(origin_file) + "|" + normalize(statement))[:6]
    normalize: 去空白、全角转半角、数字统一为半角
    invariant: 同一披露文件同一句话，跨期重跑 ID 不变；statement 修订则 ID 变，旧 ID 保留在 ledger 并标 SUPERSEDED

  judgment_rules:             # 五枚枚举，裁决时只能执行不得新增
    threshold_gte:   "观测值与 rule_param 比较，≥ 为满足；rule_param 必须来自契约或披露原文数字"
    threshold_lte:   "≤ 为满足"
    each_period_eq:  "每个观测期均等于 rule_param；任一不等即违反"
    monotonic:       "观测期序列不劣于基期（按 indicator 的 direction 定性）"
    direction_only:  "原文只给方向未给数字；只能判 PARTIALLY_SUPPORTED 或 INDETERMINATE，永不得判 CONFIRMED"
  rule_param_policy: >
    阈值必须可溯源到原文（契约条款、招募书预测值、披露数值）。
    取不到原文数字时不得用行业惯例代填，只能降级为 direction_only 并写明"原文未给量化阈值"。

  verdict_rules:              # 六态机械判据，满足即判，不得叠加主观判断
    CONFIRMED:            "所有观测期满足 judgment_rule，且观测期数 ≥ 声明覆盖期的 50%"
    REFUTED:              "任一观测期明确违反 judgment_rule"
    PARTIALLY_SUPPORTED:  "方向与陈述一致但幅度未达 rule_param，或 direction_only 且观测方向正确"
    INDETERMINATE:        "观测期未到 / 指标未披露 / rule_param 缺失 / 只有定性无量化"
    NOT_COMPARABLE:       "阈值分母与观测分母不同且不可换算；必须在 observed 写清两套口径的具体数值"
    SUPERSEDED:           "同一 indicator 出现更新表述，旧条目不参与本期裁决"

  evidence_policy:
    - origin_file、origin_page、quote 三锚缺一不得入库
    - origin_page 须能被 doc_index 反查到该 file 的总页数之内
    - verdict 非 INDETERMINATE 时，observed 必须含具体数值或算式，且能在 panel.csv 复现
    - 一条 claim 对应一个 indicator；跨指标陈述须拆成多条

  hard_checks:                # tools/check_claims.py 逐条执行
    - CC1 列名与顺序等于 columns，14 列不缺不多
    - CC2 claim_id 符合 C-[0-9a-f]{6}，且台账内唯一
    - CC3 同一 claim_id 的 statement 在 ledger 中不得被静默改写（改则须新增 SUPERSEDED 记录）
    - CC4 source_bucket ∈ 四桶，origin_file ∈ doc_index.file
    - CC5 verdict ∈ 六态；judgment_rule ∈ 五枚举
    - CC6 direction_only 不得出现 CONFIRMED
    - CC7 CONFIRMED 的 periods_covered 条数 ≥ 声明期数一半，且 observed 无"未达标/未披露"字样
    - CC8 条数 ≤ 12；S1 桶至少 1 条
    - CC9 observed 禁含"符合预期""基本达标""大致相符"等空判词
    - CC10 两文件（ledger / verdict）的 claim_id 集合一致，verdict 不得凭空新增

formula_registry:
  - formula_id: F_REV_Q
    expression: 单季收入 = 本期累计 − 上期累计（Q1 直接取累计）
    variables: [rev_cum_t, rev_cum_t-1]
    unit: 元
    freq: 季
    valid_from: 2021-06
    valid_to: null
    caliber_note: "仅当披露口径为累计时适用；Q2=H1−Q1，Q3=Q3−H1，Q4=FY−Q3"
  - formula_id: F_DIST_Q
    expression: 单季可供分配 = 本期累计 − 上期累计
    variables: [dist_cum_t, dist_cum_t-1]
    unit: 元
    freq: 季
    valid_from: 2021-06
    valid_to: null
    caliber_note: "同上；与 EBITDA、CFO 交叉校验"
  - formula_id: F_OCC_DELTA
    expression: 出租率变动 = 期末出租率_t − 期末出租率_t-4
    variables: [occ_t, occ_t-4]
    unit: pct
    freq: 季
    valid_from: 2021-06
    valid_to: null
    caliber_note: "同比口径；跨扩募期不可比，需剔除新购入资产"

source_registry:
  - source_id: SRC_SSE_REIT
    provider: 上海证券交易所
    endpoint: https://www.sse.com.cn/disclosure/fund/announcement/
    access_method: HTTP
    auth_required: false
    probe_status: VERIFIED
    probe_time: "2026-11-05"
    fallback_source_id: SRC_EM_ANN
  - source_id: SRC_EM_ANN
    provider: 东方财富基金公告
    endpoint: https://api.fund.eastmoney.com/f10/JJGG
    access_method: HTTP
    auth_required: false
    probe_status: VERIFIED
    probe_time: "2026-11-05"
    fallback_source_id: null

quality_states: [CONFIRMED, PARTIALLY_SUPPORTED, INDETERMINATE, NOT_COMPARABLE, SOURCE_UNAVAILABLE, DATA_QUALITY_WARNING, UNDEFINED_THRESHOLD]
