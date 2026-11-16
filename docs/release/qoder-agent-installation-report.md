# Qoder 协调：其他 Agent 安装、发现与加载测试报告（v1.0.0-rc1 准备）

- 日期：2026-11-16；执行者：Qoder 协调会话（harness §4）。
- 性质：安装/发现/加载测试，**不是** Host Acceptance；不改变任何 RC gate。
  没有正式合格 record 的宿主继续披露 unverified。
- 结论按 observed / inferred / expected / unverified 标注。
- 证据目录（仓库外 staging）：
  `C:\Users\tutic\IdeaProjects\LoopPilot-rc-staging\agent-install-tests\evidence\`
  （简称 E）。官方来源、抓取日期与本地核对见 staging
  `research-brief-agent-skill-conventions.md`；身份取证见 staging
  `qoder-identity-forensics.md`。

## 0. 共同安装源与既有安装保护

- 安装源：`LoopPilot-rc-staging/clean-source`（git worktree，detached HEAD
  32cf06a3eb05bca9fe3160e4c80006aea1ef9d77，clean）。release 模式源校验通过；
  source snapshot SHA-256
  `0b54c35a876253c855f6254229c5fd566db9b7afbc3b550a879f87ce14a8ffe8`（observed）。
- 既有安装一律未覆盖、未更新、未删除（observed）：
  - `~/.claude/skills/loop-pilot`：COMMIT 89b1a1f3…（FORMAT 2，unreleased）。
  - `~/.agents/skills/loop-pilot`：COMMIT 32cf06a…（FORMAT 2，unreleased），
    本次仅只读 status/C2 检查。
- 字节一致性方法：receipt FILE 行 digest 复核 + 与 32cf06a 的 git blob
  逐字节比对（worktree 检出的 CRLF 归一化差异已单独解释，75 文件；
  0 个不可解释差异）。结果见 E/digest-consistency.json。

## 1. Claude Code 2.1.323

| 项 | 结果 |
|---|---|
| 入口/版本 | `C:\Users\tutic\.local\bin\claude`，2.1.323（observed） |
| 测试目录 | `staging/agent-install-tests/claude-smoke`（全新，非 Git） |
| 安装目标 | `<fixture>/.claude/skills/loop-pilot`（Project scope，官方文档位置） |
| 文件安装 | **成功**（observed）：install.ps1 exit 0；status CURRENT，84 files current，0 modified/conflicted；C2_CLEAN（85 文件枚举，0 findings）；84/84 与 git blob 一致 |
| 宿主发现 | **成功**（observed）：全新 `-p` 会话 init 事件的 skills 与 slash_commands 均含 `claude-smoke:loop-pilot` |
| 宿主加载 | **阻塞**（observed 失败）：两次全新会话均 API 403 “访问已被拦截”（中转 ai.hybgzs.com/claude；model grok-4.7[1m] 与显式 grok-4.7 各一次），无模型回合，Skill 正文未注入 |
| smoke 文件 | 未执行；note.txt 保持原样（observed） |

- 命令（原样保存于 E）：
  `claude -p "<smoke prompt>" [--model grok-4.7] --add-dir <fixture>
  --output-format stream-json --verbose --permission-mode acceptEdits
  --allowedTools "Skill(claude-smoke:loop-pilot)" "Read" "Edit"`，exit 1 ×2。
- 同名解析（官方文档，2026-11-16）：personal 优先于 project；既有 personal
  loop-pilot（89b1a1f）会遮蔽 fixture project 安装。因此采用文档化的
  `--add-dir` 前缀名 `claude-smoke:loop-pilot`（v2.1.309+）保证加载归属指向
  fixture 字节，且不触碰用户目录。发现证据已确证该前缀名注册成功。
- 证据：E/claude-smoke-session.jsonl、E/claude-smoke-session-2.jsonl、
  E/claude-smoke-stderr*.txt、E/status-claude-smoke.txt、E/c2-claude-smoke.txt、
  E/receipt-claude-smoke.txt。
- 判定：403 为 Execution Infrastructure Incident（中转拦截/认证），不是
  LoopPilot 产品缺陷；保留原始失败结果。加载与 smoke 维持 unverified，
  解除阻塞需要可用的 Claude 端点（用户侧中转修复或授权其他端点）。

## 2. Codex CLI 0.168.0

| 项 | 结果 |
|---|---|
| 入口/版本 | npm 全局 shim → `codex.exe`（win32-x64 vendor），0.168.0（observed） |
| 测试目录 | `staging/agent-install-tests/codex-smoke`（全新 fixture Git 仓库，seed commit 972199f2…） |
| 安装目标 | `<fixture>/.agents/skills/loop-pilot`（REPO scope，官方文档位置；二进制字符串核对 0.168.0 亦支持 `$CODEX_HOME/skills`） |
| 文件安装 | **成功**（observed）：install.ps1 exit 0；status CURRENT，84 files current；C2_CLEAN（85 文件，0 findings）；84/84 与 git blob 一致 |
| 宿主发现 | **成功**（observed）：smoke 会话实际读取 fixture 路径下 SKILL.md（见下） |
| 宿主加载 | **成功**（observed）：显式 `$loop-pilot` 触发；item_1 以 `Get-Content -Raw` 读取 `<fixture>/.agents/skills/loop-pilot/SKILL.md` 全文注入；注入内容与 fixture 字节归一后逐字相等（SHA-256 6423abc7ea49b9d1ff3c4c0c2862583d46a9ed1cfc866cd174b6ad815b2b4d57）；item_5 继续读取该 Skill 的 docs/mode-selection-and-escalation.md |
| smoke 文件 | **通过**（observed）：note.txt 第一行改为 `installed-ok`，其余两行与换行保留；git diff 保存于 E/codex-smoke-note-diff.txt |

- 命令：`codex exec -C <fixture> -s workspace-write --json -o <last-message>
  "<smoke prompt（$loop-pilot 显式调用）>"`，exit 0（E/exit-codes.txt）。
- 会话：thread 01a1e277-bb3f-7de2-bc8c-0bf6fe031f59；事件流
  E/codex-smoke-session.jsonl；末条消息 E/codex-smoke-last-message.txt。
  宿主持久化 rollout 原位保留：
  `~/.codex/sessions/2026/11/16/rollout-2026-11-16T11-47-40-01a1e277-bb3f-7de2-bc8c-0bf6fe031f59.jsonl`
  （SHA-256 178bf7f7ec2e0b463bbb8cb1a7de43b3374448b6454e64fa7826dd17fe4fe140；
  向证据目录复制被权限策略拦截，未复制，按路径+digest 引用）。
- 过程事件（observed）：5 次限流重连（gpt-6.1-sol / eastus2 错误文本），
  turn 最终完成；该文本不构成上游身份证明（见身份取证记录）。
  控制台重定向中文出现 GBK 乱码；命令/路径 ASCII 不受影响。
- 同名说明：USER scope `~/.agents/skills/loop-pilot` 同为 32cf06a，文档声明
  同名不合并；本次加载事件的实际读取路径归属 fixture REPO scope（observed）。
- 隔离探针（全新会话，不计分，E/codex-probe-session.jsonl，exit 0）：
  读主仓库 README.md **允许**；写 fixture 外文件 **拒绝**（PermissionDenied）；
  fixture 内 git status **允许**。含义与正式臂阻塞见
  `docs/release/codex-rc-execution-surface.md` §3。
- 判定：安装/发现/加载/smoke 全链路 observed 通过。这是安装测试，不是
  Host Acceptance；Codex 上游身份仍 unverified，Gate 4 不变。

## 3. Qoder Desktop 0.5.12（协调者自身）

| 项 | 结果 |
|---|---|
| 版本 | 运行 0.5.12（manifest observed；运行版本 inferred，见取证记录） |
| 安装 | 未新建安装。既有 `~/.agents/skills/loop-pilot`（32cf06a）只读核验：status CURRENT（84 files current，0 modified），C2_CLEAN（含 41 个历史更新备份文件，保留不动） |
| 发现 | **成功**（observed）：本会话 available-skills 列表含 loop-pilot；官方文档（docs.qoder.com/qoder/skills，2026-11-16）声明发现 `~/.agents/skills`，同名以 Qoder 用户管理目录优先 |
| 来源归属 | inferred：官方发现规则 + 名称/描述匹配 + receipt commit 一致；Qoder 不暴露逐 Skill 来源路径，用户管理目录是否存在同名覆盖 unverified |
| 加载 smoke | **阻塞**：需在全新会话+独立临时工作目录执行；临时目录登记为 Workspace 的 `workspace.creation` 操作要求人工在 UI 提交（agent.executable=false）。列入中央 unblocker 清单 |

- E/status-qoder-agents-scope.txt、E/c2-qoder-agents-scope.txt。
- Qoder 不是 Option B Reference；本测试不申请资格变更。

## 4. 其他候选

- Gemini CLI、GitHub Copilot CLI、cursor-agent、aider：不在 PATH（observed，
  `command -v`）。未替用户安装任何新 Agent 产品。`gh` 存在但非 Agent。

## 5. 回退与保留

- 本次新建的两个 fixture 安装位于 staging 独立测试目录，保留作证据；
  如需回退，可用官方 `uninstall.ps1 -Destination <fixture target>`（仅限
  本次新建、未定制安装），回退结果将另行记录。未执行任何回退。
- 用户目录既有安装与 `~/.codex/sessions` 原始 rollout 未改动。

## 6. 验证缺口（诚实披露）

- Claude Code 加载/smoke：unverified（中转 403，原始失败已保存）。
- Qoder 加载 smoke：unverified（Workspace 需人工登记）。
- Codex 上游身份：unverified（中转；客户端错误文本不升格）。
- quick Skill validation：**已解决**。Codex 宿主自带 skill-creator 的
  `quick_validate.py`（`~/.codex/skills/.system/skill-creator/scripts/`，
  SHA-256 6068513d924ed3559e186dfcdead7439129828dcf402167fd925c06dffbf2806）
  对仓库根实跑 “Skill is valid!” exit 0（observed，
  E/quick-validate-host-bundled.txt）；用户报告 Codex 此前已用同一宿主自带
  脚本实跑通过（attributed）。早前 GitHub main 下载副本（SHA-256
  67cf5703402013936c8fb75ad6a1afecd8841d45cc5e606b634eb05825fde365，
  来源 raw.githubusercontent.com/anthropics/skills/main/skills/skill-creator/scripts/quick_validate.py，
  2026-11-16，版本与宿主自带不同）曾被权限策略拦截、未执行，记录保留为历史。
