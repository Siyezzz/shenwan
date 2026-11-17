# METADATA — npl-abs-periodic-monitor

```yaml
type: flow
name: npl-abs-periodic-monitor
version: 1.1.0
description: 不良ABS存续期回收、原始预测偏差、偿付与剩余资产质量监测
domain: 不良贷款资产支持证券投后
source_report: 运行时evidence_scope内授权附件的原始披露；参考技能只提供结构与表达规则
script_permission: false
output_dir: 运行时用户工作目录下独立版本目录，不写入技能安装目录
inputs:
  mode: skill_only | monitor | monitor_and_report
  evidence_scope: 运行时登记的用户授权附件清单、版本与内容哈希；不得套用其他案例
  archive_path: 运行时指定压缩包路径；直接提供目录时可为null
  doc_root: 运行时指定的授权附件根目录
  expected_documents: 项目候选文档清单及预期份数；可为空，仅供完整性核对
  requested_identity: 用户请求的全称、代码和档次原文
  verified_identity: 正文核实后的产品、代码、档次与来源；未核实为null
  start_scope: 成立起点，须由正文核验
  end_scope: 附件内最新可核报告实际覆盖期末，不能以发布日期代替
  focus_scope: 最新可比归集区间及最近精确半年；不可分割时沿用原区间
  report_authorized: false
upstream: 可选复用同证据链底稿；mortgage-npl-abs-protection不是执行前置
downstream: reits-report-writing（独立写作主入口）
```

## document_expectations

候选文档与份数来自运行时 `expected_documents`，不设固定产品、期数或发布日期。无预期清单时仍须枚举全部授权附件并登记覆盖缺口；有清单时将“预期、实际取得、正文已核验”分别记录。发行说明书/发行结果用于身份与原始基准，连续受托报告用于实际期间与偿付，审计/跟踪评级仅按披露范围交叉核验，不自动替代原值。

具体案例配置见 [references/report-handoff.md](references/report-handoff.md) 的“案例验收配置”。这些观察不能成为已核事实、资产数据或其他项目的默认完整性条件。

## data_requirements

| 数据组 | execution_required | thesis_required | 缺失影响 |
|---|---|---|---|
| 文件、页数、身份映射与档次条款 | true | true | 身份未解阻断相应证券层结论；不可读影响相应数据 |
| 每份报告实际期间、累计起点与支付时点 | true | true | 无法精确分期或累计，保留原文但不算偏差 |
| 实际回收分项、金额口径与费用 | true | true | 不能评价回收或净可用现金 |
| 发行说明书原始预测表及口径 | true | true | 仍可陈述实际，不得作发行预测偏差判断 |
| 逐档实付/应付、本金余额与储备 | true | true | 缺应付不能判足额；缺余额不能闭合本金桥 |
| 剩余池质量、处置笔数及回款关联 | false | true | 限定质量/效率判断；未披露不补 |
| 审计及跟踪评级 | false | false | 缺交叉复核，不能以其预测代原始发行基准 |

`execution_required` 表示必须尝试定位并登记结果，不表示缺一项就放弃独立可完成部分。

## artifact_contract

运行监测时可采用 UTF-8 CSV 加 JSON（数组字段），或等价数据库；本次技能编写不创建任何案例底稿。所有表含公共字段 `case_id, run_id, schema_version, state, quality_status, source_ids, notes`；主键不得含可变展示序号。`case_id` 沿用保护技能已核实的信托级唯一ID；没有上游时按正文核实的信托身份建立，身份待核只用临时ID，正式映射留痕，不以请求代码直接确认。`source_ids` 为文件级 source_index.source_id 数组；逐值证据位置保留在panel，派生行通过input_refs递归到原文，陈述页码保留在claims_verdict。纯运行参数及缺口等无来源时使用空数组并说明原因，不能填伪造页码。

ID规则：`source_id=sha256(文件字节)`，使用无前缀的完整小写十六进制SHA256，与保护技能共享。披露值的observation_id以source_id、PDF物理页、表名、行列、指标及必要口径生成稳定哈希；同一来源同一定位复用已有ID，不同期间/口径不得碰撞。派生观测以公式、输入ID及期间/口径生成稳定ID；其他行以表名加自然键/口径及来源指纹的完整哈希生成。重跑稳定，内容修订产生新ID，保留 `supersedes_id`；检测哈希碰撞与重复键。同一文件重复副本按内容哈希去重，不把副本当额外观测。

### source_index：文件级原始来源目录

主键 `source_id`，一行一份内容唯一的文件；来源主键不能混入页级证据ID。字段固定：

`source_id, file, relative_path, archive_member, sha256, type, filename_date, date, report_no, pages, local_path, url, status, text_layer, read_status, verification_level, requested_identity, verified_product, verified_code, verified_tranche, identity_status, identity_evidence, supersedes_id`。

- `file/type/date/sha256/local_path/status/url` 与保护技能同名；date仅存正文核实的披露日，未核为null，url固定 `NA(offline)`。source_id必须等于sha256。
- 必须有完整文件名、相对路径、哈希、页数或不可读原因，`verification_level=FILENAME_ONLY/TEXT_CHECKED/PAGE_VERIFIED`；页数未获为null，不能设0假装已检验。文档级PAGE_VERIFIED不代表所有指标已核，逐值核验仍看panel。
- 身份证据identity_evidence保留物理页、印刷页、小节及摘录；逐值原文、单位与原期间保留在panel；陈述证据保留在claims_verdict。各物理页均须满足 `1≤page_from≤page_to≤pages`，印刷页码仅辅助。文本抽取或OCR后关键数值须逐值 `PAGE_VERIFIED` 才能用于核心数值结论。
- filename_date与正文确认date分开；相对路径及local_path须落在附件解压根目录，禁止目录越界。

### period_map：真实区间与自然半年映射

主键 `period_id`，外键 `source_id→source_index`。字段固定：

`period_id, source_id, report_no, report_date, report_start, report_end, collection_start, collection_end, start_inclusive, end_inclusive, collection_days, cumulative_start, payment_date, balance_asof, calendar_buckets, mapping_status, overlap_period_ids, gap_description, allocation_method, source_ids`。

日期使用ISO，未知为null；报告覆盖、现金归集、支付及余额各自独立。精确子期间披露才允许 `allocation_method=DISCLOSED_SUBPERIOD`；完整无重叠区间可 `EXACT_AGGREGATION`；不可分割为 `NONE`。天数按原文边界约定算，不擅定包含日。

### panel：唯一标准数值与派生观测长表

主键 `observation_id`；自然唯一键 `(entity_id, tranche_id, metric, period_id, semantic, basis_id, version)`；外键 `period_id→period_map`、`source_ids→source_index`。字段固定：

`observation_id, source_id, pdf_page, page_to, printed_page, table, row, column, section, quote, raw_value, raw_unit, raw_period_text, verification_level, entity_id, tranche_id, metric, period_id, period_start, period_end, semantic, as_of, cumulative_start, basis_id, asset_scope, cash_basis, numerator, denominator, value, unit, value_kind, formula_id, expression, input_ids, input_refs, rounding_rule, version, supersedes_id`。

披露观测source_id外键指向文件；pdf_page为起始物理页，与page_to组成区间，原文定位、摘录及原值必填或登记缺口。derived观测source_id可为null，但source_ids必须汇总原始文件，input_ids与input_refs中引用的观测ID一致；非panel输入在input_refs明确表/行/列。与保护技能共享case_id/source_id/pdf_page/printed_page/table/metric/as_of/period_start/period_end/raw_value/raw_unit/numerator/denominator/state/formula_id/input_ids；basis为basis_id的可读定义，导出时随行提供，不以字段更名改变口径。

`semantic=period_flow/cumulative_flow/stock/count/ratio`；`value_kind=disclosed/derived/assumed`；金额元，比例以0—1约定存储（0.25表示25%，不是强行截断越界值），比率及覆盖倍数按数学值存储，比例差也存小数差；展示比例及比例差时分别乘100并标%及百分点。计数保留户/笔，日均元/日。数值列为数或null，状态单列；零只用于原文真实零或已复算零。`basis_id` 锁定本金/本息、毛净、现金/债权、资产范围、账户边界、档次和分母，不能仅用中文同名认定相同口径。derived行必须有formula_id、可执行含义明确的expression、具体输入表/行/列引用及来源链。assumed不得冒充历史事实。

后续比较、桥表及判断只读取标准panel及锁定预测表；发现错数回取证步骤修订并整体重算，不在正文或后续表里手改。

### forecast_baseline：预测与契约版本

主键 `baseline_id`；外键 period_id、source_ids。字段固定：

`baseline_id, baseline_type, scenario, issue_version, valuation_date, entity_id, tranche_id, metric, basis_id, period_id, expected_period, expected_cumulative, unit, cumulative_start, frequency, contractual_rule, threshold, trigger_conditions, assumptions_text, comparable_scope, supersedes_id`。

`baseline_type=ORIGINAL_ISSUANCE/REVISED_FORECAST/RATING_SCENARIO/CONTRACT`。修订预测只替代其自身旧版本，不覆盖ORIGINAL_ISSUANCE；契约无预测值时为null。保留预测假设与费用口径，只有终值不得制造中间分期。一个情景一套序列，不跨情景拼值。

### period_comparison：分期与累计同表

主键 `comparison_id`；外键 `period_id, baseline_id, actual_period_observation_id, actual_cumulative_observation_id`。字段固定：

`comparison_id, entity_id, tranche_id, metric, basis_id, period_id, baseline_id, actual_start, actual_end, expected_start, expected_end, cumulative_start, actual_period_observation_id, actual_cumulative_observation_id, period_actual, period_expected, period_diff, period_diff_ratio, cumulative_actual, cumulative_expected, cumulative_diff, cumulative_diff_ratio, period_status, cumulative_status, unit, formula_ids, input_refs`。

分期和累计分别校验可比性，不能一个可比就默认另一个可比；不同基准/情景分别成行。不可比仍保留原值和具体原因，派生偏差为null。

### cash_reconciliation：现金账户桥

主键 `cash_bridge_id`；外键 `period_id`；一行一账户边界/区间。字段固定：

`cash_bridge_id, account_scope, period_id, opening_cash, gross_collections, external_other_inflows, transfer_in, fees_paid, taxes_paid, security_interest_paid, security_principal_paid, subordinated_paid, external_other_outflows, transfer_out, calculated_closing_cash, reported_closing_cash, residual, reserve_open, reserve_close, payable_open, payable_close, untransferred_open, untransferred_close, component_refs, formula_id, reason, reason_status`。

分项值只能由component_refs指向panel。储备已包含账户现金时只作受限金额备忘，不再扣一次；应付是负债而非已流出现金，未划转是账户时点衔接，不擅当收入/费用。尚无完整桥组件为null且列缺口，不以0补齐。`reason_status=EXPLAINED/PARTLY_EXPLAINED/UNEXPLAINED`，不能用无来源其他项消残差。

### security_bridge：逐档本金、利息与覆盖

主键 `security_bridge_id`；自然键 `(verified_product,tranche_id,payment_date,version)`；外键 period_id。字段固定：

`security_bridge_id, verified_product, verified_code, tranche_id, period_id, payment_date, opening_principal, principal_paid, contractual_noncash_reduction, other_documented_principal_adjustment, adjustment_sign, calculated_closing_principal, reported_closing_principal, principal_residual, interest_due, interest_paid, interest_arrears_open, interest_arrears_close, principal_due, available_cash_ex_reserve, permitted_reserve_release, due_debt_service, coverage_ex_reserve, coverage_with_reserve, reserve_dependency, component_refs, formula_ids, reason_status`。

不能混档；契约非现金调整必须明确原文依据和符号，无依据不能设为已发生。应付、本金计划偿还与实际偿还依条款区分；覆盖定义参见F09。

### claims_verdict：原文陈述与本期裁决

主键 `claim_id`；同一陈述ID跨运行稳定；外键 `origin_source_id, baseline_id（可null）`。字段固定：

`claim_id, claim_type, statement, quote, origin_source_id, pdf_page, page_to, printed_page, table, section, verification_level, metric, basis_id, applicable_period_ids, rule, threshold, trigger_conditions, baseline_id, observed_refs, observed_expression, verdict, reason, supersedes_id`。

`claim_type=original_forecast/revised_forecast/rating_scenario/contract/manager_statement`。所有契约、原始预测及可核量化陈述逐项登记，不能为了叙事截掉不利条目。变更陈述新增ID保留旧项；`SUPERSEDED`只用于本身已修订的陈述，不用于删除原始预测基准。

### findings：事实、计算与判断分离

主键 `finding_id`；字段固定：

`finding_id, kind, subtype, claim, evidence_state, observation_refs, comparison_refs, bridge_refs, claim_refs, source_ids, calculation, assumptions_ids, counterevidence, scope, confidence_tier, depends_on, limitation, invalidation_condition, primary_question, permitted_wording`。

`kind=fact/calculation/judgment`；`subtype=inference`仅作为judgment的可选子类型，推断不得成为第四主层。事实与计算可并列支撑判断但不混成一条；`state`按共享接口使用`verified/derived/assumed/unavailable/unverified/not_comparable/not_applicable/conflict`，导出时与`quality_status`并列保留；`confidence_tier=verified_fact/reproducible_calculation/qualified_judgment/unverified_inference`。依赖未满足限定或阻断下游，用词不得升级。没有直接附件依据的原因只作`kind=judgment, subtype=inference`，不进入确定因果结论。

### assumptions：参数与内部规则

主键 `assumption_id`；字段固定：

`assumption_id, name, value, unit, basis, source_ids, assumption_type, affected_refs, sensitivity, status, approved_scope`。

`assumption_type=disclosed_assumption/internal_observation_rule/analyst_assumption`；阈值需来源，无来源标 `UNDEFINED_THRESHOLD`；内部阈值明确为研究假设，不能冒充契约、行业或监管标准。

### gaps：缺口及影响

主键 `gap_id`；字段固定：

`gap_id, gap_type, source_id, period_id, metric, expected_evidence, observed_problem, affected_refs, affected_conclusions, severity, remediation, status`。

缺口区分未披露、未取得、工具不可用、OCR待核、身份、期间、口径、冲突与残差。影响范围写到具体结论，不用一个总体免责声明替代。

### report_handoff：授权与逐条可写范围

主键 `handoff_id`；字段固定：

`handoff_id, report_type, writer_skill, report_title, output_dir, report_output_path, evidence_scope, requested_identity, verified_identity, identity_status, archive_hash, data_cutoff_date, covered_collection_intervals, latest_balance_asof, original_baseline_ids, artifact_paths, artifact_hashes, finding_ids, allowed_table_row_refs, blocking_gap_ids, limitations, protection_skill_inputs, writer_mapping, quality_check_results, report_authorized, next_action`。

report_type固定为npl_monitor，writer_skill为reits-report-writing，report_title使用已核产品身份，output_dir使用含npl_monitor与run_id的独立目录，report_output_path为目录内报告路径，与npl_issuance报告隔离；evidence_scope传递本次已锁定授权清单；规则见references/report-handoff.md。archive_hash仅用于有压缩包的运行，无压缩包时为null；完整evidence_scope及各文件哈希随运行参数、source_index和artifact_paths交付，不因该字段强制打包。protection_skill_inputs是可选复用记录，未使用上游时为空并注明NOT_APPLICABLE，不作为报告前置条件。quality_check_results记录check_id、result、method、evidence/失败原因，`result=PASS/FAIL/BLOCKED/NOT_APPLICABLE`。必须区分实际完成的检查与仅定义的规则。写作映射详见references/report-handoff.md。

## metric_naming

| 标准指标 | 必须区分的口径 |
|---|---|
| recovery_principal / recovery_interest / recovery_other / recovery_total | 本金、利息、其他、本息合计；gross/net；现金到账与债权核销 |
| disposal_cash / disposed_claim_principal / disposal_count / writeoff_principal | 处置回款元、已处置债权本金元、处置笔数、减记本金元，不互代 |
| fee_paid / tax_paid / transfer_cash / cash_balance / reserve_cash / payable_cash | 费用税费、内部划转、现金、受限储备、待付不同层级 |
| security_principal_paid / security_interest_paid / security_principal_balance | 逐档支付与余额，payment_date及asof明确 |
| security_interest_due / security_principal_due / interest_arrears | 应付来自条款和披露，不从实付倒推 |
| remaining_claim_principal / remaining_claim_interest / borrower_count / loan_count | 剩余本金、本息、户数/笔数分别保留 |
| collateral_mix / region_mix / overdue_mix / concentration / resolution_stage | 按披露定义、分母、权重及时点，不合成无依据总分 |

实际新增指标先登记标准名、单位、语义及basis_id，不以同名跨口径覆盖。

## formula_registry

公式中的所有变量必须指向底稿具体ID/列；若任一必要输入状态不合格则结果为null并继承缺口，不能跳过未知项求和。用原精度计算，输出才按登记规则舍入。

| ID | 定义 | 前提与异常处理 |
|---|---|---|
| F01 | 当期流量 `X_(a,b)=C_(s,b)-C_(s,a)`，边界按原文包含约定实现；首期仅在确知起点累计为零或直接披露当期时取值 | 同累计起点s、指标、资产范围、档次、毛净、单位及版本；不对stock差分当现金 |
| F02 | 累计实际 `A_(s,t)=Σ A_p`，累计预计 `E_(s,t)=Σ E_p` | p必须无重叠、无缺口、覆盖相同s至t；原披露累计优先作为独立对照，差异留痕 |
| F03 | 分期差额 `D_p=A_p-E_p`；累计差额 `D_c=A_(s,t)-E_(s,t)` | 两者分别同范围可比；不求ΣD_c |
| F04 | 分期偏差率 `D_p/E_p`；累计偏差率 `D_c/E_(s,t)`，均存小数比率，展示时乘100并标% | 预计>0才用于常规回收达成偏差；预计=0标ZERO_DENOMINATOR保留差额，预计<0标不适用并复核定义 |
| F05 | 累计缺口 `G_t=max(-D_c,t,0)`；缺口变化 `G_t-G_(t-1)` | 同一原始基准和累计起点；<0为追回，>0为扩大，仍需说明当期与累计方向。连续负偏差计数只在连续可比期间递增，断档重置为未知 |
| F06 | `closing_calc=opening_cash+gross_collections+external_other_inflows+transfer_in-fees_paid-taxes_paid-security_interest_paid-security_principal_paid-subordinated_paid-external_other_outflows-transfer_out`；`residual=reported_close-closing_calc` | 账户级现金桥；gross_collections若已净费用不得再扣；合并边界内部划转抵销，其他项须明确证据 |
| F07 | `closing_principal_calc=opening_principal-principal_paid-contractual_noncash_reduction+signed_documented_adjustment`；`residual=reported_close-closing_calc` | 同一已核档次、同一支付窗口；非现金减记与实付分开，调整方向依原文 |
| F08 | 回收日均 `A_p/days_p`；`mean=Σx/n`；`sd=sqrt(Σ(x-mean)^2/(n-1))`；`CV=sd/mean` | 日数边界核对；CV用相同长度/定义且n≥3的样本、mean>0。n不足标INSUFFICIENT_SAMPLE；mean=0标ZERO_MEAN，负均值或异质区间标NOT_COMPARABLE，不输出无穷或默认稳定 |
| F09 | `due_service=interest_due+principal_due`；`coverage_ex_reserve=available_cash_ex_reserve/due_service`；`coverage_with_reserve=(available_cash_ex_reserve+permitted_reserve_release)/due_service` | 同一支付窗口和受偿顺序，cash为扣更高级税费费用后可用于该层的现金；储备不能重复计入，释放须契约允许。分母=0不适用、缺失不可判；偿债覆盖与仅利息覆盖分名列示 |
| F10 | `recovered_share=matched_disposal_cash/matched_disposed_claim_principal`；`large_event_share=disclosed_event_cash/same_period_recovery` | 必须逐笔或相同处置集合关联，回款与债权分母口径清楚，分母>0；披露不足不算，不以笔数推金额 |

现金桥与本金桥的容差只允许按各原始披露精度推导舍入上界，登记依据；无依据不设置任意“差1%以内就闭合”规则。残差即使在舍入范围内仍保留原值与原因。

## verdict_rules

| 裁决 | 条件 |
|---|---|
| CONFIRMED | 明确可核陈述在截至期已到的全部适用观测和触发前提上满足规则，必要证据完整；不以覆盖一半代替全覆盖 |
| REFUTED | 同口径已核证据明确反驳量化/事实陈述；需具体观测ID与不满足条件 |
| ABOVE_FORECAST / AT_FORECAST / BELOW_FORECAST | 对指定预测、情景和精确期间的差额正/零/负；零以原精度及已登记舍入界说明，不推导法律违约 |
| PARTIALLY_SUPPORTED | 可独立证实陈述中的限定部分，明确未证部分；不能用来掩盖明确违反的条款 |
| INDETERMINATE | 尚未到期、缺失触发条件、应付数、证据或仅无阈值定性表述 |
| NOT_COMPARABLE | 身份、期间、资产范围、本息、毛净、分母等无法统一，明确双方口径 |
| SUPERSEDED | 陈述自身有明确修订来源；原始发行基准保留，不因后续预测而移除 |

契约与预测分开裁决。定性方向一致至多PARTIALLY_SUPPORTED，不能自动CONFIRMED；实付存在不能单独确认契约足额履行。

## quality_states

`VERIFIED` 原文核验；`DERIVED_VERIFIED` 输入合格且复算；`FILENAME_ONLY` 仅文件名；`NOT_DISCLOSED` 附件正文未披露；`NOT_EXTRACTED` 尚未取得；`NOT_APPLICABLE` 不适用；`SOURCE_UNAVAILABLE` 文件不可得；`TOOL_UNAVAILABLE` 工具不可用；`NO_TEXT_LAYER` 无文字层；`OCR_UNVERIFIED` OCR待原页核；`IDENTITY_UNRESOLVED` 身份冲突；`NOT_COMPARABLE` 不可比；`ZERO_DENOMINATOR` 分母零；`ZERO_MEAN` CV均值零；`INSUFFICIENT_SAMPLE` 样本不足；`DATA_CONFLICT` 披露冲突；`RECONCILIATION_GAP` 未解释桥差；`UNDEFINED_THRESHOLD` 无阈值来源。

共享state取 `verified/derived/assumed/unavailable/unverified/not_comparable/not_applicable/conflict`；quality_status保留详细原因。映射：VERIFIED→verified、DERIVED_VERIFIED→derived、分析假设→assumed、文件不可得及确认未提供/未披露→unavailable、工具不可用/尚未抽取/无文字层/仅文件名/OCR待核/样本不足/身份未解→unverified、NOT_COMPARABLE→not_comparable、NOT_APPLICABLE及零分母导致的无定义比率→not_applicable、DATA_CONFLICT及未解桥差→conflict。单条观测同时多项异常时优先保留阻断用途的state，所有原因另存quality_status数组；裁决不直接冒充数值状态。判断的state表示证据是否完备，不将judgment误标derived；未证实推断只能unverified。status若作为来源/缺口处理进度字段，须单独定义，不覆盖state。

质量状态与裁决、原因状态分列，不用“0/NA/未披露”混作一个值。工具不可用不能写成文件未披露；关键证据OCR待核不能标VERIFIED。

## quality_checks

以下为执行时必须完成并在handoff留痕的检查定义，未附可执行脚本，不宣称已自动实现。

| 检查ID | 验收规则 |
|---|---|
| QC-SCOPE | 所有证据文件均在运行时evidence_scope内；无外部金融资料；模式与授权一致 |
| QC-ID | PK唯一，ID跨重跑稳定；FK及input_refs全部解析，derived依赖图无环 |
| QC-PAGE | 证据物理页在文件页数内，关键数值原页/单位/脚注已核对 |
| QC-IDENTITY | requested与verified并存；冲突未解时无依赖该档身份的计算或结论 |
| QC-PERIOD | 报告/归集/支付/余额/累计起点分列；报告序列未强套自然半年；重叠审计未重复求和 |
| QC-BASIS | 本金/本息、现金/债权、毛净、计数/金额、应付/实付及单位未串用 |
| QC-FORECAST | ORIGINAL与修订/评级/契约分开；年度终值未虚拆；原始基准不可覆盖 |
| QC-CALC | 每个派生值有公式、输入及状态；同范围分期合计对累计，差额与偏差率复算；累计差额未累加 |
| QC-BRIDGE | 两桥逐项可追；残差保留；跨期划转/待付/储备无双计；逐档本金与利息不混 |
| QC-TREND | 稳定性样本和期间可比；CV异常处理；追回与累计达标分离；无虚造显著阈值 |
| QC-CLAIM | 契约履行证据包括应付与触发；预测偏差不等于违约；事实计算判断和推断分离 |
| QC-HANDOFF | 所有可写结论指向有效finding和底稿行；缺口影响明确；未授权无实际报告 |

非核心检查失败仅阻断受影响链；核心身份、期间或口径失败必须在对应finding与handoff列明，不能用一张总表的PASS掩盖。
