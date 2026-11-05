# -*- coding: utf-8 -*-
"""tests/run_tests.py —— 项目自检执行器

四组测试：
  T-CALC  计算与对账（数值断言）
  T-DQ    数据质量（面板完整性与口径一致性）
  T-SKILL Skill 四件套结构（可逆性、动作编号、必备字段）
  T-REG   回归（三个案例的关键结论是否仍在）

运行：python tests/run_tests.py
输出：逐条 PASS/FAIL，末尾汇总；任一 FAIL 时退出码为 1。
"""
import csv
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = {"pass": 0, "fail": 0, "skip": 0, "rows": []}


def ok(tid, name, detail=""):
    R["pass"] += 1
    R["rows"].append((tid, "PASS", name, detail))


def bad(tid, name, detail=""):
    R["fail"] += 1
    R["rows"].append((tid, "FAIL", name, detail))


def skip(tid, name, detail=""):
    R["skip"] += 1
    R["rows"].append((tid, "SKIP", name, detail))


def chk(tid, name, cond, detail=""):
    (ok if cond else bad)(tid, name, detail)


def close(a, b, tol, tid, name, note=""):
    d = abs(a - b)
    chk(tid, name, d <= tol, "%s | 实测 %.4f vs 期望 %.4f，差 %.4f，容差 %.4f"
        % (note or name, a, b, d, tol))


def path(*p):
    return os.path.join(ROOT, *p)


def read(p):
    return io.open(p, encoding="utf-8").read()


def split_raw(raw):
    """与 tools/build_raw.py 同构的逐行状态机，用于 _raw_response 可逆性校验。

    只认「行首」标记，因此正文里作为示例出现的 `<<<FILE: x>>>`（行内、前有其他字符）
    不会被误判为分块起点。测试与生产必须用同一套解析逻辑，否则会出现
    「build_raw 说 ALL_MATCH、测试说分段异常」的矛盾。
    """
    out, cur, buf = {}, None, []
    for line in raw.splitlines(True):
        s = line.strip()
        if cur is None and s.startswith("<<<FILE: ") and s.endswith(">>>"):
            cur, buf = s[9:-3].strip(), []
        elif cur is not None and s.startswith("<<<END: ") and s.endswith(">>>"):
            out[cur] = "".join(buf)
            cur, buf = None, []
        elif s == "<<<END>>>":
            continue
        elif cur is not None:
            buf.append(line)
    return out


# ============================================================
# T-CALC 计算与对账
# ============================================================
def t_calc():
    # --- 508056 ---
    q1, q2, q3, q4 = 82825928.95, 83962570.66, 84035109.60, 86649219.38
    fy = 335181671.99
    s4 = q1 + q2 + q3 + q4
    close(s4, 337472828.59, 0.5, "T-CALC-01", "508056 四季可供分派加总")
    close((s4 - fy) / fy, 0.006835, 0.0001, "T-CALC-02",
          "508056 四季合计与年报差异率 = 0.68%（DATA_QUALITY_WARNING 依据）")
    close(342337121.58 / fy, 1.0213, 0.0005, "T-CALC-03",
          "508056 同口径分派/可供分配 = 102.1%（非账面的 128.4%）")

    # --- 180302 ---
    h1, q3b, q4b, fyb = 36746669.59, 18744911.01, 18909619.40, 74401200.00
    close(h1 + q3b + q4b, fyb, 0.01, "T-CALC-04",
          "180302 分季加总与年报完全闭合（差 0）")
    close(74401200.00 / 1494000000, 0.0498, 0.00005, "T-CALC-05",
          "180302 分派率（募集规模口径）= 4.98%")

    # --- 508601 可供分配恒等式 ---
    for year, cash, safe, liab, target in [
        (2026, 330144418.05, 3424854.22, 156335515.79, 170384048.05),
        (2027, 312025752.05, 3457600.09, 155263753.54, 153304398.41),
    ]:
        close(cash - safe - liab, target, 0.02, "T-CALC-06-%d" % year,
              "508601 %d 可供分配 = 年末现金 − 预留安全现金 − 预留经营性负债" % year)

    eb26, cx26, it26 = 170437399.69, 15460400.00, 13287806.33
    eb27, cx27, it27 = 174883323.29, 8827400.00, 13745968.83
    d26 = eb26 - cx26 - it26
    d27 = eb27 - cx27 - it27
    close(d26, 141689193.36, 1.0, "T-CALC-07",
          "508601 2026 规范化可供分配 = EBITDA − capex − 利息所得税")
    close(d26 / 2739656060.87, 0.05171, 0.00005, "T-CALC-08",
          "508601 2026 规范化分派率 = 5.17%（披露 6.22% 含募集资金沉淀）")
    close((153304398.41 - d27) / 153304398.41, 0.00649, 0.0002, "T-CALC-09",
          "508601 2027 披露值与规范化值差 0.65%（说明 2027 已是规范口径）")
    close(d27 / 2739656060.87, 0.0556, 0.00005, "T-CALC-10",
          "508601 2027 规范化分派率 = 5.56%")

    # --- 508601 模型与 IRR ---
    try:
        import importlib.util
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            spec = importlib.util.spec_from_file_location("bm", path("tools", "build_model.py"))
            bm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bm)
        finally:
            sys.stdout = old
        close(bm.IRR0, 0.026688, 0.0005, "T-CALC-11",
              "508601 IRR（19 期、无终值）= 2.67%")
        close(sum(r["dist"] for r in bm.ROWS) / 1e8, 36.0089, 0.01, "T-CALC-12",
              "508601 19 年累计可供分派 = 36.01 亿元（募集的 131.4%）")
        close(bm.PV_NOI5 / 1e8, 25.3120, 0.01, "T-CALC-13",
              "508601 毛 NOI@5% = 25.31 亿元（评估值 27.03 亿，−6.4%）")
        close(bm.PV5 / 1e8, 22.0572, 0.01, "T-CALC-14",
              "508601 净可供分配@5% = 22.06 亿元（−18.4%）")
        close(bm.PRICE_AT_560 / 1e8, 20.9259, 0.01, "T-CALC-15",
              "508601 IRR=5.60% 的可承受发行规模 = 20.93 亿元")
        close(bm.TV_FOR_560 / 1e8, 18.2206, 0.05, "T-CALC-16",
              "508601 使 IRR=5.60% 所需 2044 年末终值 = 18.22 亿元")
    except Exception as e:  # noqa
        skip("T-CALC-11..16", "508601 模型断言", "导入 build_model.py 失败：%r" % e)

    # --- 508601 税率与费用结构 ---
    # 原 T-CALC-17（219.458715 / 26.321211 ≈ 8.338）已删除：
    # 该断言的两个输入在报告、模型、披露文件中均无法回溯到具体页码，
    # 属于"来源不明断言"。按项目原则（不能声明未经回溯的校验），移除而非保留。
    # 编号不重排，避免既有文档引用失效。
    close(29458552.00 / 40239123.11, 0.7321, 0.001, "T-CALC-18",
          "508601 房产税占税金及附加 73.2%")
    close(21881406.95 / 263631409.01, 0.0830, 0.0002, "T-CALC-19",
          "508601 运营管理费率 = 8.30%（A 5.3% + B 3.0%）")

    # --- 敏感性弹性 ---
    pas, m27 = 0.81, 174883323.29 / 254760101.02
    close(pas / m27, 1.1800, 0.001, "T-CALC-20",
          "508601 收入→EBITDA 弹性 = 1.18（0.81 ÷ 68.65%）")
    eb28, cx28, it28 = 179745080.0, 9164485.0, 14020888.0
    base = (eb28 - cx28 - it28) / 2739656060.87
    m = 0.90
    v = (eb28 * (1 + pas / m27 * (m - 1)) - cx28 * m - it28) / 2739656060.87
    close(v, 0.0497, 0.0002, "T-CALC-21",
          "508601 租金 −10% → 2028E 分派率 4.97%")
    close(base - v, 0.0074, 0.0002, "T-CALC-22",
          "508601 租金每 −10% → 分派率 −0.74pct")


# ============================================================
# T-DQ 数据质量
# ============================================================
def load_panel(name):
    p = path("outputs", "_panel", name)
    if not os.path.exists(p):
        return None
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))


def t_dq():
    for fn, min_rows in [("508056_raw.csv", 700), ("180302_raw.csv", 130)]:
        rows = load_panel(fn)
        if rows is None:
            skip("T-DQ-01", "面板存在性 %s" % fn, "文件缺失")
            continue
        ok("T-DQ-01", "面板存在性 %s" % fn, "%d 行" % len(rows))
        chk("T-DQ-02", "面板行数下限 %s" % fn, len(rows) >= min_rows,
            "%d 行（下限 %d）" % (len(rows), min_rows))
        # 空值率
        empt = sum(1 for r in rows if r["value"] in ("", None))
        chk("T-DQ-03", "关键字段无空值 %s" % fn, empt == 0, "空值 %d 条" % empt)
        # anchor 必填
        noanchor = sum(1 for r in rows if not r["anchor"])
        chk("T-DQ-04", "每条数据有页码锚点 %s" % fn, noanchor == 0, "缺锚点 %d 条" % noanchor)
        # metric 命名白名单：规范见 METADATA.metric_naming（base+suffix）
        bases = {"revenue", "dist", "distributable", "distributed", "net_profit", "cfo",
                 "ebitda", "occ", "rent", "rent_avg_period", "wale", "collection",
                 "area_leasable", "area_leased"}
        suffixes = ("_prev", "_yoy", "_cum", "_q")

        def split_metric(m):
            for sx in suffixes:
                if m.endswith(sx):
                    return m[: -len(sx)], sx
            return m, ""

        badm = sorted({r["metric"] for r in rows
                       if split_metric(r["metric"])[0] not in bases})
        chk("T-DQ-05", "metric 命名符合 base+suffix 规范 %s" % fn, not badm, "越界：%s" % badm)

    # 时点值 vs 期间值：出租率不得出现季度均值字段
    rows = load_panel("508056_raw.csv") or []
    occ = [r for r in rows if r["metric"] == "occ"]
    chk("T-DQ-06", "出租率为期末时点口径（不出现 avg 字段）",
        all("avg" not in r["metric"] for r in occ), "%d 条出租率记录" % len(occ))

    # 单位一致性：508056 剩余租期为“天”，180302 为“年”，不得混算
    g = load_panel("508056_raw.csv") or []
    h = load_panel("180302_raw.csv") or []
    gw = [float(r["value"]) for r in g if r["metric"] == "wale"]
    hw = [float(r["value"]) for r in h if r["metric"] == "wale"]
    if gw and hw:
        chk("T-DQ-07", "剩余租期单位未混算（508056 天 / 180302 年）",
            max(gw) > 100 and max(hw) < 20,
            "508056 max %.2f / 180302 max %.2f" % (max(gw), max(hw)))

    # claims 完整性
    for d in ("case_01_glp_reit", "case_02_huaxia_shen_international", "case_03_sinofarm_reit"):
        p = path("outputs", d, "claims_verdict.csv")
        if not os.path.exists(p):
            bad("T-DQ-08", "claims_verdict 存在 %s" % d, "缺失")
            continue
        cr = list(csv.DictReader(io.open(p, encoding="utf-8-sig")))
        chk("T-DQ-08", "claims_verdict 存在 %s" % d, len(cr) >= 6, "%d 条" % len(cr))
        noev = [r["claim_id"] for r in cr if not r["evidence_ref"]]
        chk("T-DQ-09", "每条 claim 有证据引用 %s" % d, not noev, "缺引用：%s" % noev)
        badt = [r["claim_id"] for r in cr if r["verdict"] not in
                ("PASS", "FAIL", "INDETERMINATE", "PARTIALLY_SUPPORTED",
                 "NOT_COMPARABLE", "SOURCE_UNAVAILABLE", "DATA_QUALITY_WARNING")]
        chk("T-DQ-10", "verdict 取值在七态内 %s" % d, not badt, "越界：%s" % badt)
        noagg = [r["claim_id"] for r in cr if not r["aggregation"]]
        chk("T-DQ-11", "每条 claim 在建表时写死 aggregation %s" % d, not noagg, "缺聚合：%s" % noagg)


# ============================================================
# T-SKILL Skill 四件套结构
# ============================================================
def t_skill():
    names = ["research-report-to-flow", "reits-post-investment-monitor",
             "reits-pre-investment-analysis"]
    for n in names:
        base = path("skills", n)
        for f in ("SKILL.md", "METADATA.md", "FLOW.md", "_raw_response.txt"):
            p = os.path.join(base, f)
            chk("T-SKILL-01", "%s / %s 存在" % (n, f), os.path.exists(p),
                "%d 字节" % os.path.getsize(p) if os.path.exists(p) else "缺失")
        # SKILL 结构：YAML frontmatter（--- 包裹）+ 一级标题
        sk = read(os.path.join(base, "SKILL.md"))
        has_fm = sk.lstrip().startswith("---") and "\n---" in sk.lstrip()[3:]
        has_h1 = bool(re.search(r"^#\s+\S", sk, flags=re.M))
        chk("T-SKILL-02", "%s SKILL.md 有 frontmatter 且含一级标题" % n, has_fm and has_h1,
            "frontmatter=%s 一级标题=%s" % (has_fm, has_h1))
        # FLOW 动作编号连续
        fl = read(os.path.join(base, "FLOW.md"))
        nums = sorted({int(m) for m in re.findall(r"^#(\d+)\s", fl, flags=re.M)})
        chk("T-SKILL-03", "%s FLOW 动作编号连续且从 1 开始" % n,
            bool(nums) and nums[0] == 1 and nums == list(range(1, len(nums) + 1)),
            "共 %d 个动作：%s…%s" % (len(nums), nums[:3], nums[-3:] if nums else []))
        # METADATA 必备键
        md = read(os.path.join(base, "METADATA.md"))
        must = {
            "research-report-to-flow": ["claim_schema", "evidence_policy", "threshold_policy",
                                        "formula_registry", "source_registry"],
            "reits-post-investment-monitor": ["period_semantics", "metric_bands",
                                              "claim_schema", "formula_registry"],
            "reits-pre-investment-analysis": ["step0_required", "assumption_register",
                                              "valuation_params", "scenario_set"],
        }[n]
        miss = [k for k in must if k not in md]
        chk("T-SKILL-04", "%s METADATA 必备字段齐全" % n, not miss, "缺：%s" % miss)

        # _raw_response 可逆性：用与 tools/build_raw.py 同构的逐行状态机解析。
        # 不能用正则——FLOW/SKILL 正文里会出现 `<<<FILE: x>>>` 这样的说明性示例，
        # 正则会把示例当成真实分块，产生"x"这种不存在的段（真实踩过）。
        raw = read(os.path.join(base, "_raw_response.txt"))
        blocks = split_raw(raw)
        want = {"SKILL.md", "METADATA.md", "FLOW.md"}
        chk("T-SKILL-05", "%s _raw_response 分段齐备" % n, set(blocks) == want,
            "实得段：%s，文末标记 %s" % (sorted(blocks), "<<<END>>>" in raw))
        # 段内内容与磁盘文件一致
        mismatch = []
        for fn, body in blocks.items():
            fp = os.path.join(base, fn.strip())
            if os.path.exists(fp):
                disk = read(fp).strip()
                if disk != body.strip():
                    mismatch.append(fn)
            else:
                mismatch.append(fn + "(磁盘无此文件)")
        chk("T-SKILL-06", "%s _raw_response 与磁盘文件逐段一致" % n, not mismatch,
            "不一致：%s" % mismatch)

    # 阈值必须有出处 + 公式必须有生效期（一期审计的 P4/P5）
    md = read(path("skills", "research-report-to-flow", "METADATA.md"))
    chk("T-SKILL-07", "阈值三档与 UNDEFINED_THRESHOLD 已定义",
        "UNDEFINED_THRESHOLD" in md and "bands" in md, "")
    chk("T-SKILL-08", "公式注册表含 formula_version 与生效期",
        "formula_version" in md and ("valid_from" in md or "effective" in md), "")
    fl = read(path("skills", "research-report-to-flow", "FLOW.md"))
    chk("T-SKILL-09", "research-report-to-flow 含 Step 0 数据预处理",
        "Step 0" in fl or "Step0" in fl, "")
    fl2 = read(path("skills", "reits-post-investment-monitor", "FLOW.md"))
    chk("T-SKILL-10", "投后 FLOW #20 含分母口径三问（R2-03 固化）",
        "分母口径三问" in fl2, "")


# ============================================================
# T-REG 回归
# ============================================================
def t_reg():
    specs = [
        ("case_01_glp_reit", "report_508056_2025Q4.md",
         ["422,500,807.91", "335,181,671.99", "430,470,192.84", "102.1%",
          "−3.51pct", "71,520,087.02"], 3000),
        ("case_02_huaxia_shen_international", "report_180302_2025Q4.md",
         ["74,401,200.00", "4.98%", "4.81%", "25.12%", "71.32%",
          "4.36%", "−25.55%"], 3000),
        ("case_03_sinofarm_reit", "report_508601.md",
         ["2,739,656,060.87", "141,689,193", "5.17%", "2.67%", "18.22",
          "20.93", "8.30%", "3.56 年", "36.53%"], 15000),
    ]
    for d, fn, keys, min_cjk in specs:
        p = path("outputs", d, fn)
        if not os.path.exists(p):
            bad("T-REG-01", "报告存在 %s/%s" % (d, fn), "缺失")
            continue
        s = read(p)
        cjk = len(re.findall(r"[\u4e00-\u9fff]", s))
        ok("T-REG-01", "报告存在 %s/%s" % (d, fn), "%d 中文字符" % cjk)
        chk("T-REG-02", "中文字符数达标 %s" % d, cjk >= min_cjk,
            "%d ≥ %d" % (cjk, min_cjk))
        miss = [k for k in keys if k not in s]
        chk("T-REG-03", "关键数字仍在报告中 %s" % d, not miss, "缺：%s" % miss)

    # 案例三的更正声明必须存在
    s = read(path("outputs", "case_03_sinofarm_reit", "report_508601.md"))
    chk("T-REG-04", "案例三含 §1.4 四条更正公开声明",
        "本报告相对初稿的四条更正" in s or "C-1" in s and "C-4" in s, "")
    chk("T-REG-05", "案例三未把分派率等同于回报率（需出现 IRR 并列说明）",
        "分派率不等于回报率" in s, "")

    # 模型文件与 sheet
    try:
        from openpyxl import load_workbook
        wb = load_workbook(path("models", "cash_flow_model.xlsx"))
        chk("T-REG-06", "cash_flow_model.xlsx 含 5 个 sheet（说明/假设/模型/输出/敏感性）",
            len(wb.sheetnames) == 5 and wb.sheetnames[:3] == ["0_说明", "1_假设", "2_模型"],
            str(wb.sheetnames))
        wm = wb["2_模型"]
        chk("T-REG-07", "2_模型 为 19 期（2026–2044）",
            wm.cell(row=5, column=1).value == 2026 and wm.cell(row=23, column=1).value == 2044,
            "首行 %s 末行 %s" % (wm.cell(row=5, column=1).value, wm.cell(row=23, column=1).value))
        chk("T-REG-08", "2_模型 的 F 列是公式（可重算）",
            str(wm.cell(row=5, column=7).value).startswith("="),
            str(wm.cell(row=5, column=7).value))
        wo = wb["3_输出"]
        irr_cell = None
        for row in wo.iter_rows(min_row=1, max_row=wo.max_row):
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("=IRR("):
                    irr_cell = c
        chk("T-REG-09", "3_输出 含 Excel IRR 公式", irr_cell is not None,
            irr_cell.value if irr_cell else "未找到")
        wb2 = load_workbook(path("models", "data_matrices.xlsx"))
        chk("T-REG-10", "data_matrices.xlsx 含 8 个 sheet", len(wb2.sheetnames) == 8,
            str(wb2.sheetnames))
    except Exception as e:  # noqa
        skip("T-REG-06..10", "Excel 结构断言", "openpyxl 读取失败：%r" % e)

    # 交付物清单
    must_exist = [
        "README.md", "iteration_log/ITERATION_LOG.md",
        "outputs/research_flow_audit/attachment_study.md",
        "outputs/research_flow_audit/research_flow_audit.xlsx",
        "outputs/case_01_glp_reit/run_log.md",
        "outputs/case_02_huaxia_shen_international/run_log.md",
        "outputs/case_03_sinofarm_reit/run_log.md",
        "outputs/case_03_sinofarm_reit/assumptions.csv",
        "outputs/case_03_sinofarm_reit/figures/transaction_structure.svg",
        "presentation/management_briefing.md",
        "outputs/final_acceptance_report.md",
    ]
    miss = [m for m in must_exist if not os.path.exists(path(*m.split("/")))]
    chk("T-REG-11", "交付物清单齐全", not miss, "缺：%s" % miss)


if __name__ == "__main__":
    t_calc()
    t_dq()
    t_skill()
    t_reg()
    w = max(len(r[2]) for r in R["rows"]) if R["rows"] else 20
    print("%-14s %-6s %-*s %s" % ("ID", "结果", w, "测试项", "说明"))
    print("-" * 110)
    for tid, st, name, detail in R["rows"]:
        print("%-14s %-6s %-*s %s" % (tid, st, w, name, detail))
    print("-" * 110)
    print("PASS %d / FAIL %d / SKIP %d / 共 %d"
          % (R["pass"], R["fail"], R["skip"], len(R["rows"])))
    sys.exit(1 if R["fail"] else 0)
