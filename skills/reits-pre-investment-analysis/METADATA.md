type: flow

name: reits-pre-investment-analysis

version: 1.0.0

description: "公募REITs投前深度分析：基于招募说明书、法律意见书、基金合同、资产评估报告，完成产品概况、交易结构、基础资产、运营、收入成本、可供分配测算、估值、投资价值、风险与结论十部分分析，配套可复核现金流模型、情景与敏感性分析。"

domain: 公募REITs投前

source_report: "内部方法论；具体监管规则、交易所业务办法及评估准则须在每次运行的 REFERENCE_MAP/来源清单中登记全称、发布机构、文号或版本、生效日期、条款及官方 URL。不得将此描述当作已完成的法规引用。"

script_permission: true

output_dir: ./output

inputs:
  - name: fund_name
    description: 基金全称或简称，如 中信建投首农食品集团封闭式商业不动产证券投资基金
  - name: doc_root
    description: 披露文件根目录，需包含招募说明书、法律意见书、基金合同、资产评估报告；缺失项在报告中登记
  - name: analysis_date
    description: 分析基准日（YYYY-MM-DD）。用于确定可用的最新披露版本与份额参考价
  - name: discount_rate_scenarios
    description: 折现率情景，格式 "低,中,高"，如 "5.5,6.0,6.5"。为空时使用 #18 默认三档并标为研究假设
  - name: target_yield
    description: 投资者要求的分派率下限（%），用于 #21 判断是否满足投资门槛。为空时不作门槛判断
  - name: holding_years
    description: 拟持有期（年），默认 3。用于 #22 持有期回报测算

# 注意：data_requirements 中的 source_id 是来源渠道/发现入口映射，不是具体文件证据 ID。
# 每次运行必须将字段映射到 source_manifest.csv 中真实存在的 source_id，并记录文件名、页码/表格及原文定位。
# 未完成该映射的字段不得标记为 CONFIRMED。

data_requirements:
  - name: 基金募集规模
    freq: 一次性
    unit: 元
    role: "被解释变量：分派率分母"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "分派率无法计算，投前结论不可判定"
    source_id: SRC_SSE_REIT

  - name: 发行份额与发行价格
    freq: 一次性
    unit: 份 / 元
    role: "解释变量：单位分派与估值锚"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "单位分派无法验证，只能给总额"
    source_id: SRC_SSE_REIT

  - name: 资产评估值
    freq: 一次性
    unit: 元
    role: "被解释变量：估值水平核心"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "无法判断发行定价相对评估值的折溢价"
    source_id: SRC_SSE_REIT

  - name: 评估折现率
    freq: 一次性
    unit: "%"
    role: "解释变量：评估值的第一驱动"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "无法评估估值敏感性，参数合理性判断失效"
    source_id: SRC_SSE_REIT

  - name: 资本化率
    freq: 一次性
    unit: "%"
    role: "解释变量：与可比资产横向比较"
    nature: 历史事实
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "横向估值比较缺一把标尺，只能用折现率替代"
    source_id: SRC_SSE_REIT

  - name: 预测期与收益年限
    freq: 一次性
    unit: 年
    role: "解释变量：终值与期限结构"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "终值占比无法计算，长期估值结论不可判定"
    source_id: SRC_SSE_REIT

  - name: 历史营业收入与结构
    freq: 年
    unit: 元
    role: "被解释变量：预测起点"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "收入预测无锚，模型退化为纯假设"
    source_id: SRC_SSE_REIT

  - name: 历史运营成本与管理费
    freq: 年
    unit: 元
    role: "解释变量：EBITDA 的扣减项"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "EBITDA 无法测算，可供分配链条断裂"
    source_id: SRC_SSE_REIT

  - name: 出租率与租金单价
    freq: 年
    unit: "% / 元/平方米/月"
    role: "解释变量：收入的第一驱动"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "收入预测无法自下而上构建"
    source_id: SRC_SSE_REIT

  - name: 租约到期结构与租户集中度
    freq: 一次性
    unit: "% "
    role: "解释变量：现金流稳定性"
    nature: 历史事实
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "稳定性判断只能依赖出租率单指标，结论偏乐观"
    source_id: SRC_SSE_REIT

  - name: 资本性支出计划
    freq: 年
    unit: 元
    role: "解释变量：可供分配的最大扣减项"
    nature: 文件预测
    execution_required: false
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "可供分配被高估，分派率结论偏乐观"
    source_id: SRC_SSE_REIT

  - name: 可供分配金额预测
    freq: 年
    unit: 元
    role: "被解释变量：分派能力"
    nature: 文件预测
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "只能自建模型，须声明为独立假设"
    source_id: SRC_SSE_REIT

  - name: 专项计划与项目公司结构
    freq: 一次性
    unit: 文本
    role: "约束条件：现金流路径与税负"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "交易结构图无法绘制，关联交易与税负分析缺失"
    source_id: SRC_SSE_REIT

  - name: 原始权益人及关联方信息
    freq: 一次性
    unit: 文本
    role: "约束条件：利益一致性与潜在冲突"
    nature: 历史事实
    execution_required: false
    thesis_required: true
    importance: medium
    evidence_role: supporting
    missing_data_impact: "治理与关联交易风险段落缺失"
    source_id: SRC_SSE_REIT

  - name: 土地使用权到期日与剩余年限
    freq: 一次性
    unit: 年
    role: "约束条件：资产价值的时间边界"
    nature: 历史事实
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "评估终值与期限匹配无法验证，估值合理性不可判定"
    source_id: SRC_SSE_REIT

  - name: 可比REITs分派率与估值倍数
    freq: 一次性
    unit: "% / 倍"
    role: "解释变量：相对定价"
    nature: 历史事实
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "相对估值段落只能引用评估值，缺市场对照"
    source_id: SRC_CSINDEX

step0_required:
  - 确认基金名称、代码、分析基准日及输入文件真实存在、可读取
  - 按文件类型和用途裁决版本；记录候选版本、选用理由和基准日后信息
  - 关键事实记录具体文件名、PDF页码、章节/表格、单位、期间及事实类型
  - 区分历史披露、文件预测、独立研究假设；区分时点值、单季值和累计值
  - 缺失、扫描件、冲突和不适用分别登记，并说明对结论的影响

assumption_register:
  fields: [assumption_id, category, value, basis, sensitivity, owner, source_ref, status]
  categories: [收入端, 成本端, 资本性支出, 税费, 折现率, 增长率, 期限]
  status_enum: [CONFIRMED, UNVERIFIED, INDETERMINATE, SOURCE_UNAVAILABLE, DATA_QUALITY_WARNING]
  traceability_rule: |
    凡不能标注「文件 + 页码 + 表格名」的数字，一律进 assumptions.csv，不得在正文中作为披露值引用。
    反例（必须避免）：用「评估值 × CapRate」反推 NOI，再把 NOI − capex − 可供分配 的残差命名为
    「税费及预留」，并据此宣称发现「2026 年预留仅 75 万元、2027 年 3,059 万元，差 40 倍」。
    招募书并无该科目；该残差只是把口径误差塞进了一个不存在的行。见 ITERATION_LOG R3/C-2。
  reconciliation_rule: |
    每条从披露值反算的参数，必须同时给出「正算校验」：用反算参数重新构造披露值，与原文比对，
    差额超过 1% 的必须标注原因，无法标注原因的降级为 INDETERMINATE，不得进入估值基准情景。

valuation_params:
  groups:
    - name: 收益法
      fields: [discount_rate, forecast_years, terminal_growth, terminal_method]
    - name: 资本化率法
      fields: [cap_rate, stabilized_noi]
  rule: "两组参数必须同时给出；只给一组的，另一组标 NOT_COMPARABLE"

scenario_set:
  pessimistic:
    occupancy_delta: -3
    rent_growth: 0.0
    capex_uplift: 1.2
  base:
    occupancy_delta: 0
    rent_growth: 0.02
    capex_uplift: 1.0
  optimistic:
    occupancy_delta: 2
    rent_growth: 0.03
    capex_uplift: 0.9

formula_registry:
  - formula_id: F_NOI
    expression: 按底层资产经营口径逐项定义，不作为所有 REIT 通用的统一公式
    unit: 元
    freq: 年
    valid_from: 2021-06
    valid_to: null
    caliber_note: "不含折旧摊销与利息，不含资本性支出"
  - formula_id: F_EBITDA
    expression: 仅在 NOI 定义及折旧摊销处理明确时勾稽，不机械套用
    unit: 元
    freq: 年
    valid_from: 2021-06
    valid_to: null
    caliber_note: "若披露口径已为 EBITDA，直接引用并注明"
  - formula_id: F_DIST
    expression: 以招募说明书披露的可供分配金额测算表为准，逐项复原调整项
    unit: 元
    freq: 年
    valid_from: 2021-06
    valid_to: null
    caliber_note: "以招募说明书可供分配测算表的调整项为准，逐项对齐"
  - formula_id: F_YIELD
    expression: 发行规模口径分派率 = 可供分配金额 ÷ 实际募集规模；其他分母必须另行命名
    unit: "%"
    freq: 年
    valid_from: 2021-06
    valid_to: null
    caliber_note: "分母为募集规模（含扩募）；用评估值作分母时须改名为"评估值分派率""
  - formula_id: F_DCF
    expression: 按评估方法、现金流口径、收益期限和终值方法计算；DCF 仅适用于相应假设成立时
    unit: 元
    freq: 年
    valid_from: 2021-06
    valid_to: null
    caliber_note: "TV 可为期末价值或永续增长；商业不动产常用剩余年限内现金流+期末价值"

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
  - source_id: SRC_CSINDEX
    provider: 中证指数公司
    endpoint: https://www.csindex.com.cn/
    access_method: HTTP
    auth_required: false
    probe_status: DEGRADED
    probe_time: "2026-11-05"
    fallback_source_id: null
    note: "REITs 指数与分派率数据非全部公开，部分需终端"

quality_states: [CONFIRMED, PARTIALLY_SUPPORTED, INDETERMINATE, NOT_COMPARABLE, SOURCE_UNAVAILABLE, DATA_QUALITY_WARNING, UNDEFINED_THRESHOLD]
