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
└── presentation/management_briefing.md   # 上级汇报材料
```

## 当前进度

| 阶段 | 状态 | 产出 |
|---|---|---|
| 一、附件审计与模板研究 | **完成** | `outputs/research_flow_audit/attachment_study.md`、`research_flow_audit.xlsx`、`template/template_convention_audit.md` |
| 二、研报转 FLOW 方法论 Skill | 未开始 | — |
| 三、两个 REITs 业务 Skill | 未开始 | — |
| 四、真实资料获取 | 部分（复用上一轮已下载的上交所文件，需复核） | `source_documents/` |
| 五、三案例实跑 | 未开始 | — |
| 六、三轮迭代 | 未开始 | — |
| 七、GitHub | 本地 git 已初始化，**无远端**（环境无 gh CLI） | — |
| 八、最终目录 | 骨架已建 | — |
| 九、汇报材料 | 未开始 | — |
| 十、最终验收 | 未开始 | — |

## 数据来源

全部案例文件来自上海证券交易所 REITs 公告页（`www.sse.com.cn`）与基金管理人官网披露的原始 PDF，逐份记录在 `source_documents/*/SOURCE_INDEX.md`。不引用搜索引擎摘要。

## 许可与边界

- 原始披露文件版权归发行人/管理人，仅作研究留档，不再分发。
- 本仓库不含任何非公开信息。
