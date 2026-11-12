# -*- coding: utf-8 -*-
"""report .md → 单文件 .html（图 base64 内嵌，拷走即完整）

用法
    python tools/render_report.py report_508056_2025Q4.md
    python tools/render_report.py report.md -o out/report.html
    python tools/render_report.py report.md --title "自定义标题"

版式来源：中金普洛斯 508056 2025Q4 投后跟踪的成稿。深蓝标题 + 橙色左边线 +
白纸卡片 + 表头深蓝反白，正文 15.5px / 行高 1.85 / 最大宽 960px。

零第三方依赖（只用标准库），任何装了 Python 3 的机器都能跑。
"""
from __future__ import print_function

import argparse
import base64
import io
import os
import re
import sys

# ---------------------------------------------------------------- CSS

CSS = """
:root{--ink:#1F3864;--acc:#C55A11;--grey:#5A5A5A;--line:#DCE3F0}
*{box-sizing:border-box}
body{margin:0;background:#F4F6FA;font-family:"Microsoft YaHei","微软雅黑",-apple-system,sans-serif;
color:#222;line-height:1.85;font-size:15.5px}
.page{max-width:960px;margin:0 auto;background:#fff;padding:56px 64px 72px;
box-shadow:0 2px 18px rgba(31,56,100,.08)}
h1{font-size:25px;line-height:1.5;color:var(--ink);margin:0 0 28px;padding-bottom:18px;border-bottom:3px solid var(--ink)}
h2{font-size:20px;color:var(--ink);margin:44px 0 14px;padding-left:12px;border-left:5px solid var(--acc)}
h3{font-size:17px;color:var(--ink);margin:30px 0 10px}
h4{font-size:15.5px;color:var(--ink);margin:24px 0 8px}
p{margin:0 0 15px;text-align:justify}
strong{color:#111}
table{width:100%;border-collapse:collapse;margin:12px 0 8px;font-size:13.5px}
th{background:var(--ink);color:#fff;font-weight:600;padding:9px 8px;text-align:left;border:1px solid #17305A}
td{padding:7px 8px;border:1px solid var(--line);vertical-align:top}
tbody tr:nth-child(even){background:#F7F9FD}
figure{margin:26px 0 8px}
img{width:100%;height:auto;border:1px solid var(--line);border-radius:4px;background:#fff}
code{background:#EEF2F9;padding:1px 5px;border-radius:3px;font-size:13px}
table:first-of-type td:first-child{width:118px;white-space:nowrap;font-weight:600;color:var(--ink)}
table:first-of-type td{white-space:normal}
ol{margin:0 0 16px 22px;padding:0}
ul{margin:0 0 16px 22px;padding:0}
li{margin:5px 0;text-align:justify}
blockquote{margin:14px 0 16px;padding:10px 16px;background:#F7F9FD;border-left:3px solid var(--line);color:var(--grey)}
pre{background:#F7F9FD;border:1px solid var(--line);border-left:3px solid var(--acc);border-radius:4px;
padding:12px 14px;margin:12px 0 16px;font-size:12.5px;line-height:1.75;white-space:pre-wrap;overflow-x:auto;
font-family:Consolas,"Courier New",monospace;color:#333}
hr{border:0;border-top:1px solid var(--line);margin:34px 0}
a{color:var(--acc);text-decoration:none}
@media print{body{background:#fff}.page{box-shadow:none;padding:0}}
"""

MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp'}


class Renderer(object):
    def __init__(self, md_path, missing=None):
        self.base = os.path.dirname(os.path.abspath(md_path))
        self.missing = missing if missing is not None else []
        self.n_img = 0

    # -------------------------------------------------- 行内
    def img_src(self, rel):
        """相对 md 所在目录解析图片，命中则转 base64。"""
        p = os.path.join(self.base, rel.lstrip('./'))
        if not os.path.isfile(p):
            self.missing.append(rel)
            return rel
        ext = os.path.splitext(p)[1].lower()
        mime = MIME.get(ext, 'application/octet-stream')
        with io.open(p, 'rb') as fp:
            b64 = base64.b64encode(fp.read()).decode('ascii')
        self.n_img += 1
        return 'data:%s;base64,%s' % (mime, b64)

    def inline(self, s):
        s = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)',
                   lambda m: '<img alt="%s" src="%s">' % (m.group(1), self.img_src(m.group(2))), s)
        s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        return s

    # -------------------------------------------------- 块级
    def render(self, md):
        lines = md.split('\n')
        out = []
        i = 0
        n = len(lines)
        while i < n:
            ln = lines[i]
            if not ln.strip():
                i += 1
                continue

            # 代码块（围栏内原文输出，不做行内解析，避免块内 # 被当成标题）
            if re.match(r'^\s*```', ln):
                i += 1
                blk = []
                while i < n and not re.match(r'^\s*```\s*$', lines[i]):
                    blk.append(lines[i])
                    i += 1
                i += 1                      # 跳过闭合围栏
                txt = '\n'.join(blk)
                txt = txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                out.append('<pre>%s</pre>' % txt)
                continue

            # 标题
            m = re.match(r'^(#{1,4})\s+(.*)$', ln)
            if m:
                lv = len(m.group(1))
                out.append('<h%d>%s</h%d>' % (lv, self.inline(m.group(2)), lv))
                i += 1
                continue

            # 分隔线
            if re.match(r'^\s*(-{3,}|\*{3,})\s*$', ln):
                out.append('<hr>')
                i += 1
                continue

            # 表格
            if ln.startswith('|'):
                blk = []
                while i < n and lines[i].startswith('|'):
                    blk.append(lines[i])
                    i += 1
                rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in blk]
                if len(rows) > 1 and re.match(r'^:?-{2,}', rows[1][0]):
                    head, body = rows[0], rows[2:]
                else:
                    head, body = None, rows
                t = ['<table>']
                if head:
                    t.append('<thead><tr>' + ''.join(
                        '<th>%s</th>' % self.inline(c) for c in head) + '</tr></thead>')
                t.append('<tbody>')
                for r in body:
                    t.append('<tr>' + ''.join('<td>%s</td>' % self.inline(c) for c in r) + '</tr>')
                t.append('</tbody></table>')
                out.append('\n'.join(t))
                continue

            # 图片（独占一行）
            if ln.startswith('!['):
                out.append('<figure>%s</figure>' % self.inline(ln))
                i += 1
                continue

            # 有序列表
            if re.match(r'^\d+\.\s', ln):
                blk = []
                while i < n and re.match(r'^\d+\.\s', lines[i]):
                    blk.append(re.sub(r'^\d+\.\s+', '', lines[i]))
                    i += 1
                out.append('<ol>' + ''.join('<li>%s</li>' % self.inline(b) for b in blk) + '</ol>')
                continue

            # 无序列表
            if re.match(r'^[-*+]\s', ln):
                blk = []
                while i < n and re.match(r'^[-*+]\s', lines[i]):
                    blk.append(re.sub(r'^[-*+]\s+', '', lines[i]))
                    i += 1
                out.append('<ul>' + ''.join('<li>%s</li>' % self.inline(b) for b in blk) + '</ul>')
                continue

            # 引用块
            if ln.startswith('>'):
                blk = []
                while i < n and lines[i].startswith('>'):
                    blk.append(re.sub(r'^>\s?', '', lines[i]))
                    i += 1
                out.append('<blockquote>%s</blockquote>' % self.inline(' '.join(blk)))
                continue

            # 普通段落
            out.append('<p>%s</p>' % self.inline(ln))
            i += 1
        return '\n'.join(out)


def document(title, body):
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><style>%s</style></head>'
            '<body><div class="page">%s</div></body></html>'
            % (title, CSS, body))


def guess_title(md, fallback):
    for ln in md.split('\n'):
        m = re.match(r'^#\s+(.+)$', ln)
        if m:
            return re.sub(r'[*`]', '', m.group(1)).strip()
    return fallback


def main(argv=None):
    ap = argparse.ArgumentParser(description='把报告 .md 渲染成单文件 .html（图 base64 内嵌）')
    ap.add_argument('md', help='输入 markdown 路径')
    ap.add_argument('-o', '--out', help='输出 html 路径，默认同名 .html')
    ap.add_argument('--title', help='浏览器标签标题，默认取 md 的一级标题')
    a = ap.parse_args(argv)

    md_path = os.path.abspath(a.md)
    if not os.path.isfile(md_path):
        sys.stderr.write('找不到输入文件：%s\n' % md_path)
        return 2
    out_path = os.path.abspath(a.out) if a.out else os.path.splitext(md_path)[0] + '.html'

    with io.open(md_path, 'r', encoding='utf-8') as fp:
        md = fp.read()

    r = Renderer(md_path)
    body = r.render(md)
    title = a.title or guess_title(md, os.path.basename(md_path))
    html = document(title, body)

    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with io.open(out_path, 'w', encoding='utf-8') as fp:
        fp.write(html)

    print('输入  %s' % md_path)
    print('输出  %s' % out_path)
    print('大小  %.1f KB   内嵌图 %d 张   表格 %d 个'
          % (len(html.encode('utf-8')) / 1024.0, r.n_img, html.count('<table>')))
    if r.missing:
        print('缺失图片 %d 个（按原相对路径保留，未内嵌）：' % len(r.missing))
        for p in r.missing:
            print('  %s' % p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
