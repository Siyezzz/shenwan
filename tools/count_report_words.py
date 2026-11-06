#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""count_report_words.py — 按"中文正文"口径统计报告字数

为什么需要单独一个工具
----------------------
`tests/run_tests.py` 原来用 `len(re.findall(r"[\\u4e00-\\u9fff]", s))` 统计全文。
这个口径有两个问题：

1. 附录、来源索引、自检表全被计入。把附录堆到 5,000 字，正文只写 10,000 字，
   也能"达标"——这正是本工具要堵的漏洞。
2. 中文、英文、数字混成一个数。报告写"17,559 个中文字符"时，实际包含了
   英文缩写与数字，读者无法判断这 17,559 到底是中文还是总字符。

本工具的原则：**只统计读者真正会读的正文，且四类字符分开报**。

口径定义
--------
计入：一级章节标题以数字开头的章节（"## 1 投资摘要…"、"## 4 运营…"），
      含该章内的表格文字与公式块文字。
不计：第一个 `## ` 之前的内容（封面）、标题含"附录/参考文献/来源索引/
      执行记录/自检/版本变更"的章节、目录。
分开报：中文（CJK）、英文字母、数字字符、Markdown 总字符——四项不得合并。

用法
----
    python tools/count_report_words.py outputs/case_03_sinofarm_reit/report_508601.md
    python tools/count_report_words.py <file> --min 15000 --json out.json --sections
"""
import argparse
import io
import json
import os
import re
import sys

CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")
DIGIT = re.compile(r"[0-9]")

# 标题含以下关键词即整章排除（附录类）
EXCLUDE_KEYS = ("附录", "参考文献", "来源索引", "执行记录", "自检", "版本变更",
                "纠错记录", "数据来源索引", "运行日志", "目录")
# 一级章节标题须以数字或"第X章"开头才计入正文
BODY_HEAD = re.compile(r"^(第[一二三四五六七八九十]+章|\d+)[\s.、：:]")


def split_sections(text):
    """按二级标题切分，返回 [(title, body)]；首段 title=''"""
    lines = text.splitlines(True)
    out, cur, buf = [], "", []
    for ln in lines:
        if ln.startswith("## "):
            out.append((cur, "".join(buf)))
            cur, buf = ln[3:].strip(), []
        else:
            buf.append(ln)
    out.append((cur, "".join(buf)))
    return out


def is_body(title):
    if not title:
        return False
    if any(k in title for k in EXCLUDE_KEYS):
        return False
    return bool(BODY_HEAD.match(title))


def dup_30(body):
    """连续 30 个中文字符的重复片段数（用于反注水）"""
    plain = "".join(CJK.findall(body))
    seen, dup = set(), 0
    for i in range(0, max(0, len(plain) - 29)):
        seg = plain[i:i + 30]
        if seg in seen:
            dup += 1
        else:
            seen.add(seg)
    return dup


def longest_para(body):
    best = 0
    for para in re.split(r"\n\s*\n", body):
        if para.strip().startswith("|") or para.strip().startswith("```"):
            continue   # 表格与代码块不计入段落长度
        best = max(best, len(CJK.findall(para)))
    return best


def analyze(path, min_body=15000):
    text = io.open(path, encoding="utf-8").read()
    secs = split_sections(text)
    rows, body = [], []
    for title, content in secs:
        cjk = len(CJK.findall(content))
        keep = is_body(title)
        rows.append({"title": title or "(封面与前置信息)", "cjk": cjk, "body": keep})
        if keep:
            body.append(content)
    body_txt = "\n".join(body)
    res = {
        "report": path.replace("\\", "/"),
        "cjk_body": len(CJK.findall(body_txt)),
        "cjk_total": len(CJK.findall(text)),
        "latin_body": len(LATIN.findall(body_txt)),
        "digit_body": len(DIGIT.findall(body_txt)),
        "md_total_chars": len(text),
        "figures": len(re.findall(r"^图\s*\d+", text, flags=re.M)),
        "tables": len(re.findall(r"^表\s*\d+", text, flags=re.M)),
        "we_think_count": text.count("我们认为"),
        "longest_paragraph_cjk": longest_para(body_txt),
        "duplicate_30char": dup_30(body_txt),
        "min_required": min_body,
        "pass": len(CJK.findall(body_txt)) >= min_body,
        "sections": rows,
    }
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--min", type=int, default=15000)
    ap.add_argument("--json", default="")
    ap.add_argument("--sections", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(a.path):
        print("找不到文件：%s" % a.path)
        return 2
    r = analyze(a.path, a.min)

    print("=" * 68)
    print("报告：%s" % r["report"])
    print("=" * 68)
    print("中文正文字符数        %8d   （下限 %d）" % (r["cjk_body"], r["min_required"]))
    print("中文全文（含附录）    %8d" % r["cjk_total"])
    print("英文正文字母数        %8d" % r["latin_body"])
    print("正文数字字符数        %8d" % r["digit_body"])
    print("Markdown 总字符数     %8d" % r["md_total_chars"])
    print("-" * 68)
    print("图 %d 张 / 表 %d 张 / \"我们认为\" %d 次 / 最长段 %d 字 / 30 字重复 %d 处"
          % (r["figures"], r["tables"], r["we_think_count"],
             r["longest_paragraph_cjk"], r["duplicate_30char"]))
    print("统计口径：中文正文，不含封面、目录、附录、参考文献、来源索引与运行日志")
    print("是否达到要求：%s" % ("是" if r["pass"] else "否"))

    if a.sections:
        print("-" * 68)
        print("%-52s %8s %s" % ("章节", "中文字符", "计入"))
        for s in r["sections"]:
            print("%-52s %8d %s" % (s["title"][:50], s["cjk"],
                                    "正文" if s["body"] else "不计"))

    if a.json:
        d = os.path.dirname(a.json)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        io.open(a.json, "w", encoding="utf-8").write(
            json.dumps(r, ensure_ascii=False, indent=2))
        print("-" * 68)
        print("指标已写入 %s" % a.json)

    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
