#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_claims.py —— claim 台账与裁决表的结构校验（对应 METADATA.claim_schema v2）

问题来源：同一只 REIT 换一次运行，claim 的列数、态名、条数、ID 全都变了。
根因是规范本身三处不一致（METADATA 9 列 / FLOW 5 列 / 实际 8 列；3 态与 4 态并存）。
本脚本把 schema 变成可执行的断言，跑不过就不许交付。

用法：
  python tools/check_claims.py --output <产出目录> [--code 508056]
  python tools/check_claims.py --verdict claims_verdict_508056.csv --ledger claims_508056.yaml

退出码：0 全通过；1 有 FAIL。

  CC1  列名与顺序等于 14 列 schema
  CC2  claim_id 形如 C-[0-9a-f]{6}，表内唯一
  CC3  ledger 内同一 claim_id 不得有两个不同 statement 并存（改口径须新增 SUPERSEDED 条目）
  CC4  source_bucket ∈ S1_契约义务/S2_招募书预测/S3_管理层表述/S4_扩募评估
  CC5  verdict ∈ 六态；judgment_rule ∈ 五枚举；threshold_* 类必须有 rule_param
  CC6  direction_only 不得判 CONFIRMED（没有数字就没有达标）
  CC7  CONFIRMED 须 periods_covered 非空、observed 不含否定观测词
  CC8  台账条数 ≤ 12，且 S1 桶至少 1 条
  CC9  observed 不得含空判词（符合预期/基本达标/大致相符…）
  CC10 ledger 与 verdict 的 claim_id 集合一致（verdict 不得凭空新增或漏项）
"""
import argparse
import csv
import os
import re
import sys

COLUMNS = ["seq", "claim_id", "statement", "origin_file", "origin_page", "quote",
           "source_bucket", "indicator", "judgment_rule", "rule_param",
           "aggregation", "periods_covered", "observed", "verdict"]

BUCKETS = {"S1_契约义务", "S2_招募书预测", "S3_管理层表述", "S4_扩募评估"}
VERDICTS = {"CONFIRMED", "REFUTED", "PARTIALLY_SUPPORTED",
            "INDETERMINATE", "NOT_COMPARABLE", "SUPERSEDED"}
RULES = {"threshold_gte", "threshold_lte", "each_period_eq", "monotonic", "direction_only"}
AGGREGATIONS = {"each_period", "mean", "latest"}

ID_RE = re.compile(r"^C-[0-9a-f]{6}$")
ID_FIND_RE = re.compile(r"claim_id:\s*[\"']?(C-[0-9a-f]{6})")
STMT_PAIR_RE = re.compile(r"claim_id:\s*[\"']?(C-[0-9a-f]{6})[\"']?[\s\S]{0,400}?statement:\s*[\"']?(.{0,120})")

EMPTY_JUDGE = ["符合预期", "基本达标", "大致相符", "基本一致", "表现良好",
               "符合计划", "按计划推进", "整体平稳", "无异常"]
NEG_IN_OBSERVED = ["未达标", "未披露", "未公布", "无法取得", "缺失"]


def read_csv_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), list(r)


def find_one(out, prefix, exts):
    if not os.path.isdir(out):
        return None
    hits = [os.path.join(out, f) for f in sorted(os.listdir(out))
            if f.startswith(prefix) and os.path.splitext(f)[1].lower() in exts]
    return hits[0] if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", help="产出目录，自动定位 claims_*.yaml 与 claims_verdict_*.csv")
    ap.add_argument("--verdict", help="裁决表 csv 路径")
    ap.add_argument("--ledger", help="台账 yaml 路径")
    ap.add_argument("--code", help="基金代码，用于拼文件名")
    args = ap.parse_args()

    verdict_path = args.verdict
    ledger_path = args.ledger
    if args.output:
        if args.code:
            verdict_path = verdict_path or os.path.join(args.output, "claims_verdict_%s.csv" % args.code)
            ledger_path = ledger_path or os.path.join(args.output, "claims_%s.yaml" % args.code)
        else:
            verdict_path = verdict_path or find_one(args.output, "claims_verdict_", {".csv"})
            ledger_path = ledger_path or find_one(args.output, "claims_", {".yaml", ".yml"})

    fails, warns, notes = [], [], []

    if not verdict_path or not os.path.exists(verdict_path):
        print("[FAIL] CC1 裁决表缺失：claims_verdict_<code>.csv")
        print("结果：FAIL（1 项）。")
        return 1

    header, rows = read_csv_rows(verdict_path)

    # ---------- CC1 列名与顺序 ----------
    if header != COLUMNS:
        missing = [c for c in COLUMNS if c not in header]
        extra = [c for c in header if c not in COLUMNS]
        detail = []
        if missing:
            detail.append("缺 " + ",".join(missing))
        if extra:
            detail.append("多 " + ",".join(extra))
        if not detail:
            detail.append("顺序不符")
        fails.append("CC1 列不符 14 列 schema：%s" % "；".join(detail))
    else:
        notes.append("CC1 列结构合规：%d 列，%d 行" % (len(COLUMNS), len(rows)))

    # ---------- CC2 ID 格式与唯一 ----------
    ids = [(r.get("claim_id") or "").strip() for r in rows]
    bad_id = [i for i in ids if not ID_RE.match(i)]
    if bad_id:
        fails.append("CC2 claim_id 格式错误 %d 个（应为 C-六位十六进制）：%s" % (len(bad_id), bad_id[0]))
    elif len(set(ids)) != len(ids):
        dup = [i for i in set(ids) if ids.count(i) > 1]
        fails.append("CC2 claim_id 重复：%s" % ",".join(dup[:4]))
    else:
        notes.append("CC2 claim_id 全部合规且唯一")

    # ---------- CC4/CC5 桶、态、规则 ----------
    bad_bucket = [(r.get("claim_id"), r.get("source_bucket")) for r in rows
                  if (r.get("source_bucket") or "").strip() not in BUCKETS]
    if bad_bucket:
        fails.append("CC4 来源桶越界 %d 条：%s" % (len(bad_bucket), bad_bucket[0]))
    bad_verdict = [(r.get("claim_id"), r.get("verdict")) for r in rows
                   if (r.get("verdict") or "").strip() not in VERDICTS]
    if bad_verdict:
        fails.append("CC5 裁决态非法 %d 条：%s" % (len(bad_verdict), bad_verdict[0]))
    bad_rule = [(r.get("claim_id"), r.get("judgment_rule")) for r in rows
                if (r.get("judgment_rule") or "").strip() not in RULES]
    if bad_rule:
        fails.append("CC5 判定规则非法 %d 条：%s" % (len(bad_rule), bad_rule[0]))
    bad_agg = [(r.get("claim_id"), r.get("aggregation")) for r in rows
               if (r.get("aggregation") or "").strip() not in AGGREGATIONS]
    if bad_agg:
        fails.append("CC5 聚合方式非法 %d 条：%s" % (len(bad_agg), bad_agg[0]))
    no_param = [r.get("claim_id") for r in rows
                if (r.get("judgment_rule") or "").strip().startswith("threshold_")
                and not (r.get("rule_param") or "").strip()]
    if no_param:
        fails.append("CC5 阈值规则缺 rule_param %d 条：%s" % (len(no_param), no_param[0]))

    # ---------- CC6 direction_only 不得 CONFIRMED ----------
    cheat = [r.get("claim_id") for r in rows
             if (r.get("judgment_rule") or "").strip() == "direction_only"
             and (r.get("verdict") or "").strip() == "CONFIRMED"]
    if cheat:
        fails.append("CC6 direction_only 被判 CONFIRMED %d 条：%s（无量化阈值不得判达标）"
                     % (len(cheat), ",".join(cheat[:4])))

    # ---------- CC7 CONFIRMED 的证据自洽 ----------
    weak = []
    for r in rows:
        if (r.get("verdict") or "").strip() != "CONFIRMED":
            continue
        obs = r.get("observed") or ""
        periods = (r.get("periods_covered") or "").strip()
        if not periods or any(w in obs for w in NEG_IN_OBSERVED):
            weak.append(r.get("claim_id"))
    if weak:
        fails.append("CC7 CONFIRMED 证据不自洽 %d 条：%s（观测期为空或含否定观测词）"
                     % (len(weak), ",".join(weak[:4])))

    # ---------- CC8 条数与 S1 覆盖 ----------
    if len(rows) > 12:
        fails.append("CC8 台账 %d 条超上限 12" % len(rows))
    if not any((r.get("source_bucket") or "").strip() == "S1_契约义务" for r in rows):
        fails.append("CC8 缺 S1 契约义务条目（义务条款是台账的底线，不可缺）")

    # ---------- CC9 空判词 ----------
    empty = []
    for r in rows:
        obs = r.get("observed") or ""
        hit = [w for w in EMPTY_JUDGE if w in obs]
        if hit:
            empty.append("%s「%s」" % (r.get("claim_id"), hit[0]))
    if empty:
        fails.append("CC9 observed 含空判词 %d 条：%s（须写数值或算式）" % (len(empty), "; ".join(empty[:3])))

    # ---------- CC3/CC10 台账比对 ----------
    if ledger_path and os.path.exists(ledger_path):
        txt = open(ledger_path, encoding="utf-8").read()
        ledger_ids = ID_FIND_RE.findall(txt)
        if not ledger_ids:
            fails.append("CC3 台账未解析出 claim_id：%s" % os.path.basename(ledger_path))
        else:
            pair = {}
            conflict = []
            for cid, stmt in STMT_PAIR_RE.findall(txt):
                s = stmt.strip().strip('"').strip("'")
                if cid in pair and pair[cid] != s:
                    conflict.append(cid)
                pair[cid] = s
            if conflict:
                fails.append("CC3 同一 claim_id 并存两个 statement：%s（应新增 SUPERSEDED 条目）"
                             % ",".join(sorted(set(conflict))[:4]))
            if len(set(ledger_ids)) != len(ledger_ids):
                dups = [i for i in set(ledger_ids) if ledger_ids.count(i) > 1]
                fails.append("CC3 台账 claim_id 重复：%s" % ",".join(dups[:4]))
            miss = [i for i in set(ledger_ids) if i not in set(ids)]
            extra = [i for i in set(ids) if i not in set(ledger_ids)]
            if miss:
                fails.append("CC10 台账有 %d 条未裁决：%s" % (len(miss), ",".join(sorted(miss)[:4])))
            if extra:
                fails.append("CC10 裁决表出现台账外条目 %d 条：%s" % (len(extra), ",".join(sorted(extra)[:4])))
            if not miss and not extra:
                notes.append("CC10 台账与裁决表 %d 条一一对应" % len(set(ledger_ids)))
    else:
        warns.append("CC3/CC10 跳过：未找到 claims_<code>.yaml 台账")

    print("=" * 68)
    print("check_claims  verdict=%s" % os.path.basename(verdict_path))
    print("              ledger=%s" % (os.path.basename(ledger_path) if ledger_path else "N/A"))
    print("=" * 68)
    for n in notes:
        print("  [INFO] " + n)
    for w in warns:
        print("  [WARN] " + w)
    for f in fails:
        print("  [FAIL] " + f)
    print("-" * 68)
    if fails:
        print("结果：FAIL（%d 项）。按 claim_schema v2，未通过不得进入报告。" % len(fails))
        return 1
    print("结果：PASS。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
