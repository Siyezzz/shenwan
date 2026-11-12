#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""panel.csv 结构校验（对应 METADATA 的 metric_naming.validation）

    python tools/check_panel.py --panel output/20261112_1340/panel.csv

  T-DQ-01 主键唯一：(period, dim, metric) 不得重复
  T-DQ-02 取值可解析：value 必须是数字；空值只允许出现在 quality != OK 的行
  T-DQ-03 锚点格式：anchor 必须形如 `<tag> p<page>` 或 `<tag> p<a>-<b>`
  T-DQ-12 累计单调：同一 (dim, metric, 年度) 内，*_cum 序列不得下降

只依赖标准库。退出码非 0 即视为数据层不合格。
"""
from __future__ import annotations

import argparse
import csv
import re
import sys

ANCHOR_RE = re.compile(r"^(?:q|h|y)\d{4}(?:Q[1-4]|H[1-2])?\s*p\.?\s*\d+(\s*[-–]\s*\d+)?$")


def year_of(period):
    m = re.match(r"(\d{4})", str(period))
    return m.group(1) if m else str(period)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.panel, encoding="utf-8-sig", newline="")))
    fails, notes = [], []
    notes.append("panel 共 %d 行" % len(rows))

    # T-DQ-01
    seen, dup = set(), []
    for r in rows:
        k = (r.get("period"), r.get("dim"), r.get("metric"))
        if k in seen:
            dup.append(k)
        seen.add(k)
    if dup:
        fails.append("T-DQ-01 主键重复 %d 处：%s" % (len(dup), dup[0]))

    # T-DQ-02 / 03
    bad_val, bad_anchor = [], []
    for r in rows:
        v = (r.get("value") or "").strip()
        if v == "":
            if (r.get("quality") or "OK").strip().upper() == "OK":
                bad_val.append("%s/%s/%s 空值但 quality=OK" % (r.get("period"), r.get("dim"), r.get("metric")))
        else:
            try:
                float(v.replace(",", ""))
            except ValueError:
                bad_val.append("%s 无法解析为数值" % v)
        if not ANCHOR_RE.match((r.get("anchor") or "").strip()):
            bad_anchor.append("%s/%s 锚点=%r" % (r.get("period"), r.get("metric"), r.get("anchor")))
    if bad_val:
        fails.append("T-DQ-02 取值异常 %d 处：%s" % (len(bad_val), bad_val[0]))
    if bad_anchor:
        fails.append("T-DQ-03 锚点格式异常 %d 处：%s" % (len(bad_anchor), bad_anchor[0]))

    # T-DQ-12
    seq = {}
    for r in rows:
        m = (r.get("metric") or "")
        if not m.endswith("_cum"):
            continue
        v = (r.get("value") or "").strip()
        if v == "":
            continue
        key = (r.get("dim"), m, year_of(r.get("period")))
        seq.setdefault(key, []).append((str(r.get("period")), float(v.replace(",", ""))))
    drops = []
    for key, arr in seq.items():
        for (p0, v0), (p1, v1) in zip(arr, arr[1:]):
            if v1 < v0:
                drops.append("%s %s %s→%s：%s→%s" % (key[1], key[2], p0, p1, v0, v1))
    if drops:
        fails.append("T-DQ-12 累计下降 %d 处：%s" % (len(drops), drops[0]))
    else:
        notes.append("T-DQ-12 通过：%d 组 *_cum 序列均单调不减" % len(seq))

    print("=" * 60)
    print("check_panel  %s" % args.panel)
    print("=" * 60)
    for n in notes:
        print("  [INFO] " + n)
    for f in fails:
        print("  [FAIL] " + f)
    print("-" * 60)
    if fails:
        print("结果：FAIL（%d 项）" % len(fails))
        return 1
    print("结果：PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
