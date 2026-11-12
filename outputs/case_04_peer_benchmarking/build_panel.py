# -*- coding: utf-8 -*-
"""case_04 横向基准（peer benchmarking）面板构建脚本。

与 case_01/02 的单标的投后跟踪不同，本脚本只做一件事：
把 6 只仓储物流 REIT 放进同一张可比表，并计算三个收益率口径与五个资产质量维度。

样本边界
--------
A 股名称含"仓储/物流"的公募 REIT 共 10 只（tools/fetch_disclosures.py 全量枚举，
fund.eastmoney.com/js/fundcode_search.js）。截至 2026-04-30，披露 2025 完整财年年报
且满足资产同质、规模下限的共 6 只。逐条理由见 sample_funnel.csv。

证据分级
--------
A = 一手年报逐页抽取；B = 由 A 派生；C = 未提取；D = 披露缺失/不可得。
每条数值必须能回溯到 anchor。

用法
----
    python build_panel.py            # 输出 5 个 csv 到脚本同级目录
"""
import csv
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 原始值（A 级）
F = {
    "508056": dict(
        name="中金普洛斯仓储物流REIT", short="普洛斯", code="508056",
        listed="2021-06-21", n_proj=9, city="6 城", city_tier="一线+新一线",
        recap="已扩募", sponsor="普洛斯（GLP）",
        area=1163212.0, occ=89.54, rent_pm=33.07, rent_yoy=-7.48, wale=389.71, coll=100.91,
        rev=422500807.91, rev_yoy=-7.36, cfo=231950053.99,
        dist=335181671.99, dist_yoy=-6.49, ebitda=192719420.60,
        impair=71520087.02, other_adj=84070555.06, carry=84070555.06,
        yield_mkt=5.34, fee=72307580.87, top1=6.21, top5=25.26, related=0.0,
        a_fin="2025 年报 p13 §3.1/§3.3.2.1", a_op="2025 年报 p18 §4.1",
        a_imp="2025 年报 §4.3 及附注",
    ),
    "180301": dict(
        name="红土创新盐田港仓储物流REIT", short="盐田港", code="180301",
        listed="2021-06-21", n_proj=2, city="1 城（深圳盐田）", city_tier="一线（保税）",
        recap="已扩募", sponsor="深圳港集团",
        area=318540.79, occ=92.60, rent_pm=round(1.26 * 365 / 12, 2), rent_yoy=-0.79,
        wale=456.0, coll=100.00,
        rev=125303202.80, rev_yoy=-3.95, cfo=88558933.17,
        dist=92586147.23, dist_yoy=-2.16, ebitda=49078538.10,
        impair=45605977.65, other_adj=0.0, carry=0.0,
        yield_mkt=4.15, fee=11327232.65, top1=40.69, top5=74.86, related=74.86,
        a_fin="2025 年报 p9–p11 §3.1/§3.3.2.1", a_op="2025 年报 p15 §4.1.2",
        a_imp="2025 年报 p13 §3.9",
    ),
    "180302": dict(
        name="华夏深国际仓储物流REIT", short="深国际", code="180302",
        listed="2024-06-25", n_proj=2, city="2 城（杭州、贵州）", city_tier="新一线+三线",
        recap="无扩募", sponsor="深圳国际",
        area=354313.77, occ=89.35, rent_pm=27.92, rent_yoy=-17.45,
        wale=round(1.55 * 365, 2), coll=99.63,
        rev=111528606.01, rev_yoy=-17.65, cfo=83656185.80,
        dist=74401200.00, dist_yoy=None, ebitda=76637693.75,
        impair=0.0, other_adj=-2236493.75, carry=0.0,
        yield_mkt=4.36, fee=16133660.04, top1=21.21, top5=68.42, related=55.22,
        a_fin="2025 年报 p10 §3.1/§3.3.2.1", a_op="2025 年报 §4.1；Q4 季报 §4.1.2",
        a_imp="2025 年报（未计提）",
    ),
    "508098": dict(
        name="嘉实京东仓储物流REIT", short="京东仓储", code="508098",
        listed="2023-01-11", n_proj=4, city="3 城", city_tier="新一线+二线",
        recap="无扩募", sponsor="京东物流",
        area=341316.96, occ=100.00, rent_pm=round(0.90 * 365 / 12, 2), rent_yoy=-5.26,
        wale=1192.0, coll=100.00,
        rev=106735027.16, rev_yoy=-1.77, cfo=71340758.63,
        dist=71894866.23, dist_yoy=-8.68, ebitda=70051372.16,
        impair=0.0, other_adj=21341737.98, carry=21341737.98,
        yield_mkt=4.05, fee=14929939.91, top1=54.08, top5=100.00, related=100.00,
        a_fin="2025 年报 p9–p11 §3.1/§3.3.2.1", a_op="2025 年报 p16 §4.1.2",
        a_imp="2025 年报（未计提）",
    ),
    "180303": dict(
        name="华泰紫金宝湾物流仓储REIT", short="宝湾物流", code="180303",
        listed="2024-09-13", n_proj=3, city="3 城（天津、南京、嘉兴）", city_tier="二线",
        recap="无扩募", sponsor="宝湾物流（南山控股）",
        area=309533.65, occ=97.64, rent_pm=27.54, rent_yoy=None,
        wale=567.81, coll=99.28,
        rev=92483304.48, rev_yoy=None, cfo=56672066.25,
        dist=54995965.67, dist_yoy=None, ebitda=29409887.78,
        impair=31976892.34, other_adj=0.0, carry=35998653.43,
        # 固定 2,444,186.00 + 托管 122,209.30 + 运营管理费（减免后不含税）6,942,413.67
        yield_mkt=4.59, fee=9508808.97, top1=18.61, top5=62.27, related=18.61,
        a_fin="2025 年报 p8–p12 §3.1/§3.3.2.1", a_op="2025 年报 p14 §4.1.1",
        a_imp="2025 年报 p16 §3.9（嘉兴项目）",
    ),
    "508078": dict(
        name="中航易商仓储物流REIT", short="中航易商", code="508078",
        listed="2024-12-24", n_proj=1, city="1 城（昆山花桥）", city_tier="新一线（临沪）",
        recap="无扩募", sponsor="ESR 易商",
        area=382417.82, occ=88.16, rent_pm=round(1.20 * 365 / 12, 2), rent_yoy=None,
        wale=458.75, coll=99.75,
        rev=132849777.15, rev_yoy=None, cfo=90599914.81,
        dist=124120457.58, dist_yoy=None, ebitda=89861454.91,
        impair=0.0, other_adj=26179245.35, carry=26179245.35,
        yield_mkt=5.36, fee=19603802.28, top1=22.34, top5=79.05, related=0.0,
        a_fin="2025 年报 p8–p10 §3.1/§3.3.2.1", a_op="2025 年报 p15 §4.1.1",
        a_imp="2025 年报（未计提；净利润为负系折旧摊销 1.72 亿）",
    ),
}

# 被排除的 4 只（只登记理由，不入面板）
EXCLUDED = [
    ("180305", "南方顺丰仓储物流REIT", "2025-03-27 成立，报告期 280 天",
     "期间不完整：年化后可比，但同比与周转类指标失真", "边界检验（见报告 §2.4）"),
    ("180306", "华夏安博仓储物流REIT", "截至 2026-04-30 未披露 2025 年报",
     "披露不可得：无法取得 §3.3 可供分配与 §4.1 运营指标", "D 级，下一期纳入"),
    ("180307", "中金菜鸟仓储物流REIT", "截至 2026-04-30 未披露 2025 年报",
     "披露不可得：同上", "D 级，下一期纳入"),
    ("508090", "中银中外运仓储物流REIT", "截至 2026-04-30 未披露 2025 年报",
     "披露不可得：同上", "D 级，下一期纳入"),
]

# ---------------------------------------------------------------- 派生（B 级）
for c, d in F.items():
    d["mcap"] = d["dist"] / (d["yield_mkt"] / 100)          # 反推市值，保证与分派率同时点
    d["mcap_psm"] = d["mcap"] / d["area"]
    d["rev_psm"] = d["rev"] / d["area"]
    d["cfo_psm"] = d["cfo"] / d["area"]
    d["dist_psm"] = d["dist"] / d["area"]
    d["cfo_yield"] = d["cfo"] / d["mcap"] * 100
    d["dist_over_cfo"] = d["dist"] / d["cfo"]                 # 分派纯度：>1 表示分派超过经营现金
    d["ebitda_adj"] = d["ebitda"] + d["impair"]               # 回加减值，否则减值大的被低估
    d["ebitda_margin_adj"] = d["ebitda_adj"] / d["rev"] * 100
    d["impair_over_rev"] = d["impair"] / d["rev"] * 100
    d["fee_rate"] = d["fee"] / d["rev"] * 100
    d["dist_yield_pure"] = (d["dist"] - d["carry"]) / d["mcap"] * 100
    d["carry_ratio"] = d["carry"] / d["dist"] * 100
    d["rent_yield"] = d["rent_pm"] * 12 / d["mcap_psm"] * 100  # 毛租金/市值，粗资本化率

COLS = list(F.keys())

# ---------------------------------------------------------------- 排名工具
def rank(vals, reverse=False):
    """返回 {code: 名次}；reverse=True 表示数值越小越好。缺失值不参与。"""
    items = [(c, v) for c, v in vals.items() if v is not None]
    s = sorted(items, key=lambda x: -x[1] if not reverse else x[1])
    return {c: i + 1 for i, (c, _) in enumerate(s)}


# ---------------------------------------------------------------- 三个收益率口径
r1 = rank({c: F[c]["yield_mkt"] for c in COLS})
r2 = rank({c: F[c]["cfo_yield"] for c in COLS})
r3 = rank({c: F[c]["cfo_psm"] for c in COLS})
flip = {c: max(r1[c], r2[c], r3[c]) - min(r1[c], r2[c], r3[c]) for c in COLS}

# ---------------------------------------------------------------- 五个资产质量维度
QUALITY = [
    ("occ", "期末出租率", "%", "越高越好", 1, {"c": F, "k": "occ"}),
    ("rent_yoy", "租金单价同比", "%", "降幅越小越好", 1, {"c": F, "k": "rent_yoy"}),
    ("wale", "剩余租期", "天", "越长越好", 1, {"c": F, "k": "wale"}),
    ("top1", "最大租户占比", "%", "越低越好", -1, {"c": F, "k": "top1"}),
    ("impair", "减值/收入", "%", "越低越好", -1, {"c": F, "k": "impair_over_rev"}),
]

qrank = {}
for key, _cn, _u, _dir, sign, spec in QUALITY:
    qrank[key] = rank({c: spec["c"][c][spec["k"]] for c in COLS}, reverse=(sign < 0))

# 参与度不同（rent_yoy 只有 4 只有值），用"排名中位数"而不是"排名和"；
# 集中度不并入资产质量——它是客户结构，与"资产好不好"是两个问题。
def median_rank(c, keys):
    v = sorted(qrank[k][c] for k in keys if c in qrank[k])
    n = len(v)
    return (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2), n

QKEYS = ["occ", "rent_yoy", "wale", "impair"]          # 资产质量四维
qpos = {c: median_rank(c, QKEYS) for c in COLS}
# 稳健性：剔除租期（租期方向随租金周期反转，见报告 §5.3）
qpos3 = {c: median_rank(c, ["occ", "rent_yoy", "impair"]) for c in COLS}

# ---------------------------------------------------------------- 输出
def wcsv(name, header, rows):
    p = os.path.join(OUT, name)
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return p


RAW_ROWS = [
    ("area", "期末可供出租面积", "㎡", "时点", "a_op"),
    ("occ", "期末出租率", "%", "时点", "a_op"),
    ("rent_pm", "期末租金单价", "元/㎡/月", "时点/换算", "a_op"),
    ("rent_yoy", "租金单价同比", "%", "期末 vs 上年同期", "a_op"),
    ("wale", "剩余租期", "天", "时点/换算", "a_op"),
    ("coll", "收缴率", "%", "当年累计", "a_op"),
    ("rev", "营业收入", "元", "期间", "a_fin"),
    ("rev_yoy", "营业收入同比", "%", "期间", "a_fin"),
    ("cfo", "经营活动现金流净额", "元", "期间", "a_fin"),
    ("dist", "可供分配金额", "元", "期间", "a_fin"),
    ("dist_yoy", "可供分配同比", "%", "期间", "a_fin"),
    ("ebitda", "EBITDA（披露桥）", "元", "期间（未回加减值）", "a_fin"),
    ("impair", "资产减值损失", "元", "期间", "a_imp"),
    ("yield_mkt", "披露现金流分派率", "%", "市值口径", "a_fin"),
    ("fee", "管理费合计", "元", "期间", "a_fin"),
    ("top1", "最大租户占比", "%", "时点", "a_op"),
    ("top5", "前五大租户占比", "%", "时点", "a_op"),
]
DERIVED = [
    ("mcap", "反推市值", "元", "可供分配 ÷ 分派率"),
    ("mcap_psm", "单位面积市值", "元/㎡", "市值 ÷ 可租面积"),
    ("rev_psm", "单位面积收入", "元/㎡/年", "收入 ÷ 可租面积"),
    ("cfo_psm", "单位面积经营现金流", "元/㎡/年", "CFO ÷ 可租面积"),
    ("cfo_yield", "现金分派率", "%", "CFO ÷ 市值"),
    ("dist_over_cfo", "分派对 CFO 倍数", "倍", "可供分配 ÷ CFO"),
    ("ebitda_margin_adj", "EBITDA 率（回加减值）", "%", "(EBITDA+减值) ÷ 收入"),
    ("impair_over_rev", "减值/收入", "%", "减值 ÷ 收入"),
    ("fee_rate", "费用率", "%", "管理费合计 ÷ 收入"),
    ("carry_ratio", "结转类调增/可供分配", "%", "结转项 ÷ 可供分配"),
    ("dist_yield_pure", "分派率（剔结转）", "%", "(可供分配−结转) ÷ 市值"),
    ("rent_yield", "毛租金/市值", "%", "租金×12 ÷ 单位面积市值"),
]

long_rows = []
for c in COLS:
    d = F[c]
    for k, cn, unit, cal, ak in RAW_ROWS:
        v = d.get(k)
        long_rows.append([c, d["name"], k, cn, "" if v is None else v, unit, cal, d[ak], "A"])
    for k, cn, unit, cal in DERIVED:
        v = d.get(k)
        long_rows.append([c, d["name"], k, cn, "" if v is None else round(v, 4), unit, cal,
                          "派生：见 caliber", "B"])
p1 = wcsv("panel_2025.csv",
          ["fund", "name", "metric", "metric_cn", "value", "unit", "caliber", "anchor", "grade"],
          long_rows)

# 收益率矩阵
yield_rows = []
for c in COLS:
    d = F[c]
    yield_rows.append([d["short"], round(d["yield_mkt"], 2), r1[c],
                       round(d["cfo_yield"], 2), r2[c],
                       round(d["cfo_psm"], 1), r3[c], flip[c],
                       round(d["dist_over_cfo"], 2), round(d["carry_ratio"], 1),
                       round(d["dist_yield_pure"], 2), round(d["mcap"] / 1e8, 2)])
p2 = wcsv("matrix_yield.csv",
          ["标的", "C1分派率%", "C1排名", "C2现金分派率%", "C2排名",
           "C3单位面积CFO元", "C3排名", "排名极差",
           "分派对CFO倍数", "结转占比%", "剔结转分派率%", "反推市值亿"], yield_rows)

# 资产质量矩阵
quality_rows = []
qkeys = [k for k, *_ in QUALITY]
for c in COLS:
    d = F[c]
    row = [d["short"]]
    for k in qkeys:
        v = {"impair": d["impair_over_rev"]}.get(k, d.get(k))
        row.append("" if v is None else round(v, 2))
    row += [qrank["occ"][c], qrank["wale"][c], qrank["top1"][c], qrank["impair"][c],
            "" if c not in qrank["rent_yoy"] else qrank["rent_yoy"][c],
            qpos[c][0], qpos3[c][0]]
    quality_rows.append(row)
p3 = wcsv("matrix_quality.csv",
          ["标的", "出租率%", "租金同比%", "剩余租期天", "最大租户%", "减值/收入%",
           "出租率名次", "租期名次", "集中度名次", "减值名次", "租金趋势名次",
           "资产质量位次", "位次(剔租期)"], quality_rows)

# 选样漏斗
fun_rows = []
for c in COLS:
    d = F[c]
    fun_rows.append([c, d["short"], "纳入", "满足五项条件：仓储物流 / 2025 完整财年 / "
                     "年报可获取 / 可租面积≥10 万㎡ / 有可比运营披露", d["area"], ""])
for code, name, why, kind, action in EXCLUDED:
    fun_rows.append([code, name, "排除", why, "", action])
p4 = wcsv("sample_funnel.csv", ["代码", "简称", "结论", "理由", "可租面积㎡", "后续"], fun_rows)

# 兼容版
print("=" * 86)
print(f"{'指标':<22}" + "".join(f"{F[c]['short']:>10}" for c in COLS))
for label, key, fmt in [
    ("期末出租率%", "occ", "{:.2f}"), ("租金元/㎡/月", "rent_pm", "{:.2f}"),
    ("租金同比%", "rent_yoy", "{:.2f}"), ("剩余租期天", "wale", "{:.0f}"),
    ("C1分派率%", "yield_mkt", "{:.2f}"), ("C2现金分派率%", "cfo_yield", "{:.2f}"),
    ("C3单位面积CFO", "cfo_psm", "{:.1f}"), ("分派对CFO倍数", "dist_over_cfo", "{:.2f}"),
    ("结转/可供分配%", "carry_ratio", "{:.1f}"), ("EBITDA率(调)%", "ebitda_margin_adj", "{:.2f}"),
    ("减值/收入%", "impair_over_rev", "{:.2f}"), ("费用率%", "fee_rate", "{:.2f}"),
    ("单位面积市值", "mcap_psm", "{:.0f}"), ("市值亿", "mcap", "{:.1f}"),
]:
    cells = []
    for c in COLS:
        v = F[c].get(key)
        cells.append(f"{fmt.format(v / 1e8 if key == 'mcap' else v):>10}" if v is not None else f"{'NA':>10}")
    print(f"{label:<22}" + "".join(cells))

print("\n名次（1 = 最优）")
print(f"{'维度':<22}" + "".join(f"{F[c]['short']:>10}" for c in COLS))
for k, cn, *_ in QUALITY:
    print(f"{cn:<22}" + "".join(f"{qrank[k].get(c, 'NA'):>10}" for c in COLS))
print(f"{'资产质量位次':<22}" + "".join(f"{qpos[c][0]:>10}" for c in COLS))
print(f"{'位次(剔租期,稳健性)':<22}" + "".join(f"{qpos3[c][0]:>10}" for c in COLS))
print(f"{'排名极差':<22}" + "".join(f"{flip[c]:>10}" for c in COLS))
print("\n输出：", ", ".join(os.path.basename(x) for x in (p1, p2, p3, p4)))
