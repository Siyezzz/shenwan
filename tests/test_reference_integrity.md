# Reference Integrity Tests — Pre-investment Skill

本测试用于检查 Skill 的引用是否落到真实文件，而不只是文档里出现了一个看似合理的名称或 URL。

## Test R1 — Source index existence
- 前置：仓库中存在 `source_documents/source_index.csv`。
- 检查：CSV 可解析，包含 `case, code, file, type, period, disclose_date, url, local_path, status` 列。
- 通过：索引存在且列齐全。
- 失败：停止材料抽取，报告索引不可用。

## Test R2 — Local file existence
- 对筛选出的每一条索引记录检查 `local_path`。
- 通过：本地文件存在，记录大小与 SHA-256。
- 未通过：状态标记 `INDEXED_NOT_DOWNLOADED`；不得把索引记录当成已读文件。
- 仅在 GitHub 上看到索引路径，不构成文件存在证明。

## Test R3 — Readability and OCR
- 检查 PDF 页数、文本层、可检索字符数。
- 扫描件标记 `OCR_NEEDED`；OCR 后保留原始 PDF 与 OCR 输出的关联。
- 关键页 OCR 未完成时，对应字段不得为 `CONFIRMED`。

## Test R4 — Citation completeness
抽样所有关键事实，检查是否具备：
`source_id + exact file_name + pdf_page + section/table + quote/location + unit + nature`。
缺一项即失败；只有来源机构代号或公告首页 URL 不算完整引用。

## Test R5 — Version and as-of date
- 同类型多版本需保留候选清单与裁决理由。
- 披露日期晚于 `analysis_date` 的文件不得作为基准日可得信息，除非单独列为事后信息。
- 不允许用旧法律意见书的版本优先级覆盖更新招募书中的现行数据，须按文件类型和字段用途裁决。

## Test R6 — Internal artifact references
检查 FLOW/SKILL 引用的模板、模型、脚本和测试文件是否存在于仓库。
- 脚本参数必须来自源码或 `--help`，不能凭文件名推测。
- 未执行脚本不得写“执行成功”。
- 输出文件名必须与 SKILL、FLOW、run_log 一致。

## Test R7 — Cross-fund contamination
- 所有原始材料必须匹配当前基金代码/名称。
- 历史案例只能提供方法和比较样本，不得将其资产数据写入当前标的 facts。
- 任何跨标的引用必须显式标记为可比数据，并说明可比性。

## Test R8 — Claim-to-source trace
每个投资结论拆解为可核验的 claim，追溯到指标、计算过程和源文件。
- 事实型 claim 必须引用原始披露。
- 计算型 claim 必须引用输入事实与公式/模型单元格。
- 判断型 claim 必须列出事实依据和研究假设。
- 不能完成追溯的 claim 降级为 `PARTIALLY_SUPPORTED` 或 `INDETERMINATE`。

## Acceptance
R1–R8 全部通过，且关键 thesis fields 无未解释缺失，才可标记 `REFERENCE_GATE=PASS`。
若存在缺失但已完整登记，可标记 `REFERENCE_GATE=PASS_WITH_GAPS`；不得标记为完全通过。
