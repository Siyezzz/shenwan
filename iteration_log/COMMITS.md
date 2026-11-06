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
| `ae690ce` | 2026-11-06 | docs：新增本文件，记录各轮提交 SHA |
| `4b94bcd` | 2026-11-06 | docs：记录 GitHub 推送失败的三次尝试与本地提交状态（当时未推送） |
| `a0e48d6` | 2026-11-06 | docs：同步汇报材料与验收报告中的过期数字（Skill 数、字数、断言数、迭代轮次） |

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

## 推送状态（最终：已推送）

**已推送成功。远端 `main` = `a0e48d6`，与本地 `master` 一致**（`git ls-remote origin refs/heads/main` 实测）。

推送范围 `5bf176e..a0e48d6`，共 4 笔提交：`892da8f`（第六轮主体）、`ae690ce`、`4b94bcd`、`a0e48d6`。

### 失败过，原因是网络而不是仓库

前三次尝试全部失败，记录下来，因为它决定了后面怎么绕：

| 尝试方式 | 结果 |
|---|---|
| 清空代理变量直连（`HTTP_PROXY= ... git push`） | `Recv failure: Connection was reset` |
| 直连 + `GIT_HTTP_VERSION=HTTP/1.1` | `Failed to connect to github.com:443 after 21112 ms` |
| 经当时的环境代理 | `CONNECT tunnel failed, response 502` |

**根因定位**（用 `curl` 逐项试出来的，不是猜的）：

| 探测 | 结果 | 说明 |
|---|---|---|
| `curl https://api.github.com` | `200` | 代理对 `api.github.com` 放行 |
| `curl https://github.com/` | 间歇性 `502` / 约 1/3 成功率 | 代理对 `github.com` 的 CONNECT 概率性失败，非全封 |
| `curl https://github.com/` 连试 5 次 | 5 次全 502 | 失败是连片的，不是每次都能撞上 |
| `curl --tlsv1.2 --tls-max 1.2 https://github.com/` 连试 3 次 | 1 次 `200` | 与 TLS 版本无稳定关系，仍是概率问题 |
| `ssh -T git@github.com`（22 端口） | 连接超时 | 22 端口不通 |
| `ssh -T -p 443 git@ssh.github.com` | `Permission denied (publickey)` | **443 端口 SSH 握手成功**，只是本地没有密钥；这条路可作备用 |

### 最终怎么推上去的

不是换协议，是**加了一个重试循环**——既然是概率性 502，就重试到撞上窗口：

```bash
TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p')
for i in $(seq 1 12); do
  git -c http.sslVersion=tlsv1.2 push \
    "https://x-access-token:$TOKEN@github.com/Siyezzz/shenwan.git" master:main && break
  sleep 3
done
```

第 2 次就成功：`5bf176e..a0e48d6  master -> main`。

**两点值得记下来**：

- 凭据用的是本机已有的 `git credential` 存储（用户名 `Siyezzz` + 一个 `gho_` 开头的 OAuth token），没有新建也没有把 token 写进任何文件或 `.git/config`；
- 顺带发现一个环境问题：配置里的 `credential.helper` 指向 `PortableGit/.../git-credential-wincred.exe`，该路径实际不存在（每次 git 操作都会打印一行 `No such file or directory`）。不影响推送（`git credential fill` 仍能取到值），但**属于待修**，见下方遗留。

### 遗留（网络侧，与代码无关）

| 项 | 状态 | 建议 |
|---|---|---|
| `credential.helper` 路径失效 | 每次 git 命令打印一行报错 | 改为 `manager` 或指向真实存在的 helper；不影响功能，未擅自改全局配置 |
| 直连 GitHub 443 无路由 | 需代理 | 保持现有代理；`ssh.github.com:443` 可作为备用通道（需先配置并上传公钥） |
| 代理对 `github.com` 概率性 502 | 约 1/3 成功率 | 推送脚本一律带重试；单次 `git push` 失败不代表仓库有问题 |


## 如何复核这一轮

```bash
python tools/build_raw.py                 # 期望 ALL_MATCH（四 Skills 可逆性）
python tools/count_report_words.py outputs/case_03_sinofarm_reit/report_508601.md --min 15000
python tests/run_tests.py                 # 期望 PASS 151 / FAIL 0 / SKIP 2
git show --stat 892da8f                   # 本轮的完整文件清单
```

第二条命令的输出应与 `report_508601.md` 封面声明的「中文正文字符数 22,314」一致；`T-REPORT-01b` 会自动校验这一致性，不需要人工比对。
