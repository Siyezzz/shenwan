#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_source_index.py — 重建 source_documents/source_index.csv

为什么必须重建
--------------
旧版的 url 字段对案例二整体错用了 508056 的基金代码（如
`fund.eastmoney.com/gonggao/508056,AN202510271769985860.html`），
按该链接打开是普洛斯的公告。**文件内容是对的，链接是错的**——
任何人按索引去核对，都会得出"文件与报告对不上"的结论。

本版做法：从公告接口重新拉取 (日期, 标题) → 公告 ID 的映射，
用本地文件名反查，生成可点击且能打开正确文件的链接。

字段
----
case, code, file, type, period, disclose_date, size_mb, pages, text_chars,
ocr, url, local_path, status

status:
  OK              有文字层，可直接引用
  OCR_NEEDED      疑似扫描件（文字极少），引用前需 OCR
  SOURCE_UNAVAILABLE  登记在案但未能获取（如首农的评估报告）
"""

import csv
import io
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXTROOT = os.path.join(os.path.dirname(ROOT), "reits", "_txt")
OUT = os.path.join(ROOT, "source_documents", "source_index.csv")

CASES = [
    ("glp_reit", "508056"),
    ("huaxia_shen_international", "180302"),
    ("sinofarm_reit", "508601"),
]
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://fundf10.eastmoney.com/"}
API = ("https://api.fund.eastmoney.com/f10/JJGG"
       "?fundcode={code}&pageIndex=1&pageSize=100&type={ty}")


def pull(code, ty, retry=4):
    # 该接口在本机网络下会间歇性抛 SSL: UNEXPECTED_EOF；单次失败不代表没有数据，
    # 不重试会导致索引残缺（曾只剩 8 条），进而在“url 未匹配”里制造假阳性。
    last = None
    for i in range(retry):
        try:
            req = urllib.request.Request(API.format(code=code, ty=ty), headers=HEADERS)
            data = json.loads(urllib.request.urlopen(req, timeout=25).read().decode("utf-8"))
            return data.get("Data") or []
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    print("  [WARN] %s type=%d 重试 %d 次仍失败: %s" % (code, ty, retry, last))
    return []


def norm(t):
    # 全角括号/顿号统一为半角，否则同一份文件在文件名与公告标题里会因括号形式不同而匹配失败
    t = (t.replace("（", "(").replace("）", ")")
          .replace("【", "[").replace("】", "]")
          .replace("：", ":").replace("，", ","))
    return re.sub(r"\s+", "", t)


def build_id_map(code):
    """(日期, 归一化标题) -> 公告 ID"""
    m = {}
    for ty in (1, 2, 3, 6):
        for it in pull(code, ty):
            m[(it["PUBLISHDATEDesc"], norm(it["TITLE"]))] = it["ID"]
    return m


TYPE_LABEL = [
    (r"^q(\d{4})Q([1-4])$", lambda a: "季度报告"),
    (r"^h(\d{4})$", lambda a: "中期报告"),
    (r"^y(\d{4})$", lambda a: "年度报告"),
    (r"^pg(\d{4})$", lambda a: "年度评估报告"),
    (r"^sj(\d{4})$", lambda a: "年度审计报告"),
    (r"^zmsms$", lambda a: "招募说明书"),
    (r"^fl_yijian$", lambda a: "法律意见书"),
    (r"^yunying$", lambda a: "运营数据公告"),
]


def period_of(tcode):
    m = re.match(r"^q(\d{4})Q([1-4])$", tcode)
    if m:
        return "%sQ%s" % (m.group(1), m.group(2))
    m = re.match(r"^h(\d{4})$", tcode)
    if m:
        return "%sH1" % m.group(1)
    m = re.match(r"^y(\d{4})$", tcode)
    if m:
        return "%sFY" % m.group(1)
    m = re.match(r"^(pg|sj)(\d{4})$", tcode)
    if m:
        return "%s%s" % (m.group(2), "评估" if m.group(1) == "pg" else "审计")
    return "-"


def main():
    rows = []
    for case, code in CASES:
        src = os.path.join(ROOT, "source_documents", case)
        if not os.path.isdir(src):
            continue
        idmap = build_id_map(code)
        print("%s(%s) 公告索引 %d 条" % (case, code, len(idmap)))
        for fn in sorted(os.listdir(src)):
            if not fn.lower().endswith(".pdf"):
                continue
            # 类型码必须显式枚举：用 ([A-Za-z0-9_]+?) 非贪婪匹配会把 "fl_yijian"
            # 截成 "fl"，标题变成 "yijian_..."，导致该条永远匹配不到公告 ID（真实踩过）。
            m = re.match(r"^(\d{4}-\d{2}-\d{2})_"
                         r"(q\d{4}Q[1-4]|h\d{4}|y\d{4}|pg\d{4}|sj\d{4}|"
                         r"zmsms|fl_yijian|yunying|qt)_(.+)\.pdf$", fn)
            if not m:
                day, tcode, title = "-", "qt", fn
            else:
                day, tcode, title = m.group(1), m.group(2), m.group(3)
            aid = idmap.get((day, norm(title)))
            url = ("https://fund.eastmoney.com/gonggao/%s,%s.html" % (code, aid)
                   if aid else "NOT_IN_API_CACHE")
            sz = os.path.getsize(os.path.join(src, fn)) / 1048576.0
            tp = os.path.join(TXTROOT, code, fn[:-4] + ".txt")
            chars = -1
            if os.path.exists(tp):
                with io.open(tp, encoding="utf-8") as f:
                    chars = len(f.read())
            ocr = "否" if chars >= 5000 else ("待OCR（扫描件）" if chars >= 0 else "未转文本")
            rows.append({
                "case": case, "code": code, "file": fn, "type": tcode,
                "period": period_of(tcode), "disclose_date": day,
                "size_mb": "%.2f" % sz, "pages": "", "text_chars": chars,
                "ocr": ocr, "url": url, "local_path": "source_documents/%s/%s" % (case, fn),
                "status": "OK" if chars >= 5000 else ("OCR_NEEDED" if chars >= 0 else "NO_TEXT"),
            })

    # 登记不可得项：只保留仍然成立的
    rows.append({"case": "sinofarm_reit", "code": "508601", "file": "（资产评估报告原件）",
                 "type": "pg", "period": "-", "disclose_date": "-", "size_mb": "",
                 "pages": "", "text_chars": "", "ocr": "-", "url": "NOT_DISCLOSED",
                 "local_path": "", "status": "SOURCE_UNAVAILABLE"})
    rows.append({"case": "huaxia_shen_international", "code": "180302", "file": "（2024Q1/Q2 季报运营指标表：旧披露格式）",
                 "type": "q2024Q1", "period": "2024Q1/Q2", "disclose_date": "-", "size_mb": "",
                 "pages": "", "text_chars": "", "ocr": "-", "url": "LEGACY_FORMAT",
                 "local_path": "", "status": "NOT_COMPARABLE_FORMAT"})

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case", "code", "file", "type", "period",
                                          "disclose_date", "size_mb", "pages", "text_chars",
                                          "ocr", "url", "local_path", "status"])
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    print("\n写入 %d 条" % len(rows))
    print("case:", dict(Counter(r["case"] for r in rows)))
    print("status:", dict(Counter(r["status"] for r in rows)))
    miss = [r["file"][:50] for r in rows if r["url"] == "NOT_IN_API_CACHE"]
    if miss:
        print("url 未匹配到公告 ID（%d 条）:" % len(miss))
        for x in miss[:8]:
            print("   ", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
