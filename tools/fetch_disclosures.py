#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch_disclosures.py — 公募 REITs 法定披露文件抓取器

背景
----
上交所公告接口 query.sse.com.cn 需要内部 channelId，公开 HTTP 无法枚举（已记为
SOURCE_UNAVAILABLE）。本脚本改用东方财富基金公告接口，按“公告分类”枚举：

    type=1  基金文件（招募说明书、基金合同、托管协议、法律意见书、产品资料概要）
    type=2  收益分配公告
    type=3  定期报告（季报 / 中期报告 / 年报 / 年度评估报告 / 年度审计报告）
    type=6  临时公告（运营数据、开放日、流动性服务商等）

关键点：type 参数必须显式指定。只查 type=1 会漏掉全部定期报告——本项目的
案例二曾因此缺 2025Q1、Q2 季报，报告却没有任何说明（见 ITERATION_LOG 第 5 轮）。

用法
----
    python tools/fetch_disclosures.py --dry-run          # 只列清单，不下载
    python tools/fetch_disclosures.py --since 2024-01-01 # 下载该日期之后的
    python tools/fetch_disclosures.py --code 180302      # 只处理一只

设计约束
--------
1. 幂等：目标文件已存在则跳过，不重复下载；
2. 命名：`日期_类型码_原始标题.pdf`，类型码与既有文件保持一致
   （q2025Q1 / h2025 / y2025 / pg2025 / sj2025 / zmsms / fl_yijian / yunying / qt）；
3. 只改 source_documents/，不碰任何产出物；
4. 下载失败不静默：逐条打印原因，最后汇总。
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CASES = {
    "508056": "glp_reit",
    "180302": "huaxia_shen_international",
    "508601": "sinofarm_reit",
}

LIST_API = ("https://api.fund.eastmoney.com/f10/JJGG"
            "?fundcode={code}&pageIndex=1&pageSize=100&type={ty}")
PDF_TPL = "https://pdf.dfcfw.com/pdf/H2_{id}_1.pdf"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://fundf10.eastmoney.com/",
}
TYPES = {1: "基金文件", 2: "收益分配", 3: "定期报告", 6: "临时公告"}

# 白名单：只保留研究必需的六类。其余（基金合同、托管协议、产品资料概要、
# 询价/发售/配售公告、战略投资者核查、流动性服务商等）一律跳过——
# 它们对"结构—资产—现金流—估值—风险"分析没有增量信息，只会让目录噪音化。
KEEP_RULES = [
    r"第[1-4]季度报告",
    r"中期报告",
    r"年度报告",
    r"年度评估报告",
    r"年度审计报告",
    r"招募说明书",
    r"法律意见书",
    r"运营数据",
    r"经营情况",
    r"基金合同",     # 投前分析要看交易结构、费用与分配条款；此前按“非必需”过滤，
                      # 却在文档里写成“不可得”，属把可得当不可得，已纠正
    r"托管协议",
]
# 过程稿排除：草案 / 申报稿 / 反馈回复稿。同一份招募书会有 4–5 个版本，
# 全下会让"哪一个才是定价依据"变成新的歧义来源。
DRAFT_RULES = [r"\(草案\)", r"（草案）", r"\(申报稿\)", r"（申报稿）", r"\(反馈回复稿\)", r"（反馈回复稿）"]


def keep(title):
    for d in DRAFT_RULES:
        if re.search(d, title):
            return False
    return any(re.search(k, title) for k in KEEP_RULES)


# 标题 → 类型码。顺序敏感：先匹配更具体的。
PATTERNS = [
    (r"(\d{4})年第([1-4])季度报告", lambda m: "q%sQ%s" % (m.group(1), m.group(2))),
    (r"(\d{4})年中期报告", lambda m: "h%s" % m.group(1)),
    (r"(\d{4})年年度评估报告|(\d{4})年度评估报告", lambda m: "pg%s" % (m.group(1) or m.group(2))),
    (r"(\d{4})年年度审计报告|(\d{4})年度审计报告", lambda m: "sj%s" % (m.group(1) or m.group(2))),
    (r"(\d{4})年年度报告", lambda m: "y%s" % m.group(1)),
    (r"招募说明书", lambda m: "zmsms"),
    (r"法律意见书", lambda m: "fl_yijian"),
    (r"运营数据|经营情况", lambda m: "yunying"),
    (r"评估报告", lambda m: "pg"),
    (r"审计报告", lambda m: "sj"),
]


def classify(title):
    for pat, fn in PATTERNS:
        m = re.search(pat, title)
        if m:
            return fn(m)
    return "qt"


def fetch_list(code, ty, retry=3):
    url = LIST_API.format(code=code, ty=ty)
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8")
            data = json.loads(raw)
            return data.get("Data") or []
        except Exception as e:
            if i == retry - 1:
                print("  [WARN] type=%d 列表获取失败：%s" % (ty, e))
                return []
            time.sleep(2)
    return []


def safe_name(s):
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    return s.replace("（", "(").replace("）", ")")


def existing_keys(directory):
    """已存在文件的 (日期, 类型码) 集合，用于幂等判断。"""
    keys = set()
    if not os.path.isdir(directory):
        return keys
    for fn in os.listdir(directory):
        m = re.match(r"^(\d{4}-\d{2}-\d{2})_([A-Za-z0-9]+)_", fn)
        if m:
            keys.add((m.group(1), m.group(2)))
        else:
            m2 = re.match(r"^(\d{4}-\d{2}-\d{2})_", fn)
            if m2:
                keys.add((m2.group(1), "?"))
    return keys


def download(item, directory, dry_run=False):
    aid = item["ID"]
    title = item["TITLE"]
    day = item["PUBLISHDATEDesc"]
    tcode = classify(title)
    fn = "%s_%s_%s.pdf" % (day, tcode, safe_name(title))
    if len(fn) > 150:
        fn = fn[:146] + ".pdf"
    path = os.path.join(directory, fn)
    if os.path.exists(path):
        return ("SKIP", path, 0)
    if dry_run:
        return ("DRY", path, 0)
    url = PDF_TPL.format(id=aid)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        blob = urllib.request.urlopen(req, timeout=60).read()
        if not blob.startswith(b"%PDF"):
            return ("BAD", path, 0)
        with open(path, "wb") as f:
            f.write(blob)
        return ("OK", path, len(blob))
    except Exception as e:
        return ("FAIL", "%s (%s)" % (path, e), 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", default=None, help="只处理某只基金")
    ap.add_argument("--since", default="2024-01-01", help="只取该日期之后的公告")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--types", default="1,3", help="公告分类，默认 1,3")
    args = ap.parse_args()

    codes = [args.code] if args.code else list(CASES)
    want = [int(x) for x in args.types.split(",")]
    tally = {}

    for code in codes:
        case = CASES[code]
        directory = os.path.join(ROOT, "source_documents", case)
        os.makedirs(directory, exist_ok=True)
        have = existing_keys(directory)
        print("\n===== %s (%s) 目录已有 %d 份 =====" %
              (code, case, len([f for f in os.listdir(directory) if f.endswith(".pdf")])))

        items = []
        for ty in want:
            for it in fetch_list(code, ty):
                it["_ty"] = ty
                items.append(it)
        items.sort(key=lambda x: (x["PUBLISHDATEDesc"], x["TITLE"]))

        for it in items:
            if it["PUBLISHDATEDesc"] < args.since:
                continue
            if not keep(it["TITLE"]):
                tally["FILTER"] = tally.get("FILTER", 0) + 1
                continue
            tcode = classify(it["TITLE"])
            if (it["PUBLISHDATEDesc"], tcode) in have:
                tally["EXIST"] = tally.get("EXIST", 0) + 1
                continue
            status, path, size = download(it, directory, args.dry_run)
            tally[status] = tally.get(status, 0) + 1
            if status in ("OK", "DRY", "BAD", "FAIL"):
                print("  %-4s %s  %-10s %s" % (
                    status,
                    it["PUBLISHDATEDesc"],
                    tcode,
                    os.path.basename(path)[:60] + ("" if status == "DRY" else "  %.2fMB" % (size / 1048576.0) if status == "OK" else "")))

    print("\n===== 汇总 =====")
    for k, v in sorted(tally.items()):
        print("  %-6s %d" % (k, v))
    if args.dry_run:
        print("  （dry-run，未写入任何文件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
