type: flow

name: reits-peer-benchmarking

version: 1.0.0

description: "公募REITs横向基准：构造可解释的可比样本，用三个收益率口径与四个资产质量维度定位，用最小二乘残差判断定价偏离，用四问框架拆商业模式优劣，输出相对位置判断与本项目的可改进项。"

domain: 公募REITs横向比较

source_report: "内部方法论（无单一来源研报）。口径依据《公开募集基础设施证券投资基金指引》与沪深交易所定期报告编制要求；残差方法为常规 OLS，不涉及推断统计"

script_permission: true

output_dir: ./output

inputs:
  - name: project_funds
    required: true
    description: 本项目标的，代码列表，如 ["508056","180302"]。报告的所有"位置"判断围绕这几只展开
  - name: peer_universe
    required: true
    description: 对标范围。可给资产类型标签（如"仓储物流"）或代码清单。给标签时本 skill 必须自行全量枚举候选池并回报
  - name: as_of
    required: true
    description: 比较时点，格式 YYYY-MM-DD（时点指标基准日）＋ YYYY 年度（期间指标）。两者必须配对使用
  - name: asset_type
    required: true
    description: 资产类型边界，如 仓储物流 / 产业园 / 消费基础设施。决定哪些指标有意义（出租率只对租赁型资产有意义）
  - name: min_area
    default: 100000
    description: 规模下限（可租面积 ㎡）。低于此值的不纳入，避免单位化指标失真；连续型资产改用产能或里程门槛
  - name: comparability_thresholds
    default: {area_ratio: 3.0, rank_range: 2}
    description: area_ratio = 最大/最小面积倍数上限，超过即强制单位化；rank_range = 排名极差告警阈值
  - name: doc_root
    default: ./source_documents
    description: 披露文件根目录。本 skill 优先从一手年报取数，取不到才降级到仓库内既有报告

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
        name: 市值（反推）
        unit: 元
        comparability: 时点可比
        criticality: critical
        binding: 派生：可供分配 ÷ 分派率
        note: 反推而非取行情，保证与分派率同时点。代价是不可跨期使用
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
    stable: 1
    unstable: 3
    note: ≥3 位时禁止写"排第几"而不带口径

output_contract:
  report_md: "report_peer_benchmarking_<year>.md"
  report_html: "report_peer_benchmarking_<year>.html"
  figures_dir: "figures/"
  panel: "panel.csv"
  matrix_yield: "matrix_yield.csv"
  matrix_quality: "matrix_quality.csv"
  sample_funnel: "sample_funnel.csv"
  min_cjk: 15000
  figures: 5
  figure_rule: "坐标由脚本计算；HTML 版内联，Markdown 版走相对路径"
  forbidden:
    - "给商业模式打总分或评级"
    - "用 n<10 的样本做分位表述或显著性检验"
    - "只取一套集中度披露"
    - "用'排序不一致'代替相关性检验"
    - "正文出现 FLOW 编号或状态码"
    - "图作为单独附件交付"
