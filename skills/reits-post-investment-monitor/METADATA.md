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
      拦截方式：tests/run_tests.py 的 T-DQ-12。
      实例：revenue_cum 曾装 2025Q4 单季收入 2,462 万元，被读成"全年"，实际全年 1.115 亿元（差 4.5 倍）。
    period_sum_identity: |
      Q1+Q2 = 中期报告 H1；Q1+Q2+Q3+Q4 = 年报 FY。不符须记差额并双列并行，不得静默取一。
      实例：某案例四季现金流加总与年报差 0.59%（审计调整，真实差异，须披露）；另一案例 H1 现金流误录为
      58,616,560.98，而原文 37,588,381.33 恰等于 Q1+Q2——前者在任何原始文件中都不存在。
    反例（必须避免）：把年报的"本年累计可供分配"命名为 dist，再与季报单季值并列比较，
    会在 Q1 之后逐季放大偏差（Q4 时差 4 倍）。

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
  - claim_id
  - statement
  - origin
  - indicator
  - judgment_rule
  - aggregation
  - band_ref
  - verdict
  - evidence_anchor

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
