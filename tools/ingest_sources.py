# -*- coding: utf-8 -*-
"""案例资料入库：按案例复制所需 PDF 到 source_documents/，并生成 source_index.csv"""
import csv, os, shutil, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(BASE), "reits", "_docs")
MAN = os.path.join(os.path.dirname(BASE), "reits", "_data", "manifest.csv")
DST = os.path.join(BASE, "source_documents")

CASE_MAP = {
    "glp_reit": ("508056", [
        "2025-04-22_q2025Q1", "2025-07-21_q2025Q2", "2025-10-28_q2025Q3",
        "2026-01-22_q2025Q4", "2025-08-29_h2025", "2026-03-31_y2025",
        "2025-03-28_y2024", "2026-07-01_zmsms",
    ]),
    "huaxia_shen_international": ("180302", [
        "2025-10-28_q2025Q3", "2026-01-22_q2025Q4", "2025-08-30_h2025",
        "2026-03-31_y2025", "2026-01-10_yunying", "2026-06-24_zmsms",
        "2024-06-06_zmsms", "2024-10-25_q2024Q3", "2025-01-22_q2024Q4",
        "2025-01-11_yunying",
    ]),
    "sinofarm_reit": ("508601", [
        "2026-05-15_zmsms", "2026-07-28_zmsms", "2026-10-28_zmsms",
        "2026-04-24_fl_yijian", "2026-10-27_q2026Q3",
    ]),
}

PERIOD = {
    "q2025Q1": "2025Q1", "q2025Q2": "2025Q2", "q2025Q3": "2025Q3", "q2025Q4": "2025Q4",
    "q2024Q3": "2024Q3", "q2024Q4": "2024Q4", "q2026Q3": "2026Q3",
    "h2025": "2025H1", "y2025": "2025FY", "y2024": "2024FY",
}
TYPE = {"q": "季度报告", "h": "中期报告", "y": "年度报告", "yunying": "运营数据公告",
        "zmsms": "招募说明书", "fl": "法律意见书", "pg": "评估报告"}


def load_manifest():
    rows = list(csv.DictReader(open(MAN, encoding="utf-8-sig")))
    idx = {}
    for r in rows:
        key = "%s_%s" % (r["date"], r["tag"])
        idx.setdefault(key, []).append(r)
    return idx


def main():
    man = load_manifest()
    out = []
    for case, (code, keys) in CASE_MAP.items():
        d = os.path.join(DST, case)
        os.makedirs(d, exist_ok=True)
        srcdir = os.path.join(SRC, [x for x in os.listdir(SRC) if x.startswith(code)][0])
        files = sorted(os.listdir(srcdir))
        for k in keys:
            date, tag = k.split("_", 1)
            hits = [f for f in files if f.startswith(date + "_" + tag)]
            if not hits:
                print("MISS %s %s" % (case, k))
                continue
            for f in hits:
                s, t = os.path.join(srcdir, f), os.path.join(d, f)
                if not os.path.exists(t):
                    shutil.copy2(s, t)
                mrow = (man.get(k) or [{}])[0]
                url = mrow.get("ann_page", "") or ""
                size = os.path.getsize(t) / 1048576
                # 判断是否可提取文字（用已抽取文本大小近似）
                txtdir = os.path.join(os.path.dirname(BASE), "reits", "_txt", code)
                tname = f[:-4] + ".txt"
                tpath = os.path.join(txtdir, tname)
                ocr = "否"
                chars = 0
                if os.path.exists(tpath):
                    chars = os.path.getsize(tpath)
                    ocr = "否（有文字层）" if chars > 20000 else "疑似无文字层"
                out.append({
                    "case": case, "code": code, "file": f,
                    "type": TYPE.get(tag.split("_")[-1] if tag.startswith("fl") else tag.split("_")[0], tag),
                    "period": PERIOD.get(tag, tag),
                    "disclose_date": date,
                    "size_mb": round(size, 2),
                    "url": url,
                    "local_path": os.path.relpath(t, BASE).replace("\\", "/"),
                    "text_chars": chars,
                    "ocr": ocr,
                    "status": "OK",
                })
    # 缺失项登记
    out.append({"case": "sinofarm_reit", "code": "508601", "file": "基金合同", "type": "基金合同",
                "period": "—", "disclose_date": "—", "size_mb": 0, "url": "",
                "local_path": "", "text_chars": 0, "ocr": "—",
                "status": "SOURCE_UNAVAILABLE（东财公告库与上交所公开检索均未列出；上交所 query.sse.com.cn 公告接口需内部 channelId，公开 HTTP 无法枚举）"})
    out.append({"case": "sinofarm_reit", "code": "508601", "file": "资产评估报告", "type": "评估报告",
                "period": "—", "disclose_date": "—", "size_mb": 0, "url": "",
                "local_path": "", "text_chars": 0, "ocr": "—",
                "status": "SOURCE_UNAVAILABLE（未单独披露；评估方法、折现率、评估结论以招募说明书对应章节为准，来源等级下降）"})

    p = os.path.join(DST, "source_index.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print("写入 %d 条 -> %s" % (len(out), p))
    for c in CASE_MAP:
        rs = [r for r in out if r["case"] == c]
        print("  %-26s %2d 份  %.1f MB" % (c, len(rs), sum(r["size_mb"] for r in rs)))


if __name__ == "__main__":
    main()
