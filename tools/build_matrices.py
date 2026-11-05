# -*- coding: utf-8 -*-
"""生成 models/data_matrices.xlsx（案例一、案例二运营数据矩阵）
数据来源：outputs/_panel/*_raw.csv（由 extract_panel.py 从披露原文抽取）
          + 年报/招募书关键财务事实（手工核对，带锚点）
"""
import csv, os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(BASE, "outputs", "_panel")
OUT = os.path.join(BASE, "models", "data_matrices.xlsx")

HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
SUB_FILL = PatternFill("solid", fgColor="DDEBF7")
WARN_FILL = PatternFill("solid", fgColor="FFF2CC")
NA_FILL = PatternFill("solid", fgColor="F2F2F2")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def load(code):
    rows = list(csv.DictReader(open(os.path.join(PANEL, "%s_raw.csv" % code), encoding="utf-8-sig")))
    d = {}
    for r in rows:
        d.setdefault((r["period"], r["dim"]), {})[r["metric"]] = r["value"]
    return d


def num(v):
    try:
        return float(v)
    except Exception:
        return None


def title(ws, text, ncol, sub=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    c = ws.cell(row=1, column=1, value=text)
    c.font = Font(size=13, bold=True, color="FFFFFF")
    c.fill = HEAD_FILL
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 26
    if sub:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncol)
        c2 = ws.cell(row=2, column=1, value=sub)
        c2.font = Font(size=9, italic=True, color="595959")
        c2.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.row_dimensions[2].height = 30


def header(ws, row, cols):
    for i, v in enumerate(cols, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = Font(bold=True, size=10, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2E75B6")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[row].height = 32


def put(ws, row, vals, fmt=None, fills=None):
    for i, v in enumerate(vals, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.border = BORDER
        c.alignment = Alignment(horizontal="center" if i > 1 else "left", vertical="center")
        c.font = Font(size=10)
        if isinstance(v, float) and i > 1:
            c.value = round(v, 4)
        if fmt and i > 1 and isinstance(v, (int, float)):
            c.number_format = fmt
        if fills and i in fills:
            c.fill = fills[i]


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------- 案例一：508056 中金普洛斯 ----------------
def glp(wb):
    d = load("508056")
    ws = wb.active
    ws.title = "508056_1运营指标"
    title(ws, "中金普洛斯REIT（508056）整体运营指标矩阵 2025Q1–2025FY", 9,
          "口径：期末时点值（非期间平均）。出租率=期末实际出租面积/期末可供出租面积；租金单价=期末合同租金及物业管理服务费（不含税）有效平均；"
          "剩余租期、收缴率口径见季报注6。数据来源：各期定期报告§4.1.2，页码见 source_index。")
    header(ws, 3, ["指标", "单位", "2025Q1", "2025Q2", "2025H1", "2025Q3", "2025Q4", "2025FY", "备注"])
    order = ["2025Q1", "2025Q2", "2025H1", "2025Q3", "2025Q4", "2025FY"]
    rows = [("期末出租率", "%", "occ", "0.00"), ("期末租金单价", "元/㎡/月", "rent", "0.00"),
            ("期末剩余租期", "天", "wale", "0.00"), ("期末租金收缴率", "%", "collection", "0.00"),
            ("期末实际出租面积", "㎡", "area_leased", "#,##0.00"), ("期末可供出租面积", "㎡", "area_leasable", "#,##0.00")]
    r = 4
    for name, unit, key, fmt in rows:
        vals = [num(d.get((p, "overall"), {}).get(key)) for p in order]
        put(ws, r, [name, unit] + vals + [""], fmt)
        r += 1
    put(ws, r, ["【同比】出租率", "pct", None, num(d[("2025Q2", "overall")].get("occ_yoy")), num(d[("2025H1", "overall")].get("occ_yoy")),
                num(d[("2025Q3", "overall")].get("occ_yoy")), num(d[("2025Q4", "overall")].get("occ_yoy")), None, "vs 上年同期"], "0.00")
    put(ws, r + 1, ["【同比】租金单价", "%", None, num(d[("2025Q2", "overall")].get("rent_yoy")), num(d[("2025H1", "overall")].get("rent_yoy")),
                    num(d[("2025Q3", "overall")].get("rent_yoy")), num(d[("2025Q4", "overall")].get("rent_yoy")), None, "vs 上年同期"], "0.00")
    put(ws, r + 2, ["【同比】剩余租期", "%", None, num(d[("2025Q2", "overall")].get("wale_yoy")), num(d[("2025H1", "overall")].get("wale_yoy")),
                    num(d[("2025Q3", "overall")].get("wale_yoy")), num(d[("2025Q4", "overall")].get("wale_yoy")), None, "vs 上年同期"], "0.00")
    put(ws, r + 4, ["说明", "", "H1 与 FY 为时点快照（6/30、12/31），不取季度平均。FY 值 = Q4 期末值（89.54%），说明年末未做短期填铺。", "", "", "", "", "", ""])
    widths(ws, [22, 12, 11, 11, 11, 11, 11, 11, 26])

    # 分项目
    ws2 = wb.create_sheet("508056_2区域归因")
    title(ws2, "分项目运营指标（2025Q1–2025Q4）", 8,
          "项目口径与季报§4.1.3一致；Q4 报告使用“不动产项目名称”表述，已统一。出租率与租金同步下行且出租率上升 → 量升价降（以价换量）。")
    header(ws2, 3, ["项目", "指标", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "Q4同比", "归类"])
    projs = sorted({k[1] for k in d if k[1] != "overall"})
    r = 4
    for p in projs:
        occ = [num(d.get((q, p), {}).get("occ")) for q in ["2025Q1", "2025Q2", "2025Q3", "2025Q4"]]
        rent = [num(d.get((q, p), {}).get("rent")) for q in ["2025Q1", "2025Q2", "2025Q3", "2025Q4"]]
        oy = num(d.get(("2025Q4", p), {}).get("occ_yoy"))
        ry = num(d.get(("2025Q4", p), {}).get("rent_yoy"))
        if oy is not None and ry is not None:
            tag = "量升价降" if oy > 0 and ry < 0 else ("量价齐跌" if oy <= 0 and ry < 0 else ("量跌价升" if oy < 0 and ry >= 0 else "量价齐升"))
        else:
            tag = "缺同比"
        put(ws2, r, [p, "出租率%"] + occ + [oy, tag], "0.00")
        put(ws2, r + 1, [p, "租金单价元/㎡/月"] + rent + [ry, ""], "0.00")
        r += 2
    widths(ws2, [24, 18, 10, 10, 10, 10, 10, 14])

    # 收入与可供分配
    ws3 = wb.create_sheet("508056_3收入与可供分配")
    title(ws3, "收入与可供分配金额（单季 / 累计）", 8,
          "关键口径：季报“本期收入”为单季数，无需差分；可供分配金额同时披露“本期”与“本年累计”，单季直接取“本期”。"
          "四季度可供分配合计 337,472,828.59 元，年报审计口径 335,181,671.99 元，差异 2,291,156.60 元（0.68%）——以年报为准，季报累计值记 DATA_QUALITY_WARNING。")
    header(ws3, 3, ["项目", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2025FY（年报）", "口径", "锚点"])
    q = ["2025Q1", "2025Q2", "2025Q3", "2025Q4"]
    rev = [num(d[(p, "overall")].get("revenue_cum")) for p in q]
    cfo = [num(d[(p, "overall")].get("cfo_cum")) for p in q]
    dist = [num(d[(p, "overall")].get("distributable_q")) for p in q]
    distr = [num(d[(p, "overall")].get("distributed_q")) for p in q]
    put(ws3, 4, ["营业收入（单季）"] + rev + [422500807.91, "单季", "季报§3.1 / 年报§3.1"], "#,##0.00")
    put(ws3, 5, ["经营活动现金流净额（单季）"] + cfo + [231950053.99, "单季", "季报§3.1 / 年报§3.1"], "#,##0.00")
    put(ws3, 6, ["可供分配金额（单季）"] + dist + [335181671.99, "单季", "季报§3.3.1 / 年报§3.3.1.1"], "#,##0.00")
    put(ws3, 7, ["实际分配金额（单季）"] + distr + [430470192.84, "单季", "季报§3.3.2 / 年报§3.3.1.2"], "#,##0.00")
    put(ws3, 8, ["合计校验：单季可供分配之和", None, None, None, sum(x for x in dist if x), 335181671.99, "—", "差异 −2,291,156.60"], "#,##0.00")
    put(ws3, 10, ["年报拆解项", "金额（元）", "说明", "", "", "", "", ""])
    for c in ws3[10]:
        c.fill = SUB_FILL
        c.font = Font(bold=True, size=10)
    items = [("合并净利润", -80106019.41, "含商誉减值 71,520,087.02 元"),
             ("折旧和摊销", 335974269.07, "回加项"),
             ("利息支出", 11869376.93, "回加项"),
             ("所得税费用", -75018205.99, "回加项"),
             ("EBITDA", 192719420.60, "息税折旧摊销前利润"),
             ("未来合理支出预留", 31047781.50, "调增"),
             ("资产减值准备变动", 71520087.02, "调增（商誉减值回加）"),
             ("其他调整项", 84070555.06, "调增（期初现金等）"),
             ("应收应付变动", -9209954.92, "调减"),
             ("资本性支出", -14215896.06, "调减"),
             ("支付的利息及所得税", -20750321.21, "调减"),
             ("= 本期可供分配金额", 335181671.99, "年报 §3.3.2.1")]
    r = 11
    for n, v, note in items:
        put(ws3, r, [n, v, note, "", "", "", "", ""], "#,##0.00")
        r += 1
    widths(ws3, [26, 16, 16, 16, 16, 18, 10, 34])

    # 分项目收入
    ws4 = wb.create_sheet("508056_4分项目收入")
    title(ws4, "分项目营业收入（2025FY vs 2024FY）", 5, "来源：2025年年度报告 §4.3.3 重要不动产项目公司的营业收入分析。单位：元。")
    header(ws4, 3, ["项目公司/项目", "2025FY", "2024FY", "同比%", "备注"])
    proj_rev = [("合计（9家项目公司）", 418542744.66, 449670364.47, -6.92, "租金及物业管理服务费占 99.50%"),
                ("北京普洛斯空港物流发展（空港+通州）", 119841008.99, 128814511.86, -6.97, "空港约占 80%，通州约 20%"),
                ("广州普洛斯仓储设施管理", 49496061.22, 53933927.01, -8.23, ""),
                ("佛山市顺德区普顺物流园", 45518390.22, 51576920.68, -11.75, ""),
                ("苏州普洛斯望亭物流园", 42125855.13, 41950467.65, 0.42, "唯一正增长"),
                ("昆山普淀仓储", 47896236.13, 57193438.40, -16.26, "降幅最大；商誉减值 7152 万")]
    r = 4
    for row in proj_rev:
        put(ws4, r, list(row), "#,##0.00")
        r += 1
    widths(ws4, [38, 18, 18, 10, 30])
    return wb


# ---------------- 案例二：180302 华夏深国际 ----------------
OVR = {("2025Q3", "overall"): {"collection": 99.06},
       ("2025Q4", "overall"): {"collection": 99.63, "rent_avg_period": 27.35, "wale": 1.55},
       ("2025H1", "overall"): {"collection": 99.44}}
PREV = {"occ_prev": "occ", "rent_prev": "rent", "wale_prev": "wale", "collection_prev": "collection",
        "rent_avg_period_prev": "rent_avg_period"}


def hx(wb):
    d = load("180302")
    for (per, dim), kv in OVR.items():
        d.setdefault((per, dim), {}).update(kv)
    # 2024 基线：取自 2025 年报告披露的“上年同期/上年同期末”列，不自行回算
    for src, dst in [("2025Q3", "2024Q3"), ("2025Q4", "2024Q4")]:
        kv = d.get((src, "overall"), {})
        d.setdefault((dst, "overall"), {})
        for k, v in PREV.items():
            if k in kv:
                d[(dst, "overall")][v] = kv[k]
    d.setdefault(("2024Q4", "overall"), {}).update({"wale": 1.68, "rent_avg_period": 33.87, "collection": 95.41})
    d.setdefault(("2024Q3", "overall"), {}).update({"collection": 97.52})
    ws = wb.create_sheet("180302_1运营指标")
    title(ws, "华夏深国际仓储REIT（180302）整体运营指标矩阵 2024Q3–2025FY", 8,
          "口径提示：本基金季报同时披露“期末有效租金单价”与“报告期平均租金单价”，二者不可混用；剩余租期单位为【年】，与 508056 的【天】不可直接比较（NOT_COMPARABLE）。"
          "Q3 另披露“考虑报告披露日前已起租面积的整体出租率 88.69%”，属期后事项，列示但不替代期末值。")
    header(ws, 3, ["指标", "单位", "2024Q3", "2024Q4", "2025H1", "2025Q3", "2025Q4", "2025FY"])
    order = ["2024Q3", "2024Q4", "2025H1", "2025Q3", "2025Q4", "2025FY"]
    rows = [("期末出租率", "%", "occ", "0.00"), ("期末有效租金单价", "元/㎡/月", "rent", "0.00"),
            ("报告期平均租金单价", "元/㎡/月", "rent_avg_period", "0.00"),
            ("期末加权平均剩余租期", "年", "wale", "0.00"),
            ("期末租金收缴率", "%", "collection", "0.00"),
            ("期末实际出租面积", "㎡", "area_leased", "#,##0.00")]
    r = 4
    for name, unit, key, fmt in rows:
        vals = [num(d.get((p, "overall"), {}).get(key)) for p in order]
        put(ws, r, [name, unit] + vals, fmt)
        r += 1
    put(ws, r, ["同比：出租率（pct）", "pct", None, None, None,
                num(d.get(("2025Q3", "overall"), {}).get("occ_yoy")), num(d.get(("2025Q4", "overall"), {}).get("occ_yoy")), None], "0.00")
    put(ws, r + 1, ["同比：有效租金（%）", "%", None, None, None,
                    num(d.get(("2025Q3", "overall"), {}).get("rent_yoy")), num(d.get(("2025Q4", "overall"), {}).get("rent_yoy")), None], "0.00")
    put(ws, r + 2, ["同比：剩余租期（%）", "%", None, None, None,
                    num(d.get(("2025Q3", "overall"), {}).get("wale_yoy")), num(d.get(("2025Q4", "overall"), {}).get("wale_yoy")), None], "0.00")
    put(ws, r + 3, ["同比：收缴率（pct）", "pct", None, None, None, 1.58, 4.42, None], "0.00")
    put(ws, r + 5, ["数据缺口", "", "2024Q3/Q4 报告未按现口径披露运营指标（旧版披露格式），同比值直接取自 2025 年报告披露的上年同期列，未自行回算。",
                    "", "", "", "", ""])
    widths(ws, [24, 14, 11, 11, 11, 11, 11, 11])

    ws2 = wb.create_sheet("180302_2区域归因")
    title(ws2, "分项目运营指标（2025Q3–2025Q4）", 7,
          "两项目结构：杭州一期（可租 206,881.52 ㎡）、贵州（147,432.25 ㎡）。杭州为量价齐跌的主因，贵州出租率创新高但租金降幅最大。")
    header(ws2, 3, ["项目", "指标", "2025Q3", "2025Q4", "Q4同比", "Q4环比", "归因"])
    for i, p in enumerate(["杭州一期项目", "贵州项目"]):
        r = 4 + i * 4
        occ3, occ4 = num(d.get(("2025Q3", p), {}).get("occ")), num(d.get(("2025Q4", p), {}).get("occ"))
        rent3, rent4 = num(d.get(("2025Q3", p), {}).get("rent")), num(d.get(("2025Q4", p), {}).get("rent"))
        oy, ry = num(d.get(("2025Q4", p), {}).get("occ_yoy")), num(d.get(("2025Q4", p), {}).get("rent_yoy"))
        put(ws2, r, [p, "出租率%", occ3, occ4, oy, (occ4 - occ3) if occ3 and occ4 else None, "同比仍降、环比修复" if p.startswith("杭州") else "同比转正"], "0.00")
        put(ws2, r + 1, [p, "有效租金元/㎡/月", rent3, rent4, ry, (rent4 - rent3) if rent3 and rent4 else None, "续租降价" ], "0.00")
        put(ws2, r + 2, [p, "剩余租期（年）", num(d.get(("2025Q3", p), {}).get("wale")), num(d.get(("2025Q4", p), {}).get("wale")),
                         num(d.get(("2025Q4", p), {}).get("wale_yoy")), None, "短租约，续租频度高"], "0.00")
    widths(ws2, [16, 20, 11, 11, 11, 11, 22])

    ws3 = wb.create_sheet("180302_3收入与可供分配")
    title(ws3, "收入与可供分配金额（2025Q3 / Q4 / FY）", 7,
          "校验：H1 36,746,669.59 + Q3 18,744,911.01 + Q4 18,909,619.40 = 74,401,200.00，与年报审计口径完全一致（差异 0）。"
          "本基金 2024 年 6 月 25 日成立，2024 年数据为不足整年，同比不可比（NOT_COMPARABLE）。")
    header(ws3, 3, ["项目", "2025Q1–Q2（H1）", "2025Q3", "2025Q4", "2025FY", "口径", "锚点"])
    put(ws3, 4, ["营业收入（单季）", None, 27352541.72, 24620378.20, 111528606.01, "单季", "季报§3.1 / 年报§3.1"], "#,##0.00")
    put(ws3, 5, ["经营活动现金流净额（单季）", None, 27539181.15, 18039624.82, 83656185.80, "单季", "同上"], "#,##0.00")
    put(ws3, 6, ["可供分配金额（单季）", 36746669.59, 18744911.01, 18909619.40, 74401200.00, "单季", "季报§3.3.1 / 年报§3.3.1.1"], "#,##0.00")
    put(ws3, 7, ["实际分配金额", None, 17639999.47, 18179999.81, 72149995.93, "单季", "季报§3.3.2 / 年报§3.3.1.2"], "#,##0.00")
    put(ws3, 9, ["年报拆解项", "金额（元）", "说明", "", "", "", ""])
    for c in ws3[9]:
        c.fill = SUB_FILL
        c.font = Font(bold=True, size=10)
    items = [("合并净利润", 26629527.89, ""), ("折旧和摊销", 54834972.76, "回加"),
             ("所得税费用", -4826806.90, "回加"), ("EBITDA", 76637693.75, ""),
             ("应收和应付项目变动", 7008625.60, "调增"), ("购买不动产项目资本性支出", -2426001.32, "调减"),
             ("未来合理相关支出预留", -6819118.03, "调减"), ("= 可供分配金额", 74401200.00, "年报§3.3.2.1")]
    r = 10
    for n, v, note in items:
        put(ws3, r, [n, v, note, "", "", "", ""], "#,##0.00")
        r += 1
    widths(ws3, [26, 18, 16, 16, 18, 8, 32])

    ws4 = wb.create_sheet("180302_4分项目收入")
    title(ws4, "分项目营业收入结构（2025FY）", 6, "来源：2025年年度报告 §4.3.3。本基金上年同期为不足整年（2024/6/25–12/31），同比增速不具可比性，故不列同比。")
    header(ws4, 3, ["项目公司", "租赁收入", "管理费收入", "其他收入", "合计", "租赁占比%"])
    put(ws4, 4, ["杭州深国际综合物流港", 53752882.22, 16942661.64, 1513328.93, 72208872.79, 74.44], "#,##0.00")
    put(ws4, 5, ["贵州深国际综合物流港", 30758421.88, 7276885.96, 224266.20, 38259574.04, 80.39], "#,##0.00")
    put(ws4, 6, ["合计", 84511304.10, 24219547.60, 1737595.13, 110468446.83, 76.50], "#,##0.00")
    widths(ws4, [26, 16, 16, 14, 16, 12])
    return wb


if __name__ == "__main__":
    wb = Workbook()
    glp(wb)
    hx(wb)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print("saved", OUT, "sheets:", wb.sheetnames)
