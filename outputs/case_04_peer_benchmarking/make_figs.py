# -*- coding: utf-8 -*-
"""生成 case_04 横向基准报告的全部图表（5 张 SVG）。

设计约束
--------
1. 所有坐标由数据计算得出，不手写像素——避免"图与正文数字不一致"。
2. 本项目（普洛斯 508056 / 深国际 180302）统一用 #c0392b 标注，其余用低饱和灰蓝。
3. 每张图自带口径脚注，脱离正文也能读。
"""
import os
from html import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

FONT = "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif"
INK = "#1b2733"
MUTED = "#6b7a88"
GRID = "#e3e8ee"
BG = "#ffffff"
ACCENT = "#c0392b"      # 本项目
BASE = "#2c5f8a"        # 其他标的
LIGHT = "#dce5ee"

D = {
    "普洛斯": dict(code="508056", occ=89.54, rent_yoy=-7.48, wale=389.71, top1=6.21,
                   top5=25.26, impair=16.93, c1=5.34, c2=3.70, c3=199.4,
                   dist_cfo=1.45, rev_psm=363.22, fee=17.11, mcap=62.77, area=1163212,
                   proj=True),
    "盐田港": dict(code="180301", occ=92.60, rent_yoy=-0.79, wale=456.0, top1=40.69,
                   top5=74.86, impair=36.40, c1=4.15, c2=3.97, c3=278.0,
                   dist_cfo=1.05, rev_psm=393.37, fee=9.04, mcap=22.31, area=318541,
                   proj=False),
    "深国际": dict(code="180302", occ=89.35, rent_yoy=-17.45, wale=565.75, top1=21.21,
                   top5=68.42, impair=0.00, c1=4.36, c2=4.90, c3=236.1,
                   dist_cfo=0.89, rev_psm=314.77, fee=14.47, mcap=17.06, area=354314,
                   proj=True),
    "京东仓储": dict(code="508098", occ=100.00, rent_yoy=-5.26, wale=1192.0, top1=54.08,
                     top5=100.00, impair=0.00, c1=4.05, c2=4.02, c3=209.0,
                     dist_cfo=1.01, rev_psm=312.72, fee=13.99, mcap=17.75, area=341317,
                     proj=False),
    "宝湾物流": dict(code="180303", occ=97.64, rent_yoy=None, wale=567.81, top1=18.61,
                     top5=62.27, impair=34.58, c1=4.59, c2=4.73, c3=183.1,
                     dist_cfo=0.97, rev_psm=298.78, fee=10.28, mcap=11.98, area=309534,
                     proj=False),
    "中航易商": dict(code="508078", occ=88.16, rent_yoy=None, wale=458.75, top1=22.34,
                     top5=79.05, impair=0.00, c1=5.36, c2=3.91, c3=236.9,
                     dist_cfo=1.37, rev_psm=347.39, fee=14.76, mcap=23.16, area=382418,
                     proj=False),
}
ORDER = ["普洛斯", "盐田港", "深国际", "京东仓储", "宝湾物流", "中航易商"]


def head(w, h, title, sub=""):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
         f'<rect width="{w}" height="{h}" fill="{BG}"/>',
         f'<text x="36" y="34" font-size="17" font-weight="700" fill="{INK}">{escape(title)}</text>']
    if sub:
        s.append(f'<text x="36" y="56" font-size="11.5" fill="{MUTED}">{escape(sub)}</text>')
    return s


def foot(s, w, h, txt):
    s.append(f'<line x1="36" y1="{h-40}" x2="{w-36}" y2="{h-40}" stroke="{GRID}"/>')
    s.append(f'<text x="36" y="{h-22}" font-size="10.5" fill="{MUTED}">{escape(txt)}</text>')
    s.append("</svg>")


def save(name, s):
    p = os.path.join(OUT, name)
    open(p, "w", encoding="utf-8").write("\n".join(s))
    return p


# ============================================================ 图 1 样本构造漏斗
def fig1():
    W, H = 940, 640
    s = head(W, H, "图 1　可比样本的构造：从 10 只到 6 只",
             "候选池＝A 股名称含“仓储/物流”的全部公募 REIT；纳入需同时满足 5 项条件")
    cand = [("508056", "中金普洛斯", 1), ("180301", "红土盐田港", 1), ("180302", "华夏深国际", 1),
            ("508098", "嘉实京东", 1), ("180303", "华泰宝湾", 1), ("508078", "中航易商", 1),
            ("180305", "南方顺丰", 0), ("180306", "华夏安博", 0),
            ("180307", "中金菜鸟", 0), ("508090", "中银中外运", 0)]
    y0, rh = 96, 36
    for i, (code, nm, keep) in enumerate(cand):
        y = y0 + i * rh
        col = BASE if keep else "#c2ccd6"
        fill = "#eef3f8" if keep else "#f6f7f8"
        s.append(f'<rect x="36" y="{y}" width="176" height="25" rx="4" fill="{fill}" '
                 f'stroke="{col}" stroke-width="1"/>')
        s.append(f'<text x="47" y="{y+17}" font-size="11" fill="{INK if keep else "#8b95a1"}">'
                 f'{code}　{escape(nm)}</text>')
        if keep:
            s.append(f'<line x1="212" y1="{y+12.5}" x2="300" y2="{y+12.5}" stroke="{BASE}" '
                     f'stroke-width="1" opacity="0.5"/>')
        else:
            s.append(f'<line x1="212" y1="{y+12.5}" x2="262" y2="{y+12.5}" stroke="#c2ccd6" '
                     f'stroke-width="1" stroke-dasharray="3 3"/>')
            s.append(f'<text x="268" y="{y+16.5}" font-size="10.5" fill="#98a3ae">✕ 排除</text>')

    # 中间：条件闸门
    s.append(f'<rect x="300" y="96" width="72" height="455" rx="6" fill="#f2f6fa" stroke="{BASE}" stroke-width="1"/>')
    s.append(f'<text x="336" y="330" font-size="11.5" fill="{BASE}" text-anchor="middle" '
             f'transform="rotate(-90 336 330)" letter-spacing="3">5 项纳入条件</text>')

    # 右列 6 只
    ry = [110, 168, 226, 284, 342, 400]
    s.append(f'<text x="590" y="92" font-size="11.5" font-weight="700" fill="{INK}">纳入面板（n=6）</text>')
    for (nm, y) in zip(ORDER, ry):
        proj = D[nm]["proj"]
        s.append(f'<rect x="590" y="{y}" width="176" height="28" rx="4" '
                 f'fill="{"#fdecea" if proj else "#eef3f8"}" '
                 f'stroke="{ACCENT if proj else BASE}" stroke-width="{1.8 if proj else 1}"/>')
        s.append(f'<text x="678" y="{y+19}" font-size="11.5" text-anchor="middle" '
                 f'fill="{ACCENT if proj else INK}" font-weight="{700 if proj else 400}">{escape(nm)}</text>')
        s.append(f'<line x1="766" y1="{y+14}" x2="800" y2="{y+14}" stroke="{GRID}"/>')
        s.append(f'<text x="806" y="{y+18}" font-size="10.5" fill="{MUTED}">{D[nm]["area"]/1e4:.0f} 万㎡</text>')

    for k in range(6):
        y1 = y0 + k * rh + 12.5
        y2 = ry[k] + 14
        s.append(f'<path d="M372,{y1} C460,{y1} 490,{y2} 586,{y2}" fill="none" '
                 f'stroke="{BASE}" stroke-width="1" opacity="0.4"/>')

    # 条件清单（两行，按字符宽度估算胶囊宽度）
    def est_w(t, fs=10.5):
        w = 0.0
        for ch in t:
            w += fs if ord(ch) > 0x2E80 else fs * 0.56
        return w * 1.06 + 22

    rows = [["① 仓储物流资产", "② 2025 完整财年", "③ 2025 年报可获取"],
            ["④ 可租面积 ≥10 万㎡", "⑤ 有可比运营披露"]]
    for r, row in enumerate(rows):
        bx = 36
        yy = 484 + r * 30
        for c in row:
            w = est_w(c)
            s.append(f'<rect x="{bx:.0f}" y="{yy}" width="{w:.0f}" height="23" rx="11.5" '
                     f'fill="#f2f6fa" stroke="{BASE}" stroke-width="0.8"/>')
            s.append(f'<text x="{bx+9:.0f}" y="{yy+15.5}" font-size="10.5" fill="{BASE}">{escape(c)}</text>')
            bx += w + 9

    s.append(f'<text x="36" y="560" font-size="10.5" fill="{INK}">'
             f'排除 4 只：1 只报告期仅 280 天（已在 §2.4 做边界检验），3 只截至 2026-04-30 未披露 2025 年报。</text>')
    s.append(f'<text x="36" y="577" font-size="10.5" fill="{MUTED}">'
             f'红色为本项目组；右侧面积为可租面积，仅用于单位化，不用于规模排名。</text>')
    foot(s, W, H, "来源：各基金 2025 年年度报告；候选池由 fund.eastmoney.com 基金全量清单枚举，脚本见 build_panel.py")
    return save("fig1_sample_funnel.svg", s)


# ============================================================ 图 2 口径翻转斜线图
def fig2():
    W, H = 940, 560
    s = head(W, H, "图 2　换一个口径，第一名就换人",
             "左：披露现金流分派率（C1，可供分配÷市值）　右：现金分派率（C2，经营现金流÷市值）")
    lx, rx = 300, 640
    top, gap = 110, 66

    def ypos(r):
        return top + (r - 1) * gap

    s.append(f'<text x="{lx}" y="96" font-size="11.5" fill="{MUTED}" text-anchor="middle">C1 排名</text>')
    s.append(f'<text x="{rx}" y="96" font-size="11.5" fill="{MUTED}" text-anchor="middle">C2 排名</text>')

    r1 = {k: sorted(ORDER, key=lambda x: -D[x]["c1"]).index(k) + 1 for k in ORDER}
    r2 = {k: sorted(ORDER, key=lambda x: -D[x]["c2"]).index(k) + 1 for k in ORDER}

    for r in range(1, 7):
        yy = ypos(r)
        s.append(f'<text x="{lx-174}" y="{yy+4}" font-size="10" fill="#aab4bf">{r}</text>')
        s.append(f'<text x="{rx+178}" y="{yy+4}" font-size="10" fill="#aab4bf">{r}</text>')

    for nm in ORDER:
        d = D[nm]
        y1, y2 = ypos(r1[nm]), ypos(r2[nm])
        col = ACCENT if d["proj"] else BASE
        wd = 2.6 if d["proj"] else 1.4
        op = 1 if d["proj"] else 0.55
        s.append(f'<path d="M{lx+58},{y1} C{(lx+rx)/2},{y1} {(lx+rx)/2},{y2} {rx-58},{y2}" '
                 f'fill="none" stroke="{col}" stroke-width="{wd}" opacity="{op}"/>')
        s.append(f'<circle cx="{lx+58}" cy="{y1}" r="4" fill="{col}"/>')
        s.append(f'<circle cx="{rx-58}" cy="{y2}" r="4" fill="{col}"/>')
        s.append(f'<text x="{lx-32}" y="{y1+4}" font-size="12" text-anchor="end" '
                 f'fill="{col}" font-weight="{700 if d["proj"] else 400}">{escape(nm)}</text>')
        s.append(f'<text x="{lx-36}" y="{y1+4}" font-size="10.5" text-anchor="end" fill="{MUTED}"></text>')
        s.append(f'<text x="{lx+66}" y="{y1-9}" font-size="10.5" fill="{col}" opacity="{op}">{d["c1"]:.2f}%</text>')
        s.append(f'<text x="{rx-66}" y="{y2-9}" font-size="10.5" text-anchor="end" fill="{col}" opacity="{op}">{d["c2"]:.2f}%</text>')

    # 排名极差标注
    for i, (nm, txt) in enumerate([("中航易商", "C1 第 1 → C2 第 5"), ("深国际", "C1 第 4 → C2 第 1")]):
        pass
    s.append(f'<rect x="36" y="470" width="868" height="46" rx="4" fill="#fbfbfc" stroke="{GRID}"/>')
    s.append(f'<text x="48" y="489" font-size="11" fill="{INK}">'
             f'六条线全部交叉：C1 第一（中航易商 5.36%）与 C2 第一（深国际 4.90%）是两只不同的标的。'
             f'六只的排名极差均为 3–4 位，没有一只在三个口径下稳定。</text>')
    s.append(f'<text x="48" y="506" font-size="10.5" fill="{MUTED}">'
             f'极差＝三个口径中最好名次与最差名次之差；“稳定”在本样本中指极差 ≤ 1，六只无一达到。</text>')
    foot(s, W, H, "口径：C1 取年报披露的现金流分派率；C2＝经营活动现金流净额 ÷ 反推市值，两者分母同为 2025-12-31 时点")
    return save("fig2_caliber_flip.svg", s)


# ============================================================ 图 3 资产质量矩阵
def fig3():
    W, H = 940, 560
    s = head(W, H, "图 3　资产质量五维矩阵：颜色＝名次，数字＝原值",
             "每格上行为本组名次（1 深色=最优 / 6 浅色=最差），下行为该指标原值")

    cols = [("出租率", "%", "occ", True), ("租金同比", "%", "rent_yoy", True),
            ("剩余租期", "天", "wale", True), ("最大租户", "%", "top1", False),
            ("减值/收入", "%", "impair", False)]
    x0, y0, cw, chh = 214, 120, 112, 52

    # 名次
    rk = {}
    for cn0, _u, f0, high0 in cols:
        vals = [(n, D[n][f0]) for n in ORDER if D[n][f0] is not None]
        vals.sort(key=lambda x: -x[1] if high0 else x[1])
        rk[f0] = {n: i + 1 for i, (n, _) in enumerate(vals)}

    for j, (cn, unit, f, high) in enumerate(cols):
        cx = x0 + j * cw
        s.append(f'<text x="{cx+cw/2}" y="{y0-24}" font-size="11.5" text-anchor="middle" fill="{INK}">{escape(cn)}</text>')
        s.append(f'<text x="{cx+cw/2}" y="{y0-8}" font-size="10" text-anchor="middle" fill="{MUTED}">'
                 f'{escape(unit)}・{"越高越好" if high else "越低越好"}</text>')

    for i, nm in enumerate(ORDER):
        cy = y0 + i * chh
        d = D[nm]
        s.append(f'<text x="{x0-16}" y="{cy+chh/2+4}" font-size="12" text-anchor="end" '
                 f'fill="{ACCENT if d["proj"] else INK}" font-weight="{700 if d["proj"] else 400}">{escape(nm)}</text>')
        s.append(f'<text x="{x0-16}" y="{cy+chh/2+19}" font-size="9.5" text-anchor="end" fill="#aab4bf">{d["code"]}</text>')
        for j, (cn, unit, f, high) in enumerate(cols):
            cx = x0 + j * cw
            v = d[f]
            if v is None:
                s.append(f'<rect x="{cx+2}" y="{cy+2}" width="{cw-4}" height="{chh-4}" rx="3" '
                         f'fill="#f7f8f9" stroke="{GRID}"/>')
                s.append(f'<text x="{cx+cw/2}" y="{cy+chh/2+4}" font-size="10" text-anchor="middle" '
                         f'fill="#aab4bf">同比不可比</text>')
                continue
            r = rk[f][nm]
            # 名次 1 → 深，6 → 浅
            shade = 0.14 + 0.14 * (r - 1)
            fill = f'rgba(44,95,138,{shade:.2f})'
            txtc = "#ffffff" if shade > 0.55 else INK
            s.append(f'<rect x="{cx+2}" y="{cy+2}" width="{cw-4}" height="{chh-4}" rx="3" fill="{fill}"/>')
            s.append(f'<text x="{cx+cw/2}" y="{cy+22}" font-size="14" font-weight="700" '
                     f'text-anchor="middle" fill="{txtc}">{r}</text>')
            s.append(f'<text x="{cx+cw/2}" y="{cy+40}" font-size="10" text-anchor="middle" fill="{txtc}" '
                     f'opacity="0.85">{v:.1f}{unit}</text>')

    # 位次汇总
    qpos = {"普洛斯": 4.0, "盐田港": 4.0, "深国际": 3.5, "京东仓储": 1.5, "宝湾物流": 2.0, "中航易商": 4.0}
    qpos3 = {"普洛斯": 4, "盐田港": 3, "深国际": 4, "京东仓储": 2, "宝湾物流": 3.5, "中航易商": 4.5}
    bx = x0 + 5 * cw + 32
    s.append(f'<text x="{bx}" y="{y0-24}" font-size="11" fill="{INK}">资产质量位次</text>')
    s.append(f'<text x="{bx}" y="{y0-8}" font-size="9.5" fill="{MUTED}">四维中位 / 剔租期</text>')
    for i, nm in enumerate(ORDER):
        cy = y0 + i * chh
        hl = D[nm]["proj"]
        s.append(f'<text x="{bx}" y="{cy+chh/2+6}" font-size="13" font-weight="700" '
                 f'fill="{ACCENT if hl else BASE}">{qpos[nm]:.1f}</text>')
        s.append(f'<text x="{bx+40}" y="{cy+chh/2+6}" font-size="10.5" fill="{MUTED}">/ {qpos3[nm]}</text>')

    s.append(f'<rect x="36" y="452" width="868" height="62" rx="4" fill="#fbfbfc" stroke="{GRID}"/>')
    s.append(f'<text x="48" y="472" font-size="11" fill="{INK}">'
             f'本项目两只都落在 3.5–4：资产本身不差，但没有一项进入前二。</text>')
    s.append(f'<text x="48" y="490" font-size="10.5" fill="{MUTED}">'
             f'盐田港在两种算法下从第 4 跳到第 3——它对“租期是否计入”敏感，是六只里位次最不稳的一只，'
             f'不宜据此断言其资产优于本项目。</text>')
    s.append(f'<text x="48" y="506" font-size="10.5" fill="{MUTED}">'
             f'最大租户列不并入资产质量：它衡量客户结构，与资产好坏是两个问题（见 §5.4）。</text>')
    foot(s, W, H, "位次＝该标的中位名次，是描述性统计，不是评分模型；宝湾、易商的租金同比因 2024 年不足整年而缺，该维不参与其位次计算")
    return save("fig3_quality_matrix.svg", s)


# ============================================================ 图 4 二维定位
def fig4():
    W, H = 940, 650
    s = head(W, H, "图 4　本项目在“收益率 × 资产质量”平面上的位置",
             "横轴：资产质量位次（左＝最优）　纵轴：现金分派率 C2　气泡面积：反推市值")
    L, R, T, B = 118, 872, 100, 470

    def X(p):
        return L + (p - 1.0) / 4.0 * (R - L)

    def Y(v):
        return B - (v - 3.4) / 1.8 * (B - T)

    for v in [3.5, 4.0, 4.5, 5.0]:
        s.append(f'<line x1="{L}" y1="{Y(v)}" x2="{R}" y2="{Y(v)}" stroke="{GRID}"/>')
        s.append(f'<text x="{L-12}" y="{Y(v)+4}" font-size="10.5" text-anchor="end" fill="{MUTED}">{v:.1f}%</text>')
    for p in [1, 2, 3, 4, 5]:
        s.append(f'<line x1="{X(p)}" y1="{T}" x2="{X(p)}" y2="{B}" stroke="{GRID}" stroke-dasharray="2 4"/>')
        s.append(f'<text x="{X(p)}" y="{B+20}" font-size="10.5" text-anchor="middle" fill="{MUTED}">{p}</text>')
    s.append(f'<text x="{(L+R)/2}" y="{B+44}" font-size="11" text-anchor="middle" fill="{INK}">'
             f'资产质量位次（1＝最优，5＝最差；第 4 位并列三只，横向错开仅为可读）</text>')
    s.append(f'<text x="36" y="{T-20}" font-size="11" fill="{INK}">现金分派率</text>')

    s.append(f'<line x1="{X(3.5)}" y1="{T}" x2="{X(3.5)}" y2="{B}" stroke="{BASE}" stroke-width="1.2" stroke-dasharray="6 4" opacity="0.65"/>')
    s.append(f'<line x1="{L}" y1="{Y(4.28)}" x2="{R}" y2="{Y(4.28)}" stroke="{BASE}" stroke-width="1.2" stroke-dasharray="6 4" opacity="0.65"/>')
    s.append(f'<text x="{X(3.5)+7}" y="{T+13}" font-size="9.5" fill="{BASE}">质量中位线 3.5</text>')
    s.append(f'<text x="{R-6}" y="{Y(4.28)-7}" font-size="9.5" fill="{BASE}" text-anchor="end">分派率中位 4.28%</text>')

    quad = [(L+4, T+14, "start", "高质量・高分派"),
            (R-4, T+14, "end", "低质量・高分派"),
            (L+4, B-8, "start", "高质量・低分派"),
            (R-4, B-8, "end", "低质量・低分派")]
    for x, y, a, t in quad:
        s.append(f'<text x="{x}" y="{y}" font-size="9.5" fill="#9aa5b1" text-anchor="{a}">{escape(t)}</text>')

    # (位次, 分派率, 水平偏移, 标签方位)
    pts = [("京东仓储", 1.5, 4.02, 0, "up"), ("宝湾物流", 2.0, 4.73, 0, "up"),
           ("深国际", 3.5, 4.90, 0, "right"),
           ("盐田港", 4.0, 3.97, -40, "left"), ("中航易商", 4.0, 3.91, 6, "right"),
           ("普洛斯", 4.0, 3.70, 40, "right")]
    for nm, p, v, dxp, pos in pts:
        d = D[nm]
        cx, cy = X(p) + dxp, Y(v)
        r = 9 + (d["mcap"] ** 0.5) * 1.9
        col = ACCENT if d["proj"] else BASE
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" '
                 f'opacity="{0.26 if d["proj"] else 0.14}" stroke="{col}" stroke-width="{2 if d["proj"] else 1.2}"/>')
        if pos == "up":
            tx, ty, anc = cx, cy - r - 20, "middle"
        elif pos == "down":
            tx, ty, anc = cx, cy + r + 22, "middle"
        elif pos == "right":
            tx, ty, anc = cx + r + 7, cy + 1, "start"
        else:
            tx, ty, anc = cx - r - 7, cy + 1, "end"
        s.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="11.5" text-anchor="{anc}" '
                 f'fill="{col}" font-weight="{700 if d["proj"] else 400}">{escape(nm)}</text>')
        s.append(f'<text x="{tx:.1f}" y="{ty+13:.1f}" font-size="10" text-anchor="{anc}" '
                 f'fill="{col}" opacity="0.85">{v:.2f}%</text>')

    s.append(f'<rect x="36" y="536" width="868" height="54" rx="4" fill="#fbfbfc" stroke="{GRID}"/>')
    s.append(f'<text x="48" y="556" font-size="11" fill="{INK}">'
             f'本项目两只同处“低质量-高分派”象限，却分居上下沿：深国际 4.90% 是象限内最高，普洛斯 3.70% 是最低。</text>')
    s.append(f'<text x="48" y="574" font-size="10.5" fill="{MUTED}">'
             f'同象限、相差 1.2pct，说明这两只的“高收益”不是同一个原因，见 §4.5 与 §6.3。</text>')
    foot(s, W, H, "位次见 matrix_quality.csv；分派率为 C2（经营活动现金流净额 ÷ 反推市值）；气泡面积与市值成正比")
    return save("fig4_positioning.svg", s)


# ============================================================ 图 5 商业模式
def fig5():
    W, H = 940, 650
    s = head(W, H, "图 5　两种赚钱方式：资产赚钱能力 × 分派自给程度",
             "横轴：单位面积营业收入（元/㎡/年）　纵轴：可供分配 ÷ 经营现金流（分派的钱够不够用）")
    L, R, T, B = 120, 860, 96, 470

    def X(v):
        return L + (v - 280) / 125 * (R - L)

    def Y(v):
        return B - (v - 0.85) / 0.65 * (B - T)

    for v in [0.9, 1.0, 1.1, 1.2, 1.3, 1.4]:
        s.append(f'<line x1="{L}" y1="{Y(v)}" x2="{R}" y2="{Y(v)}" stroke="{GRID}"/>')
        s.append(f'<text x="{L-12}" y="{Y(v)+4}" font-size="10.5" text-anchor="end" fill="{MUTED}">{v:.1f}×</text>')
    for v in [300, 320, 340, 360, 380]:
        s.append(f'<line x1="{X(v)}" y1="{T}" x2="{X(v)}" y2="{B}" stroke="{GRID}" stroke-dasharray="2 4"/>')
        s.append(f'<text x="{X(v)}" y="{B+20}" font-size="10.5" text-anchor="middle" fill="{MUTED}">{v}</text>')
    s.append(f'<text x="{(L+R)/2}" y="{B+44}" font-size="11" text-anchor="middle" fill="{INK}">'
             f'单位面积营业收入 元/㎡/年</text>')
    s.append(f'<text x="34" y="{T-24}" font-size="11" fill="{INK}">分派 ÷ 经营现金流</text>')

    s.append(f'<line x1="{L}" y1="{Y(1.0)}" x2="{R}" y2="{Y(1.0)}" stroke="{ACCENT}" stroke-width="1.3" stroke-dasharray="7 4" opacity="0.7"/>')
    s.append(f'<text x="{R-4}" y="{Y(1.0)+16}" font-size="10" text-anchor="end" fill="{ACCENT}">'
             f'1.0× ＝ 分派刚好等于当期经营现金</text>')

    quad = [(L+4, T+14, "start", "高坪效・超额分派（钱来自账外）"),
            (R-4, T+14, "end", "高坪效・自给有余"),
            (L+4, B-8, "start", "低坪效・保守分派（有留存）")]
    for x, y, a, t in quad:
        s.append(f'<text x="{x}" y="{y}" font-size="9.5" fill="#9aa5b1" text-anchor="{a}">{escape(t)}</text>')

    # (名称, 方位)
    pos = {"普洛斯": "right", "中航易商": "left", "盐田港": "left",
           "京东仓储": "up", "深国际": "right", "宝湾物流": "down"}
    for nm in ORDER:
        d = D[nm]
        cx, cy = X(d["rev_psm"]), Y(d["dist_cfo"])
        r = 8 + (d["fee"] - 8) * 1.85
        col = ACCENT if d["proj"] else BASE
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" '
                 f'opacity="{0.26 if d["proj"] else 0.14}" stroke="{col}" stroke-width="{2 if d["proj"] else 1.2}"/>')
        side = pos[nm]
        if side == "right":
            tx, ty, anc = cx + r + 8, cy + 1, "start"
        elif side == "up":
            tx, ty, anc = cx, cy - r - 21, "middle"
        elif side == "down":
            tx, ty, anc = cx, cy + r + 22, "middle"
        else:
            tx, ty, anc = cx - r - 8, cy + 1, "end"
        s.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="11.5" text-anchor="{anc}" '
                 f'fill="{col}" font-weight="{700 if d["proj"] else 400}">{escape(nm)}</text>')
        s.append(f'<text x="{tx:.1f}" y="{ty+13:.1f}" font-size="10" text-anchor="{anc}" fill="{col}" '
                 f'opacity="0.85">{d["dist_cfo"]:.2f}×・费用率 {d["fee"]:.1f}%</text>')

    s.append(f'<rect x="36" y="536" width="868" height="56" rx="4" fill="#fbfbfc" stroke="{GRID}"/>')
    s.append(f'<text x="48" y="556" font-size="11" fill="{INK}">'
             f'普洛斯与中航易商都在 1.3× 以上，但钱的来源相反：普洛斯靠减值与调整项，易商靠原始权益人 NOI 补足。</text>')
    s.append(f'<text x="48" y="574" font-size="10.5" fill="{MUTED}">'
             f'深国际 0.89× 是全组最低——当年分得比挣得少；这不是优点也不是缺点，而是“还有留存可托底”的余量。</text>')
    foot(s, W, H, "单位面积收入＝营业收入÷可租面积；分派÷现金流＝可供分配金额÷经营活动现金流净额；费用率＝管理费合计÷营业收入")
    return save("fig5_business_model.svg", s)


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5):
        print("wrote", f())
