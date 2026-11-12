#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate the 508601 REIT model outputs against the independent bottom-up engine."""
import math
import os
import sys
from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import build_bottomup
XLSX = os.path.join(ROOT, "models", "cash_flow_model.xlsx")
CSV = os.path.join(ROOT, "models", "scenario_2028.csv")

def close(a, b, tol=0.02):
    return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)

def main():
    assert os.path.isfile(XLSX), "cash_flow_model.xlsx was not generated"
    assert os.path.isfile(CSV), "scenario_2028.csv was not generated"
    with open(CSV, encoding="utf-8") as f:
        csv_lines = [x.strip() for x in f if x.strip()]
    assert len(csv_lines) == 58, "expected header + 57 scenario-year rows"
    assert csv_lines[0] == "scenario,year,revenue,ebitda,capex,intax,wc_change,distributable,rate,source"
    assert abs(build_bottomup.validate_revenue_bridge() - build_bottomup.D["rev_2027"]) < 1.0

    wb_formula = load_workbook(XLSX, data_only=False)
    wb_values = load_workbook(XLSX, data_only=True)
    expected_sheets = ["0_说明", "1_假设", "2_模型", "3_输出", "4_敏感性",
                       "5_到期重定价", "6_情景回报"]
    assert wb_formula.sheetnames == expected_sheets, wb_formula.sheetnames

    ws = wb_values["5_到期重定价"]
    for i, name in enumerate(("悲观", "中性", "乐观")):
        expected = build_bottomup.build(name)
        first = 5 + i * 19
        for j, item in enumerate(expected):
            row = first + j
            assert ws.cell(row, 1).value == name
            assert int(ws.cell(row, 2).value) == item["year"]
            for col, key in ((3, "rev"), (4, "ebitda"), (5, "capex"),
                             (6, "intax"), (7, "wc"), (8, "dist")):
                assert close(ws.cell(row, col).value, item[key]), (
                    name, item["year"], key, ws.cell(row, col).value, item[key])
            assert close(ws.cell(row, 9).value, item["rate"], 1e-7)
            if item["year"] >= 2028:
                assert close(item["wc"], 0.0, 1e-9)  # 显式占位假设，不是披露事实

    # Formula cells must be present and recalculated to numeric cached values.
    wf = wb_formula["6_情景回报"]
    wv = wb_values["6_情景回报"]
    for i, name in enumerate(("悲观", "中性", "乐观")):
        row = 5 + i
        cf_row_100 = 12 + i * 2
        cf_row_90 = cf_row_100 + 1
        formula_90 = wf.cell(row, 2).value
        formula_100 = wf.cell(row, 3).value
        cached_90 = wv.cell(row, 2).value
        cached_100 = wv.cell(row, 3).value
        rows = build_bottomup.build(name)
        expected_90 = build_bottomup.irr_of(rows, distribution_ratio=0.90)
        expected_100 = build_bottomup.irr_of(rows, distribution_ratio=1.00)
        assert isinstance(formula_90, str) and formula_90.startswith("=IRR("), (name, formula_90)
        assert isinstance(formula_100, str) and formula_100.startswith("=IRR("), (name, formula_100)
        assert close(cached_90, expected_90, 1e-6), (name, cached_90, expected_90)
        assert close(cached_100, expected_100, 1e-6), (name, cached_100, expected_100)
        assert wf.cell(cf_row_100, 2).value < 0 and wf.cell(cf_row_90, 2).value < 0
        assert all(isinstance(wv.cell(cf_row_100, col).value, (int, float))
                   for col in range(3, 22))
        for col in range(3, 22):
            assert close(wv.cell(cf_row_90, col).value,
                         wv.cell(cf_row_100, col).value * 0.90, 0.02)

    # 2_模型 的 2028 起现金流必须链接到中性情景输出，不再使用评估现金流 CAGR 外推收入。
    assert "5_到期重定价" in str(wb_formula["2_模型"]["G7"].value)
    assert "H26" in str(wb_formula["2_模型"]["G7"].value)
    # Sensitivity sheet must reference the neutral 2028 repricing row, not the appraisal-growth baseline.
    sens = wb_formula["4_敏感性"]
    assert "5_到期重定价" in str(sens["K5"].value)
    assert "5_到期重定价" in str(sens["K6"].value)
    assert "5_到期重定价" in str(sens["K7"].value)

    errors = []
    for sheet in wb_values.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("#"):
                    errors.append((sheet.title, cell.coordinate, cell.value))
    assert not errors, errors[:10]

    print("MODEL_VALIDATION=PASS")
    print("sheets=7; scenario_rows=57; excel_irr_matches_python=3/3; formula_errors=0")
    for name in ("悲观", "中性", "乐观"):
        print("%s IRR=%.6f%%" % (name, build_bottomup.irr_of(build_bottomup.build(name)) * 100))

if __name__ == "__main__":
    main()
