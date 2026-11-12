# -*- coding: utf-8 -*-
"""记者腔检查（reits-report-writing 的 voice_rules / E-9 可机检部分）

用法：
    python tools/check_voice.py <report.md> [--appendix 附录]

只查三件可机检的事，不判断文采：
  V-1 自指语   正文出现「本报告/本文/本篇」作论证主语
  V-7 读者语   正文出现「读者/综上/由此可见/需要说明的是/值得注意的是」
  V-3 裸数字   含「万元/亿元」的句子，没有占比、相当于、或与对手比较

正文 = 全文减去附录（从第一个以「附录」开头的标题起）。
只作文本定位，不判 FAIL：命中数写进 report_metrics.json 的 self_ref_hits 等字段。
"""
import io
import re
import sys

SELF_REF = ["本报告", "本文", "本篇"]
READER = ["读者", "综上", "由此可见", "需要说明的是", "值得注意的是", "请注意"]
# 数字后是否有参照系：占比 / 相当于 / 比较词
ANCHOR_WORDS = ["相当于", "占", "比", "%", "个百分点", "pct", "倍", "分之", "高于", "低于", "多出", "少了"]
MONEY = re.compile(r"[\d,\.]+\s*(万元|亿元)")


def split_body(text, appendix_kw="附录"):
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#") and appendix_kw in ln:
            return "\n".join(lines[:i]), "\n".join(lines[i:])
    return text, ""


def sentences(text):
    # 以句号、分号、换行断句；表格行整体算一句
    parts = re.split(r"(?<=[。；!?])|\n", text)
    return [p.strip() for p in parts if p.strip()]


def scan(text):
    body, _ = split_body(text)
    hits = {"self_ref": [], "reader": [], "bare_number": []}

    for kw in SELF_REF:
        for m in re.finditer(kw, body):
            s = body[max(0, m.start() - 18): m.start() + 22].replace("\n", " ")
            hits["self_ref"].append(s)
    for kw in READER:
        for m in re.finditer(kw, body):
            s = body[max(0, m.start() - 18): m.start() + 22].replace("\n", " ")
            hits["reader"].append(s)

    for sent in sentences(body):
        if not MONEY.search(sent):
            continue
        if any(w in sent for w in ANCHOR_WORDS):
            continue
        if len(sent) > 6:
            hits["bare_number"].append(sent[:60])
    return hits


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    text = io.open(path, encoding="utf-8").read()
    h = scan(text)

    print("文件：%s" % path)
    print("自指语 V-1      %3d 处" % len(h["self_ref"]))
    print("读者语 V-7      %3d 处" % len(h["reader"]))
    print("裸数字 V-3      %3d 处" % len(h["bare_number"]))
    for name, label in (("self_ref", "自指"), ("reader", "读者"), ("bare_number", "裸数字")):
        if h[name]:
            print("\n[%s] 前 6 条：" % label)
            for s in h[name][:6]:
                print("  - " + s)
    ok = not (h["self_ref"] or h["reader"])
    print("\n判定：%s" % ("通过（自指与读者语 0 处）" if ok else "需改写（自指或读者语未清零）"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
