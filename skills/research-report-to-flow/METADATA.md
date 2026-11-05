type: flow

name: research-report-to-flow

version: 1.0.0

description: "把卖方研究报告转化为可执行 FLOW 的方法论流程：抽取核心结论与论证链，标定证据权重与阈值出处，登记公式版本与生效期，映射为 Step/动作，并通过数据可得性与反向复现测试验收。"

domain: 方法论

source_report: "多源（11 份卖方研报 + 11 套既有 Skill 的横向审计结论）"

script_permission: true

output_dir: ./output

inputs:
  - name: source_report_path
    description: 待转化研报的本地路径（PDF 或已抽取的 .txt）。运行时必须由用户确认，不接受"目录下随便挑一份"
  - name: target_domain
    description: 目标研究领域，用于确定阈值与数据源的行业口径（如 煤炭行业 / 仓储物流REITs / 商业地产REITs）
  - name: output_skill_name
    description: 产出 FLOW 的 skill 名称，英文 kebab-case，须与目标目录名一致
  - name: knowledge_cutoff
    description: 研报的写作时点（YYYY-MM）。用于判定公式、阈值、可比公司在运行期的适用性；不填则取研报首页日期
  - name: run_mode
    description: "dry_run 或 full。dry_run 只做数据可得性探测与结构校验，不产出数值裁决"

data_requirements:
  - name: 研报正文全文
    freq: 一次性
    unit: 文本
    role: "被解释对象：结论、论证链、证据的唯一来源"
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "无法提取论证链，整个转化不可执行"
    source_id: local_file://source_report_path

  - name: 研报内表格与图表数据
    freq: 一次性
    unit: 数值
    role: "解释变量：量化论据的原始取值与口径"
    execution_required: true
    thesis_required: true
    importance: critical
    evidence_role: core
    missing_data_impact: "只能得到定性论证链，阈值与公式无法标定，产出 FLOW 不可数值化"
    source_id: local_file://source_report_path#tables

  - name: 研报引用的外部数据源名称与口径说明
    freq: 一次性
    unit: 文本
    role: "解释变量：source_registry 的初始候选"
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: supporting
    missing_data_impact: "数据源需从零探测，转化周期变长但不影响结论结构"
    source_id: local_file://source_report_path#references

  - name: 数据源可用性探测结果
    freq: 每次运行
    unit: 布尔
    role: "约束条件：决定 FLOW 是 dry_run 还是 full"
    execution_required: true
    thesis_required: false
    importance: critical
    evidence_role: core
    missing_data_impact: "无法判定可执行性，只能产出未验证的 FLOW 草稿"
    source_id: runtime://probe

  - name: 历史制度与口径变更记录
    freq: 一次性
    unit: 文本
    role: "约束条件：formula_registry 的分段依据"
    execution_required: false
    thesis_required: true
    importance: high
    evidence_role: core
    missing_data_impact: "公式无法分段，跨期套用风险，相关动作须标 NOT_COMPARABLE"
    source_id: runtime://policy_lookup

claim_schema:
  - claim_id
  - statement
  - type
  - premise_ids
  - evidence_ids
  - judgment_rule
  - aggregation
  - threshold_ref
  - formula_ref
  - verdict_states
  - source_anchor

evidence_policy:
  dimensions:
    - execution_required
    - thesis_required
    - importance
    - evidence_role
    - missing_data_impact
  importance_levels: [critical, high, medium, low]
  evidence_roles: [core, supporting, background]
  rules:
    - "thesis_required=true 时 importance 必须为 critical 或 high"
    - "evidence_role=core 且 thesis_required=false 时，必须在 research_graph.yaml 写明降级理由"
    - "execution_required 与 thesis_required 至少一个为 true，否则该指标不应进入 data_requirements"

threshold_policy:
  required_fields: [direction, bands, window, calculation_method, applicable_period, threshold_source]
  direction_levels: [higher_is_better, lower_is_better, context_dependent]
  threshold_sources: [研报明示, 历史分位, 行业惯例, 监管规则]
  fallback: UNDEFINED_THRESHOLD

formula_registry:
  required_fields: [formula_id, formula_version, expression, variables, unit, freq, valid_from, valid_to, source, caliber_note]
  versioned: true
  rule: "valid_to 为空表示仍有效；跨制度必须拆条，禁止单条覆盖多制度"
  versioning_rule: |
    formula_id 恒定，formula_version 随口径变化递增（v1, v2, …）。
    同一 formula_id 的不同 formula_version 必须有互不重叠的 [valid_from, valid_to) 区间。
    引用公式的 claim 必须同时记录 formula_id 与计算时实际使用的 formula_version，
    否则历史结论无法复算——这是本方法论"可复现"要求的落地检查点。
    反例（必须避免）：把 2024 年前"可供分配 = 净利润 + 折旧摊销"与 2024 年后
    "可供分配 = EBITDA − 资本性支出 − 利息及所得税"写成同一条无版本公式，
    跨年比较会得出错误的增长率。

source_registry:
  required_fields: [source_id, provider, endpoint, access_method, auth_required, probe_status, probe_time, fallback_source_id]
  status_values: [VERIFIED, DEGRADED, SOURCE_UNAVAILABLE]

quality_states: [CONFIRMED, PARTIALLY_SUPPORTED, INDETERMINATE, NOT_COMPARABLE, SOURCE_UNAVAILABLE, DATA_QUALITY_WARNING, UNDEFINED_THRESHOLD]

acceptance_test:
  - name: structural_check
    rule: "8 个产出文件齐备，METADATA 字段可解析，FLOW 每个动作有 [输出] 与 [输出示例]"
  - name: coverage_check
    rule: "研报中 thesis_required=true 的证据 100% 在 FLOW 中有对应动作；覆盖率 <100% 判 PARTIAL"
  - name: reverse_reproduction
    rule: "仅给数据跑一遍，核心裁决方向与研报结论一致，且未遗漏决定性论据"
  - name: degradation_path
    rule: "抽掉任一 critical 证据后，流程输出 INDETERMINATE 而非崩溃或编数"
