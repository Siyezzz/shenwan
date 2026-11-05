# Skill 执行结构测试（T-SKILL）

**对象**：三个 Skill 的四件套（`SKILL.md` / `METADATA.md` / `FLOW.md` / `_raw_response.txt`）
**执行**：`python tests/run_tests.py` 中的 `t_skill()`
**条数**：31
**当前结果**：31 / 31 PASS

## 为什么 Skill 也要测试

Skill 是"给未来的自己看的操作规程"。它不像代码，跑不通会报错——**格式错了、字段缺了、编号断了，文档照样读起来很顺**，直到真正执行时才发现某一步没法做。

本组要回答的问题是：**这份 Skill 现在能不能被一个没参与编写的人直接执行？** 所以检的不是文笔，是结构完整性、可逆性和关键条款是否在位。

---

## 一、四件套存在性（T-SKILL-01，12 条）

3 个 Skill × 4 个文件 = 12 条，全部 PASS。

| Skill | SKILL.md | METADATA.md | FLOW.md | _raw_response.txt |
|---|---|---|---|---|
| research-report-to-flow | ✓ | ✓ | ✓ | ✓ 26,694 字节 |
| reits-post-investment-monitor | ✓ | ✓ | ✓ | ✓ 35,729 字节 |
| reits-pre-investment-analysis | ✓ | ✓ | ✓ | ✓ 36,987 字节 |

**为什么 `_raw_response.txt` 也算必备**：它是对外分发时的"单文件形态"——把三份文档打包成一段带边界标记的纯文本，便于在不支持多文件的宿主里一次性载入。它必须与磁盘上的三份文件**逐字节一致**，否则分发出去的是旧版本。

---

## 二、SKILL.md 结构（T-SKILL-02，3 条）

**检验**：文件以 YAML frontmatter（`---` 包裹）开头，且正文含一级标题 `# `。

**当前结果**：3/3 PASS。

**这条断言改过一次，过程值得记录**：

初版断言写的是 `sk.lstrip().startswith("#")` —— 要求文件第一个字符是 `#`。三个 Skill 全部 FAIL。

检查后发现：**不是文件错，是断言错**。SKILL.md 的标准格式是

```
---
name: reits-post-investment-monitor
description: Use when 需要对已上市公募REITs做季度/半年度/年度投后跟踪时。...
---

# 公募 REITs 投后定期跟踪
```

frontmatter 在第一位，标题在其后。这是模板规范，断言却按"纯 Markdown 文档"的格式去要求，两者不一致。

**处理**：断言改为校验"frontmatter 存在 + 含一级标题"两件事，而不是"首字符是 #"。

**这里的分寸**：如果把断言放宽成"文件里只要出现过 `#` 就算过"，那 FLOW 的动作编号 `#1`、`#2` 也会让它通过，等于没检。所以必须同时检 frontmatter 和一级标题，两者都成立才算结构正确。

---

## 三、FLOW 动作编号连续（T-SKILL-03，3 条）

**检验**：所有 `^#(\d+)\s` 形式的动作编号，必须从 1 开始、连续、无跳号。

| Skill | 动作数 | 编号范围 |
|---|---|---|
| research-report-to-flow | 18 | #1–#18 |
| reits-post-investment-monitor | 22 | #1–#22 |
| reits-pre-investment-analysis | 26 | #1–#26 |

**为什么必须连续**：FLOW 的动作之间是**有依赖**的——`#12` 要用 `#9` 的输出。跳号会让执行者不确定"是不是漏了一步"，也让人工复核时无法确认是否跳过了某个动作。

**这类问题为什么测试能抓而人眼抓不到**：Markdown 渲染时编号跳号完全没有视觉提示，`#19` 后面接 `#21` 看起来和 `#19` 接 `#20` 一样整齐。只有把编号抽出来做集合比较，才能发现中间缺了一个。

---

## 四、METADATA 必备字段（T-SKILL-04，3 条）

每个 Skill 有各自的必备字段集，检的是"这一层最关键的结构是否在"：

| Skill | 必备字段 | 理由 |
|---|---|---|
| research-report-to-flow | `claim_schema`、`evidence_policy`、`threshold_policy`、`formula_registry`、`source_registry` | 方法论层的五个支柱：论断结构、证据权重、阈值标尺、公式版本、数据源登记 |
| reits-post-investment-monitor | `period_semantics`、`metric_bands`、`claim_schema`、`formula_registry` | 投后场景特有：期间语义（累计 vs 单季）和指标阈值带 |
| reits-pre-investment-analysis | `step0_required`、`assumption_register`、`valuation_params`、`scenario_set` | 投前场景特有：假设登记、估值参数、情景集 |

**当前结果**：3/3 PASS，缺失字段均为空列表。

**为什么按 Skill 分别列字段而不是统一一套**：统一会逼着每个 Skill 都塞一些用不上的字段来"凑齐"，最后字段变成装饰。分别列虽然麻烦，但每个字段都对应一个真实的使用场景。

---

## 五、`_raw_response.txt` 可逆性（T-SKILL-05、06，各 3 = 6 条）

### 容器格式

```
<<<FILE: SKILL.md>>>
（SKILL.md 全文）
<<<END: SKILL.md>>>
<<<FILE: METADATA.md>>>
（METADATA.md 全文）
<<<END: METADATA.md>>>
<<<FILE: FLOW.md>>>
（FLOW.md 全文）
<<<END: FLOW.md>>>
<<<END>>>
```

### T-SKILL-05 段集合必须完全一致

**检验**：解析出的段名集合必须**恰好等于** `{SKILL.md, METADATA.md, FLOW.md}`。

**当前结果**：3/3 PASS，实得段均为 `['FLOW.md', 'METADATA.md', 'SKILL.md']`，文末 `<<<END>>>` 存在。

**这条断言在写本文件的过程中改严过一次，原因是抓到一个真实隐患**：

初版用正则 `<<<FILE: (.+?)>>>\n(.*?)\n<<<END: \1>>>` 解析，结果 research-report-to-flow 解出 **5 个段**：

```
['SKILL.md', 'x', 'METADATA.md', 'FLOW.md', 'x']
```

多出来的 `x` 从哪来？——因为该 Skill 的 SKILL.md 和 FLOW.md 正文里有一句说明性文字，写着"分隔符统一为逐文件 `<<<FILE: x>>> ... <<<END: x>>>`"。正则不区分"行首标记"和"行内示例"，把这个示例当成了真实分块。

更麻烦的是：**这个错误不会导致 FAIL**。因为 `x` 在磁盘上不存在，逐段比对时被 `os.path.exists` 跳过，测试照样 PASS。也就是说，容器格式已经产生了歧义，测试却报告一切正常。

**处理**（两处）：

1. 测试改用与 `tools/build_raw.py` **同构的逐行状态机** `split_raw()`——只认行首标记，行内示例不会被误判；
2. 断言从 `len(blocks) >= 3` 收紧为 `set(blocks) == want`，多一个段也算 FAIL。

**这条的教训**：测试与生产必须用**同一套解析逻辑**。用两套实现去互相验证，看似更严格（"双重独立"），实际是引入了两个可能不一致的判据——一旦不一致，你无法判断是数据错还是解析错。真正该做的是：解析逻辑统一一处，测试去校验**结果**。

### T-SKILL-06 逐段与磁盘一致

**检验**：每个段的内容，与磁盘上同名文件的内容（去掉首尾空白后）**逐字符相等**；磁盘上找不到同名文件也算 FAIL。

**当前结果**：3/3 PASS，不一致列表为空。

**这条是真实失效过两次的**：

本项目两次修改了 `FLOW.md` 与 `METADATA.md`（一次加"分母口径三问"，一次加 `assumption_register` 的追溯规则），但**都忘了重跑 `tools/build_raw.py`**。结果是：磁盘上的文档是新的，`_raw_response.txt` 还是旧的，两者内容不同——四件套失去可逆一致性。

这种情况下分发出去的 `_raw_response.txt` 会把旧条款带给使用者，而作者以为新条款已经生效。

**修复**：`python tools/build_raw.py` 重建，输出 `ALL_MATCH`。并且这条断言现在会持续守着——以后任何一次改文档忘了重建 raw，它立刻红。

---

## 六、四条单点条款（T-SKILL-07 ~ T-SKILL-10，4 条）

### T-SKILL-07 阈值三档与 `UNDEFINED_THRESHOLD`

**检验**：`research-report-to-flow/METADATA.md` 中同时存在 `UNDEFINED_THRESHOLD` 与 `bands`。

**为什么是这两样**：只定义"高/中/低"三档不够——**真正的问题是有些指标根本没有公认阈值**。此时流程必须能说"我不知道该用什么阈值"，而不是随手填一个。`UNDEFINED_THRESHOLD` 就是这个出口。

**PASS**。

### T-SKILL-08 公式注册表含 `formula_version` 与生效期

**检验**：`formula_version` 出现，且 `valid_from` 或 `effective` 至少出现一个。

**当前结果**：PASS —— 但**这条是修出来的**。

首轮实现时，`formula_registry.required_fields` 是：

```
[formula_id, expression, variables, unit, freq, valid_from, valid_to, source, caliber_note]
```

有 `valid_from` / `valid_to`，**但没有 `formula_version`**。也就是说，同一条公式如果口径变了，只能靠有效期区间去区分，无法回答"这条结论当时用的是哪一版公式"。

**修复**：补齐 `formula_version`，并新增 `versioning_rule`，规定：

- `formula_id` 恒定，`formula_version` 随口径变化递增；
- 同一 `formula_id` 的不同版本，有效期不得重叠；
- 引用公式的 claim 必须同时记录 `formula_id` 与计算时实际使用的 `formula_version`。

**这条修正的意义**：`valid_from/valid_to` 解决的是"公式什么时候有效"，`formula_version` 解决的是"结论用的是哪一版"。前者管数据，后者管结论复算。缺了后者，历史报告在公式换代后就无法复算。

### T-SKILL-09 Step 0 数据预处理

**检验**：`research-report-to-flow/FLOW.md` 含 "Step 0"。

**为什么必须有 Step 0**：数据进来第一件事不是算，是**裁决**——这份文件是哪个版本？编码是什么？单位是元还是万元？期间是累计还是单季？这四件事没定，后面每一步都在错误前提上跑。

**实例**：案例三有 4 份招募说明书（2026-05-15 初稿、2026-07-28 更新、2026-10-28 更新、法律意见书封卷稿），Step 0 裁决以 **2026-10-28 更新稿**为主版本，所有引用页码均指向该版本。

**PASS**。

### T-SKILL-10 投后 FLOW #20 含分母口径三问

**检验**：`reits-post-investment-monitor/FLOW.md` 含"分母口径三问"。

**这条是**整个项目最重要的一次流程进化**的固化点**。

**背景**：案例二初稿用年报的市值口径分派率 4.36% 去对标招募书的募集规模口径预测 4.81%，判"未达标 0.45pct"。这是错的——市值高于募集规模时，市值口径分派率必然低于募集规模口径，与经营好坏无关。

**关键事实**：**这个错误不是 Skill 自动拦下的**，是复核时人工发现的。当时的 #20 只规定了聚合方式（`each_period` / `mean` / `latest`），没有任何分母校验。

**发现后补进 #20 的前置校验**（未答完不得进入裁决）：

1. claim 的阈值是哪个口径下给的？（招募书预测 / 实际·募集规模 / 实际·期末市值 / 实际·评估值）
2. 观测值的分母与阈值的分母是否同一口径？不同则先换算，换算不可行则判 `NOT_COMPARABLE`
3. 若分母随市场变化（市值），该 claim 是否只适用于"投资者实际收益率"而非"是否达标"？

**PASS**。这条断言的存在，等于把那次人工发现永久钉在流程里。

---

## 七、这 31 条的共同逻辑

| 原则 | 体现 |
|---|---|
| **结构可执行** | 四件套齐备、动作编号连续、必备字段在位 → 一个没参与编写的人能照着跑 |
| **分发可逆** | raw 与磁盘逐段一致 → 分发出去的就是作者手上的版本 |
| **条款可追溯** | 每条关键条款（分母三问、假定登记、公式版本）都有对应断言 → 改文档时漏改会被抓住 |
| **测试可信** | 解析逻辑与生产同构、断言收紧到集合相等 → 避免"测试通过但实际有歧义" |

## 八、本组未能覆盖的部分

- **语义正确性未检**：断言只验"字段存在""编号连续""内容一致"，不验"这条条款写得对不对"。例如 #20 的三问是否覆盖了所有分母情形，脚本判断不了；
- **跨 Skill 一致性未检**：三个 Skill 对同一概念（如 `claim_schema`）的定义是否完全兼容，当前没有断言；
- **可执行性未自动验证**：真正的可执行性要看"照着 FLOW 走能不能产出报告"，这由三个案例的实跑（见 `regression_tests.md`）间接证明，不是结构测试能覆盖的。
