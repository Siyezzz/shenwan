# -*- coding: utf-8 -*-
"""生成/校验 skills/*/_raw_response.txt
规则（继承附件 531887 的自闭合风格，并修正另外 10 套只有文末单标记的问题）：
  <<<FILE: SKILL.md>>> ... <<<END: SKILL.md>>>
  <<<FILE: METADATA.md>>> ... <<<END: METADATA.md>>>
  <<<FILE: FLOW.md>>> ... <<<END: FLOW.md>>>
  <<<END>>>
"""
import os, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills")
ORDER = ["SKILL.md", "METADATA.md", "FLOW.md"]


def build(name):
    d = os.path.join(SK, name)
    parts = []
    for f in ORDER:
        p = os.path.join(d, f)
        txt = open(p, encoding="utf-8").read()
        if f == "FLOW.md" and "--{abstract}--" not in txt:
            raise SystemExit("FLOW 缺 abstract: " + p)
        parts.append("<<<FILE: %s>>>\n%s\n<<<END: %s>>>\n" % (f, txt.rstrip("\n"), f))
    raw = "".join(parts) + "<<<END>>>\n"
    open(os.path.join(d, "_raw_response.txt"), "w", encoding="utf-8", newline="\n").write(raw)
    return raw


def split(raw):
    """把 raw 拆回 dict，用于可逆性校验"""
    out, cur, buf = {}, None, []
    for line in raw.splitlines(True):
        s = line.strip()
        if s.startswith("<<<FILE: ") and s.endswith(">>>"):
            cur = s[9:-3].strip()
            buf = []
        elif s.startswith("<<<END: ") and s.endswith(">>>"):
            out[cur] = "".join(buf)
            cur, buf = None, []
        elif s == "<<<END>>>":
            continue
        elif cur:
            buf.append(line)
    return out


def main():
    names = [d for d in os.listdir(SK) if os.path.isdir(os.path.join(SK, d))]
    ok = True
    for n in sorted(names):
        raw = build(n)
        back = split(raw)
        for f in ORDER:
            orig = open(os.path.join(SK, n, f), encoding="utf-8").read().rstrip("\n")
            same = back.get(f, "").rstrip("\n") == orig
            ok &= same
            print("%-6s %-32s %-12s %7d chars  split=%s" %
                  ("OK" if same else "DIFF", n, f, len(orig), "match" if same else "MISMATCH"))
        print("       raw=%d chars, sha1=%s" % (len(raw), hashlib.sha1(raw.encode()).hexdigest()[:12]))
    print("\nALL_MATCH" if ok else "\nHAS_MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
