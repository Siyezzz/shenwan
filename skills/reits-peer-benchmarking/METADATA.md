type: flow

name: reits-peer-benchmarking

version: 2.5.0

description: "公募REITs横向基准的取数层：用户只给感兴趣的标的，流程自行枚举同类样本并说明进出理由（含 ABS/类 REITs 的收敛与排除）。默认围绕组内相对位置、关键绝对锚、收益与资产/现金流质量、商业模式差异展开；定价函数残差与额外风险维度按数据充分性和问题需要启用，不强制复杂模型。只交论证底稿 findings.csv 与必要图表，不写成文，正文由 reits-report-writing 按 comparison 骨架完成。篇幅按内容需要，不设字数下限。"

domain: 公募REITs横向比较

source_report: "内部方法论（无单一来源研报）。口径依据《公开募集基础设施证券投资基金指引》与沪深交易所定期报告编制要求；残差方法为常规 OLS，不涉及推断统计"

reference_provenance:
  policy: "外部资料逐项记录发布主体、标题、发布日期/版本、完整 URL、本地副本、获取日期、用途与核验状态；内部文件标注仓库根目录相对路径、生成者与上游依赖。URL 可访问不等于内容已核验；第三方转载不冒充一手发布。"
  fund_discovery: "https://fund.eastmoney.com/js/fundcode_search.js 是东方财富/天天基金的基金检索静态列表（JavaScript 数组），不是交易所 REITs 名录。引入出处：提交 3246547、outputs/case_04_peer_benchmarking/run_log.md 与 build_panel.py；2026-11-12 实际访问确认结构。仅用于候选发现，数量与覆盖须每次重新核验。"
  disclosure_channels: "https://api.fund.eastmoney.com/f10/JJGG 与 https://np-cnotice-fund.eastmoney.com/api/content/ann 是案例四使用的第三方公告检索/附件解析渠道；经验记录见该案例 run_log.md，已有列表实现见 tools/fetch_disclosures.py、tools/build_source_index.py。无稳定公开接口契约保证；本次未重验详情接口，不得宣称永久可用。pdf.dfcfw.com 仅为返回附件的托管域名，具体 URL 须逐文件登记。优先核对管理人/交易所发布的原件。"
  regulations: "《公开募集基础设施证券投资基金指引》及交易所编制要求仅是待逐次定位的文件名称；使用前补发布主体、正式标题、版本/生效日期、原文 URL 与具体条款。未完成定位时不得称某个指标/阈值由其规定。年报章节号仅作查找提示，须核对实际文件。"
  internal_method: "三层参照、四坐标、五轴、OLS 与 metric_bands 是本仓库研究方法/分析参数，不是监管标准或公认健康线。案例数值和经验来源见 outputs/case_04_peer_benchmarking/；旧案例只作方法线索，未经原文复核不可作为新报告事实。"

artifact_contract:
  source_index:
    path: "source_documents/source_index.csv（可复用全仓索引或等价案例索引）"
    purpose: "资料目录，一行一份原始文件/网页快照；回答材料由谁、何时发布、从哪获得和能否回查，不存指标或分析结论。由取数层维护，已有生成器 tools/build_source_index.py。"
    fields: "source_id / publisher / file / type / period / disclose_date / url / local_path / retrieved_at / status；网页可用 snapshot/hash，PDF 另记 pages。旧索引无 source_id 时用唯一 local_path 作键并在本次运行固定映射，不强制改写历史索引。"
  panel:
    path: "outputs/{case_dir}/panel.csv"
    purpose: "数值长表，一行一个标的、期间、指标与口径的观测值。由取数层从原件提取或由脚本派生，不是资料下载列表。"
    fields: "observation_id / 标的 / 期间 / 指标 / 值 / 单位 / 口径 / source_id / 锚点 / 证据等级 / 备注；派生行另记 formula / input_observation_ids / script_ref，原始行不伪装为派生。source_id 必须解析到来源索引，锚点须定位页码/章节/表行。"
  findings:
    path: "outputs/{case_dir}/findings.csv"
    purpose: "判断底稿，一行一个有证据边界的判断/缺口，记录为什么能说、能说多强和什么条件下失效；不是新的事实来源。取数层产出，写作层消费。"
    links: "evidence_value 引 observation_id 或矩阵行键；source_anchor 指 source_id + 原文锚点；depends_on 引其他 finding_id。primary_section/reuse_sections 在取数移交时可为 none，由写作层按骨架补齐，不反向规定研究章节。"
  lineage: "source_index（资料）→ panel（观测值）→ matrix_*.csv（脚本计算/排序）→ findings（带限定的判断）→ report（含图表的成品）；既有等价底稿可字段映射，缺引用/孤立 ID/未满足依赖必须修复或降级。"

script_permission: true

output_dir: outputs/{case_dir}

inputs:
  # 只有 focus_funds 必填。用户说的话可能只有一句"我关心 508056 和 180302"，
  # 其余四项由流程自行推导并回报，不得因缺省而缩小范围或改用印象中的样本。
  - name: focus_funds
    required: true
    description: 用户感兴趣的标的，1 只或几只，代码或简称皆可（如 "508056,180302" 或 "普洛斯、深国际"）。报告中称"本项目组"。简称须先解析为代码并回显确认
  - name: as_of
    default: 最近一个完整财年
    description: 比较时点。给日期即锁定该财年年报；不给则取焦点标的最近一个完整财年的年度报告。半年报与年报不得拼成"年度"
  - name: peer_scope
    default: auto
    description: "auto = 由流程按焦点标的的资产类型全量枚举同类并自行筛选（默认，用户无须提供样本）；list = 仅用用户给定的名单，此时仍须做 #5 的五项筛查并说明为何未全量枚举"
  - name: asset_type
    default: 由 focus_funds 推导
    description: 资产类型边界。决定哪些指标有意义（出租率只对租赁型资产有意义），也决定候选池的关键词与筛子。推导结果须在报告第二节写明
  - name: focus_role
    default: 本项目组
    description: 焦点标的在报告中的角色标签。仅影响表述，不改变计算口径；多只焦点标的按组合处理时，须补互补性矩阵
  - name: min_area
    default: 100000
    description: 规模下限（可租面积 ㎡）。低于此值不纳入，避免单位化指标失真；连续型资产改用产能或里程门槛
  - name: comparability_thresholds
    default: {area_ratio: 3.0, rank_range: 2}
    description: area_ratio = 最大/最小面积倍数上限，超过即强制单位化；rank_range = 兼容旧脚本的提醒阈值（2 位起提示口径敏感），最终表述按下方 rank_range 三档规则
  - name: doc_root
    default: ./source_documents
    description: 披露文件根目录。优先从一手年报取数，取不到才降级到仓库内既有报告

baseline_contract:
  # 报告的"结论质量"由这八项共同决定，缺任一项即不得出定位结论
  required_outputs:
    - comparison_standard: 组内位次与幅度、关键绝对锚（如国债收益率、适用健康线或评估值）及判定用词的三档定义；定价残差仅在启用时登记其阈值与限制，须在取数前定稿
    - position_table: 四个坐标各自的位次、与中位数的差、换口径后的位次、名次变动幅度；每行须带绝对锚一列（对国债溢价／对健康线／残差率）与"判断依据指向哪一节"。只有名次一列的表不算位置表
    - pricing_function: 可选。仅在样本量、分母口径和数据质量足够且确需解释定价差异时，提供拟合式 C = a×P + b、斜率、残差率及口径声明；否则记录跳过原因，不能把残差当成错价或目标价
    - risk_allocation: 五类风险（出租率／租金／资本开支／关联方／扩募）各自的承担者、凭据、上限；条款存在但未触发的须注明"实际仍由持有人承担"
    - findings_brief: `findings.csv` 一行一条判断，字段含 finding_id / claim / evidence_state / evidence_value / source_anchor / assumptions / counterevidence / scope / coordinate / confidence_tier / primary_section / reuse_sections / depends_on / invalidation_condition；移交前须通过字段与依赖校验
    - comparability_registry: 每个指标登记资产类型适用范围、经济含义、方向条件、单位分母、时点/期间属性、阈值来源与不可比规则；不同经济机制或分母不得合并排名
    - evidence_dependency: 对下游计算建立前置条件；分母、时点或资产边界未核实时，阻断依赖该输入的估值/排名结论，或明确降级为不可判定
    - sample_provenance: 候选池数量、纳入与排除数量、每条排除的三级理由、至少一只标的的边界检验结论
    - scope_statement: 用户提到 ABS／类 REITs／境外 REITs 时的收敛与排除说明（成交结构、披露口径、市值可比性三条理由至少给两条）；只字不提即为擅自更换问题
    - caliber_log: 五处换算方式、市值反推的分子分母来源、每只标的分派率的分母口径、proxy 指标清单
    - distribution_composition: 可供分配按四类来源（当年经营/往年结转/会计调整/第三方补足）的占比
    - conditional_verdict: 模式比较默认覆盖现金流可预测性、分派自给度、增长来源；用户问题涉及治理或周期风险且有可靠披露时，再补充利益一致性或周期弹性；每项给方向、适用条件、代价与验证指标，不得出现评分或评级
    - improvement_chain: 每条可改进项须同时满足"坐标位次落后（带差幅）+ 某一核心商业模式维度落后 + 可迁移性归入可复制或可购买（后者给成本量级）+ 下一期可查字段与阈值"；缺任一条即删除，归入不可复制的改写为结构性差异
    - advantage_test: 每条独特优势须同时满足"组内唯一（两只以上具备即降为较好）+ 可核对 + 消失条件"；缺任一条即删除
    - model_diversity: 样本内模式是否同质；同质时的参照标的清单及其"不入排名"声明
    - invalidation: 每个结论句的限定词，以及下一期可观测的改写条件（指标+阈值+会改写哪一句）
  decision_rule: "判定用词受证据边界约束：只有 L1 位次称'组内排序'；位次加可核实的 L2 绝对锚称'相对位置'；L3 模型结果只称'模型条件下的偏离'，不得因三层齐备就自动称'确认了位置'。来源可靠性、样本覆盖、假设依赖与稳健性不足时继续降级。跳级用词（只有名次就写'处于中游''明显占优'）一律改写。任何排名第一的句子都必须带分子构成、与中位差与名次变动幅度。"
  anchor_rule: "绝对锚必须与样本无关，不随纳入哪几只而变；不得因样本普遍偏低而下调健康线。全部样本一起低于国债 + 风险溢价时，组内第一只能称'组内最高'。"
  length_rule: "篇幅由内容决定，不设字数下限，也不设上限。删减只删重复判断，不删证据、口径与反例；不得为凑长度增写方法论述。"
  non_goals: "不给买入建议、不给目标价、不给商业模式总分、不做显著性检验。四项须在报告第一节显式声明。隐含应有市值只作位置度量，不得写成涨跌空间。"
  handoff_rule: "判断与用词档位在本层定稿。写作层只负责表达：不得新造数字，不得把'组内排序'升格为'有吸引力'，不得把残差写成错价。需新数字时退回本流程重算。"
  layer_rule: "本 skill 不产出章节。九节骨架属 reits-report-writing 的 outline_schema.comparison；在取数层定章节，等于让工序顺序决定论证顺序。"

data_requirements:

  - layer: L0 样本层
    items:
      - id: fund_code
        name: 基金代码
        unit: —
        comparability: 直接可比
        criticality: blocker
        binding: 交易所代码
        note: 六位数字。用于定位公告与年报
      - id: list_date
        name: 成立/上市日
        unit: 日期
        comparability: 直接可比
        criticality: critical
        binding: 年报封面
        note: 决定"2025 是否完整财年"。成立日在下半年的，当年同比不可算
      - id: n_project
        name: 项目数
        unit: 个
        comparability: 直接可比
        criticality: informative
        binding: 年报 §4.1
        note: 项目数 <3 的标的，单项目风险权重高，需在商业模式一节单列
      - id: city_spread
        name: 城市分布
        unit: 城市名
        comparability: 定性
        criticality: informative
        binding: 年报 §4.1.3
        note: 用于区位质量判断，不做数值排名

  - layer: L1 收益率
    items:
      - id: dist
        name: 可供分配金额
        unit: 元
        comparability: 期间可比
        criticality: blocker
        binding: 年报 §3.3.1.1 / §3.3.2.1
        note: 必须是本期实际数，不用预测值。含调整项，需与 CFO 分开看
      - id: cfo
        name: 经营活动现金流净额
        unit: 元
        comparability: 期间可比
        criticality: blocker
        binding: 年报 §3.1 主要财务指标
        note: 现金流量表口径，不含筹资活动。与可供分配的差额即调整项
      - id: yield_disclosed
        name: 披露现金流分派率
        unit: %
        comparability: 口径依赖
        criticality: critical
        binding: 年报 §3.1 或 §3.3
        note: 分母可能是募集规模/评估值/市值，必须查清并登记
      - id: mcap
        name: 市值（须核实分母与基准日）
        unit: 元
        comparability: 时点可比
        criticality: critical
        binding: 同基准日行情 × 总份额；或原文证实为市值分母后核验的反推值
        note: 可供分配 ÷ 分派率首先只是隐含分母，不自动等于市值；分母性质/日期未核实则阻断依赖计算
      - id: rf_10y
        name: 10 年期国债到期收益率
        unit: %
        comparability: 时点可比
        criticality: critical
        binding: 中债收益率曲线日评（取报告期最后交易日）
        note: 绝对锚，用于把 C1 分派率转成溢价。须写明日评日期与来源，不得用年初值或年均值代替
      - id: carry
        name: 结转类调增项
        unit: 元
        comparability: 期间可比
        criticality: informative
        binding: 年报 §3.3.2.1 调整项明细
        note: 期初现金余额、前期预留释放等。用于"分派构成"敏感性别表，不用于改主口径

  - layer: L2 资产质量
    items:
      - id: occupancy
        name: 期末出租率
        unit: %
        comparability: 时点可比
        criticality: blocker
        binding: 年报 §4.1.2
        note: 期末时点，不用期间平均。含承诺出租的需注明
      - id: rent
        name: 期末租金单价
        unit: 元/㎡/月
        comparability: 需换算
        criticality: critical
        binding: 年报 §4.1.2
        note: 天→月 ×365÷12；含税/不含税、含物业费与否必须统一
      - id: rent_yoy
        name: 租金单价同比
        unit: %
        comparability: 需基期
        criticality: critical
        binding: 年报 §4.1.2
        note: 基期不足整年时不可算，标 NA，不插值
      - id: wale
        name: 剩余租期
        unit: 天
        comparability: 需换算
        criticality: critical
        binding: 年报 §4.1.2
        note: 年→天 ×365。方向随租金周期反转，位次计算需给剔除版本
      - id: renew_spread
        name: 续租/新签租金变动
        unit: %
        comparability: 需基期
        criticality: informative
        binding: 年报 §4.1.2 / §4.1.3
        note: 续租单价对到期单价。前瞻性优于租金同比，有则单列，无则记 C 级缺口
      - id: expiry_wall
        name: 分年到期面积
        unit: ㎡ / %
        comparability: 时点可比
        criticality: informative
        binding: 年报 §4.1.2 / 招募说明书
        note: 平均剩余租期会掩盖"次年到期四成"，有则列示，不得用均值代替分布
      - id: impairment
        name: 资产减值损失
        unit: 元
        comparability: 期间可比
        criticality: critical
        binding: 年报 §3.9 / 附注
        note: 减值率 = 减值 ÷ 营业收入。零减值 ≠ 未贬值
      - id: top1
        name: 最大租户占比
        unit: %
        comparability: 口径依赖
        criticality: critical
        binding: 年报 §4.1.4 / §4.4.2
        note: 必须注明面积/租金/现金流口径。一只标的常有多套，全列
      - id: top5
        name: 前五大租户占比
        unit: %
        comparability: 口径依赖
        criticality: critical
        binding: 年报 §4.1.4
        note: 与 top1 同口径才能相减
      - id: related
        name: 关联方/同集团占比
        unit: %
        comparability: 口径依赖
        criticality: critical
        binding: 年报 §4.4.2
        note: 季报常不披露，必须回年报。这是最容易漏的一项
      - id: collection
        name: 收缴率
        unit: %
        comparability: 期间可比
        criticality: informative
        binding: 年报 §4.1.2
        note: 实测六只全在 99.3—100.9%，几乎无区分度，不并入位次

  - layer: L3 定价
    items:
      - id: mcap_psm
        name: 单位面积市值
        unit: 元/㎡
        comparability: 需单位化
        criticality: critical
        binding: 派生：市值 ÷ 可租面积
        note: 面积差 ≥3 倍时，绝对额排名无意义，一律用每㎡
      - id: appraisal
        name: 评估值（或重置成本）
        unit: 元
        comparability: 口径依赖
        criticality: informative
        binding: 年报 §4.2 评估报告摘要
        note: 与反推市值比得 P/NAV，是脱离样本的绝对锚。评估基准日不一致时只做方向判断，不入排名
      - id: rev_psm
        name: 单位面积收入
        unit: 元/㎡/年
        comparability: 需单位化
        criticality: informational
        binding: 派生：营业收入 ÷ 可租面积
        note: 与 mcap_psm 配对做相关性检验

  - layer: L4 商业模式
    items:
      - id: sponsor
        name: 原始权益人
        unit: —
        comparability: 定性
        criticality: critical
        binding: 年报 §2 / 招募说明书
        note: 决定"增长靠什么"与"风险谁承担"
      - id: fee_total
        name: 管理费合计
        unit: 元
        comparability: 期间可比
        criticality: critical
        binding: 年报 §3.4.1
        note: 含基金管理费、ABS 管理费、托管费、运营管理费
      - id: fee_rate
        name: 费用率
        unit: %
        comparability: 需单位化
        criticality: critical
        binding: 派生：管理费合计 ÷ 营业收入
        note: 单看高低无意义，要结合运营强度（项目数、租户数、租期）
      - id: incentive
        name: 浮动/激励管理费执行结果
        unit: 元
        comparability: 期间可比
        criticality: critical
        binding: 年报 §3.4.2
        note: 负值或零值说明未达标。这是"谁为结果负责"的合同化证据
      - id: recap
        name: 扩募状态
        unit: —
        comparability: 定性
        criticality: informative
        binding: 年报 §5 / 公告
        note: 决定增长是否有外生通道
      - id: guarantee
        name: 兜底/补足安排
        unit: 元
        comparability: 期间可比
        criticality: critical
        binding: 年报 §3.3.2.1 / 招募说明书
        note: NOI 补足、管理费豁免等。金额与占可供分配比例都要给

metric_bands:
  provenance: "以下数值均为本仓库方法参数，部分源自案例四经验，未提供外部权威验证，不得称监管要求/行业健康线。每次使用前登记 threshold_id / value / unit / rationale / source_anchor / asset_scope / as_of / sensitivity；无外部依据时标 assumed，仅作情景或敏感性切分，不能支持绝对优劣结论。不适用时弃用，不为迁就结果调参。"
  occupancy:
    high: 95
    mid: 90
    note: 低于 90% 视为存在去化压力，需在正文说明原因，不得只写"基本稳定"
  rent_yoy:
    stable: -3
    pressure: -8
    severe: -15
    note: 仓储物流 2025 年实测区间 -17.45% 至 -0.79%，档位按此校准
  dist_over_cfo:
    conservative: 1.0
    moderate: 1.3
    note: >1.3 需拆解差额来源；<1.0 说明有留存，需问留存用途
  impair_ratio:
    low: 5
    high: 30
    note: 超过 30% 时，EBITDA 必须回加减值，否则盈利能力被系统性低估
  rank_range:
    stable_max: 1
    sensitive: 2
    unstable_min: 3
    note: 这是三个收益率口径下的名次变动幅度：0–1 位可直接描述名次；2 位须提醒名次会随口径改变；≥3 位不单独引用某一个名次，改写为不同口径下位置不稳定
  yield_spread:
    low: 150
    mid: 300
    unit: bp
    note: C1 分派率减同期 10 年期国债收益率。这是与样本无关的绝对锚；低于 150bp 时"组内第一"不得写成"收益率有吸引力"
  residual:
    threshold: 5
    unit: "%"
    note: OLS 残差率绝对值超过此值才作为结论对象。全部落在阈值内时，只能说"定价与结构一致"，不能称"确认了位置"
  pricing_function:
    min_n: 6
    amplification: "1/(1 - b/(a×P))"
    note: 样本少于 6 只不报斜率，只报残差方向。残差率换算成市值偏离会被截距放大，两个口径只能用一个并注明；隐含应有市值不是目标价

depth_policy: "默认先完成可比性、组内位置、关键绝对锚、收益与资产/现金流质量、商业模式三项核心维度；定价残差、费用细拆、治理与周期弹性按问题需要和数据充分性启用。不得为了填满模板强行补维度；未启用的分析登记原因。"

output_contract:
  # 本层交付底稿与图；报告由 reits-report-writing 产出，文件名沿用其约定
  findings: "findings.csv"
  figures_dir: "figures/"
  report_md_owner: reits-report-writing
  report_html_owner: reits-report-writing
  panel: "panel.csv"
  matrix_yield: "matrix_yield.csv"
  matrix_quality: "matrix_quality.csv"
  sample_funnel: "sample_funnel.csv"
  length: "不设字数下限与目标；按 tools/count_report_words.py 的正文口径统计一次写入封面，仅作记录"
  figures: "按启用的分析生成；至少覆盖选样、收益口径变化与质量对比，定价和模式图按需生成"
  figure_rule: "坐标由脚本计算；图片作为内部素材移交写作层，必须嵌入最终报告对应正文，不默认单独呈现。HTML 版内联，Markdown 版走相对图片引用并随报告打包资源；交付前检查引用与渲染有效。"
  figure_manifest: "figure_id / path / finding_ids / section_id / caption / source_anchor / disposition；由写作层完成章节映射和采用状态登记"
  forbidden:
    - "给商业模式打总分或评级"
    - "用 n<10 的样本做分位表述或显著性检验"
    - "只取一套集中度披露"
    - "用'排序不一致'代替相关性检验"
    - "正文出现 FLOW 编号或状态码"
    - "图作为单独附件交付"
    - "为凑字数增写方法论述，或为压篇幅删掉口径、证据与反例"
    - "把 proxy 指标放进排名表，把模式参照标的放进位次表或结论句"
    - "用户提到 ABS/类 REITs 却不在第二节交代边界"
    - "位置表只有名次一列，没有与中位差或绝对锚"
    - "只有组内位次却写'处于中游''明显占优''性价比突出'"
    - "为迁就样本而调低健康线或国债锚"
    - "把'某轴领先但解释不了任何坐标差'写成优势"
    - "把不可复制的项（区位、股东背景、牌照）写成可改进项"
    - "残差率与隐含市值偏离率混用，或把隐含应有市值写成目标价"
    - "在取数层排章节，或在成文层改动判断与用词档位"
