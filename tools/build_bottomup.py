#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_bottomup.py — 508601 自下而上测算与到期重定价情景

为什么要有这个脚本
------------------
旧版报告 2028 年以后的现金流是这样外推的：EBITDA 率固定 68.65%，收入按 2.78%
复合增长。得到的分派率是 5.71% → 6.04% → … → 8.51% 单调上升。

这与报告自己前四章的三条判断直接冲突：
  · 租金连续两年下行（−5.46%、−8.03%），且降幅在扩大；
  · 2027-11 至 2028-05 有 39.10% 的已租面积集中到期；
  · 续租必须以降价换取（贵州案例：−25.55% 换 2.26pct 出租率）。

一个"每年涨价 2.78%、永不重定价"的模型，无法回答"2028 年那批租约到期会怎样"。
本脚本补的就是这一段：把 2028 年到期的那 39.10% 面积单独拿出来重定价，
其余面积按市场趋势走，三情景分别给出 2028 年收入与分派率。

所有参数都写死在 PARAMS 里并标注来源，运行结果可复算。

用法
----
    python tools/build_bottomup.py            # 打印报告用表格
    python tools/build_bottomup.py --csv models/scenario_2028.csv
"""
import argparse
import io
import os
import sys

# ---------------------------------------------------------------- 披露锚点
# 全部来自招募说明书（更新）2026-10-28 稿，单位：元
D = {
    "rev_2025": 264_482_179.70,      # 备考利润表，p134
    "rev_2026": 253_582_575.48,      # 预测利润表，p133
    "rev_2027": 254_760_101.02,
    "rent_fix_2026": 234_867_171.72,  # 营业收入预测分项
    "rent_fix_2027": 235_927_878.79,
    "nonrent_2027": 15_982_525.26,   # 提成 2,849,696.97 + 停车 6,927,272.73 + 多经 8,305,252.53 + 其他 750,000
    "ebitda_2026": 170_437_399.69,
    "ebitda_2027": 174_883_323.29,
    "capex_2026": 15_460_400.00,
    "capex_2027": 8_827_400.00,
    "intax_2026": 13_287_806.33,     # 支付利息及所得税
    "intax_2027": 13_745_968.83,
    "wc_2026": 2_609_355.18,         # 经营性应收应付变动
    "wc_2027": 44_572.42,
    "cashadj_2027": 1_036_616.37,
    "dist_disc_2026": 170_384_048.05,  # 披露（余额法）
    "dist_disc_2027": 153_304_398.41,
    "size": 2_739_656_060.87,        # 募集规模
    "appraisal": 2_703_000_000.00,   # 评估值 27.03 亿
    "leased_area": 149_121.21,       # 2025 年末已租面积
    "leasable_area": 151_761.81,
    "dep_2025": 76_446_700.00,       # 备考营业成本中折旧摊销 7,644.67 万元
    "om_fee_2026": 21_881_406.95,    # 运营管理费 A+B
    "noi_eval_2027": 183_900_000.00,  # 评估口径 NOI（由 CapRate 7.13% 反算）
}

# 规范化可供分配（EBITDA − capex − 利息所得税 − 营运资本变动）
NORM = {
    2026: D["ebitda_2026"] - D["capex_2026"] - D["intax_2026"] - D["wc_2026"],
    2027: D["ebitda_2027"] - D["capex_2027"] - D["intax_2027"]
          - D["wc_2027"] + D["cashadj_2027"],
}

# ------------------------------------------------------- 到期重定价分组
# 占 2025 年末已租面积与固定租金收入的比重（招募书 p148 前十大租户表）
G1 = {"name": "2027-11~2028-05 到期组", "area_pct": 0.3910, "rent_pct": 0.2482,
      "members": "次主力店2 1.36% + 百安居 4.17% + 万达影院 6.40% + 翠微 25.96% + 次主力店4 1.21%"}
G1_AREA = D["leased_area"] * G1["area_pct"]
G1_RENT_2027 = D["rent_fix_2027"] * G1["rent_pct"]
OTHER_RENT_2027 = D["rent_fix_2027"] - G1_RENT_2027

# 三情景参数（研究假设，见报告第六章参数表）
SCEN = {
    "悲观": {"renew": 0.55, "repricing": -0.15, "vacant_m": 9,
             "other_g": -0.06, "long_g": -0.010,
             "basis": "翠微不续约或大幅压价；其余面积延续 2025 年 −8% 的降价速度"},
    "中性": {"renew": 0.85, "repricing": -0.08, "vacant_m": 4,
             "other_g": -0.03, "long_g": 0.010,
             "basis": "续租率维持 2025 年 76.83% 以上；降价幅度与 2025 年持平后收敛"},
    "乐观": {"renew": 0.95, "repricing": -0.03, "vacant_m": 2,
             "other_g": -0.01, "long_g": 0.0225,
             "basis": "续租率回到 95%；价格基本守住；长期增长取评估假设 2.25%"},
}
PASSTHROUGH = 0.81      # 收入→EBITDA 传导系数（房产税与运营管理费随收入下降）
CAPEX_RATIO = 0.035     # 2028 年起 capex = 收入 × 3.5%
INTAX_STEP = 0.02

FIRST, LAST = 2026, 2044


def build(scen_name):
    s = SCEN[scen_name]
    rows = []
    rev_prev = D["rev_2027"]
    eb_prev = D["ebitda_2027"]

    # 2026 / 2027 用规范化值
    for y in (2026, 2027):
        dist = NORM[y]
        rev = D["rev_2026"] if y == 2026 else D["rev_2027"]
        eb = D["ebitda_2026"] if y == 2026 else D["ebitda_2027"]
        rows.append({"year": y, "rev": rev, "ebitda": eb,
                     "capex": D["capex_%d" % y], "intax": D["intax_%d" % y],
                     "dist": dist, "rate": dist / D["size"], "src": "披露值规范化"})

    # 2028：到期组重定价 + 其余面积按市场趋势
    decay = 1 - s["vacant_m"] / 12.0
    g1_2028 = G1_RENT_2027 * (s["renew"] * (1 + s["repricing"])
                              + (1 - s["renew"]) * decay * (1 + s["repricing"]))
    other_2028 = OTHER_RENT_2027 * (1 + s["other_g"])
    rent_2028 = g1_2028 + other_2028
    rev_2028 = rent_2028 + D["nonrent_2027"] * 1.01
    eb_2028 = eb_prev + PASSTHROUGH * (rev_2028 - rev_prev)
    cx_2028 = rev_2028 * CAPEX_RATIO
    it_2028 = D["intax_2027"] * (1 + INTAX_STEP)
    rows.append({"year": 2028, "rev": rev_2028, "ebitda": eb_2028,
                 "capex": cx_2028, "intax": it_2028,
                 "dist": eb_2028 - cx_2028 - it_2028,
                 "rate": (eb_2028 - cx_2028 - it_2028) / D["size"], "src": "本报告模型"})

    # 2029–2044：长期增长率
    for y in range(2029, LAST + 1):
        rev = rows[-1]["rev"] * (1 + s["long_g"])
        eb = rows[-1]["ebitda"] + PASSTHROUGH * (rev - rows[-1]["rev"])
        cx = rev * CAPEX_RATIO
        it = rows[-1]["intax"] * (1 + INTAX_STEP)
        dist = eb - cx - it
        rows.append({"year": y, "rev": rev, "ebitda": eb, "capex": cx, "intax": it,
                     "dist": dist, "rate": dist / D["size"], "src": "本报告模型"})
    return rows


def irr(cfs, lo=-0.9, hi=2.0):
    def npv(r):
        return sum(cf / (1 + r) ** i for i, cf in enumerate(cfs))
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(300):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def irr_of(rows, terminal=0.0):
    cfs = [-D["size"]] + [r["dist"] for r in rows]
    if terminal:
        cfs[-1] += terminal
    return irr(cfs)


def pv_at(rows, rate, terminal=0.0):
    return sum(r["dist"] / (1 + rate) ** (i + 1) for i, r in enumerate(rows)) \
        + terminal / (1 + rate) ** len(rows)


def terminal_for(rows, target):
    """使 IRR = target 所需的末年终值（二分）"""
    lo, hi = 0.0, 1e10
    for _ in range(200):
        mid = (lo + hi) / 2
        v = irr_of(rows, mid)
        if v is None:
            return None
        if v < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def size_for(rows, target):
    """使 IRR = target 的可承受发行规模 = 现金流按 target 折现"""
    return pv_at(rows, target)


# --------------------------------------------------------- 备考 → 基金层桥
def bridge():
    """项目公司备考 EBITDA（加回折旧）→ 基金预测 EBITDA 的差额分解"""
    rev_25 = D["rev_2025"]
    op_profit = 131_201_855.91   # 备考营业利润
    fin_exp = -954_270.08        # 备考财务费用（净利息收入，负数代表收益）
    eb_cg = op_profit + fin_exp  # 备考 EBITDA（未加回折旧时）
    eb_cg_adj = eb_cg + D["dep_2025"]
    # 收入下降传导
    d_rev = D["rev_2026"] - rev_25
    d_eb_rev = d_rev * (eb_cg_adj / rev_25)
    # 新增运营管理费
    # 管理费用与税金及附加口径差 = 残差
    residual = eb_cg_adj + d_eb_rev - D["om_fee_2026"] - D["ebitda_2026"]
    return {
        "eb_cg_reported": eb_cg,
        "dep": D["dep_2025"],
        "eb_cg_adj": eb_cg_adj,
        "margin_cg": eb_cg_adj / rev_25,
        "d_rev": d_rev,
        "d_eb_rev": d_eb_rev,
        "om_fee": D["om_fee_2026"],
        "residual": residual,
        "eb_fund": D["ebitda_2026"],
    }


def land_extension():
    """若收益期为 29.24 年（与地下车库同）而非 19.24 年，估值增加多少"""
    base = build("乐观")
    noi_2044 = base[-1]["ebitda"]
    rate, g = 0.05, 0.0225
    extra = 0.0
    for k in range(1, 11):     # 多 10 年
        extra += noi_2044 * (1 + g) ** k / (1 + rate) ** (19 + k)
    return {"noi_2044": noi_2044, "extra_pv": extra,
            "pct_of_appraisal": extra / D["appraisal"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="")
    a = ap.parse_args()

    out = []
    hdr = ("%-6s %14s %14s %12s %12s %14s %8s" %
           ("年度", "营业收入", "EBITDA", "资本性支出", "利息所得税", "可供分配", "分派率"))
    print("=" * 96)
    print("一、到期重定价三情景（2028 年起为模型，2026–2027 为披露值规范化）")
    for name in ("悲观", "中性", "乐观"):
        rows = build(name)
        print("\n【%s】%s" % (name, SCEN[name]["basis"]))
        print(hdr)
        for r in rows:
            if r["year"] in (2026, 2027, 2028, 2029, 2030, 2035, 2040, 2044):
                print("%-6d %14.0f %14.0f %12.0f %12.0f %14.0f %7.2f%%" %
                      (r["year"], r["rev"], r["ebitda"], r["capex"],
                       r["intax"], r["dist"], r["rate"] * 100))
        print("  2028 收入同比 %+.2f%%；2028 分派率较 2027 变动 %+.2f pct" %
              ((rows[2]["rev"] / rows[1]["rev"] - 1) * 100,
               (rows[2]["rate"] - rows[1]["rate"]) * 100))
        print("  19 年累计可供分派 %.2f 亿元（募集的 %.1f%%）；持有到期 IRR = %.2f%%" %
              (sum(r["dist"] for r in rows) / 1e8,
               sum(r["dist"] for r in rows) / D["size"] * 100,
               irr_of(rows) * 100))
        print("  IRR = 5.60%% 所需年末终值 = %.2f 亿元；可承受发行规模 = %.2f 亿元" %
              (terminal_for(rows, 0.056) / 1e8, size_for(rows, 0.056) / 1e8))
        out.append((name, rows))

    print("\n" + "=" * 96)
    print("二、项目公司备考 EBITDA → 基金层预测 EBITDA 桥（2025 实际 → 2026 预测）")
    b = bridge()
    print("备考营业利润 + 财务费用（未加回折旧）        %14.0f" % b["eb_cg_reported"])
    print("+ 折旧摊销（备考营业成本内）                %14.0f" % b["dep"])
    print("= 备考 EBITDA（加回折旧）                   %14.0f   率 %.2f%%" %
          (b["eb_cg_adj"], b["margin_cg"] * 100))
    print("− 收入下降的传导影响                        %14.0f" % abs(b["d_eb_rev"]))
    print("− 新增运营管理费（结构中原本不存在）        %14.0f" % b["om_fee"])
    print("− 管理费用与税金及附加口径差（残差）        %14.0f" % b["residual"])
    print("= 基金层预测 EBITDA（2026E）                %14.0f" % b["eb_fund"])

    print("\n" + "=" * 96)
    print("三、土地年限对估值的影响")
    le = land_extension()
    print("2044 年 EBITDA                              %14.0f" % le["noi_2044"])
    print("若收益期延长 10 年（至 2054），新增现值      %14.0f  = 评估值的 %.1f%%" %
          (le["extra_pv"], le["pct_of_appraisal"] * 100))

    if a.csv:
        lines = ["scenario,year,revenue,ebitda,capex,intax,distributable,rate,source"]
        for name, rows in out:
            for r in rows:
                lines.append("%s,%d,%.2f,%.2f,%.2f,%.2f,%.2f,%.6f,%s" %
                             (name, r["year"], r["rev"], r["ebitda"], r["capex"],
                              r["intax"], r["dist"], r["rate"], r["src"]))
        d = os.path.dirname(a.csv)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        io.open(a.csv, "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("\n已写出 %s（%d 行）" % (a.csv, len(lines) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
