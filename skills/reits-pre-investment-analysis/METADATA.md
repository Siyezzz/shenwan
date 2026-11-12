type: flow

name: reits-pre-investment-analysis

version: 1.3.0

description: "公募REITs投资分析报告：以真实披露资料和可复算模型为依据，完成资产、运营、现金流、估值、投资者回报与投资决策分析；输出路径必须与仓库/运行环境实际文件一致。"

domain: 公募REITs投前

source_report: "内部方法论；具体监管规则、交易所业务办法及评估准则须在每次运行的来源清单中登记全称、发布机构、文号或版本、生效日期、条款及官方 URL。不得将此描述当作已完成的法规引用。"

script_permission: true

output_dir: outputs/{case_dir}

# 交付路径以仓库脚本实际配置为准；模型可位于案例目录之外。
deliverables:
  case_dir_required:
    - source_index.csv
    - assumptions.csv
    - claims_verdict.csv
    - thesis.md
    - report_<fund_code>.md
    - report_metrics.json
    - run_log.md
    - figures/
  model_paths:
    current_508601:
      - models/cash_flow_model.xlsx
      - models/scenario_2028.csv
    rule: "先检查脚本实际输出配置；不得把模型文件强制复制到 outputs/{case_dir}/，也不得仅凭示例推断路径。"
  quality_control: "来源、计算、逻辑和表达核验嵌入 reits-report-writing 的既有步骤及模型验证。"

case_dir: "由 fund_code + fund_slug 生成，例如 case_03_sinofarm_reit；不得使用未创建的 ./output 目录。"

report_output: "outputs/{case_dir}/report_<fund_code>.md；写作阶段衔接 skills/reits-report-writing，不得以模型或数据表代替报告。"

inputs:
  - name: fund_name
    description: 待分析公募 REITs 的全称或简称；不限定管理人、资产类型或案例
  - name: doc_root
    description: 披露文件根目录，需包含招募说明书、法律意见书、基金合同、资产评估报告；缺失项在报告中登记
  - name: analysis_date
    description: 分析基准日（YYYY-MM-DD）。用于确定可用披露版本和投资者可获得的信息集；市场价格仅在研究任务需要时获取
  - name: investment_case
    description: IPO 发行定价复盘 / 上市后二级市场投资分析 / 两者比较。未指定时默认按所给文件对应的项目/发行分析；仅在研究任务明确要求时加入二级市场分析
  - name: purchase_date
    description: 特定投资者的假设或实际买入日期；未提供时不得将分析基准日误写为实际成交日
  - name: purchase_price
    description: 特定投资者的实际或假设买入价格（元/份）；仅在研究任务需要特定投资者回报时获取，缺失则不给精确 XIRR
  - name: discount_rate_scenarios
    description: 折现率情景，格式 "低,中,高"；由披露值、独立值或合同/历史依据校准，未提供且无依据则不设默认档
  - name: target_yield
    description: 投资者要求的分派率下限（%），仅用于步骤17/24的门槛或目标收益判断；为空时不作门槛判断
  - name: holding_years
    description: 拟持有期（年），仅在研究任务提供时用于持有期回报测算；未提供不设默认值

investment_decision_contract:
  required_outputs:
    - investment_rating: 积极 / 中性 / 谨慎 / 回避，并说明适用投资者与持有期限
    - valuation_range: 说明估值对象、方法、关键参数和证据限制
    - entry_condition: 基于要求回报率和投资者现金流推导价格条件；无法推导时说明缺失数据
    - return_profile: 分派收益率与总回报分开，按任务选择认购/买入视角，并说明 IRR/XIRR 的期限和假设
    - catalysts_and_risks: 上行催化、主要风险、可监测触发条件
    - invalidation: 可观测的投资逻辑失效条件
  decision_rule: "资产质量、现金流、估值、安全边际和投资者期限必须共同支持评级；不得仅凭分派率给出买入建议。"

# 注意：data_requirements 中的 source_id 是来源渠道/发现入口映射，不是具体文件证据 ID。
# 每次运行按 outputs/{case_dir}/source_index.csv 的真实字段定位具体文件，记录文件名、页码/表格及原文位置；不假定索引含 source_id 列。
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
    missing_data_impact: "横向估值比较缺一把标尺；不得用折现率替代，资本化率法为非强制的第二方法"
    source_id: SRC_SSE_REIT
    evidence_note: "cap_rate 仅用于可比横向核对，不能替代 discount_rate；资本化率法非强制第二方法"

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
    missing_data_impact: "租约与集中度风险无法充分核验，稳定性结论受限"
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
    missing_data_impact: "资本开支扣减与分派可持续性无法充分验证"
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
    关键参数须记录披露值、独立值、合同/历史依据、合理性及结果影响；优先利用已有字段，不扩展 schema。
    阈值/判断标尺须区分法规或合同明示、历史观测、可比市场数据、研究者预警线；不得把研究者阈值称为行业标准。
    不以残差造不存在的科目，不将口径差异命名为税费、预留等披露项目。
  reconciliation_rule: |
    每条从披露值反算的参数，须给出「正算校验」并标注差异原因；1% 仅为复核提示，不得机械拒绝或自动降级。

valuation_params:
  groups:
    - name: 收益法
      fields: [discount_rate, forecast_years, terminal_growth, terminal_method]
    - name: 资本化率法
      fields: [cap_rate, stabilized_noi]
  rule: "收益法为主；资本化率法非强制第二方法，使用时须独立说明口径；cap_rate 不得替代 discount_rate"

scenario_set:
  # 情景数字须由披露、独立研究、合同或历史证据校准，不设固定默认数。
  pessimistic: {occupancy_delta: null, rent_growth: null, capex_uplift: null}
  base: {occupancy_delta: null, rent_growth: null, capex_uplift: null}
  optimistic: {occupancy_delta: null, rent_growth: null, capex_uplift: null}

formula_registry:
  - formula_id: F_NOI
    expression: 按底层资产经营口径逐项定义，不作为所有 REIT 通用的统一公式
    unit: 元
    freq: 年
    valid_from: null
    valid_to: null
    caliber_note: "本项目按披露口径定义；不得将 NOI 与 EBITDA、项目公司现金流或基金可供分配金额互换。仅在组成项与层级一致时使用。"
  - formula_id: F_EBITDA
    expression: 仅在 NOI 定义及折旧摊销处理明确时勾稽，不机械套用
    unit: 元
    freq: 年
    valid_from: null
    valid_to: null
    caliber_note: "必须按报表/评估报告的具体组成项复核；折旧摊销回加不自动解决税费、管理费和层级差异。"
  - formula_id: F_DIST
    expression: 以招募说明书披露的可供分配金额测算表为准，逐项复原调整项
    unit: 元
    freq: 年
    valid_from: null
    valid_to: null
    caliber_note: "以招募说明书可供分配测算表的调整项为准，逐项对齐"
  - formula_id: F_YIELD
    expression: 发行规模口径分派率 = 可供分配金额 ÷ 实际募集规模；其他分母必须另行命名
    unit: "%"
    freq: 年
    valid_from: null
    valid_to: null
    caliber_note: '分母为募集规模（含扩募）；用评估值作分母时须改名为「评估值分派率」'
  - formula_id: F_DCF
    expression: 按评估方法、现金流口径、收益期限和终值方法计算；DCF 仅适用于相应假设成立时
    unit: 元
    freq: 年
    valid_from: null
    valid_to: null
    caliber_note: "先匹配估值对象与现金流层级，再选折现率、收益期限和终值；物业层现金流不得直接与基金层可供分配现金流比较。"

source_registry:
  - source_id: SRC_SSE_REIT
    provider: 上海证券交易所
    endpoint: https://www.sse.com.cn/disclosure/fund/announcement/
    access_method: HTTP
    auth_required: false
    fallback_source_id: SRC_EM_ANN
    note: "公开查询接口需内部 channelId，当前案例原始 PDF 实际通过东方财富基金公告接口获取；不得声称交易所直连已验证。"
  - source_id: SRC_EM_ANN
    provider: 东方财富基金公告
    endpoint: https://api.fund.eastmoney.com/f10/JJGG
    access_method: HTTP
    auth_required: false
    fallback_source_id: null
  - source_id: SRC_CSINDEX
    provider: 中证指数公司
    endpoint: https://www.csindex.com.cn/
    access_method: HTTP
    auth_required: false
    fallback_source_id: null
    note: "REITs 指数与分派率数据非全部公开，部分需终端"

quality_states: [CONFIRMED, PARTIALLY_SUPPORTED, INDETERMINATE, NOT_COMPARABLE, SOURCE_UNAVAILABLE, DATA_QUALITY_WARNING, UNDEFINED_THRESHOLD]
