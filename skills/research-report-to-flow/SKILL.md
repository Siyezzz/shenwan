---
name: research-report-to-flow
description: Use when 需要把一份卖方研究报告（PDF/文本）转化为可执行、可复现、带证据门槛的 FLOW 时。先抽结论与论证链，再定证据权重、阈值与公式版本，最后映射为 Step/动作并做可执行性与反向复现测试。适用于"把研报做成流程""研报转 FLOW""复刻研报研究逻辑""审计现有 FLOW 是否覆盖研报论点"。
---

# 研报转 FLOW（论证链驱动）

本 skill 是一个 flow（可执行分析流程）。

**执行方式**：阅读同目录下的 FLOW.md，按 `#1 → #18` 顺序执行。Step 0 产出的 `research_graph.yaml` 是后续所有动作的唯一事实来源，任何动作不得跳过它直接回读 PDF 或凭印象补论证。

**运行前检查**：
1. METADATA.md 的 `inputs` 中，`source_report_path`、`target_domain`、`output_skill_name` 三项必须由用户确认；缺任一项即停止。
2. `data_requirements` 中标注 `execution_required: true` 的条目必须先通过 `#11 source_registry` 验证；未验证通过时只能产出 `dry_run` 版 FLOW，不得声称"可直接运行"。

**输出位置**：默认 `./output/YYYYMMDD_HHMMSS/`（可在 METADATA.md 的 `output_dir` 修改）。一个标的的完整产出包含 8 个文件，清单见 FLOW `#18`。

---

## 这个 skill 不做什么

- 不按研报目录抄章节。研报的"第三章"不是 FLOW 的"Step 3"。
- 不把研报结论直接写成 FLOW 的结论。FLOW 输出的是**判据 + 裁决**，结论由数据决定。
- 不产出"看起来完整"的空壳。宁可产出 `INDETERMINATE`，不产出没有证据支撑的 `CONFIRMED`。

## 与附件旧模板的差异（继承关系说明）

继承：四件套命名（SKILL/FLOW/METADATA/_raw_response）、YAML frontmatter、`--{abstract}--` 包裹、`#N --{动作}-- [数据|非数据]` 动作格式、`[输出]/[输出示例]` 逐动作声明、METADATA 原有 10 个字段名不变。

修改（有实测依据，见 `template/template_convention_audit.md`）：
1. `required` 拆成 `execution_required` + `thesis_required`，因为旧模板中 `role` 与 `required` 36/36 一一对应，导致 15 处核心论据被降级为 `false`。
2. 新增 `Step 0` 数据预处理。旧模板 11/11 无 Step 0，同一份原始数据在多个动作里被重复清洗、口径不一。
3. 新增 `formula_version / valid_from / valid_to`。旧模板 0/11 有版本字段，531887 把 2022 年后的长协公式套用到 2017 年。
4. `source_id: null` 不再被容忍。旧模板 645/645 为 null，等于没有任何一条数据真实对接。
5. 分隔符统一为逐文件 `<<<FILE: x>>> ... <<<END: x>>>` + 文末 `<<<END>>>`。旧模板 10/11 只有文末单个 `<<<END>>>`，拆分时丢失文件边界。

## 三条硬约束

- **论据不可静默降级**：任何在研报中承担结论转折作用的证据，`thesis_required` 必须为 `true`，且 `importance ∈ {critical, high}`。降级必须在 `research_graph.yaml` 里写明理由。
- **阈值必须有出处**：`threshold_source` 只能是 `研报明示 / 历史分位 / 行业惯例 / 监管规则` 四者之一。四者皆无 → `UNDEFINED_THRESHOLD`，不得拍脑袋。
- **公式必须有生效期**：跨制度、跨口径的公式必须分段。无法分段而强行套用时，该动作用 `NOT_COMPARABLE` 输出，不给数值。

## 验收口径

一个 FLOW 算"转成功"，不是因为它结构完整，而是因为它能通过 `#17` 的反向复现测试：**在只给数据、不给研报结论的条件下跑一遍，产出的核心裁决与研报核心结论方向一致，且关键论据没有被省略**。方向一致但论据不足，判 `PARTIALLY_SUPPORTED`，不算通过。
