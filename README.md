# reits-research-skills

公募 REITs 投研 Skills 仓库：**研报方法论迁移 + 两个业务 Skill（投后跟踪 / 投前分析）+ 三个真实案例验证**。

## 这个仓库解决什么问题

卖方研报的研究逻辑很难复用：结论留在 PDF 里，方法留在分析师脑子里。已有的"研报转 Skill"做法（见 `template/template_convention_audit.md` 审计的 11 个样本）能把研报变成结构完整的 FLOW，但存在三个系统性缺陷：

1. **数据层空转**——645 条数据需求的 `source_id` 全为 `null`，流程一条都跑不通；
2. **判断层无标尺**——"高/中/低"出现 35 次却没有任何区间定义；
3. **时间层无版本**——公式不记适用期，制度变化后被跨期套用。

本项目不重写模板，而是在**保留原 10 个 METADATA 字段与 FLOW 四段骨架**的前提下，补上数据探针、标尺、公式有效期和"不可判定"四件事，然后用真实披露文件跑三个 REITs 案例来证明它跑得通。

## 目录

```
reits-research-skills/
├── README.md
├── skills/
│   ├── reits-post-investment-monitor/    # Skill A 投后定期跟踪
│   ├── reits-pre-investment-analysis/    # Skill B 投前深度分析
│   └── research-report-to-flow/          # Skill C 研报转 FLOW 方法论
├── template/
│   └── template_convention_audit.md      # 继承规范（写作约束 + 机器校验清单）
├── source_documents/                     # 三案例原始披露文件（PDF）
├── outputs/
│   ├── research_flow_audit/              # 附件学习与 FLOW 审计
│   ├── case_01_glp_reit/
│   ├── case_02_huaxia_shen_international/
│   └── case_03_sinofarm_reit/
├── models/                               # 现金流模型、数据矩阵
├── tests/                                # 数据质量 / 计算 / 执行 / 回归测试记录
├── iteration_log/ITERATION_LOG.md        # 三轮以上迭代留痕
└── presentation/                         # 两版汇报材料
    ├── management_briefing.md            # 面向管理层（提纲+口述稿+追问应答）
    └── teacher_briefing.md               # 面向老师（纯口语：流程/思路/亮点/疑惑）
```

## 当前进度

| 阶段 | 状态 | 产出 |
|---|---|---|
| 一、附件审计与模板研究 | **完成** | `outputs/research_flow_audit/attachment_study.md`、`research_flow_audit.xlsx`、`template/template_convention_audit.md` |
| 二、研报转 FLOW 方法论 Skill | **完成** | `skills/research-report-to-flow/`（SKILL + METADATA + FLOW #1–#18 + raw，可逆一致） |
| 三、两个 REITs 业务 Skill | **完成** | `skills/reits-post-investment-monitor/`（FLOW #1–#22）、`skills/reits-pre-investment-analysis/`（FLOW #1–#26） |
| 四、真实资料获取 | **部分** | `source_documents/` 共 **24 份 PDF** + `source_index.csv`。上交所公告接口需内部 `channelId`，公开请求不可用，已登记 `SOURCE_UNAVAILABLE` 并配置东方财富备用源；首农另有 2 项不可得（资产评估报告、基金合同） |
| 五、三案例实跑 | **完成** | 三份报告（4,230 / 3,728 / **17,559** 中文字符）+ `run_log.md` + `claims_verdict.csv` + `source_index.csv`；案例三另有 `assumptions.csv`（20 条）与 `figures/` |
| 六、三轮以上迭代 | **完成（4 轮）** | `iteration_log/ITERATION_LOG.md`，Iteration 1 可执行性 / 2 研究质量 / 3 鲁棒性 / 4 自检可信度，每轮含修改前后数值对比 |
| 七、GitHub | **完成** | 已推送至 `github.com/Siyezzz/shenwan`（`main` 分支，首次提交 47 文件 / 10,419 行）。经代理报 502，清除 `HTTP(S)_PROXY` 后直连成功。**原始 PDF（24 份 / 112MB）按 `.gitignore` 不入库**，仅入库 `source_index.csv`——与「许可与边界」中「不再分发」一致 |
| 八、最终目录 | **完成** | 见上节目录结构 |
| 九、汇报材料 | **完成（两版）** | `presentation/management_briefing.md`（管理层版：5 页提纲 + 1,342 字口述稿 + 数据卡 + 12 条追问 + 边界声明）；`presentation/teacher_briefing.md`（老师版：纯口语 2,928 字，按「流程/思路/亮点/疑惑」四段，含 3 档时长裁剪 + 7 条追问备用） |
| 十、最终验收 | **完成** | `outputs/final_acceptance_report.md`（19 项：16 PASS / 2 PARTIAL / 0 FAIL / 1 NOT TESTED） |

## 自检

```bash
python tools/build_raw.py      # 重建并校验 _raw_response.txt 可逆性（期望 ALL_MATCH）
python tests/run_tests.py      # 94 条断言（期望 PASS 94 / FAIL 0）
```

| 测试组 | 条数 | 说明文档 |
|---|---|---|
| T-CALC 计算与对账 | 22 | `tests/test_calculations.md` |
| T-DQ 数据质量 | 24 | `tests/test_data_quality.md` |
| T-SKILL Skill 结构 | 31 | `tests/test_skill_execution.md` |
| T-REG 回归 | 17 | `tests/regression_tests.md` |

## 数据来源

全部案例文件来自上海证券交易所 REITs 公告页（`www.sse.com.cn`）与基金管理人官网披露的原始 PDF，逐份记录在 `source_documents/source_index.csv`。不引用搜索引擎摘要。

## 许可与边界

- 原始披露文件版权归发行人/管理人，仅作研究留档，不再分发。
- 本仓库不含任何非公开信息。
