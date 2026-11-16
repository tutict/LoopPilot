# Codex 正式执行面准备记录（v1.0.0-rc1）

- 日期：2026-11-16；准备者：Qoder 协调会话。
- 性质：harness §5 要求的基础设施准备记录，不是正式臂，不计分。
  所有结论按 observed / inferred / expected / unverified 标注。
- 证据目录：`C:\Users\tutic\IdeaProjects\LoopPilot-rc-staging\agent-install-tests\evidence\`
  （下文简称 E）。研究来源与日期见 staging `research-brief-agent-skill-conventions.md`。

## 1. 真正的宿主入口（observed）

-  shim：`C:\Users\tutic\AppData\Roaming\npm\codex`（npm 全局）。
- 实际二进制：`C:\Users\tutic\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`。
- 版本：codex-cli 0.168.0（`codex --version`）。
- 已验证启动命令（本记录全部实测）：
  `codex exec -C <fixture> -s workspace-write --json -o <last-message-file> "<prompt>"`
  - `--json`：stdout JSONL 事件（thread.started / turn.started / item.* / turn.completed / error）。
  - 默认持久化会话 rollout：`~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<thread-id>.jsonl`。
  - `--ephemeral` 可关闭持久化（正式臂不应使用）。
- help 已核对（E 外，命令 `codex exec --help`）；未照搬 Claude flags。

## 2. Skill 加载（observed 机制；designation 绑定 BLOCKED）

- 官方发现规则（docs，2026-11-16）：REPO `$CWD/.agents/skills` 向上至 repo root；
  USER `$HOME/.agents/skills`；ADMIN `/etc/codex/skills`；SYSTEM 内置。
  二进制字符串核对：0.168.0 同时支持 `$CODEX_HOME/skills`（默认 `~/.codex/skills`）。
- 实测加载机制（E/codex-smoke-session.jsonl，thread 01a1e277-bb3f-7de2-bc8c-0bf6fe031f59）：
  显式 `$loop-pilot` 触发后，宿主以 shell `Get-Content -Raw` 读取
  fixture `.agents/skills/loop-pilot/SKILL.md` 全文并注入上下文（item_1），
  随后按 Skill 指引读取 `docs/mode-selection-and-escalation.md`（item_5）。
  注入内容与 fixture 字节一致（CRLF/尾换行归一后逐字相等；SKILL.md SHA-256
  6423abc7ea49b9d1ff3c4c0c2862583d46a9ed1cfc866cd174b6ad815b2b4d57）。
- 安装目标（本次实测）：全新 fixture Git 仓库
  `staging/agent-install-tests/codex-smoke/.agents/skills/loop-pilot`，
  源 `staging/clean-source`（HEAD 32cf06a，clean，git-release 模式），
  receipt CURRENT、C2_CLEAN、84/84 文件与 32cf06a git blob 逐字节一致。
- 同名冲突（observed docs + 本地）：USER scope `~/.agents/skills/loop-pilot`
  已存在且同为 32cf06a；文档声明同名不合并、均可见。smoke 事件中的实际读取
  路径归属 fixture REPO scope。正式臂必须固定唯一加载来源并记录实际路径。
- 与 designation 一致的加载模式：**BLOCKED**。当前矩阵含 explicit 与 implicit
  （IMP-1）两种模式，而 designation/record 的 `Skill loading mode` 为单值，
  冲突已复现（staging repro-loading-mode/，6 案例）；P1 集合语义修正待授权。
  在修正与 designation finalization 前不得发起正式臂。
- 安装 Hash B：**BLOCKED（operator 输入）**。仓库内无字节级定义；现行程序
  （rc1-preflight E11/E12、successor C06）要求 operator 识别既有定义/来源并
  独立绑定所选已验证 receipt。已测候选输入（不构成 Hash B 声明）：
  source snapshot SHA-256 0b54c35a876253c855f6254229c5fd566db9b7afbc3b550a879f87ce14a8ffe8；
  receipt 见 E/receipt-codex-smoke.txt。不自行发明定义或自签哈希。
  定义方案已成文待 operator 裁决：staging `hash-b-definition-proposal.md`
  （推荐 HB-1 = receipt 原始字节 SHA-256，实测
  00781c743ed5434746157b5ed6a6800cc0277ab2cab6ac5fe157210753261080；
  含 HB-2/3/4 备选与绑定程序；若 installer 修复先行提交则 receipt 须重生成、
  Hash B 须重绑定）。

## 3. C1/C2 隔离（原生读控制已 observed；exec 级集成 unverified）

- fixture 位于主仓库外（observed）；安装目录 C2_CLEAN（observed，E/c2-codex-smoke.txt，
  85 文件枚举、0 findings）。
- 旧配置隔离探针（E/codex-probe-session.jsonl，全新会话，不计分）：
  1. 读取主仓库 `README.md` 第一行：**允许**（exit 0）。→ 旧
     `unelevated + workspace-write` 配置下宿主工具面可读取主仓库验收材料；
     cwd 在仓库外 + C2_CLEAN 不构成 C1。
  2. 写 fixture 外 `staging/agent-install-tests/probe-outside.txt`：**拒绝**
     （PermissionDenied，exit 1；文件未产生，observed）。
  3. fixture 内 `git status --short`：**允许**（exit 0）。
- 用户全局上下文注入（observed，smoke rollout）：Codex 会话注入用户全局
  指令、USER scope 全部 Skill 列表与插件 Skill（如 superpowers）；宿主可读
  `~/.codex` 插件缓存。正式臂的 C1 必须覆盖这些通道。
- 2026-11-16 后续核查（observed，staging 探针，不计分；完整矩阵与来源见
  staging `c1-read-isolation-verification.md`、
  `research-brief-codex-sandbox-controls.md`；证据 E/c1-probe-battery*.json/.txt、
  E/c1-p1c-noargconv.txt、E/c1-p3b-p5b-profile-deny.txt）：
  - 0.168.0 存在三种 Windows sandbox 后端（mxc / elevated / unelevated）与
    Beta 权限 profile（`[permissions.<name>]`、`default_permissions`、`-P`）。
  - MXC 在本机可用（build 26300.9974；官方文档精确测试命令输出 MXC_OK，
    exit 0），无需管理员 setup、专用账户或防火墙改动；未做任何机器级变更。
  - MXC + root-deny profile（staging CODEX_HOME，extends :workspace、
    `:root`=deny、`:minimal`=read、`.git`=write、network off）实测：主仓库
    README 与 evaluations 模板、Qoder 项目 memory、`~/.codex/config.toml`、
    staging 证据 receipt、USER scope Skill、staging 保护文件全部 **DENIED**；
    fixture 内读写与 git status/add/commit/log 全部允许（seed commit 164dba2）；
    fixture 外写拒绝且文件未产生。
  - 现行配置的 `unelevated` 后端对 deny-read profile **fail-closed 拒绝**
    （"Restricted read-only access requires the elevated Windows sandbox
    backend"，exit 1），不会静默降级为无沙箱执行。
  - `elevated` setup 未运行（机器级变更，未授权，且本机 MXC 已可用）。
- 结论：原生**读隔离**控制存在且在 sandboxed-command 层已被强制（observed）。
  仍 unverified：`codex exec` 模型会话级集成（exec 无 `-P`，须用无
  `sandbox_mode` 键的专用 CODEX_HOME + `default_permissions`；中转 token 须由
  operator 放入该 home，不上命令行、不入证据）；非命令通道（插件/MCP/
  browser/computer-use/web-search/notify）不受 profile 管辖，正式臂 home 必须
  全部关闭并复核宿主侧 Skill/AGENTS.md 枚举通道。正式臂发起前须以最终
  arm-home 重跑探针矩阵。禁止以增加目录访问或模型口头保证替代隔离。

## 4. 新鲜上下文（observed 机制）

- 每臂一个独立 `codex exec` 进程/线程；smoke 与探针各自新 thread（observed）。
- 不使用 `exec resume`/`fork`；FL-1R 的前序 checkpoint 依赖必须按 runbook
  以显式输入传递，不用宿主 resume 冒充（程序要求）。
- 不继承 Qoder 对话：exec 会话无本会话历史（observed，rollout 仅含该次输入）。

## 5. 权限与 AOS（observed 基础；交集待正式固定）

- 用户配置 `sandbox_mode=workspace-write`（observed，脱敏读取）；实测以
  `-s workspace-write` 显式固定，未使用 danger-full-access 或
  --dangerously-bypass-approvals-and-sandbox。
- 拒绝行为可观察（探针 2 的 PermissionDenied 原文保存于 E）。
- fixture 内本地 Git 操作能力：旧 `-s workspace-write` 路径下 status observed
  允许、commit inferred 未实测；MXC + c1arm profile 路径下 status/add/commit/log
  全部 observed 允许（staging fixture seed commit 164dba2，需 `.git`=write
  覆盖与 fixture 内 GIT_CONFIG_GLOBAL）。正式臂授权 = 宿主能力 ∩ 原始 prompt
  授权；原始任务 prompt 的 Git 授权按权威规格固定，不放宽。

## 6. 原始输入（机制 observed；内容固定待正式臂）

- 输入经命令行 prompt 参数传入；rollout 记录实际收到的用户消息（observed）。
- 正式臂要求：从权威规格取原任务文本，启动前固定文件字节与 SHA-256，
  启动后核对 rollout 中的实际输入与固定字节一致。本次未发起正式臂，
  未固定任何正式输入。

## 7. 公开事件与身份（事件 observed；上游身份 unverified）

- 事件面：`--json` JSONL + 持久化 rollout 可保存输入、命令、输出、退出码、
  时间、thread id；cwd 由 `-C` 固定（observed）。
- 身份：host version 0.168.0 observed；configured gpt-6.1-sol /
  anyrouter.top/v1 observed（配置声明）；上游 provider/model/endpoint
  **unverified**（中转；限流错误文本仅为客户端事件，不构成上游证明）。
  详见 staging `qoder-identity-forensics.md`。现行证据合同要求 observed
  identity 非 unknown → 正式臂硬前置未满足。
- 编码注意：Windows 控制台重定向的中文输出出现 GBK 乱码（observed，
  E/codex-smoke-session.jsonl 首条 agent_message）；命令与路径为 ASCII 不受
  影响。正式臂采集应固定 UTF-8 输出（如经 `--json` 文件直写或 chcp 65001），
  该缓解措施 expected，未实测。

## 8. Reviewer 路径（BLOCKED；输入清单已备）

- 需要真实独立 operator/session 与密封输入路径；同一 operator 自签或改标签
  不算独立。本次运行无可用独立 Reviewer/operator 输入，未创建任何
  review.json 或 operator index。列入中央 unblocker 清单。
- 输入清单已成文：staging `reviewer-input-checklist.md`（readiness receipt
  精确 schema、外部 raw-SHA-256 pin 规则、runbook 顺序、preflight 五键、
  阻塞条件），依据 behavior_validation.py:125,144-200 与 two-stage runbook。

## 结论

执行面在入口、加载机制、新鲜上下文、写隔离、事件保存方面已有 observed
基础；C1 原生读控制已在 sandboxed-command 层 observed（MXC + root-deny
profile），exec 模型会话级集成与非命令通道仍 unverified。正式臂发起前仍缺：
loading-mode 冲突修正授权、designation finalization、上游身份可信取证、
最终 arm-home 的 exec 级 C1 复核（operator 提供中转配置）、Hash B operator
绑定（方案已备）、独立 Reviewer/operator 输入（清单已备）、主仓库 commit
授权（指定记录提交）。全部列入工作报告的中央 unblocker 清单；本记录不声称
任何正式臂已具备发起条件。
