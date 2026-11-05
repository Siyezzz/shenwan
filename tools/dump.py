# -*- coding: utf-8 -*-
"""从已抽取文本中按关键词截取段落，便于人工核对与建表。
用法: python dump.py <code> <file关键子串> <关键词1,关键词2> [窗口行数]
"""
import os, sys, glob

TXT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "reits", "_txt")


def load(code, key):
    d = os.path.join(TXT, code)
    hits = [f for f in os.listdir(d) if key in f]
    if not hits:
        raise SystemExit("no file match: " + key)
    return sorted(hits)[-1], open(os.path.join(d, sorted(hits)[-1]), encoding="utf-8").read()


def blocks(text, kws, win=18):
    lines = text.splitlines()
    page = 0
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("=== P") and ln.endswith("==="):
            try:
                page = int(ln.strip("= P").strip())
            except Exception:
                pass
        for kw in kws:
            if kw in ln:
                seg = lines[max(0, i - 2):i + win]
                out.append((page, kw, "\n".join(seg)))
                break
    return out


if __name__ == "__main__":
    code, key = sys.argv[1], sys.argv[2]
    kws = sys.argv[3].split(",")
    win = int(sys.argv[4]) if len(sys.argv) > 4 else 18
    name, text = load(code, key)
    print("#### FILE:", name, "(%d chars)" % len(text))
    seen = set()
    for page, kw, seg in blocks(text, kws, win):
        h = hash(seg)
        if h in seen:
            continue
        seen.add(h)
        print("\n--- p%d [%s] ---" % (page, kw))
        print(seg)
