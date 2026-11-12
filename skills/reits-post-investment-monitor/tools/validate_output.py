#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""reits-post-investment-monitor 产出校验器

用途：把 FLOW #22 的"五条硬校验"变成可执行断言，一次跑完，退出码非 0 即不得交付。

    python tools/validate_output.py --output output/20261112_1340 --doc-root "C:/.../508056_中金普洛斯REIT"

校验项
  C0  doc_index.csv 存在且字段齐全（file/type/tag/period/disclose_date/pages/status）
  C1  外键：source_index.file ⊆ doc_index.file
  C2  页码上界：page_to ≤ doc_index.pages
  C3  自算必带公式：computed=是 → formula 非空
  C4  URL 回验：url 非空且非 NA(offline) → 含基金代码
  C5  锚点覆盖：报告正文 <tag> p<page> 能在 source_index 命中同一 file 且页码落在区间内
  C6  物理存在：source_index.file 能在 doc_root 下找到同名文件
  C7  面板位置：<output>/dataset/panel.csv（或 panel.parquet）存在——#5 的唯一数据源须按约定落盘
  C8  图表内嵌：正文每个 ![..](..) 路径可解析；有 charts/ 却无内嵌引用则失败
  C9  孤儿图：charts/ 下每个图件都须被正文引用（按去扩展名的文件名匹配）
  C10 禁止指路：正文不得出现「文件：charts/xx」「见 charts/xx」这类把图推给附件的写法
  C11 阅读版：缺 report_*.html（图 base64 内嵌）仅告警，不阻断
  另：claim 表结构由 tools/check_claims.py 独立校验（CC1-CC10）

只依赖标准库，可对任意 output 目录重复运行。离线场景（无公告 URL）用 NA(offline) 显式标注，
不允许留空以"绕过"校验。
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

DOC_INDEX_COLS = ["file", "type", "tag", "period", "disclose_date", "pages", "status"]
SRC_COLS = ["source_id", "file", "page_from", "section", "metric", "value", "unit",
            "kind", "computed", "formula", "url", "local_path"]

ANCHOR_RE = re.compile(r"\b((?:q|h|y)\d{4}(?:Q[1-4]|H[1-2])?|zmsms|pg\d{4}|sj\d{4})\s*p\.?\s*(\d+)")


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def find_file(doc_root, name):
    """在 doc_root 及其子目录里找同名文件。"""
    direct = os.path.join(doc_root, name)
    if os.path.isfile(direct):
        return direct
    hits = glob.glob(os.path.join(doc_root, "**", name), recursive=True)
    return hits[0] if hits else None


def to_int(x):
    try:
        return int(str(x).strip())
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True, help="产出目录，含 report_*.md / source_index_*.csv")
    ap.add_argument("--doc-root", required=True, help="原始 PDF 根目录")
    ap.add_argument("--code", default=None, help="基金代码，缺省从文件名推断")
    args = ap.parse_args()

    out = os.path.abspath(args.output)
    doc_root = os.path.abspath(args.doc_root)
    fails, warns, notes = [], [], []

    # ---------- C0 doc_index ----------
    doc_index_path = None
    for cand in (os.path.join(out, "dataset", "doc_index.csv"), os.path.join(out, "doc_index.csv")):
        if os.path.isfile(cand):
            doc_index_path = cand
            break
    if not doc_index_path:
        fails.append("C0 doc_index.csv 缺失：应在 <output>/dataset/doc_index.csv（FLOW #1 落盘要求）")
        docs = []
    else:
        docs = read_csv(doc_index_path)
        missing = [c for c in DOC_INDEX_COLS if c not in (docs[0].keys() if docs else [])]
        if missing:
            fails.append("C0 doc_index.csv 缺列：" + ", ".join(missing))
        else:
            notes.append("C0 doc_index.csv 就绪：%d 份文件，%s" % (len(docs), os.path.basename(doc_index_path)))

    by_file = {d["file"].strip(): d for d in docs if d.get("file")}
    by_tag = {}
    for d in docs:
        t = (d.get("tag") or "").strip()
        if t:
            by_tag.setdefault(t, d["file"].strip())

    # ---------- source_index ----------
    src_files = sorted(glob.glob(os.path.join(out, "source_index_*.csv")))
    if not src_files:
        fails.append("source_index_*.csv 缺失")
        rows = []
    else:
        rows = read_csv(src_files[0])
        missing = [c for c in SRC_COLS if c not in (rows[0].keys() if rows else [])]
        if missing:
            fails.append("source_index 缺列：" + ", ".join(missing))
        notes.append("source_index 共 %d 行：%s" % (len(rows), os.path.basename(src_files[0])))

    code = args.code
    if not code:
        m = re.search(r"(\d{6})", os.path.basename(src_files[0]) if src_files else "")
        code = m.group(1) if m else None

    bad_fk, bad_page, bad_formula, bad_url, bad_phys = [], [], [], [], []
    for i, r in enumerate(rows, start=2):  # 表头占第 1 行
        f = (r.get("file") or "").strip()
        # C1
        if by_file and f not in by_file:
            bad_fk.append("第 %d 行 file=%r 不在 doc_index 中" % (i, f))
        # C6
        if f and find_file(doc_root, f) is None:
            bad_phys.append("第 %d 行 file=%r 在 doc_root 下找不到" % (i, f))
        # C2
        d = by_file.get(f)
        if d:
            pages = to_int(d.get("pages"))
            pf = to_int(r.get("page_from"))
            pt = to_int(r.get("page_to")) or pf
            if pages and (pf is None or pt is None or pf < 1 or pt > pages):
                bad_page.append("第 %d 行 页码 %r-%r 越界（文件 %d 页）" % (i, r.get("page_from"), r.get("page_to"), pages))
        # C3
        if str(r.get("computed", "")).strip() in ("是", "Y", "true", "1") and not (r.get("formula") or "").strip():
            bad_formula.append("第 %d 行 computed=是 但 formula 为空" % i)
        # C4
        u = (r.get("url") or "").strip()
        if not u:
            bad_url.append("第 %d 行 url 为空（无源请写 NA(offline)）" % i)
        elif u.upper() != "NA(OFFLINE)" and code and code not in u:
            bad_url.append("第 %d 行 url 不含基金代码 %s" % (i, code))

    if bad_fk:
        fails.append("C1 外键失败 %d 处：%s" % (len(bad_fk), bad_fk[0]))
    if bad_page:
        fails.append("C2 页码越界 %d 处：%s" % (len(bad_page), bad_page[0]))
    if bad_formula:
        fails.append("C3 自算缺公式 %d 处：%s" % (len(bad_formula), bad_formula[0]))
    if bad_url:
        fails.append("C4 URL 校验失败 %d 处：%s" % (len(bad_url), bad_url[0]))
    if bad_phys:
        fails.append("C6 文件不存在 %d 处：%s" % (len(bad_phys), bad_phys[0]))

    # ---------- C7 panel 位置 ----------
    panel_hits = [p for p in (os.path.join(out, "dataset", "panel.csv"),
                              os.path.join(out, "dataset", "panel.parquet")) if os.path.isfile(p)]
    if panel_hits:
        notes.append("C7 panel 就绪：%s" % os.path.basename(panel_hits[0]))
    else:
        fails.append("C7 面板缺失：应在 <output>/dataset/panel.csv（#5 的唯一数据源）")

    # ---------- C5 锚点覆盖 ----------
    reports = sorted(glob.glob(os.path.join(out, "report_*.md")))
    if not reports:
        warns.append("C5 跳过：未找到 report_*.md")
    else:
        md = open(reports[0], encoding="utf-8").read()
        span = {}
        for r in rows:
            f = (r.get("file") or "").strip()
            pf = to_int(r.get("page_from"))
            pt = to_int(r.get("page_to")) or pf
            if f and pf:
                span.setdefault(f, []).append((pf, pt))
        uncovered = []
        for tag, page in ANCHOR_RE.findall(md):
            page = int(page)
            f = by_tag.get(tag)
            if not f:
                # 只有标签没有 doc_index 映射：无法判断指向哪个文件，本身就是缺陷
                uncovered.append("%s p%d（doc_index 无此 tag）" % (tag, page))
                continue
            rng = span.get(f, [])
            if not any(a <= page <= b for a, b in rng):
                uncovered.append("%s p%d（%s 无该页来源行）" % (tag, page, os.path.basename(f)[:24]))
        if uncovered:
            fails.append("C5 锚点未覆盖 %d 处：%s" % (len(uncovered), "; ".join(uncovered[:3])))
        else:
            notes.append("C5 正文锚点全部命中 source_index")

    # ---------- C8/C9/C10 图表必须内嵌在报告里 ----------
    charts_dir = os.path.join(out, "charts")
    IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*([^)\s]+)")
    ROAD_RE = re.compile(r"(?:文件|见|详见|另见|参见)\s*[：:]?\s*`?charts/")
    if reports:
        md = open(reports[0], encoding="utf-8").read()
        targets = IMG_RE.findall(md)

        broken = []
        for t in targets:
            p = t if os.path.isabs(t) else os.path.join(out, t.lstrip("./"))
            if not os.path.exists(p):
                broken.append(t)
        has_charts = os.path.isdir(charts_dir) and any(
            os.path.splitext(f)[1].lower() in (".svg", ".png", ".jpg", ".jpeg", ".webp")
            for f in os.listdir(charts_dir)
        )
        if not targets:
            if has_charts:
                fails.append("C8 图表未内嵌：charts/ 有图件但正文无 ![..](..) 引用（图不得作为报告附件单独存在）")
        elif broken:
            fails.append("C8 图片引用不可解析 %d 处：%s" % (len(broken), "; ".join(broken[:3])))
        else:
            notes.append("C8 正文内嵌图 %d 张，引用路径全部可解析" % len(targets))

        bad_ref = [l.strip()[:48] for l in md.splitlines() if ROAD_RE.search(l)]
        if bad_ref:
            fails.append("C10 指路式图引用 %d 处（应改为就地内嵌）：%s" % (len(bad_ref), bad_ref[0]))
        else:
            notes.append("C10 无指路式图引用")

        if has_charts:
            used = {os.path.splitext(os.path.basename(t))[0] for t in targets}
            orphans = [f for f in sorted(os.listdir(charts_dir))
                       if os.path.splitext(f)[1].lower() in (".svg", ".png", ".jpg", ".jpeg", ".webp")
                       and os.path.splitext(f)[0] not in used]
            if orphans:
                fails.append("C9 孤儿图 %d 个未被正文引用：%s" % (len(orphans), ", ".join(orphans[:4])))
            else:
                notes.append("C9 charts/ 图件全部被正文引用")

        html_hits = [f for f in os.listdir(out) if f.endswith(".html")]
        if not html_hits:
            warns.append("C11 缺 .html 单文件阅读版（图为 base64 内嵌，拷走即完整）")

    # ---------- 输出 ----------
    print("=" * 68)
    print("validate_output  output=%s" % out)
    print("                 doc_root=%s" % doc_root)
    print("=" * 68)
    for n in notes:
        print("  [INFO] " + n)
    for w in warns:
        print("  [WARN] " + w)
    for f in fails:
        print("  [FAIL] " + f)
    print("-" * 68)
    if fails:
        print("结果：FAIL（%d 项）。按 FLOW #22，未通过不得交付。" % len(fails))
        return 1
    print("结果：PASS。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
