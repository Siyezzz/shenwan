# -*- coding: utf-8 -*-
"""扫正文里的自指语、读者语与空转开头，只报位置，不判风格。

用法
    python tools/check_voice.py report.md
    python tools/check_voice.py report.md --section body   # 只看正文（默认）

判据来自 METADATA 的 voice_rules 与 banned_patterns：
    自指语  本报告 / 本文 / 本篇 / 本报告组（作论证主语时才算，但工具一律报出让人工判）
    读者语  读者可以 / 可以看到 / 请注意 / 需要说明的是 / 值得注意的是 / 综上 / 由此可见
    状态码  CONFIRMED / PARTIALLY_SUPPORTED / INDETERMINATE / NOT_COMPARABLE /
            SOURCE_UNAVAILABLE / DATA_QUALITY_WARNING / UNDEFINED_THRESHOLD
    测试语  PASS / FAIL / 断言 / 自检通过
    运行语  run_log / 执行 skill / 按 FLOW 执行 / 产出物 / FLOW #
    修订语  初稿 / 本版 / 上一版 / 修订说明 / 更正清单
    空转    从…来看 / 就…而言 / 整体来看 / 总体而言（段首）
    形容词  显著 / 明显 / 较为 / 一定程度（修饰结论时）

附录不受限（banned_patterns 只管正文），所以默认只扫 `## 附录` 之前。
退出码恒为 0：命中不等于失败，由人决定删还是补参照系。
"""
from __future__ import print_function

import argparse
import io
import os
import re
import sys

RULES = [
    ('自指语', r'本报告|本文|本篇|本报告组'),
    ('读者语', r'读者可以|可以看到|请注意|需要说明的是|值得注意的是|综上|由此可见|不妨'),
    ('状态码', r'CONFIRMED|PARTIALLY_SUPPORTED|INDETERMINATE|NOT_COMPARABLE|'
               r'SOURCE_UNAVAILABLE|DATA_QUALITY_WARNING|UNDEFINED_THRESHOLD'),
    ('测试语', r'\bPASS\b|\bFAIL\b|断言|自检通过'),
    ('运行语', r'run_log|执行\s*skill|按\s*FLOW\s*执行|产出物|FLOW\s*#\d+'),
    ('修订语', r'初稿|本版|上一版|修订说明|更正清单'),
    ('空转开头', r'^\s*(?:从[^，。]{1,12}来看|就[^，。]{1,12}而言|整体来看|总体而言|总的来看)'),
    ('形容词', r'显著|明显|较为|一定程度|某种程度上'),
]


def body_of(md, section):
    lines = md.split('\n')
    if section == 'all':
        return lines, 0
    start, end = 0, len(lines)
    for i, ln in enumerate(lines):
        if re.match(r'^##\s*附录', ln):
            end = i
            break
    return lines[start:end], start


def main(argv=None):
    ap = argparse.ArgumentParser(description='扫自指语与读者语，只报位置')
    ap.add_argument('md')
    ap.add_argument('--section', default='body', choices=['body', 'all'],
                    help='body=只扫正文（默认，附录不受限）；all=全文')
    a = ap.parse_args(argv)

    path = os.path.abspath(a.md)
    if not os.path.isfile(path):
        sys.stderr.write('找不到文件：%s\n' % path)
        return 2
    with io.open(path, 'r', encoding='utf-8') as fp:
        md = fp.read()

    lines, offset = body_of(md, a.section)
    hits = []
    for idx, ln in enumerate(lines):
        if ln.startswith('|') or ln.startswith('!['):
            continue                      # 表格与图注单独看，避免误报
        for name, pat in RULES:
            for m in re.finditer(pat, ln):
                hits.append((offset + idx + 1, name, m.group(0).strip(),
                             ln[max(0, m.start() - 18):m.end() + 22].strip()))

    total_cjk = len(re.findall(u'[\u4e00-\u9fff]', '\n'.join(lines)))
    print('文件  %s' % os.path.basename(path))
    print('范围  %s（%d 行，中文 %d 字）' % ('全文' if a.section == 'all' else '正文至附录前',
                                            len(lines), total_cjk))
    if not hits:
        print('命中  0 处')
        return 0

    print('命中  %d 处（命中不等于失败，逐条决定删或补参照系）\n' % len(hits))
    by = {}
    for ln_no, name, word, ctx in hits:
        by.setdefault(name, []).append((ln_no, word, ctx))
    for name, _ in RULES:
        if name not in by:
            continue
        print('【%s】%d 处' % (name, len(by[name])))
        for ln_no, word, ctx in by[name]:
            print('  L%-5d %-26s …%s…' % (ln_no, word, ctx))
        print('')
    return 0


if __name__ == '__main__':
    sys.exit(main())
