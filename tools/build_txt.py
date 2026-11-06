#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_txt.py — 把 source_documents 下的 PDF 转成带页码标记的文本

输出到 <仓库同级>/reits/_txt/<code>/<同名>.txt，格式与既有文本层一致：

    === P1 ===
    页面文字...
    === P2 ===
    ...

为什么单独一层文本
------------------
下游的 extract_panel.py 靠 `=== Pn ===` 反推页码，用来生成 anchor（"2025Q4 p7"）。
如果直接改 PDF 解析，页码锚点会全部失效——而 anchor 是"每个数字能追到哪一页"的
唯一凭证，不能退化。

幂等：txt 比 pdf 新则跳过。扫描件（无文字层）会写出空文件并在末尾标注，
调用方可据此判断是否需要 OCR。
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXTROOT = os.path.join(os.path.dirname(ROOT), "reits", "_txt")

CASES = {
    "glp_reit": "508056",
    "huaxia_shen_international": "180302",
    "sinofarm_reit": "508601",
}


def convert(pdf_path, txt_path):
    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    chunks = []
    for i, page in enumerate(reader.pages, 1):
        try:
            t = page.extract_text() or ""
        except Exception:
            t = ""
        chunks.append("\n=== P%d ===\n%s" % (i, t.strip()))
    body = "\n".join(chunks)
    if len(body.replace("=", "").strip()) < 200:
        body += "\n\n[[NO_TEXT_LAYER: 疑似扫描件，需 OCR]]"
    with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return len(reader.pages), len(body)


def main():
    force = "--force" in sys.argv
    only = None
    max_mb = None
    min_mb = None
    for i, a in enumerate(sys.argv[1:]):
        if a in CASES:
            only = a
        if a == "--max-mb":
            max_mb = float(sys.argv[i + 2])
        if a == "--min-mb":
            min_mb = float(sys.argv[i + 2])
    total = done = skipped = failed = 0
    for case, code in CASES.items():
        if only and case != only:
            continue
        src = os.path.join(ROOT, "source_documents", case)
        dst = os.path.join(TXTROOT, code)
        if not os.path.isdir(src):
            continue
        os.makedirs(dst, exist_ok=True)
        for fn in sorted(os.listdir(src)):
            if not fn.lower().endswith(".pdf"):
                continue
            sp = os.path.join(src, fn)
            mb = os.path.getsize(sp) / 1048576.0
            if max_mb is not None and mb > max_mb:
                continue
            if min_mb is not None and mb < min_mb:
                continue
            total += 1
            tp = os.path.join(dst, fn[:-4] + ".txt")
            if (not force) and os.path.exists(tp) and os.path.getmtime(tp) >= os.path.getmtime(sp):
                skipped += 1
                continue
            try:
                pages, chars = convert(sp, tp)
                done += 1
                flag = ""
                if chars < 1500:
                    flag = "  [警告：文字极少，疑似扫描件]"
                print("  OK %-58s %3d 页 %7d 字符%s" % (fn[:56], pages, chars, flag))
            except Exception as e:
                failed += 1
                print("  FAIL %s -> %s" % (fn[:50], e))
    print("\n新转 %d / 跳过 %d / 失败 %d / 共 %d" % (done, skipped, failed, total))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
