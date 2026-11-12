# -*- coding: utf-8 -*-
"""把 report_*.md 转成单文件自包含 HTML：SVG 图内联，无外部依赖。

为什么要有这一步
----------------
Markdown 版在 GitHub 上读没问题（图走相对路径，GitHub 会渲染 SVG），但一旦
把报告当附件发给别人、或离线打开，图就丢了。本脚本把 5 张 SVG 直接嵌进 HTML，
产出**一个文件、双击即读**的版本。图与正文同源，改数据只需重跑两个脚本。

用法：python build_html.py
"""
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "report_peer_benchmarking_2025.md")
OUT = os.path.join(HERE, "report_peer_benchmarking_2025.html")


def inline_svg(path):
    """读取 SVG 并去掉固定宽高，交给 CSS 自适应。"""
    with open(os.path.join(HERE, path), encoding="utf-8") as f:
        s = f.read()
    s = re.sub(r'(<svg[^>]*?)\swidth="\d+"\s+height="\d+"', r"\1", s, count=1)
    return s


def inline_md(t):
    """行内标记：粗体、代码、箭头转义。"""
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def convert(md):
    lines = md.split("\n")
    out, i = [], 0
    n = len(lines)

    def flush_table(start):
        """从 start 起收集表格行，返回 (html, 下一行索引)。"""
        rows = []
        j = start
        while j < n and lines[j].strip().startswith("|"):
            rows.append(lines[j].strip())
            j += 1
        if len(rows) < 2:
            return "", start
        body = []
        head = [c.strip() for c in rows[0].strip("|").split("|")]
        for r in rows[2:]:
            cells = [c.strip() for c in r.strip("|").split("|")]
            body.append(cells)
        h = ['<div class="tw"><table>', "<thead><tr>"]
        for c in head:
            h.append(f"<th>{inline_md(c)}</th>")
        h.append("</tr></thead><tbody>")
        for cells in body:
            h.append("<tr>")
            for c in cells:
                h.append(f"<td>{inline_md(c)}</td>")
            h.append("</tr>")
        h.append("</tbody></table></div>")
        return "".join(h), j

    while i < n:
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        if line.startswith("![]("):
            path = line[4:-1]
            out.append(f'<figure>{inline_svg(path)}</figure>')
            i += 1
            continue

        if line == "---":
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            out.append(f"<h{lvl}>{inline_md(txt)}</h{lvl}>")
            i += 1
            continue

        if line.startswith("|"):
            tb, j = flush_table(i)
            if tb:
                out.append(tb)
                i = j
                continue

        if line.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline_md(x)}</li>" for x in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s", line):
            items = []
            while i < n and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline_md(x)}</li>" for x in items) + "</ol>")
            continue

        if re.match(r"^图\s*\d+　", line):
            out.append(f'<p class="figcap">{inline_md(line)}</p>')
            i += 1
            continue

        out.append(f"<p>{inline_md(line)}</p>")
        i += 1

    return "\n".join(out)


def main():
    md = open(MD, encoding="utf-8").read()
    body = convert(md)

    css = """
:root{--ink:#17222e;--muted:#65727f;--line:#e2e8ef;--accent:#b2372b;--base:#2c5f8a;--bg:#fff}
*{box-sizing:border-box}
body{margin:0;background:#f5f7fa;color:var(--ink);
 font:16px/1.85 -apple-system,"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
 -webkit-font-smoothing:antialiased}
.page{max-width:940px;margin:0 auto;background:var(--bg);padding:56px 64px 80px;
 box-shadow:0 1px 3px rgba(20,35,50,.08)}
h1{font-size:27px;line-height:1.4;margin:0 0 26px;letter-spacing:-.2px}
h2{font-size:20px;margin:52px 0 16px;padding-left:12px;border-left:4px solid var(--accent)}
h3{font-size:16.5px;margin:32px 0 10px;color:#0f2b45}
h4{font-size:15px;margin:24px 0 8px}
p{margin:0 0 15px;text-align:justify}
strong{color:#0b2239;font-weight:650}
hr{border:0;border-top:1px solid var(--line);margin:44px 0}
figure{margin:26px 0 8px;text-align:center}
figure svg{max-width:100%;height:auto}
.figcap{text-align:center;font-size:13px;color:var(--muted);margin:0 0 26px}
.tw{overflow-x:auto;margin:20px 0 26px}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.65}
th{background:#eef3f8;color:#0f2b45;font-weight:650;text-align:left;
 padding:9px 11px;border-bottom:1.5px solid #c9d6e3;white-space:nowrap}
td{padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr:nth-child(even){background:#fafbfd}
tbody tr:hover{background:#f2f6fa}
code{background:#f0f3f7;padding:1px 5px;border-radius:3px;font-size:13px;
 font-family:"SF Mono",Consolas,monospace}
ul,ol{margin:0 0 16px;padding-left:22px}
li{margin-bottom:6px}
blockquote{border-left:3px solid var(--line);margin:0 0 16px;padding-left:14px;color:var(--muted)}
@media(max-width:760px){.page{padding:28px 20px 48px}h1{font-size:22px}}
@media print{body{background:#fff}.page{box-shadow:none;padding:0;max-width:none}
 h2{page-break-after:avoid}figure{page-break-inside:avoid}}
"""

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>仓储物流公募 REITs 横向基准报告（2025 年度）</title>
<style>{css}</style>
</head>
<body><div class="page">
{body}
</div></body>
</html>
"""
    open(OUT, "w", encoding="utf-8").write(doc)
    print("wrote", OUT, f"{len(doc)/1024:.1f} KB")


if __name__ == "__main__":
    main()
