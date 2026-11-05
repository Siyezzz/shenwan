# 模板规范审计（template_convention_audit）

> 用途：作为本项目三个新 Skill 的**写作约束**。凡与本文冲突的写法，一律以本文为准。
> 依据：11 套附件（`_ref/2026_08/531887…532411`）的逐份统计，统计口径见 `outputs/research_flow_audit/research_flow_audit.xlsx` → `规范一致性统计`。

---

## 一、三档处置结论

| 类别 | 条目 | 处置 |
|---|---|---|
| **原样继承** | 四文件命名与目录结构、SKILL 的 4 要素正文、FLOW 的 abstract/Step/#n/[数据][非数据]/数据依赖/[输出]+[输出示例]、METADATA 的 10 顶层 + 6 子字段、`_raw_response.txt` 保留、`inputs` 剥离政策参数 | 不改名、不改顺序、不合并 |
| **修订** | 容器分隔符统一、动作编号连续性、动作命名规范、`required` 语义、三档判断必须有标尺、公式必须有版本、数据必须有预处理层、必须有不可判定态 | 在保留原字段的前提下**加字段、加校验**，不删原字段 |
| **新增** | `execution_required` / `thesis_required` / `importance` / `evidence_role` / `missing_data_impact`；`direction` / `bands` / `window` / `threshold_source`；`formula`(version/valid_from/valid_to)；`source_probe`；`frequency_type`；`claim` 与 `evidence` 层 | 只在 FLOW 中真正被引用才加 |

---

## 二、SKILL.md 规范（条文）

1. YAML frontmatter 只有两键：`name`、`description`；`name` 为英文 kebab-case，且 **必须**与 METADATA.md 的 `name` 完全一致。
2. `description` 采用三段式："Use when 需要……（触发场景）时。基于……（方法）框架。输出……"，60–150 字，中文。
3. 正文四级固定结构，标题为中文：
   - 一级标题：Skill 中文名；
   - `本skill是一个flow（可执行分析流程）。`
   - `**执行方式**：阅读同目录下的 FLOW.md，按章节顺序执行其中的动作。`
   - `**运行前检查**：`（见第 4 条）
   - `**输出位置**：默认 ./output/YYYYMMDD_HHMMSS/（可在 METADATA.md 的 output_dir 中修改）。`
4. 运行前检查必须**可执行**，至少包含：①`source_probe` 未通过的指标清单；②`inputs` 逐项确认；③`thesis_required` 缺失时的降级声明。禁止只写"不要编造数据"这类叮嘱。
5. 文件末尾必须是 `<<<END: SKILL.md>>>`。

## 三、FLOW.md 规范（条文）

1. 首部 `--{abstract}--` … `--{/abstract}--`，内含 4–6 条编号思考路径，句式固定为"前提→核心矛盾→任务目标→方法选择→任务要求"。
2. **Step 编号从 0 开始**：`# Step 0：Data Ingestion & Preprocessing` 为强制首步，其余步骤按研究链条命名（不得照抄研报目录）。
3. 动作书写格式（逐字保留结构）：
   ```
   #n --{动作}-- [数据]        （或 [非数据]）
   **动词+对象+判据**
   * 数据依赖：指标名(频率)、…
   使用{#m}的数据，<处理步骤 1>
   - <处理步骤 2>
   [输出]：<表名>
   [输出示例]：
   | 列1 | 列2 | 列3 |
   ```
4. `#n` 必须**全局连续递增**，不得跨 Step 重排或跳号（附件 531936 的反例不可重现）。每个 Step 内动作数 ≤ 5。
5. 每个数据动作必须声明：`数据依赖`（引用 METADATA 里的指标名原文）、`窗口`、`公式或判据`、`缺失处理`。
6. 每个动作的 `[输出示例]` 必须给出**列名**，不得只写"输出分析结果"。
7. 三档判断必须写成 `判断（bands：…；window：…；source：…）`，给不出就写 `UNDEFINED_THRESHOLD`。
8. 合取型结论（如"三重底"）必须给出 0/1 分量与总分映射，不允许"三条都满足才算通过"。
9. 文件末尾必须是 `<<<END: FLOW.md>>>`。

## 四、METADATA.md 规范（条文）

1. 顶层字段**保持原 10 项与原有顺序**：
   ```
   type / name / version / description / domain / source_report /
   script_permission / output_dir / inputs / data_requirements
   ```
2. `data_requirements` 子字段**保持原 6 项**，并在其后追加（不替换）：
   ```yaml
   - name: 原始指标名（与数据源字段一致）
     freq: 季度
     unit: 元
     role: "…"                          # 保留，但改为“入边摘要”
     required: true                      # 保留，= execution_required（兼容旧解析器）
     source_id: sse_reit_report_pdf      # 必须有值；无法获取写 null 并在 probe 注明
     # —— 以下为新增 ——
     execution_required: true            # 缺了算不出来
     thesis_required: true               # 缺了核心结论不成立
     importance: critical                # critical / high / medium / low
     evidence_role: core                 # core / support / context
     missing_data_impact: "无法判断可供分配金额同比方向，结论降级为 INDETERMINATE"
     direction: higher_is_better         # higher_is_better / lower_is_better / context_dependent
     bands: {high: ">=0.95", medium: "0.90-0.95", low: "<0.90"}
     window: "近8个季度"                  # 判断窗口，必须写死
     threshold_source: convention        # report / quantile / convention / undefined
     formula:                            # 可无；有则必须带版本
       expr: "出租率 = 期末已出租面积 / 期末可租赁面积"
       version: "v1"
       valid_from: "2021-06"
       valid_to: null
       invalidate_if: ["口径改为平均出租率", "披露口径改为含物业"]
     frequency_type: recurring           # recurring / one_off（一次性披露不得当时间序列）
     source_probe: ok                    # ok / paid / build / none
     probe_note: "上交所 REITs 公告页 PDF 可直下，2025 年报第 X 页"
   ```
3. `inputs` 只放**制度常量与人工假设**（政策参数、用户指定的重点期间、独立研究假设），不得放时间序列。
4. `version` 必须随每轮实质修改递增，并在 `iteration_log/ITERATION_LOG.md` 留痕。
5. 文件末尾必须是 `<<<END: METADATA.md>>>`。

## 五、`_raw_response.txt` 规范（修订）

附件存在两套互不兼容的分隔符：

- 531887：`<<<FILE: X>>>` … `<<<END: X>>>`（自闭包，可解析）
- 其余 10 套：`<<<FILE: X>>>` … 文末单个 `<<<END>>>`（不可解析，拆分必丢标记）

**本项目统一采用自闭包写法**，每个文件块必须自闭合：

```
<<<FILE: SKILL.md>>>
…
<<<END: SKILL.md>>>
<<<FILE: METADATA.md>>>
…
<<<END: METADATA.md>>>
<<<FILE: FLOW.md>>>
…
<<<END: FLOW.md>>>
```

## 六、目录与输出规范

1. 每个 Skill 一个目录，只放四文件；参考资料放 `references/`（可选，不得让主流程依赖）。
2. 运行输出目录：`./output/YYYYMMDD_HHMMSS/`，内部固定含 `report.md`、`data_matrix.xlsx`、`source_index.md`、`run_log.md`。
3. `run_log.md` 必须记录：运行时间、输入参数、每个动作的状态（OK / PARTIAL / SOURCE_UNAVAILABLE / UNDEFINED_THRESHOLD）、缺失数据清单。

## 七、机器可校验清单（每份新 Skill 提交前逐条打勾）

| # | 检查项 | 判定方式 |
|---|---|---|
| 1 | 四文件齐全且命名正确 | 文件存在性 |
| 2 | SKILL.name == METADATA.name | 字符串相等 |
| 3 | SKILL 含 4 要素关键词 | 关键词匹配 |
| 4 | 三个文件均以 `<<<END: 文件名>>>` 结尾 | 尾部匹配 |
| 5 | FLOW 首步为 Step 0 | 正则 `^# Step 0` |
| 6 | 动作编号 1..N 连续 | 序号差分为 1 |
| 7 | 每个动作有 [数据]/[非数据] 标签 | 正则计数 |
| 8 | 每个数据动作有"数据依赖" | 段落匹配 |
| 9 | 每个动作有 `[输出示例]` 表头 | 表格行匹配 |
| 10 | METADATA 顶层 10 字段齐全且顺序不变 | 列表比对 |
| 11 | 每条指标 6 个原字段 + 新增字段齐全 | 字段计数 |
| 12 | `source_id` 非空比例 = 100%（或在 probe 注明 none） | 计数 |
| 13 | 每个"高/中/低"都有 bands 与 window | 正则 + 邻近匹配 |
| 14 | 每个 formula 有 version 与 valid_from | 字段存在性 |
| 15 | FLOW 中出现 ≥1 次七态之一 | 关键词匹配 |

---

## 附：附件规范的三处硬缺陷（本项目必须避免）

| 缺陷 | 附件现状 | 本项目做法 |
|---|---|---|
| 数据层空转 | 645/645 `source_id=null` | 每条必须探针，`probe` 记录 ok/paid/build/none |
| 判断层无标尺 | 35 次"高/中/低"零区间 | bands + window + source 三件套强制 |
| 时间层无版本 | 0/11 有 formula_version | formula 块强制 version/valid_from |
