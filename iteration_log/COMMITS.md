# 提交记录

本文件记录各轮迭代对应的提交，供复核时按 SHA 定位。

**为什么不把 SHA 写进 `final_acceptance_report.md`**：该文件本身每次修订都会产生新提交，把 SHA 写进自身会导致"引用的哈希必然不是当前版本"。因此把提交记录单独成文件，并接受"本文件记录的最后一个提交不包含本文件自身"这一事实。

## 全部提交

| SHA | 日期 | 说明 |
|---|---|---|
| `f477729` | 2026-11-05 | phase1：附件审计基线（11 套 Skill + 11 份研报），建立模板规范与问题清单 |
| `9846c10` | 2026-11-06 | feat：三 Skill 建成 + 三案例实跑 + 四轮迭代 + 19 项验收（94 条断言全过） |
| `f32e319` | 2026-11-06 | docs：GitHub 推送完成（main=9846c10），验收 A18 由 NOT TESTED 改为 PASS |
| `6dfa37d` | 2026-11-06 | docs：推送记录改为不锁定哈希的稳定表述 |
| `1e3777f` | 2026-11-06 | fix(docs)：修正验收报告结论段的 Markdown 加粗嵌套 |
| `48cce47` | 2026-11-06 | docs：新增面向老师的纯口语汇报稿 `teacher_briefing.md` |
| `c89fbb1` | 2026-11-06 | feat(data)：材料 24→60 份，修正被材料完备性照出的六个问题（第 5 轮） |
| `5bf176e` | 2026-11-06 | chore：移除误提交的临时对比文件 `_old180302.csv` |
| **`892da8f`** | **2026-11-06** | **第六轮重构：新增研报撰写 Skill，三份报告按投研体例重写** |

## 第六轮（`892da8f`）动了什么

| 类别 | 文件 |
|---|---|
| 新增 Skill | `skills/reits-report-writing/{SKILL,FLOW,METADATA}.md` + `_raw_response.txt`（`build_raw.py` 校验 `ALL_MATCH`） |
| 新增模板 | `template/investment_report_template.md`、`template/post_investment_report_template.md`、`template/report_style_analysis.md` |
| 新增工具 | `tools/count_report_words.py`、`tools/build_bottomup.py`、`models/scenario_2028.csv` |
| 新增审计 | `outputs/report_quality_audit.md`（31 条问题清单）、`outputs/source_data_audit.md`（60 份 PDF 十项核验） |
| 重写报告 | 三份 `report_*.md`（6,210 / 6,839 / 22,314 中文字符） |
| 更正数据 | `source_documents/source_index.csv`（60 条页数回填 + `channel` 字段）、`case_03` 的 `assumptions.csv`（20→25）、`claims_verdict.csv`（11→12） |
| 扩充测试 | `tests/run_tests.py`（95→153 条，新增 T-REPORT 组） |
| 更正表述 | `README.md`（数据来源渠道、进度表、测试数）、`.gitignore`（24→60 份注释）、`outputs/final_acceptance_report.md`（19→25 项） |
| 迭代留痕 | `iteration_log/ITERATION_LOG.md`（追加 Iteration 6，含两轮审稿记录） |

## 推送状态（如实记录）

**本地提交已完成，远端推送未成功。**

| 时间 | 尝试方式 | 结果 |
|---|---|---|
| 2026-11-07 | 清空代理变量直连（`HTTP_PROXY= ... git push`） | `Recv failure: Connection was reset` |
| 2026-11-07 | 直连 + `GIT_HTTP_VERSION=HTTP/1.1` | `Failed to connect to github.com:443 after 21112 ms: Could not connect to server` |
| 2026-11-07 | 经本地代理 `127.0.0.1:61071` | `CONNECT tunnel failed, response 502`（两次重试同结果） |

**结论**：当前网络环境下 GitHub 不可达（直连无路由、代理拒绝 CONNECT）。**两笔提交已在本地 `master` 分支就绪**：

- `892da8f` — 第六轮重构主体
- `ae690ce` — 新增本文件
- `4b94bcd` — 记录本推送状态（本提交即第三笔，其自身 SHA 无法写进自身）

**未做的事**：没有声称"已推送"。项目原则第 10 条要求"所有修改须提交 GitHub 并记录 Commit SHA"——前半句（提交 + SHA）已完成，后半句（推送到远端）受网络限制未完成。恢复网络后执行：

```bash
git push origin master:main
```

不需要任何额外操作，本地历史与远端是快进关系（远端当前为第 5 轮的 `c89fbb1` 之后状态，本地在其之上追加两笔）。

## 如何复核这一轮

```bash
python tools/build_raw.py                 # 期望 ALL_MATCH（四 Skills 可逆性）
python tools/count_report_words.py outputs/case_03_sinofarm_reit/report_508601.md --min 15000
python tests/run_tests.py                 # 期望 PASS 151 / FAIL 0 / SKIP 2
git show --stat 892da8f                   # 本轮的完整文件清单
```

第二条命令的输出应与 `report_508601.md` 封面声明的「中文正文字符数 22,314」一致；`T-REPORT-01b` 会自动校验这一致性，不需要人工比对。
