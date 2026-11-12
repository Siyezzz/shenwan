# -*- coding: utf-8 -*-
"""统计报告正文字数：中文正文字符 / 英文字母 / 数字字符 / 总字符，四项分开报。

用法
    python tools/count_report_words.py report.md
    python tools/count_report_words.py report.md --verbose     # 分章列出
    python tools/count_report_words.py report.md --floor 3000 # 只判下限

口径（与 METADATA 的 word_count_policy 一致）
    计入   正文各章，含正文内表格中的分析性文字
    不计入 封面（第一个二级标题之前）、附录（`## 附录` 起）、图表语法本身
    计数   中文字符按 [\\u4e00-\\u9fff]；英文字母、数字分别计；总字符计可见字符
"""
from __future__ import print_function

import argparse
import io
import os
import re
import sys

CJK = re.compile(u'[\u4e00-\u9fff]')
LATIN = re.compile(r'[A-Za-z]')
DIGIT = re.compile(r'[0-9]')


def strip_markup(s):
    """去掉不显示的标记：图片语法、链接目标、标题井号、表格竖线、加粗星号、行内码反引号。"""
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)          # 图片整体（含 alt）
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)       # 链接保留文字
    s = re.sub(r'^\s{0,3}#{1,6}\s+', '', s, flags=re.M)  # 标题井号
    s = re.sub(r'^\s*\|?[\s:|-]+\|[\s:|-]*$', '', s, flags=re.M)  # 表格分隔行
    s = s.replace('|', ' ')
    s = re.sub(r'[*`>]', '', s)
    return s


def split_body(md):
    """返回 (封面, 正文, 附录)。正文从第一个二级标题起，到 `## 附录` 前止。"""
    lines = md.split('\n')
    body_start = None
    app_start = len(lines)
    for i, ln in enumerate(lines):
        if body_start is None and re.match(r'^##\s', ln):
            body_start = i
        if re.match(r'^##\s*附录', ln):
            app_start = i
            break
    if body_start is None:
        body_start = 0
    if app_start < body_start:
        app_start = len(lines)
    return '\n'.join(lines[:body_start]), '\n'.join(lines[body_start:app_start]), '\n'.join(lines[app_start:])


def count(s):
    return dict(cjk=len(CJK.findall(s)), latin=len(LATIN.findall(s)),
                digit=len(DIGIT.findall(s)), total=len(re.sub(r'\s', '', s)))


def main(argv=None):
    ap = argparse.ArgumentParser(description='统计报告正文字数（四项分列）')
    ap.add_argument('md')
    ap.add_argument('--floor', type=int, default=None, help='正文中文下限，低于则退出码 1')
    ap.add_argument('--verbose', action='store_true', help='按章列出')
    a = ap.parse_args(argv)

    path = os.path.abspath(a.md)
    if not os.path.isfile(path):
        sys.stderr.write('找不到文件：%s\n' % path)
        return 2
    with io.open(path, 'r', encoding='utf-8') as fp:
        md = fp.read()

    cover, body, app = split_body(md)
    cb, cc, ca = count(strip_markup(body)), count(strip_markup(cover)), count(strip_markup(app))

    print('文件  %s' % os.path.basename(path))
    print('%-10s %8s %8s %8s %10s' % ('区块', '中文字符', '英文字母', '数字字符', '总字符'))
    print('%-10s %8d %8d %8d %10d' % ('正文', cb['cjk'], cb['latin'], cb['digit'], cb['total']))
    print('%-10s %8d %8d %8d %10d' % ('封面', cc['cjk'], cc['latin'], cc['digit'], cc['total']))
    print('%-10s %8d %8d %8d %10d' % ('附录', ca['cjk'], ca['latin'], ca['digit'], ca['total']))
    print('%-10s %8d %8d %8d %10d' % ('全文',
                                      cb['cjk'] + cc['cjk'] + ca['cjk'],
                                      cb['latin'] + cc['latin'] + ca['latin'],
                                      cb['digit'] + cc['digit'] + ca['digit'],
                                      cb['total'] + cc['total'] + ca['total']))

    if a.verbose:
        print('\n分章：')
        for blk in re.split(r'\n(?=##\s)', body):
            m = re.match(r'^##\s+(.+)$', blk.split('\n')[0])
            if not m:
                continue
            c = count(strip_markup(blk))
            print('  %-42s %6d' % (m.group(1)[:42], c['cjk']))

    if a.floor is not None:
        ok = cb['cjk'] >= a.floor
        print('\n正文中文 %d，下限 %d → %s' % (cb['cjk'], a.floor, '达标' if ok else '不足 %d' % (a.floor - cb['cjk'])))
        return 0 if ok else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
