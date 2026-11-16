# Qoder RC 推进工作报告（2026-11-16）

Status: preparation work report; not run evidence, not acceptance

执行指令：[`qoder-rc-harness.md`](qoder-rc-harness.md)（用户附件原文）。
本报告记录本次实际修改、验证、证据与缺口。所有结论区分
observed / inferred / expected / unverified。授权状态（2026-11-16 更新）：
operator 条件授予仅本次两个本地提交（installer 修复 / docs 记录），前提是
独立审查 + 完整验证通过；P1 revision 1 被驳回，revision 2 待授权，未获授权
的 P1 修改不得提交。push、release tag、发布、部署、外部消息、正式臂、
RC gate 勾选均未授权；交付保持 NOT_RELEASE_READY。

## 1. 实际 Git 边界与修改

- 起点与当前 HEAD：`32cf06a3eb05bca9fe3160e4c80006aea1ef9d77`，
  tree `fe98da9ca45581d4447a4dc7f0c670d25bd13e2a`（observed，工作树未提交）。
- 模式决定：单人有界准备，Lightweight（按 mode-selection 规则；无多实现者、
  无正式 Rework）。未实例化 Full Loop 模板，未新增角色/Ledger/验收层。
- 仓库内修改（全部可逆、未提交）：
  - `docs/README.md`：Acceptance preparation 索引增加 harness 链接。
  - 新增 `docs/release/qoder-rc-harness.md`（用户提供的执行指令原文入库）。
  - 新增 `docs/release/codex-rc-execution-surface.md`（§5 执行面准备记录）。
  - 新增 `docs/release/qoder-agent-installation-report.md`（§4 安装测试报告）。
  - 新增本报告。
  - `distribution/loop-pilot.ps1`：最小 Windows 兼容修复（PS<6 时设 UTF-8
    控制台输出编码），修复 cp936 控制台下中文路径传参损坏（见 §6.1）。
  - `.looppilot/HANDOFF.md` 保持 shipped 中性模板不变；会话 handoff 存于
    staging/HANDOFF-session-20261116.md（见 §6.1 的合同冲突处置）。
- 仓库外 staging（`C:\Users\tutic\IdeaProjects\LoopPilot-rc-staging\`）：
  clean-source worktree（HEAD 32cf06a）、maint-env（CPython 3.13.13 +
  requirements-dev.txt）、loading-mode 复现脚本与六组案例、P1 修正提案
  （revision 2，含 M01–M20 组合模拟与 operator 反例 M18/M19）、P1 参考模拟
  （p1_simulation.py，20/20 期望一致）、
  Research Brief（agent-skill-conventions 与 codex-sandbox-controls）、
  身份取证记录、agent-install-tests（fixture、证据、receipt）、
  C1 读隔离核查记录与探针脚本/证据、Hash B 定义方案、独立 Reviewer
  输入清单。
- 既有安装与历史证据未改动（observed）：`~/.claude/skills/loop-pilot`
  （89b1a1f）、`~/.agents/skills/loop-pilot`（32cf06a，含 41 个历史备份文件）、
  `~/.codex/sessions` 原始 rollout。

## 2. 七项 RC 条件缺口清单（事实索引）

| # | 条件 | 当前状态 | 证据 / 缺口 | 下一动作 |
|---|---|---|---|---|
| 1 | `validate.py` passes | 工作树 PASS（observed），已提交边界 unverified | run 3 链内 Static validation passed，exit 0；边界为 HEAD 32cf06a + 未提交修改（§6） | 提交授权后在已提交候选边界复跑并记录 |
| 2 | full regression passes | 工作树 PASS（observed），已提交边界 unverified | run 3：Ran 1235 tests，OK，exit 0（§6）；run 1 作废、run 2 五失败已诊断处置（§6.1） | 同上；工作草稿 PASS 不勾选 gate |
| 3 | Phase 11 independent review | unmet | 仓库内无审查记录（observed，checklist 既有结论）；P11A-4 等 disposition 需独立 Reviewer | 确认独立 operator/session，按 readiness template 保存外部 receipt |
| 4 | designated Reference qualified RC-bound accepted record | unmet | Codex 已指定为 v1.0.0-rc1 Reference（observed，designation 未 finalized）；无合格 record；上游身份 unverified；loading-mode 绑定冲突未解决；Hash B 定义/来源待 operator | 见 §5 中央 unblocker 清单 |
| 5 | candidate hosts verified/unverified 披露 | met（既有） | README limitations 全列 unverified（observed）；本次安装测试不改变 verdict | 保持披露；安装测试结果单独成表 |
| 6 | no unresolved Major/Critical Finding | unmet（无证据源） | 无 Finding instance store（observed）；不能以缺席推断无问题 | 由关闭 Phase 11 的独立审查给出 bounded disposition |
| 7 | CHANGELOG candidate section | met（既有） | `v1.0.0-rc1` NOT_RELEASE_READY 段存在（observed） | 不改 `unreleased` 安装版本 token |

Gate 4/6 的正式证据链（designation finalize → Hash B/C2 → 身份 capture →
四臂 → 盲审 → operator index → accepted record）整体未启动；本次完成的是
其可并行的准备段。

## 3. loading-mode 冲突：复现与提案（未实施）

- observed：经公共 validator 入口用测试专用 fixture 复现六组案例
  （staging/repro_loading_mode.py、repro-loading-mode/results.json）：
  A/B/D/E/F 五组反例失败（exit 1），C 组（全 explicit）为通过对照
  （exit 0）。单值
  designation/summary 的 `Skill loading mode` 无法同时绑定
  LW-1/FL-1/FL-1R（explicit）与 IMP-1（implicit）。这是 inferred 合同缺陷的
  机器复现，不是正式臂失败。
- 提案 P1（staging/proposal-loading-mode-binding.md，**revision 2**）：按
  Cross-Host Acceptance 区分宿主加载机制与任务调用方式，给出字段映射
  （set/union 语义）、兼容影响与可复现反例。revision 1 含加载机制绑定
  （现有四臂共享 boundary 签名检查，无需新机制字段）、旧字段兼容与
  M01–M17 组合模拟，**被 operator 驳回（2026-11-16）**：仍会放行
  「designation 声明 explicit+implicit 但 accepted record 只覆盖 explicit」，
  且未知 token 与旧描述值兼容不足。revision 2 新增：R3 声明模式覆盖
  （record 引用的 reference run 模式并集必须等于 designation 声明集合，
  candidate 不能满足覆盖）、R1 封闭词表 {explicit, implicit} 与显式
  unknown-token 错误、R0 regime 门（pre-successor/历史路径保持原规则
  逐字节不变，不做任何 tokenization）。M01–M20 模拟 20/20 期望一致；
  operator 两个反例 M18/M19 在旧稿下通过、revision 2 下失败（机器演示，
  staging/p1_simulation.py 与 p1-simulation/results.json）。模拟仅 staging
  证据，不是 repo validator 结果，更不是验收证据。
- **未实施**：schema/解释范围变更需当前授权（harness §2）。未用任何禁止手段
  （改 IMP-1 为 explicit、换 designation、丢臂、去绑定、重标 Candidate）
  获取 PASS。任务 #4 保持阻塞直至授权。

## 4. 身份取证、安装测试与执行面（摘要）

- 身份取证（staging/qoder-identity-forensics.md）：Qoder 宿主版本/构建
  observed，上游 unverified（平台不披露）；Codex configured
  gpt-6.1-sol / anyrouter.top（仅配置声明），上游 unverified，限流错误文本
  不升格为上游证明；Claude configured ai.hybgzs.com/claude + grok-4.7 别名，
  403 无成功回合。未输出任何 token/认证头/私密配置。
- 安装/发现/加载（详见 [安装报告](qoder-agent-installation-report.md)）：
  - Codex 0.168.0：安装/发现/加载/smoke 全链路 observed 通过（fixture REPO
    scope，CURRENT、C2_CLEAN、84/84 git-blob 字节一致，note.txt 首行
    installed-ok 其余保留）。
  - Claude Code 2.1.323：安装+发现 observed 成功（前缀名
    `claude-smoke:loop-pilot`）；加载被中转 403 阻塞（EII，原始失败保留）。
  - Qoder 0.5.12：既有安装只读核验 CURRENT/C2_CLEAN；发现 observed；
    加载 smoke 需人工登记临时 Workspace，阻塞。
  - Gemini CLI / Copilot CLI 等不在 PATH（observed）；未安装新 Agent 产品。
- Codex 执行面（[执行面记录](codex-rc-execution-surface.md)）：8 项映射中
  入口、加载机制、新鲜上下文、原始输入、事件保存 observed 可行；
  **C1 原生读控制已 observed**（MXC + root-deny 权限 profile：验收 corpus、
  项目 memory、operator 配置/证据、USER scope Skill 全部 DENIED，fixture
  读写与本地 commit 允许；旧 unelevated+workspace-write 配置读主仓库的
  发现仅对该旧配置成立）；`codex exec` 模型会话级集成与非命令通道仍
  unverified，正式臂须用最终 arm-home 复核。designation 绑定、Hash B、
  Reviewer 路径阻塞（方案/清单已备）。正式臂不得在前置清单关闭前启动。

## 5. 中央 unblocker 清单（最小解阻项）

正式臂启动前全部需要；按依赖排序：

1. **P1 loading-mode 修正授权**：revision 1 已被 operator 驳回（record 覆盖
   漏洞 + 未知 token/旧描述值兼容不足）；revision 2 已按驳回意见修正并附
   M18/M19 机器反例（§3），重新待授权。未获授权前不实施、不提交任何 P1
   修改。
2. **主仓库提交授权（已条件授予，2026-11-16）**：仅本次两个本地提交
   （A：installer cp936 修复；B：docs/README.md 索引 + docs/release 四份
   记录），前提是相关修改通过独立审查与完整验证；不 push、不打 tag、
   不发布、不启动正式臂、不勾选 RC gate；保持 NOT_RELEASE_READY。
   designation finalize 要求 baseline commit 在前、designation commit 在后；
   正式臂 baseline 必须包含 §6.1 修正。
3. **Hash B 定义与 operator 绑定**：仓库无字节级定义（rc1-preflight
   E11/E12）；需 operator 指明定义/来源并独立固定 raw SHA-256。定义方案
   已备（staging/hash-b-definition-proposal.md：推荐 HB-1 = receipt 字节
   SHA-256，实测 00781c74…；含备选与绑定程序；installer 修复若先行提交
   则须重生成 receipt 并重绑定）。
4. **Codex 上游身份可信 capture**：中转环境下需可信生产者的实际运行/传输
   证据；客户端配置与错误文本不达标。Claude 端点 403 需用户侧修复或授权
   其他端点（Candidate 臂需要时）。
5. **独立 Reviewer/operator readiness**：真实独立 operator/session 外部
   receipt + operator 批准的仓库外 evidence index 及 pin；随后盲化计划。
   输入清单已备（staging/reviewer-input-checklist.md：精确 receipt schema、
   外部 pin 规则、runbook 顺序、preflight 五键）。
6. **C1 读隔离 exec 级复核**：原生控制已 observed（MXC + root-deny profile，
   sandboxed-command 层；staging/c1-read-isolation-verification.md）。剩余：
   operator 提供含中转配置的专用 arm-home（无 sandbox_mode 键、无插件/MCP/
   notify），以 `codex exec` 模型会话复核读隔离与非命令通道，并重跑探针
   矩阵；不能以 cwd 或模型承诺替代。elevated setup 未运行（机器级变更，
   未授权且本机不需要）。
7. **Qoder 临时 Workspace 人工登记**（仅 Qoder 加载 smoke 需要，不阻塞
   Codex 正式臂）。
8. ~~quick_validate.py 执行授权~~ **已解决**：改用 Codex 宿主自带脚本实跑
   通过（§6）；不再需要外部下载副本的执行授权。

等待期间已完成所有不依赖上述输入的工作；时间经过不构成授权。

## 6. 维护验证结果

环境：仓库外 maint-env（CPython 3.13.13，requirements-dev.txt），Windows
native Git Bash / PowerShell；未改全局解释器。

| 检查 | 命令 | 结果 |
|---|---|---|
| Mermaid 提取（首次，无效） | `python scripts/validate.py --extract-mermaid .tmp/mermaid` | 该次运行因 execution-surface 尾换行 ERROR 未覆盖目标目录；目录内实为 2026-07-30 旧图（observed，文件时间戳）。首轮渲染覆盖旧源，不构成当前树证据，如实披露作废 |
| Mermaid 渲染（首轮，作废） | 逐图 `npx --yes --package @mermaid-js/mermaid-cli@11.16.0 mmdc -i … -o …` | 35/35 退出 0、SVG 非空（observed），但源为旧集；日志 E/mermaid-render-log.txt 仅证明工具链可用 |
| Mermaid 提取（最终树） | `python scripts/validate.py --extract-mermaid .tmp/mermaid-final` | Static validation passed，exit 0；35 个当前 .mmd（observed），其中 7 个内容与旧集不同（md5 比对） |
| Mermaid 渲染（当前集，pinned 11.16.0） | 逐图同上，输出 .tmp/mermaid-final/*.svg | 35/35 退出 0，35 个非空 SVG 均含 `<svg`（observed）；`mmdc --version` = 11.16.0；日志 E/mermaid-render-final-log.txt |
| 全回归（第 1 次，作废） | maint-env `python -m unittest discover -s tests -p 'test_*.py' -v` | Ran 1235 tests in 2605.649s，FAILED (failures=67)（observed）。运行期间工作树被本次新增文档修改，且三个新文件当时缺尾换行；仅存的两个失败 traceback 均为该尾换行 ERROR 经 validate 类测试放大。完整失败明细未保存（原命令仅留尾部），`unittest_exit=0` 为管道退出码而非 unittest 退出码（测量缺陷，如实披露）。该次运行不作为 Gate 2 证据 |
| 全回归（第 2 次，干净树） | 同上，完整输出与真实退出码另存 staging | Ran 1235 tests in 2634.005s，FAILED (failures=5)，unittest_exit=1（observed，staging/regression-run2.log）；5 个失败全部定位并处置，见 §6.1 |
| 定向套件（修复后） | discover 分别运行 test_distribution / test_repair_v2 / test_installation_doc_consistency / test_shared_state_validation / test_architecture_repair / test_installer_portability | 20+19+5+10+17+17 全部 OK，退出 0（observed，staging/targeted-suites.log；portability 单独运行 17/17 OK） |
| 全回归（第 3 次，修复后） | maint-env `python -m unittest discover -s tests -p 'test_*.py' -v` | **Ran 1235 tests in 2558.946s，OK，unittest_exit=0**（observed，13:23:03–14:07:03，staging/regression-run3.log）。边界：HEAD 32cf06a + 未提交工作树（§1 所列修改）；非已提交候选边界，Gate 2 勾选仍待提交后复验 |
| 全回归（第 4 次，审查前工作树） | 同上 | Ran 1235 tests in 2489.426s，OK，unittest_exit=0（observed，staging/regression-run4.log）。边界：HEAD 32cf06a + 当时工作树（含报告回填、审查返工前）；返工后最终树复验为 run 5，结果记录于 staging/pre-commit-verification-record.md，不回填入已提交树以免污染验证边界 |
| 独立审查（提交前，首轮） | 独立 code-review agent 会话，四轴，只读 | needs-rework：work report 4 处过期陈述（M01–M17 旧数字 ×2、"run 3 待完成"、"提交授权仍未获得"）+ 3 处非阻塞项；installer 修复与其余三份文档通过。返工与复核见 §6.2 |
| validate.py（run 3 链内） | `python scripts/validate.py --root .` | Static validation passed，validate_exit=0（observed）；报告回填后的最终树另复核 |
| validate-design（run 3 链内） | `python scripts/behavior_validation.py validate-design --root .` | Behavior validation design is valid，design_exit=0（observed） |
| historical audit（run 3 链内） | `python scripts/historical_evaluation_audit.py --root . --output .tmp/rc-history-audit.json` | audit_exit=0（observed）；5 个历史包保持 unverified/ineligible，无新包 |
| git diff --check（run 3 链内） | `git diff --check` | diffcheck_exit=0（observed，无输出） |
| validate.py（工作树预检与最终树） | `python scripts/validate.py --root .` | 修复尾换行后预检通过；报告回填后的最终树提取运行再次 Static validation passed，退出 0（observed，staging/validate-precheck.log 与 14:09 提取运行）；已提交候选边界复跑待提交授权 |
| validate-design | `python scripts/behavior_validation.py validate-design --root .` | Behavior validation design is valid，退出 0（observed，第 1 次链内） |
| historical audit | `python scripts/historical_evaluation_audit.py --root . --output .tmp/rc-history-audit.json` | 退出 0（observed，第 1 次链内）；5 个历史包保持 unverified/ineligible，无新包 |
| git diff --check | `git diff --check` | 退出 0（observed）；仅 HANDOFF LF→CRLF warning（checkout 归一化提示，非空白错误） |
| 原生安装检查 | install.ps1 / status.ps1 / c2_isolation_validation.py（clean-source → 两个全新 fixture 目标） | 全部退出 0；CURRENT；C2_CLEAN 0 findings（observed，详见安装报告） |
| quick Skill validation | Codex 宿主自带 skill-creator `quick_validate.py`（`~/.codex/skills/.system/skill-creator/scripts/`，SHA-256 6068513d…）对仓库根 | **Skill is valid!，exit 0**（observed，本会话实跑；E/quick-validate-host-bundled.txt）。用户报告 Codex 已用同一宿主自带脚本实跑通过（attributed）；早前 GitHub main 下载副本（67cf5703…，版本不同）曾被权限策略拦截、未执行 |
| C1 探针：MXC 可用性 | `codex -c windows.sandbox=mxc sandbox … cmd.exe /d /c echo MXC_OK`（staging，不计分） | MXC_OK，exit 0（observed，E/c1-p1c-noargconv.txt；build 26300.9974，无需管理员 setup） |
| C1 探针：读隔离矩阵 | staging CODEX_HOME + c1arm profile（:root deny / :minimal read / .git write / network off），`codex sandbox` 逐目标探针 | 主仓库 README/evaluations、Qoder memory、~/.codex 配置、staging receipt、USER scope Skill、保护文件全部 DENIED；fixture 读写允许；fixture 外写拒绝且无文件产生（observed，E/c1-probe-battery*.json/.txt） |
| C1 探针：fixture Git 能力 | 同上 profile，fixture 内 git status/add/commit/log（GIT_CONFIG_GLOBAL 在 fixture 内） | 全部 exit 0，seed commit 164dba2（observed）；~/.config/git/ignore 被拒仅产生无害 warning |
| C1 探针：unelevated 后端 | 现行配置后端 + root-deny profile | fail-closed 拒绝："Restricted read-only access requires the elevated Windows sandbox backend"，exit 1（observed）；elevated setup 未运行 |
| Hash B 候选测量 | maint-env hashlib 对 receipt/manifest/SKILL.md 交叉核对 | HB-1 receipt SHA-256 00781c74…（14543 字节）；MANIFEST 与 managed-files.txt 一致；安装 SKILL.md 与 receipt 行一致；工作树 SKILL.md 差异仅为 CRLF checkout 归一（HEAD blob 一致）（observed） |

### 6.1 回归失败诊断与最小修正（run 2 → run 3）

run 2 的 5 个失败分为两类，均已处置；未为绿灯修改任何测试或验收标准。

**A. shipped 模板中性合同冲突（4 个失败，非产品缺陷）**

- observed：`test_architecture_repair` 两项与 `test_shared_state_validation`
  一项直接读取仓库 `.looppilot/HANDOFF.md`，要求其为中性 shipped 模板
  （Status: none、无会话内容）；`test_invalid_handoff_status_is_rejected`
  依赖模板中的 `Status: none` 可替换。本会话曾按 handoff 协议把 active
  会话 handoff 写入该文件，触发 4 个失败。
- 合同判定：模板中性是文档化的有意行为合同（docs/validation.md
  “Architecture Repair Regression Properties”；README Scenario 305 指引），
  保护 shipped payload 的会话无关性。AGENTS.md 的 handoff 更新为 SHOULD，
  且 harness 要求“按协议”更新；两者冲突时遵循权威合同。
- 处置：会话 handoff 全文移至 staging/HANDOFF-session-20261116.md，仓库
  模板恢复 HEAD 原字节（git restore，仅撤销本会话自身修改）。未改测试、
  未改 validator。残余不确定性：无（定向套件复测通过）。

**B. 安装器 cp936 中文路径兼容缺陷（1 个失败，产品兼容修正）**

- observed：`test_git_source_and_destination_paths_with_spaces_and_chinese`
  的 powershell 子测试在本机稳定失败（bash 子测试通过），报
  “Git source identity unavailable; release install refused”。
- 根因证据（探针，staging 外临时目录）：PS 5.1 `-File` 调用中
  `$PSScriptRoot` 中文路径正确，但 `git -C $PSScriptRoot` 收到乱码路径；
  脚本内设 `[Console]::OutputEncoding = UTF8` 后同一调用返回正确路径、
  退出 0。本机控制台代码页 936（gb2312）；CI windows-latest 为 UTF-8
  locale，故同一测试在 CI 通过（inferred：CI 环境差异解释既往绿色）。
- 判定：产品自身 portability 合同（中文路径必须可用）在非 UTF-8 控制台
  的真实兼容缺陷，不是单纯环境事件；属 feature freeze 允许的
  compatibility 修正，直接服务 Gate 2。
- 修正：`distribution/loop-pilot.ps1` 在 `$ErrorActionPreference` 后新增
  5 行——仅 PS<6 时设 UTF-8 输出编码（PS7 原生 Unicode 传参，不受影响）。
  同时修正 git UTF-8 输出在 cp936 下的解码。无 schema/验收标准变化。
  已知限制（独立审查披露，非本次修复范围）：编码设置未保存/恢复（交互
  控制台代码页会遗留 65001）；无控制台句柄宿主（DETACHED_PROCESS 类）设
  OutputEncoding 理论上可抛异常，定向套件未覆盖该场景。
- 验证：portability 17/17 OK（证据指针：regression-run3.log，含中文路径
  子测试）；distribution 20、repair_v2 19、installation_doc_consistency 5、
  shared_state 10、architecture 17 全 OK（observed，targeted-suites.log，
  5 套件合计 71 测试）。全回归 run 3 已完成 1235 OK（§6）；run 4（含报告
  回填的提交前工作树）1235 tests OK、unittest_exit=0（observed，
  staging/regression-run4.log）；返工后最终树复验为 run 5（见 §6.2）。
- 边界影响：产品工作树偏离 32cf06a；既有 fixture 安装证据仍绑定 32cf06a
  源（当时字节），正式臂必须使用包含本修正的新 baseline 提交并重新验证。
  主仓库提交授权已条件授予（2026-11-16，见头部与 §5.2）：仅本次两个本地
  提交，以独立审查与完整验证通过为前提；未获授权的 P1 修改不得提交。

### 6.2 独立审查返工与提交前最终验证

- 首轮四轴审查（独立 agent 会话，只读）：Spec / Standards / Implementation
  Quality pass；Verification & Evidence fail，阻塞项全部为本报告过期陈述：
  ①§1 与 §8 残留 revision 1 的 M01–M17/17/17 旧数字；②§6.1 "全回归 run 3
  待完成"与 §6 run 3 OK 矛盾；③§6.1 "主仓库提交授权仍未获得"与头部/§5.2
  已条件授予矛盾。非阻塞：新增行数 4→5、portability 17/17 证据指针应指
  regression-run3.log、installer 编码已知限制披露。
- 返工：上述 7 项已一次性修正（本节即返工记录）；installer 代码未再改动
  （审查已 pass）；未改任何测试或验收标准。
- 复核与最终验证：返工后由原独立审查员复核（四轴重判），并在最终工作树
  跑 validate.py + 全回归 run 5。两者结果记录于
  staging/pre-commit-verification-record.md（证据源），不回填入已提交树，
  避免"回填→树变更→再验证"循环；提交后已提交边界复验按 §5.2 执行。
- 提交顺序：run 5 与复核均通过后立即执行两个本地提交（A：installer；
  B：docs），提交间与提交后不再改动工作树字节。

## 7. 验证缺口披露（requirement status / 理由 / 证据 / 残余不确定性）

| 缺口 | 要求状态 | 客观理由与证据 | 残余不确定性 |
|---|---|---|---|
| quick_validate.py 曾未执行（已解决） | required（validation.md 静态检查） | 改用 Codex 宿主自带脚本实跑通过（§6，observed）；下载副本拦截记录保留为历史 | 无残余；宿主自带版本与 GitHub main 版本 digest 不同，已分别记录 |
| Claude 加载/smoke | harness §4 测试项 | 中转 403 ×2，原始 jsonl/stderr 保留（EII） | Claude 实际加载行为未知 |
| Qoder 加载 smoke | harness §4 测试项 | workspace.creation 需人工 UI（observed 操作目录） | Qoder 注入字节未核对 |
| Codex rollout 复制 | 证据归档偏好 | 权限策略拦截会话转录复制；原位路径+SHA-256 已记录 | stdout JSONL 已在证据目录，rollout 原位可复核 |
| C1 exec 级集成 | required（Gate 4 前置） | 原生读控制仅在 `codex sandbox` 命令层 observed；`codex exec` 模型会话与非命令通道未实测（需 operator arm-home 与中转配置） | exec 级读隔离与通道封闭 unverified；正式臂前必须以最终 arm-home 复核 |
| 全回归/最终边界静态检查 | required（Gate 1/2） | run 3 全绿（1235 OK，链式检查全 exit 0，§6）；但边界为未提交工作树，已提交候选边界的复验待提交授权 | 提交前 Gate 1/2 保持 unverified（工作草稿 PASS 不勾选） |
| 正式臂全部前置 | required（Gate 4） | §5 清单 | 无合格 record 前 Gate 4 unmet |

无用户批准豁免；以上均不记为豁免。

## 8. 交付与状态

- 交付：本报告、[安装报告](qoder-agent-installation-report.md)、
  [执行面记录](codex-rc-execution-surface.md)、staging 证据与提案
  （P1 提案 revision 2 + M01–M20 模拟、C1 读隔离核查记录、sandbox 控制 Research
  Brief、Hash B 定义方案、独立 Reviewer 输入清单）、精简会话 handoff
  （staging/HANDOFF-session-20261116.md，含 Resume Point；仓库 shipped
  模板按行为合同保持中性）。
- checklist/candidate decision：gate 勾选状态不变（工作草稿 PASS 与安装
  测试均不构成勾选依据）；本次准备证据由本报告承载。
- 未创建任何 run package、Host Acceptance Record、虚构 Finding Ledger 或
  Project Closure 实例；`evaluations/` 未放入 placeholder。
- 最终状态与 Resume Point 见 staging 会话 handoff 及会话末尾报告。
