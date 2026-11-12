# -*- coding: utf-8 -*-
"""生成 models/cash_flow_model.xlsx（案例三 508601 首农商业REIT 现金流与估值模型）

v2.0 相对 v1.0 的三处结构性修正（依据招募说明书 2026-10-28 更新稿原文核对）：
  1. 可供分配口径改为招募书的真实框架：EBITDA − 资本性支出（不含税）− 支付利息及所得税。
     招募书披露的 2026E 1.7038 亿元是"年末现金 − 预留安全现金 − 预留经营性负债"的余额法结果，
     该余额法结果与规范化经营口径的差额尚缺逐项桥接，不可直接归因为募集资金沉淀，也不可作为稳态口径。
  2. 资本性支出 2026 年改用测算表口径 15,460,400.00（不含税），非现金流量表的 21,047,778.55。
  3. 增长率拆为两段：2026–2035 用 2.78%（披露的预测期 CAGR），2036–2045 用 2.25%
     （披露的长期增长率，同业 2.25%–2.75% 下沿）。

新增：IRR（持有到期、不设终值）与"终值—IRR"对照，这是分派率与回报率之差的量化来源。
"""
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from tools import build_bottomup as bottomup
OUT = os.path.join(BASE, "models", "cash_flow_model.xlsx")

YELLOW = PatternFill("solid", fgColor="FFF2CC")
HEAD = PatternFill("solid", fgColor="1F4E79")
SUB = PatternFill("solid", fgColor="DDEBF7")
GREY = PatternFill("solid", fgColor="F2F2F2")
RED = PatternFill("solid", fgColor="FFC7CE")
GREEN = PatternFill("solid", fgColor="C6EFCE")
AMBER = PatternFill("solid", fgColor="FFEB9C")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

A = {
    "raise": 2739656060.87,
    "appraisal": 2703000000.0,
    "discount": 0.050,
    "years": 19,                 # 2026-2044，土地 2045-03-29 到期
    "rev26": 253582575.48,
    "rev27": 254760101.02,
    "eb26": 170437399.69,        # 招募书 §可供分配金额测算表 "利息、折旧及摊销前利润"
    "eb27": 174883323.29,
    "cx26": 15460400.00,         # 测算表口径（不含税）
    "cx27": 8827400.00,
    "it26": 13287806.33,         # 支付利息及所得税费用
    "it27": 13745968.83,
    "wc26": 2609355.18,          # 经营性应收应付变动
    "wc27": 44572.42,
    "cashadj27": 1036616.37,      # 期初现金调节
    "g1": 0.0278,
    "g2": 0.0225,
    "cxr": 0.035,                # 2027 起 capex = 收入 × 3.5%（评估取值）
    "itg": 0.02,                 # 利息及所得税年递增（研究假设）
    "disc_lo": 0.030,
    "disc_hi": 0.060,
}
M27 = A["eb27"] / A["rev27"]     # EBITDA 率 68.65%
PASS_THROUGH = 0.81              # 收入每变动 1 元，EBITDA 变动 0.81 元


def series(long_g=None):
    """Return 2026-2044 neutral maturity-repricing scenario; long_g is an explicit revenue-growth sensitivity."""
    return bottomup.build("中性", long_g=long_g)


def pv(rows, d, tv=0.0):
    s = sum(r["dist"] / (1 + d) ** (i + 1) for i, r in enumerate(rows))
    return s + (tv / (1 + d) ** len(rows) if tv else 0.0)


def irr(rows, price=None, tv=0.0):
    price = A["raise"] if price is None else price
    lo, hi = -0.20, 0.30
    for _ in range(300):
        mid = (lo + hi) / 2
        if pv(rows, mid, tv) > price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


ROWS = series()
PV5 = pv(ROWS, 0.05)
IRR0 = irr(ROWS)
TOTAL_DIST = sum(r["dist"] for r in ROWS)
# 使 IRR 达到 5.60% 所需终值
TV_GAP_560 = A["raise"] - pv(ROWS, 0.056)          # 现值缺口
TV_FOR_560 = TV_GAP_560 * (1.056 ** A["years"])   # 对应的 2044 年末终值
PRICE_AT_560 = pv(ROWS, 0.056)
# 不计算物业 NOI / 物业评估值：未取得完整资产评估报告及 NOI 口径桥接；EBITDA 不等于 NOI。

print("EBITDA率 2027 = %.4f" % M27)
print("规范化 2026 可供分配 = %.0f  分派率 %.2f%%" % (ROWS[0]["dist"], ROWS[0]["dist"] / A["raise"] * 100))
print("规范化 2027 可供分配 = %.0f  分派率 %.2f%%" % (ROWS[1]["dist"], ROWS[1]["dist"] / A["raise"] * 100))
print("19年累计可供分配 = %.4f亿  占募集 %.1f%%" % (TOTAL_DIST / 1e8, TOTAL_DIST / A["raise"] * 100))
print("PV@5%% (中性情景可供分配现金流，仅作折现参考) = %.4f亿" % (PV5 / 1e8))
print("IRR(无终值) = %.4f%%" % (IRR0 * 100))
print("使 IRR=5.60%% 所需终值(2044末) = %.4f亿 (现值缺口 %.4f亿) ; 可承受发行规模 %.4f亿" % (TV_FOR_560/1e8, TV_GAP_560/1e8, PRICE_AT_560/1e8))
for tv in [0, 5e8, 1e9, 1.65e9, 1.75e9, 2e9, A["appraisal"]]:
    print("  终值 %.2f亿 -> IRR %.2f%%" % (tv / 1e8, irr(ROWS, None, tv) * 100))


# ---------------- 样式工具 ----------------
def title(ws, text, ncol, sub=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    c = ws.cell(row=1, column=1, value=text)
    c.font = Font(size=13, bold=True, color="FFFFFF")
    c.fill = HEAD
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 26
    if sub:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncol)
        c2 = ws.cell(row=2, column=1, value=sub)
        c2.font = Font(size=9, italic=True, color="595959")
        c2.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.row_dimensions[2].height = 46


def hdr(ws, row, cols, h=30):
    for i, v in enumerate(cols, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = Font(bold=True, size=10, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="2E75B6")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[row].height = h


wb = Workbook()

# ================= 0 说明 =================
ws0 = wb.active
ws0.title = "0_说明"
title(ws0, "中信建投首农商业REIT（508601）现金流与估值模型 v2.1", 3,
      "2026–2027 按招募书披露调整项规范化；2028–2044 采用到期重定价中性情景。"
      "不将评估现金流 CAGR 当作营业收入增长率，不以 EBITDA 替代 NOI；长期结果是条件情景，不是确定预测。")
notes = [
    ("模型版本", "v2.1 / 2026-11-12；公式口径、数据来源优先级和适用限制见 models/MODEL_DISCLAIMER.md 与 models/formula_registry.csv。"),
    ("标的", "中信建投首农食品集团封闭式商业不动产证券投资基金（508601）；底层资产：北京昌平龙德广场"),
    ("锚点来源", "招募说明书（更新）2026-10-28：§现金流测算、§预测报表、§可供分配金额测算表及附注、"
                "§资产评估和现金流预测；2026 年第 3 季度报告（2026-10-27）"),
    ("① 披露的 2026E 可供分配 1.7038 亿元",
     "是余额法结果：年末货币资金 330,144,418.05 − 预留安全现金 3,424,854.22 − 预留经营性负债 156,335,515.79。"
     "该数与 EBITDA 仅差约 5.3 万元，但与规范化经营口径的差额缺逐项桥接，不能据此认定由募集资金沉淀覆盖 capex 与所得税；不可作稳态口径。"),
    ("② 规范化口径（本模型采用）",
     "可供分配 = EBITDA − 资本性支出 − 支付利息及所得税 − 经营性应收应付变动 + 披露的期初现金调节。2026："
     "170,437,399.69 − 15,460,400.00 − 13,287,806.33 − 2,609,355.18 = 139,079,838 元（5.08%）；"
     "2027 再加期初现金调节后为 153,301,998 元（5.60%），与披露值差 2,400 元。"),
    ("③ 披露 2027E 与规范化值仅差 2,400 元",
     "2027 年披露值与规范化值实质相等；2026 年仍需剔除首年余额法中的一次性资金沉淀。"),
    ("④ 资本性支出口径修正",
     "测算表口径 2026 年 15,460,400.00 元（不含税），2027 年起为收入的 3.5%（约 886 万元/年）；"
     "现金流量表的 21,047,778.55 元为含税/含长期待摊口径，两者相差 5,587,378.55 元，不可混用。"),
    ("⑤ 评估增长参数的使用边界",
     "招募说明书转引 2.78% 预测期现金流 CAGR、2.25% 长期增长率。它们是评估现金流参数，"
     "不是已证实的营业收入增长率；未取得原评估报告并确认定义前，本模型不将其用于收入外推。"),
    ("⑥ 本模型的 IRR",
     "采用 2028 年租约到期中性情景，2026–2044 共 19 期年度现金流，期末不计终值。"
     "这是年度期数 IRR 情景，不是实际投资者 XIRR；期末零终值仅为压力情景，不代表法律上资产价值为零。"),
    ("⑦ 终值敏感性", "若 2045 年存在终值，IRR 显著上升；见 3_输出 的「终值—IRR」表。"),
    ("⑧ 已知局限（一）", "2018–2025 年历史 capex 年均 3,151.46 万元，其中升级改造约 2,614.70 万元、日常大修约 536.77 万元。"
                        "评估假设 886 万元约为日常大修均值的 1.65 倍；历史总均值不能直接作为未来维护性 capex 基准，仍需工程尽调核验。"),
    ("⑨ 已知局限（二）", "本工作簿的 2028–2044 现金流来自到期重定价中性情景；悲观、乐观情景见 5_到期重定价。所有 2029 年后收入增长均为研究情景，不是已披露收入预测。"),
    ("⑩ 可重算性与局限", "年度折现和 IRR 公式可重算；到期重定价情景由 build_bottomup.py 生成并写入情景表，"
                  "修改 Python 情景参数后须重新运行构建脚本。2028 年后营运资金变动暂按零处理，属于未验证简化假设。"),
]
notes.extend([
    ("⑪ 来源与口径声明", "来源优先级：基金合同/招募书定义 → 经审计及定期报告实际数据 → 原始资产评估报告 → 租约/工程/税务资料 → 外部市场数据 → 明示研究假设。每个数值均须核对单位、期间、含税状态、层级和分母。来源可追溯不等于已独立鉴证。"),
    ("⑫ 模型使用声明", "本模型是研究测算工具，不是管理人预测、评估机构估值或审计鉴证。结果仅在给定输入和假设下成立，不构成收益承诺。当前未取得原始资产评估报告，故不以 EBITDA 替代 NOI，也不声称复现物业评估值。详见 models/MODEL_DISCLAIMER.md。"),
    ("⑬ 情景与现金流限制", "2028 年后营运资金变动暂按 0 占位；利息及所得税合计按 2% 增长；CAPEX 按收入 3.5%；租约续租为聚合代理。均为待核验假设。IRR 分别展示 90%/100% 分配情景，非实际 XIRR。"),
])
hdr(ws0, 4, ["项目", "内容", ""])
r = 5
for k, v in notes:
    ws0.cell(row=r, column=1, value=k).font = Font(bold=True, size=10)
    c = ws0.cell(row=r, column=2, value=v)
    c.font = Font(size=10)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    for i in (1, 2):
        ws0.cell(row=r, column=i).border = BORDER
    ws0.row_dimensions[r].height = 46 if len(v) > 90 else (32 if len(v) > 50 else 18)
    r += 1
ws0.column_dimensions["A"].width = 34
ws0.column_dimensions["B"].width = 112

# ================= 1 假设 =================
wa = wb.create_sheet("1_假设")
title(wa, "Assumptions｜披露锚点与研究假设", 4,
      "白色 = 披露/推导锚点；黄色 = 可编辑简化输入。情景参数实际存于 tools/build_bottomup.py，修改后须重建模型。"
      "本表行号被工作表公式引用，插入行会导致公式错位；金额单位：元。")
hdr(wa, 4, ["参数", "取值", "性质", "来源 / 备注"])
items = [
    ("募集规模", A["raise"], "锚点", "招募书 §现金流测算注：2,739,656,060.87 元（封面另载 30.13 亿，见报告 §1.2）"),
    ("资产评估值", A["appraisal"], "锚点", "招募书 §资产评估：27.03 亿元"),
    ("折现率", A["discount"], "锚点", "招募书 §资产评估：5%"),
    ("收益年限", A["years"], "锚点", "商业土地 2045-03-29 到期，剩余 19.24 年；模型取 19 期"),
    ("营业收入 2026E", A["rev26"], "锚点", "招募书 §现金流测算"),
    ("营业收入 2027E", A["rev27"], "锚点", "招募书 §现金流测算"),
    ("EBITDA 2026E", A["eb26"], "锚点", "招募书 §可供分配金额测算表「利息、折旧及摊销前利润」"),
    ("EBITDA 2027E", A["eb27"], "锚点", "同上"),
    ("资本性支出 2026E", A["cx26"], "锚点", "测算表附注五（不含税）"),
    ("资本性支出 2027E", A["cx27"], "锚点", "测算表附注五（不含税）"),
    ("支付利息及所得税 2026E", A["it26"], "锚点", "测算表调整项"),
    ("支付利息及所得税 2027E", A["it27"], "锚点", "测算表调整项"),
    ("经营性应收应付变动 2026E", A["wc26"], "锚点", "招募书可供分配测算表调整项"),
    ("经营性应收应付变动 2027E", A["wc27"], "锚点", "同上"),
    ("期初现金调节 2027E", A["cashadj27"], "锚点", "招募书可供分配测算表调整项"),
    ("评估预测期现金流 CAGR（不作收入增长率）", A["g1"], "披露参数", "招募书转引 2.78%；原评估现金流定义未核验，本模型不用于收入外推"),
    ("评估长期现金流增长率（不作收入增长率）", A["g2"], "披露参数", "招募书转引 2.25%；原评估现金流定义未核验，本模型不用于收入外推"),
    ("资本性支出占收入比", A["cxr"], "锚点", "评估取值：2027 年起 3.5%"),
    ("利息及所得税年递增", A["itg"], "研究假设", "—"),
    ("EBITDA 率（2028 起）", M27, "披露推算", "推导：EBITDA2027 ÷ 收入2027 = 68.65%"),
    ("分派率分母", A["raise"], "锚点", "募集规模口径，与招募书 6.22%/5.60% 一致"),
    ("收入→EBITDA 传导系数", PASS_THROUGH, "研究假设", "1 − 房产税 12%/1.09 − 运营管理费 8.3%/1.039 ≈ 0.81"),
    ("收入→EBITDA 弹性", PASS_THROUGH / M27, "研究假设", "推导：传导系数 0.81 ÷ EBITDA 率 68.65% ≈ 1.18；收入每降 1%，EBITDA 降 1.18%"),
]
r = 5
for k, v, kind, note in items:
    wa.cell(row=r, column=1, value=k).font = Font(size=10)
    c = wa.cell(row=r, column=2, value=v)
    c.font = Font(size=10, bold=True)
    c.number_format = "0.00%" if (isinstance(v, float) and v < 1.5) else "#,##0.00"
    c.fill = YELLOW if kind == "研究假设" else PatternFill(fill_type=None)
    wa.cell(row=r, column=3, value=kind).font = Font(size=9)
    wa.cell(row=r, column=4, value=note).font = Font(size=9)
    for i in range(1, 5):
        wa.cell(row=r, column=i).border = BORDER
        wa.cell(row=r, column=i).alignment = Alignment(wrap_text=True, vertical="center")
    r += 1
wa.column_dimensions["A"].width = 24
wa.column_dimensions["B"].width = 20
wa.column_dimensions["C"].width = 12
wa.column_dimensions["D"].width = 84

# 行号映射（供公式引用）
R = {k: 5 + i for i, k in enumerate([
    "raise", "app", "disc", "years", "rev26", "rev27", "eb26", "eb27",
    "cx26", "cx27", "it26", "it27", "wc26", "wc27", "cashadj27", "g1", "g2", "cxr", "itg", "m", "den", "pt", "lev"])}
H = "'1_假设'!"

# ================= 2 模型 =================
wm = wb.create_sheet("2_模型")
title(wm, "Model｜2026E–2044E 中性到期重定价情景", 11,
      "2026/2027 为披露数据规范化；2028–2044 直接引用 5_到期重定价中的中性情景。"
      "G 为可供分配金额；I/J 仅为指定折现率下的数学折现参考，不代表物业评估值。")
hdr(wm, 4, ["年份", "营业收入", "EBITDA", "EBITDA 率", "资本性支出", "利息及所得税",
            "可供分配", "期数", "折现因子", "现值", "分派率"])
r = 5
for i, row in enumerate(ROWS):
    y = row["year"]
    wm.cell(row=r, column=1, value=y).font = Font(size=9)
    if y == 2026:
        wm.cell(row=r, column=2, value="=%sB%d" % (H, R["rev26"]))
        wm.cell(row=r, column=3, value="=%sB%d" % (H, R["eb26"]))
        wm.cell(row=r, column=5, value="=%sB%d" % (H, R["cx26"]))
        wm.cell(row=r, column=6, value="=%sB%d" % (H, R["it26"]))
    elif y == 2027:
        wm.cell(row=r, column=2, value="=%sB%d" % (H, R["rev27"]))
        wm.cell(row=r, column=3, value="=%sB%d" % (H, R["eb27"]))
        wm.cell(row=r, column=5, value="=%sB%d" % (H, R["cx27"]))
        wm.cell(row=r, column=6, value="=%sB%d" % (H, R["it27"]))
    else:
        # 中性情景在 5_到期重定价 中由统一 Python 引擎生成；这里仅链接，不重复造一套公式。
        scenario_row = 24 + (y - 2026)
        wm.cell(row=r, column=2, value="='5_到期重定价'!C%d" % scenario_row)
        wm.cell(row=r, column=3, value="='5_到期重定价'!D%d" % scenario_row)
        wm.cell(row=r, column=5, value="='5_到期重定价'!E%d" % scenario_row)
        wm.cell(row=r, column=6, value="='5_到期重定价'!F%d" % scenario_row)
    wm.cell(row=r, column=4, value="=C%d/B%d" % (r, r))
    if y == 2026:
        formula = "=C%d-E%d-F%d-%s$B$%d" % (r, r, r, H, R["wc26"])
    elif y == 2027:
        formula = "=C%d-E%d-F%d-%s$B$%d+%s$B$%d" % (r, r, r, H, R["wc27"], H, R["cashadj27"])
    else:
        scenario_row = 24 + (y - 2026)
        formula = "='5_到期重定价'!H%d" % scenario_row
    wm.cell(row=r, column=7, value=formula)
    wm.cell(row=r, column=8, value=i + 1)
    wm.cell(row=r, column=9, value="=1/(1+%s$B$%d)^H%d" % (H, R["disc"], r))
    wm.cell(row=r, column=10, value="=G%d*I%d" % (r, r))
    wm.cell(row=r, column=11, value="=G%d/%s$B$%d" % (r, H, R["den"]))
    for c in range(1, 12):
        cell = wm.cell(row=r, column=c)
        cell.border = BORDER
        cell.font = Font(size=9, bold=(c == 7))
        if c >= 2:
            if c in (4, 11):
                cell.number_format = "0.00%"
            elif c == 9:
                cell.number_format = "0.0000"
            elif c == 8:
                cell.number_format = "0"
            else:
                cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="right")
    if y <= 2027:
        for c in range(1, 12):
            wm.cell(row=r, column=c).fill = SUB
    r += 1
tot = r
wm.cell(row=tot, column=1, value="合计/均值")
wm.cell(row=tot, column=7, value="=SUM(G5:G%d)" % (r - 1))
wm.cell(row=tot, column=10, value="=SUM(J5:J%d)" % (r - 1))
wm.cell(row=tot, column=11, value="=G%d/%s$B$%d/19*1" % (tot, H, R["den"]))
for c in range(1, 12):
    wm.cell(row=tot, column=c).fill = GREY
    wm.cell(row=tot, column=c).font = Font(bold=True, size=10)
    wm.cell(row=tot, column=c).border = BORDER
    if c in (7, 10):
        wm.cell(row=tot, column=c).number_format = "#,##0"
    if c == 11:
        wm.cell(row=tot, column=c).number_format = "0.00%"
wm.cell(row=tot + 2, column=1,
        value="注：2044 年为最后一个完整年度情景；商业土地使用权 2045-03-29 到期。"
              "未建立 2045 年部分年度现金流、续期成本或处置回收模型；期末零终值仅为情景假设。地下车库期限不同，未单独建模。").font = Font(size=9, italic=True, color="C00000")
for i, w in enumerate([10, 18, 16, 11, 16, 16, 16, 7, 11, 16, 10], 1):
    wm.column_dimensions[get_column_letter(i)].width = w

MODEL_FIRST, MODEL_LAST = 5, 5 + A["years"] - 1

# ================= 3 输出 =================
wo = wb.create_sheet("3_输出")
title(wo, "Output｜分派率、IRR、DCF 与终值敏感性", 6,
      "分派率分母为募集规模 2,739,656,060.87 元（与招募书一致）。IRR 为现金流内部收益率，"
      "t=0 流出募集规模，t=1..19 流入各年可供分配，期末无残值。")
r = 4
wo.cell(row=r, column=1, value="表 1　分派率与口径对照").font = Font(bold=True, size=11)
r += 1
hdr(wo, r, ["指标", "2026E", "2027E", "2028E", "说明", ""], 24)
r += 1
rows1 = [
    ("营业收入", A["rev26"], A["rev27"], ROWS[2]["rev"], "2026/27 披露；2028 模型"),
    ("EBITDA", A["eb26"], A["eb27"], ROWS[2]["eb"], "—"),
    ("资本性支出（不含税）", A["cx26"], A["cx27"], ROWS[2]["cx"], "2026 用测算表口径"),
    ("支付利息及所得税", A["it26"], A["it27"], ROWS[2]["it"], "—"),
    ("经营性应收应付变动", A["wc26"], A["wc27"], 0, "2026/27 披露调整项"),
     ("期初现金调节", 0, A["cashadj27"], 0, "2027 披露调整项"),
     ("规范化可供分配", ROWS[0]["dist"], ROWS[1]["dist"], ROWS[2]["dist"], "计算口径：EBITDA − capex − 利息所得税 − WC + 现金调节"),
    ("披露可供分配", 170384048.05, 153304398.41, None, "招募书口径（余额法）"),
    ("分派率（规范化）", ROWS[0]["dist"] / A["raise"], ROWS[1]["dist"] / A["raise"],
     ROWS[2]["dist"] / A["raise"], "分母 = 募集规模"),
    ("分派率（披露）", 170384048.05 / A["raise"], 153304398.41 / A["raise"], None, "招募书：6.22% / 5.60%"),
    ("分派率（/评估值，规范化）", ROWS[0]["dist"] / A["appraisal"], ROWS[1]["dist"] / A["appraisal"],
     ROWS[2]["dist"] / A["appraisal"], "横向比较用"),
    ("单位分派（元/份，10 亿份）", ROWS[0]["dist"] / 1e9, ROWS[1]["dist"] / 1e9, ROWS[2]["dist"] / 1e9, "面值发行"),
]
for name, v26, v27, v28, note in rows1:
    wo.cell(row=r, column=1, value=name).font = Font(size=10, bold=("分派率" in name))
    for i, v in enumerate([v26, v27, v28], 2):
        c = wo.cell(row=r, column=i, value=v)
        if v is None:
            c.value = "—"
            c.alignment = Alignment(horizontal="center")
        else:
            c.number_format = "0.00%" if "分派率" in name else ("0.0000" if "单位" in name else "#,##0")
            c.alignment = Alignment(horizontal="right")
        c.font = Font(size=10)
    wo.cell(row=r, column=5, value=note).font = Font(size=9)
    for i in range(1, 6):
        wo.cell(row=r, column=i).border = BORDER
    r += 1

# --- IRR 现金流块 ---
r += 1
wo.cell(row=r, column=1, value="表 2　IRR 现金流（t=0 流出募集规模，t=1..19 流入分派）").font = Font(bold=True, size=11)
r += 1
hdr(wo, r, ["期数", "年份", "现金流（元）", "折现因子@5%", "现值@5%", "备注"], 22)
cf_hdr = r
r += 1
cf_first = r
wo.cell(row=r, column=1, value=0)
wo.cell(row=r, column=2, value="2026 认购")
wo.cell(row=r, column=3, value="=-%s$B$%d" % (H, R["raise"]))
wo.cell(row=r, column=4, value=1)
wo.cell(row=r, column=5, value="=C%d*D%d" % (r, r))
wo.cell(row=r, column=6, value="t=0").font = Font(size=9)
for i in range(1, 7):
    wo.cell(row=r, column=i).border = BORDER
    wo.cell(row=r, column=i).font = Font(size=9)
wo.cell(row=r, column=3).number_format = "#,##0"
r += 1
for i, row in enumerate(ROWS):
    wo.cell(row=r, column=1, value=i + 1)
    wo.cell(row=r, column=2, value=row["year"])
    wo.cell(row=r, column=3, value="='2_模型'!G%d" % (MODEL_FIRST + i))
    wo.cell(row=r, column=4, value="=1/(1+%s$B$%d)^A%d" % (H, R["disc"], r))
    wo.cell(row=r, column=5, value="=C%d*D%d" % (r, r))
    for i2 in range(1, 7):
        wo.cell(row=r, column=i2).border = BORDER
        wo.cell(row=r, column=i2).font = Font(size=9)
    wo.cell(row=r, column=3).number_format = "#,##0"
    wo.cell(row=r, column=4).number_format = "0.0000"
    wo.cell(row=r, column=5).number_format = "#,##0"
    r += 1
cf_last = r - 1

r += 1
irr_row = r
wo.cell(row=r, column=1, value="IRR（持有到期、无终值）").font = Font(bold=True, size=11, color="C00000")
c = wo.cell(row=r, column=3, value="=IRR(C%d:C%d)" % (cf_first, cf_last))
c.number_format = "0.00%"
c.font = Font(bold=True, size=12, color="C00000")
wo.cell(row=r, column=5,
        value="vs 2027E 分派率 5.60%%，差 %.2f pct" % ((IRR0 - 0.056) * 100)).font = Font(size=9, italic=True)
r += 1
wo.cell(row=r, column=1, value="19 年累计分派").font = Font(size=10)
wo.cell(row=r, column=3, value="=SUM(C%d:C%d)" % (cf_first + 1, cf_last)).number_format = "#,##0"
r += 1
wo.cell(row=r, column=1, value="累计分派 ÷ 募集规模").font = Font(size=10)
wo.cell(row=r, column=3, value="=C%d/%s$B$%d" % (r - 1, H, R["raise"])).number_format = "0.0%"

# --- 终值敏感性 ---
r += 2
wo.cell(row=r, column=1, value="表 3　终值—IRR 对照（2044 年末残值假设）").font = Font(bold=True, size=11)
r += 1
hdr(wo, r, ["2044 年末终值（亿元）", "占评估值", "IRR", "判断", "", ""], 22)
r += 1
for tv in [0, 5e8, 1e9, 1.5e9, 1.65e9, 1.75e9, 2e9, A["appraisal"]]:
    val = irr(ROWS, None, tv)
    wo.cell(row=r, column=1, value=tv / 1e8).number_format = "0.00"
    wo.cell(row=r, column=2, value=tv / A["appraisal"]).number_format = "0.0%"
    c = wo.cell(row=r, column=3, value=val)
    c.number_format = "0.00%"
    c.font = Font(bold=True, size=10)
    tag = "评估假设（无残值）" if tv == 0 else ("≈ 使 IRR 达 5.60%%" % () if abs(tv - TV_FOR_560) < 3e8 else "")
    wo.cell(row=r, column=4, value=tag).font = Font(size=9, italic=True)
    fill = RED if val < 0.04 else (AMBER if val < 0.056 else GREEN)
    c.fill = fill
    for i in range(1, 5):
        wo.cell(row=r, column=i).border = BORDER
    r += 1
wo.cell(row=r, column=1,
        value="读法：按本模型 2026–2044 年度期数、期末零终值假设，IRR 约 2.66%%；不代表法律确定的到期残值。"
              "要使 IRR 达到 5.60%%，需 2044 年末约 %.1f 亿元终值（占评估值 %.0f%%；现值缺口 %.2f 亿元）。"
              % (TV_FOR_560 / 1e8, TV_FOR_560 / A["appraisal"] * 100, TV_GAP_560 / 1e8)).font = Font(size=9, italic=True, color="C00000")
wo.merge_cells(start_row=r, start_column=1, end_row=r + 1, end_column=6)
wo.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")

# --- 基金层可供分配现金流折现参考（不代表物业估值） ---
r += 3
wo.cell(row=r, column=1, value="表 4　中性情景可供分配现金流折现参考（非物业估值）").font = Font(bold=True, size=11)
r += 1
hdr(wo, r, ["折现率", "可供分配现金流现值", "相对 5% 现值", "说明", "", ""], 22)
r += 1
for d in [0.045, 0.050, 0.055, 0.060]:
    b = pv(ROWS, d)
    wo.cell(row=r, column=1, value=d).number_format = "0.0%"
    wo.cell(row=r, column=2, value=b).number_format = "#,##0"
    wo.cell(row=r, column=3, value=b / PV5).number_format = "0.0%"
    wo.cell(row=r, column=4, value="折现参考；折现率须与投资者要求回报匹配").font = Font(size=9)
    for i in range(1, 5):
        wo.cell(row=r, column=i).border = BORDER
    r += 1
wo.cell(row=r, column=1,
        value="重要：此表只是对基金层可供分配现金流作数学折现敏感性展示，不是物业 NOI 估值、NAV 或合理市值。"
              "未取得原始资产评估报告并完成物业层 NOI 定义及现金流桥接前，不得用 EBITDA 折现复现评估值。").font = Font(size=9, italic=True, color="C00000")
wo.merge_cells(start_row=r, start_column=1, end_row=r + 1, end_column=6)
wo.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
for i, w in enumerate([26, 20, 22, 14, 26, 26], 1):
    wo.column_dimensions[get_column_letter(i)].width = w

# ================= 4 敏感性 =================
ws = wb.create_sheet("4_敏感性")
title(ws, "Sensitivity｜双因素敏感性（2028E 分派率）", 8,
      "方法：收入乘数 m =（1+出租率变动）×（1+租金变动）；EBITDA = EBITDA2028 × [1+弹性×(m−1)]，弹性约 1.18；"
      "capex = capex2028 × m；利息所得税不变。弹性 = 传导系数 0.81 ÷ EBITDA 率 68.65%（1_假设 最后一行）。"
      "所有单元格为公式，改 1_假设 即联动。")
base_eb = "='5_到期重定价'!D26"
base_cx = "='5_到期重定价'!E26"
base_it = "='5_到期重定价'!F26"
neutral_2028 = bottomup.build("中性")[2]

# 辅助区（放在右下，避免遮挡）
ws.cell(row=4, column=10, value="辅助：2028E 基数").font = Font(bold=True, size=9)
ws.cell(row=5, column=10, value="EBITDA2028")
ws.cell(row=5, column=11, value=base_eb).number_format = "#,##0"
ws.cell(row=6, column=10, value="capex2028")
ws.cell(row=6, column=11, value=base_cx).number_format = "#,##0"
ws.cell(row=7, column=10, value="利息所得税2028")
ws.cell(row=7, column=11, value=base_it).number_format = "#,##0"
for rr in (5, 6, 7):
    ws.cell(row=rr, column=10).font = Font(size=9)
    ws.cell(row=rr, column=11).font = Font(size=9)

ws.cell(row=4, column=1, value="表 1　2028E 分派率：出租率变动 × 租金变动").font = Font(bold=True, size=11)
hdr(ws, 5, ["出租率＼租金", "-10%", "-5%", "0%", "+5%", "+10%", ""], 20)
rents = [-0.10, -0.05, 0.0, 0.05, 0.10]
occs = [-3.0, -1.5, 0.0, 1.5, 3.0]
r = 6
for od in occs:
    ws.cell(row=r, column=1, value="%+.1f pct" % od).font = Font(size=10)
    for j, rd in enumerate(rents):
        m = "(1+%s/100)*(1+%s)" % (od, rd)
        f = ("=($K$5*(1+%s$B$%d*(%s-1))-$K$6*%s-$K$7)/%s$B$%d"
             % (H, R["lev"], m, m, H, R["den"]))
        c = ws.cell(row=r, column=j + 2, value=f)
        c.number_format = "0.00%"
        c.font = Font(size=10)
        c.alignment = Alignment(horizontal="center")
        c.border = BORDER
        v = neutral_2028["dist"] / A["raise"]
        mm = (1 + od / 100) * (1 + rd)
        calc = (neutral_2028["ebitda"] * (1 + PASS_THROUGH / M27 * (mm - 1)) - neutral_2028["capex"] * mm - neutral_2028["intax"]) / A["raise"]
        c.fill = GREEN if calc >= 0.060 else (RED if calc < 0.052 else AMBER)
    ws.cell(row=r, column=1).border = BORDER
    r += 1
ws.cell(row=r + 1, column=1,
        value="读法：绿色 ≥6.00%；黄色 5.20%–6.00%；红色 <5.20%。基准情形使用 2028 年中性到期重定价情景的 EBITDA、capex 与利息所得税，不使用评估增长基准。").font = Font(size=9, italic=True)

# 表 2 折现率 × 增长率（模型估值，亿元）
r += 3
ws.cell(row=r, column=1, value="表 2　情景现金流现值敏感性：折现率 × 2029 年后收入增长率（亿元）").font = Font(bold=True, size=11)
r += 1
hdr(ws, r, ["折现率＼收入增长", "-1.0%", "0.0%", "1.0%", "2.25%", ""], 20)
for d in [0.040, 0.045, 0.050, 0.055, 0.060]:
    r += 1
    ws.cell(row=r, column=1, value="%.1f%%" % (d * 100)).font = Font(size=10)
    for j, g in enumerate([-0.010, 0.0, 0.010, 0.0225]):
        val = pv(series(long_g=g), d) / 1e8
        c = ws.cell(row=r, column=j + 2, value=round(val, 2))
        c.number_format = "0.00"
        c.font = Font(size=10)
        c.alignment = Alignment(horizontal="center")
        c.border = BORDER
        c.fill = GREY
    ws.cell(row=r, column=1).border = BORDER
r += 2
ws.cell(row=r, column=1,
        value="以上仅为中性租约到期情景下的现金流折现敏感性；2029 年后增长率是研究情景输入，不是评估报告已披露的收入增长率。"
              "结果不代表物业评估值、基金 NAV 或市场合理价值。").font = Font(size=9, italic=True)
for i, w in enumerate([20, 14, 14, 14, 14, 16, 4, 4, 4, 22, 18], 1):
    ws.column_dimensions[get_column_letter(i)].width = w


# ================= 5 到期重定价情景（来自 build_bottomup.py） =================
ws5 = wb.create_sheet("5_到期重定价")
title(ws5, "Maturity repricing scenarios｜2028 年租约到期重定价", 10,
      "本表直接读取 tools/build_bottomup.py 的悲观/中性/乐观三情景。2026–2027 为披露数据规范化，2028 起为研究情景；不得将情景当作管理人预测。")
hdr(ws5, 4, ["情景", "年份", "营业收入", "EBITDA", "资本性支出", "利息及所得税", "营运资金变动", "可供分配", "分派率", "数据性质"])
scenario_rows = {}
rr = 5
for scenario_name in ("悲观", "中性", "乐观"):
    scenario_rows[scenario_name] = []
    for item in bottomup.build(scenario_name):
        vals = [scenario_name, item["year"], item["rev"], item["ebitda"],
                item["capex"], item["intax"], item["wc"], item["dist"], item["rate"], item["src"]]
        for cc, value in enumerate(vals, 1):
            cell = ws5.cell(row=rr, column=cc, value=value)
            cell.border = BORDER
            cell.font = Font(size=9)
            if cc in (3, 4, 5, 6, 7, 8):
                cell.number_format = "#,##0"
            elif cc == 9:
                cell.number_format = "0.00%"
        scenario_rows[scenario_name].append(rr)
        rr += 1
for cc, width in enumerate([14, 10, 18, 18, 18, 18, 16, 18, 12, 24], 1):
    ws5.column_dimensions[get_column_letter(cc)].width = width
ws5.freeze_panes = "A5"
ws5.auto_filter.ref = "A4:J%d" % (rr - 1)

# ================= 6 情景回报（Excel IRR） =================
ws6 = wb.create_sheet("6_情景回报")
title(ws6, "Scenario returns｜三情景发行价年度期数 IRR", 7,
      "t=0 为募集规模流出，2026–2044 每年可供分配为流入，期末无终值。此为年度期数 IRR，不是实际支付日期 XIRR。")
hdr(ws6, 4, ["情景", "年度期数 IRR（90%分配）", "年度期数 IRR（100%分配）", "19 年累计可供分配", "2028 可供分配", "2028 分派率", "口径说明"])
cashflow_start = 12
for idx, scenario_name in enumerate(("悲观", "中性", "乐观")):
    data_rows = scenario_rows[scenario_name]
    summary_row = 5 + idx
    cf_row_100 = cashflow_start + idx * 2
    cf_row_90 = cf_row_100 + 1
    ws6.cell(row=summary_row, column=1, value=scenario_name)
    ws6.cell(row=summary_row, column=2, value="=IRR(B%d:U%d)" % (cf_row_90, cf_row_90))
    ws6.cell(row=summary_row, column=3, value="=IRR(B%d:U%d)" % (cf_row_100, cf_row_100))
    ws6.cell(row=summary_row, column=2).number_format = "0.00%"
    ws6.cell(row=summary_row, column=3).number_format = "0.00%"
    ws6.cell(row=summary_row, column=4, value="=SUM(C%d:U%d)" % (cf_row_100, cf_row_100))
    ws6.cell(row=summary_row, column=4).number_format = "#,##0"
    ws6.cell(row=summary_row, column=5, value="='5_到期重定价'!H%d" % data_rows[2])
    ws6.cell(row=summary_row, column=5).number_format = "#,##0"
    ws6.cell(row=summary_row, column=6, value="='5_到期重定价'!I%d" % data_rows[2])
    ws6.cell(row=summary_row, column=6).number_format = "0.00%"
    ws6.cell(row=summary_row, column=7, value="90%–100% 分配情景；不代表实际分派")
    for cc in range(1, 8):
        ws6.cell(row=summary_row, column=cc).border = BORDER
    for cf_row, ratio, label in ((cf_row_100, 1.0, "100%"), (cf_row_90, 0.9, "90%")):
        ws6.cell(row=cf_row, column=1, value="%s-%s" % (scenario_name, label))
        ws6.cell(row=cf_row, column=2, value=-A["raise"])
        for j, data_row in enumerate(data_rows):
            ws6.cell(row=cf_row, column=3 + j,
                     value="='5_到期重定价'!H%d*%.1f" % (data_row, ratio))
            ws6.cell(row=cf_row, column=3 + j).number_format = "#,##0"
        for cc in range(1, 22):
            ws6.cell(row=cf_row, column=cc).border = BORDER
ws6.cell(row=10, column=1, value="现金流复算区：每个情景分别列示 100% 与 90% 可供分配金额流入")
for cc, width in enumerate([14, 16, 16, 18, 18, 14, 40], 1):
    ws6.column_dimensions[get_column_letter(cc)].width = width
ws6.column_dimensions["G"].width = 16
ws6.freeze_panes = "A5"

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb.save(OUT)
    print("saved", OUT)
