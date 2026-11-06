# -*- coding: utf-8 -*-
"""从 REITs 定期报告文本抽取标准面板（Step 0 的 #2–#5 实现）。
输出: <out>/panel.csv, <out>/raw_extract.csv
"""
import os, re, csv, sys, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT = os.path.join(os.path.dirname(BASE), "reits", "_txt")

NUM = r"-?[\d,]+\.?\d*"
QMAP = {"q2025Q1": "2025Q1", "q2025Q2": "2025Q2", "q2025Q3": "2025Q3", "q2025Q4": "2025Q4",
        "q2024Q1": "2024Q1", "q2024Q2": "2024Q2", "q2024Q3": "2024Q3", "q2024Q4": "2024Q4",
        "q2026Q1": "2026Q1", "q2026Q2": "2026Q2", "q2026Q3": "2026Q3",
        "h2024": "2024H1", "h2025": "2025H1", "h2026": "2026H1",
        "y2025": "2025FY", "y2024": "2024FY"}


def f(s):
    if s is None:
        return None
    s = s.replace(",", "").replace("%", "").strip()
    try:
        return float(s)
    except Exception:
        return None


def page_of(text, pos):
    """根据字符位置反推页码（=== Pn === 标记）"""
    seg = text[:pos]
    m = None
    for m in re.finditer(r"=== P(\d+) ===", seg):
        pass
    return int(m.group(1)) if m else 0


def get_period(fname):
    for k, v in QMAP.items():
        if "_" + k + "_" in fname:
            return v
    return None


def parse_fin(text):
    out = {}
    pats = {
        # 注意：季报 §3.1 只披露"本期"数（单季），没有本年累计收入。
        # 早期版本把这三个键写成 *_cum，与 metric_naming 规范里 `_cum`=本年累计
        # 直接冲突——2025Q4 的 revenue_cum=2,462 万会被读成"全年收入"，
        # 而实际全年是四季之和 1.115 亿，差 4.5 倍。见 ITERATION_LOG 第 5 轮 F-6。
        "revenue_q": r"1\.\s*本期收入\s+(" + NUM + r")",
        "net_profit_q": r"2\.\s*本期净利润\s+(" + NUM + r")",
        "cfo_q": r"3\.\s*本期经营活动产生的现金流量净额\s+(" + NUM + r")",
    }
    for k, p in pats.items():
        m = re.search(p, text)
        if m:
            out[k] = (f(m.group(1)), page_of(text, m.start()))
    # 可供分配 / 实际分配：表头后第一行数据
    for label, key in [(r"3\.3\.1[^\n]*\n(?:.*\n){0,6}?本期\s+(" + NUM + r")", "distributable_q"),
                       (r"3\.3\.2[^\n]*\n(?:.*\n){0,6}?本期\s+(" + NUM + r")", "distributed_q")]:
        m = re.search(label, text)
        if m:
            out[key] = (f(m.group(1)), page_of(text, m.start()))
    # 本年累计
    m = re.search(r"本年累计\s+(" + NUM + r")", text)
    if m:
        out["distributable_cum"] = (f(m.group(1)), page_of(text, m.start()))
    return out


ROW = re.compile(r"^\s*(\d)\s+(期末可供出租面积|期末实际出租面积|期末出租率|期末租金单价水平|"
                 r"期末剩余租期情况|期末租金收缴率)\s*(?:注\s*\d)?\s*(\S+)\s+(.+)$")
KEYS = {"期末可供出租面积": "area_leasable", "期末实际出租面积": "area_leased",
        "期末出租率": "occ", "期末租金单价水平": "rent", "期末剩余租期情况": "wale",
        "期末租金收缴率": "collection"}


def parse_ops(text):
    """返回 {'overall': {...}, 'projects': {name: {...}}}"""
    res = {"overall": {}, "projects": {}}
    # 整体段：优先取 4.1.2 至 4.1.3 之间；否则取第一个运营指标行之前
    m412 = re.search(r"4\.1\.2", text)
    m413 = re.search(r"4\.1\.3", text)
    if m412 and m413 and m413.start() > m412.start():
        seg_overall = text[m412.start():m413.start()]
        tail = text[m413.start():]
    else:
        first_row = re.search(r"^\s*1\s+期末可供出租面积", text, re.M)
        s = first_row.start() if first_row else 0
        seg_overall = text[s:s + 2500]
        tail = text[s:]
    for ln in seg_overall.splitlines():
        mm = ROW.match(ln)
        if not mm:
            continue
        vals = [f(x) for x in re.findall(NUM + r"%?", mm.group(4))]
        if not vals:
            continue
        key = KEYS[mm.group(2)]
        res["overall"].setdefault(key, vals[0])
        if len(vals) > 1:
            res["overall"].setdefault(key + "_prev", vals[1])
        if len(vals) > 2:
            res["overall"].setdefault(key + "_yoy", vals[2])
    # 项目段：只取 4.1.3 之后的项目块
    segs = [(m.start(), m.group(1).strip())
            for m in re.finditer(r"(?:资产|不动产)项目名称[：:]\s*([^\n]+)", tail)]
    for i, (s, name) in enumerate(segs):
        chunk = tail[s:(segs[i + 1][0] if i + 1 < len(segs) else len(tail))]
        holder = res["projects"].setdefault(name, {})
        for ln in chunk.splitlines():
            mm = ROW.match(ln)
            if not mm:
                continue
            key = KEYS[mm.group(2)]
            vals = [f(x) for x in re.findall(NUM + r"%?", mm.group(4))]
            if not vals:
                continue
            holder.setdefault(key, vals[0])
            if len(vals) > 1:
                holder.setdefault(key + "_prev", vals[1])
            if len(vals) > 2:
                holder.setdefault(key + "_yoy", vals[2])
    return res


FB = [
    ("occ", r"报告期末出租率.{0,300}?%\s*(" + NUM + r")\s+(" + NUM + r")\s+(-?" + NUM + r")"),
    ("rent", r"报告期末\s*有效租金\s*单价.{0,400}?元/平方米\s*/月\s*(" + NUM + r")\s+(" + NUM + r")\s+(-?" + NUM + r")"),
    ("wale", r"报告期末\s*加权平均\s*剩余租期.{0,400}?(?:年|天)\s*(" + NUM + r")\s+(" + NUM + r")\s+(-?" + NUM + r")"),
    ("collection", r"报告期末租金收缴\s*率.{0,300}?%\s*(" + NUM + r")\s+(" + NUM + r")\s+(-?" + NUM + r")"),
    ("area_leasable", r"报告期末\s*可供出租\s*面积.{0,300}?平方米\s*(" + NUM + r")"),
    ("area_leased", r"报告期末\s*实际出租\s*面积.{0,300}?平方米\s*(" + NUM + r")"),
]


def parse_ops_multiline(text):
    """适配 180302 一类表格：指标名与数值跨行、含"期末/期间"双租金口径"""
    res = {"overall": {}, "projects": {}}
    m412 = re.search(r"4\.1\.2", text)
    body = text[m412.start():] if m412 else text
    segs = [(m.start(), m.group(1).strip())
            for m in re.finditer(r"(?:资产|不动产)项目名称[：:]\s*([^\n]+)", body)]
    parts = [("overall", body[:segs[0][0]] if segs else body)]
    for i, (s, name) in enumerate(segs):
        parts.append((name, body[s:(segs[i + 1][0] if i + 1 < len(segs) else len(body))]))
    for name, chunk in parts:
        flat = re.sub(r"\s+", " ", chunk)
        holder = res["overall"] if name == "overall" else res["projects"].setdefault(name, {})
        for key, pat in FB:
            m = re.search(pat, flat)
            if not m:
                continue
            holder.setdefault(key, f(m.group(1)))
            if m.lastindex and m.lastindex >= 2:
                holder.setdefault(key + "_prev", f(m.group(2)))
            if m.lastindex and m.lastindex >= 3:
                holder.setdefault(key + "_yoy", f(m.group(3)))
        # 期间租金单价水平（与期末口径不同，单独记录）
        m = re.search(r"报告期内\s*租金单价\s*水平.{0,400}?元/平方米\s*/月\s*(" + NUM + r")\s+(" + NUM + r")\s+(-?" + NUM + r")", flat)
        if m:
            holder.setdefault("rent_avg_period", f(m.group(1)))
            holder.setdefault("rent_avg_period_prev", f(m.group(2)))
            holder.setdefault("rent_avg_period_yoy", f(m.group(3)))
    return res


def parse_project_rev(text):
    """分项目营业收入（年报/半年报常见：营业总收入按项目列示）"""
    out = {}
    for m in re.finditer(r"(?:资产|不动产)项目名称[：:]\s*([^\n]+)", text):
        name = m.group(1).strip()
        seg = text[m.start():m.start() + 3000]
        mm = re.search(r"(营业收入|营业总收入)[^\n]{0,40}\n?(?:[^\n]*\n){0,3}?[^\n]*?(" + NUM + r")", seg)
        if mm:
            out[name] = f(mm.group(2))
    return out


def main(code, keys):
    d = os.path.join(TXT, code)
    files = [x for x in sorted(os.listdir(d)) if any(k in x for k in keys)]
    raw, panel = [], []
    for fn in files:
        text = open(os.path.join(d, fn), encoding="utf-8").read()
        period = get_period(fn)
        fin = parse_fin(text)
        ops = parse_ops(text)
        if not ops['overall']:
            ops = parse_ops_multiline(text)
        for k, (v, pg) in fin.items():
            raw.append(dict(period=period, dim="overall", metric=k, value=v, anchor="%s p%d" % (period, pg), file=fn))
        for k, v in ops["overall"].items():
            raw.append(dict(period=period, dim="overall", metric=k, value=v, anchor="%s 运营表" % period, file=fn))
        for name, kv in ops["projects"].items():
            for k, v in kv.items():
                raw.append(dict(period=period, dim=name, metric=k, value=v, anchor="%s 项目表" % period, file=fn))
        print("%-10s %-14s fin=%d overall=%d projects=%d" %
              (period, fn[:12], len(fin), len(ops["overall"]), len(ops["projects"])))
        panel.extend(raw[-len(fin) - len(ops["overall"]) - sum(len(x) for x in ops["projects"].values()):])
    outdir = os.path.join(BASE, "outputs", "_panel")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "%s_raw.csv" % code), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["period", "dim", "metric", "value", "anchor", "file"])
        w.writeheader()
        w.writerows(raw)
    print("raw rows:", len(raw), "->", outdir)


if __name__ == "__main__":
    code = sys.argv[1]
    keys = sys.argv[2].split(",")
    main(code, keys)
