type: flow
name: mortgage-npl-abs-protection
version: 1.0.0
domain: 房贷不良资产证券化
source_report: 用户指定附件中的发行及存续期文档；内部方法不构成外部事实
script_permission: true
output_dir: outputs/{case_id}/protection

## inputs

| name | 默认/说明 |
|---|---|
| case_id | 信托级唯一ID，与定期跟踪共享 |
| archive_path | 本案例为E:/OneDrive/申万/22建鑫7优先（2289267.IB）.rar |
| requested_code | 保留用户所述2289267.IB，不能视为已核验优先代码 |
| verified_code | 必须从正文取得，与请求冲突则披露 |
| as_of | 初始基准/最新可核对期末；分别建模 |
| doc_root | 仅附件解压副本 |
| analysis_only | true；用户只要skills时连案例分析也不执行 |
| monitoring_panel | 可选，npl-abs-periodic-monitor已验证底稿 |

## 九项数据要求

| id | 字段 | 定义/单位/必要依赖 | 缺失影响 |
|---|---|---|---|
| A1 | B0,I0,B0/I0 | 初始起算日未偿本金/总实际发行；元、倍 | 无法判断本金覆盖倍数 |
| A2 | S0,J0,S0/I0,J0/I0,S0/J0 | 优先与劣后绝对额、比例和比值 | 无法量化分层厚度 |
| A3 | OC_amount,OC_issue,OC_pool | B0-I0、(B0-I0)/I0、(B0-I0)/B0，结合瀑布 | 只能描述条款不能量化保护 |
| A4 | loss_principal,loss_share | 损失类本金及占B0；保留披露与反推 | 不可评价该分类集中程度 |
| A5 | original_ltv,latest_weighted_ltv | 初始抵押率/最新抵押率，逐项给时点分母权重；% | 不可量化抵押覆盖变化 |
| A6 | advance_registration_amount/share/count | 预告登记本金/笔数及各自占比 | 权利实现风险无法量化 |
| A7 | city_rank,amount,share,CR10 | 地级/城市定义按原文；前十+其他 | 仅省级不得做城市排名 |
| A8 | age_type,bucket,amount,share,weighted_age | 存续/逾期/违约账龄分开；月/天 | 不可推断处置成熟度 |
| A9 | cbr_recovery_rate/amount | 中债资信、基准日/情景/分母/毛净/折现口径 | 不可做评级预测对照 |

## 标准表与主外键

source_id使用文件SHA256；observation_id使用source_id+PDF页序+表名+行列+指标生成稳定ID。所有金额标准化为元，比例在面板用0—1，报告展示乘100并标%；原始值和单位始终保留。禁止对未知口径转换。

| 文件 | 主键；必备字段 |
|---|---|
| source_index.csv | source_id；file,type,date,pages,sha256,archive_member,local_path,status,url=NA(offline) |
| identity.json | case_id,requested_code,verified_code,tranche,trust_name,evidence_refs,conflicts,status |
| panel.csv | observation_id；case_id,source_id,pdf_page,printed_page,table,metric,as_of,period_start,period_end,value,unit,raw_value,raw_unit,numerator,denominator,basis,state,formula_id,input_ids |
| terms.csv | term_id；term,value,unit,effective_date,source_id,pdf_page,quote,state |
| issuance_metrics.csv | metric_id；A1—A9,metric,value,unit,basis,observation_ids,formula_id,state,limitation |
| rights_risk.csv | group_id；registration_type,amount,count,amount_share,count_share,denominator,observation_ids,state |
| city_top10.csv | as_of+city；rank,amount,share,denominator,source_ids,observation_ids,state |
| age_profile.csv | as_of+age_type+bucket；amount,count,share,weighted_mean,weight,basis,observation_ids,state |
| forecast_rating.csv | forecast_id；agency,version,date,scenario,metric,value,unit,denominator,gross_net,discount_basis,horizon,observation_ids,state |
| protection_matrix.csv | protection_id；mechanism,beneficiary,amount,ratio,waterfall_order,trigger,failure_path,observation_ids,finding_ids |
| reconciliation.csv | check_id；lhs,rhs,difference,tolerance,tolerance_basis,input_ids,explanation,state |
| model_inputs.csv | input_id；name,value,unit,period,origin_type,observation_ids,assumption_id,state |
| assumptions.csv | assumption_id；parameter,value,unit,basis,source_refs,sensitivity,status |
| model_cashflows.csv | scenario_id+payment_date+tranche；opening_cash,gross_recovery,fees,reserve_change,interest_due,interest_paid,interest_shortfall,principal_paid,principal_end,ending_cash,bridge_difference,input_ids |
| breakeven_scenarios.csv | scenario_id；model_scope,as_of,denominator,meaning_of_r,static_floor,r_lower_infeasible,r_upper_feasible,tolerance,interest_timely,principal_final,limiting_date,forecast_comparable,status,input_ids |
| model_validation.csv | check_id+scenario_id；check,observed,expected,difference,tolerance,basis,status |
| findings.csv | finding_id；claim,kind,evidence_value,observation_ids,formula_ids,scenario_ids,source_anchor,assumptions,counterevidence,scope,confidence_tier,primary_section,depends_on,invalidation_condition,state |
| claims_verdict.csv | claim_id；statement,origin,aggregation,threshold,observed,verdict,evidence_ref,limitation |
| gaps.csv | gap_id；metric,missing_item,reason,affected_conclusion,action,state |
| report_handoff.json | case_id,source_boundary,identity,as_of,tables,findings,models,assumptions,gaps,section_mapping,ready_scope,blocked_scope |

input_ids/observation_ids/source_refs以JSON数组保存；每个外键必须存在，计算值递归可追溯至原文或明确研究假设。缺失数值置空并强制填state和缺口原因；展示时转成“未披露/未核验/不可比/不适用”，空白不等于0。

## 状态与公式登记

state取verified（原页核实事实）、derived（可复算计算）、assumed（情景假设）、unavailable（材料未提供）、unverified（无法读取或尚未核实）、not_comparable、not_applicable、conflict。零只有原文/合法计算支持才填0。findings.kind必须区分fact/calculation/judgment。

formula_registry至少登记：发行加总、A1—A6分母、CR10、加权LTV、静态本金下限、固定成本静态近似、逐期利息、现金/本金桥、动态共同r及剩余共同r。每项带formula_id/expression/input_ids/适用边界/单位/舍入/tolerance_basis。舍入公差来自原始披露精度或数值算法误差，不能用于掩盖实质差额。

## 验收门槛

不得声称“已执行校验脚本”而未提供实际脚本。可使用人工逐项核验并留验证表，动态模型必须提交可执行脚本或有公式的模型及输入引用。验证结构不代表正文取数已核实。只创建skills时不生成实例面板、不填真实测算值、不编造样例案例数值。
