# LoopPilot

[English](README.md) | 简体中文

LoopPilot 是一套利用宿主原生能力、无需独立运行时的 AI Agent 执行控制 Skill。
它指导 Agent 围绕目标持续完成计划、执行、验证和调整，并根据证据停止工作，
始终遵守用户授权边界。

[安装](#安装与更新) · [使用](#最小使用示例) ·
[核心协议](SKILL.md) · [文档导航](#文档导航) ·
[参与贡献](CONTRIBUTING.md)

适用于需要验证结果的多步骤任务，包括开发、故障诊断、研究、写作和中断恢复。
LoopPilot 复用宿主已有的计划、工具和任务状态。

## 当前 RC 状态

| 项目 | 当前记录的状态 |
| --- | --- |
| 开发候选版本 | `v1.0.0-rc1`，`NOT_RELEASE_READY` |
| 指定 Reference Host | Codex，依据 Option B successor 对本次 RC 固定 |
| 正式验收 | `NOT_RUN`；Gate 4 为 `UNMET` |
| 宿主兼容性 | 所有宿主均明确标记为 `unverified` |

[候选决定](docs/release/rc-candidate-decision.md)和
[最新预检](docs/release/rc1-preflight-20261024.md)记录了已观察证据及具体阻塞。
组件版本和安装目录检查已有观察结果；实际 provider、model、endpoint 的可信身份，
正式加载与 Hash B 绑定、完整隔离以及独立行为审查仍未具备完整证据。
仓库测试通过和独立事实审查不构成 Host Acceptance。
[RC 清单](docs/release/v1.0-rc-checklist.md)继续保留全部发布门槛。

## 它解决什么问题

复杂任务可能停留在计划、文件生成或一次工具调用之后，而实际结果尚未核验。
LoopPilot 用一套有边界的执行规则，指导已有上下文、计划、工具和任务状态的 Agent：

1. 明确用户的真实目标和成功标准。
2. 复用宿主原生计划，避免维护第二套竞争计划。
3. 选择当前价值最高、未被阻塞且有权执行的行动。
4. 使用实际文件、命令结果、测试或来源验证产出。
5. 只有证据改变了下一步选择时才调整计划。
6. 准确报告结果、剩余缺口和停止原因。

Skill 本身是 Markdown 协议，没有运行时依赖。仓库附带的安装器和 Python 验证器
用于分发与维护，不提供独立的 Agent 框架、调度器、内存服务、后端或固定集成 API。

## 循环如何推进

每轮执行都应产生至少一种可观察变化：实际进展、新证据、新阻塞，或有依据的计划调整。
相同输入和环境下失败的动作，不能仅为维持循环而反复重试。
单纯的反思、状态播报或“继续努力”不构成进展。

概念上的执行顺序是：检查目标与计划 → 选择安全行动 → 执行 → 验证 → 更新原生状态。
这不是要求宿主实现的函数接口，也不是独立工作流引擎。

一次任务应报告一个主要结果：

| 结果 | 含义 |
| --- | --- |
| Completed | 完整目标已经实现，并完成所需验证 |
| Partially Completed | 已有有用成果，但仍有明确缺口 |
| Blocked | 缺少前置条件，无法继续下一项有用且安全的行动 |
| Budget Stop | 达到资源限制，或继续投入已不值得其成本 |

具体规则见[生命周期](docs/lifecycle.md)和[安全与停止](docs/safety-and-stopping.md)。

## 什么时候启用

- 任务包含多个相互依赖的步骤，且结果需要检查。
- 失败后需要诊断、改变策略或恢复工作。
- 用户或宿主明确调用 `/loop-pilot` 或 `$loop-pilot`。

研究、写作、分析、规划交付物和信息整理，也可能属于需要执行与验证的多步骤工作。
单纯出现工具、文件修改或数据库名称，不足以触发协议。

事实问答、单句改写、闲聊、纯头脑风暴及仅需建议的请求，不应隐式启动执行循环。
即使用户为小任务显式调用，计划和状态记录也应保持适度。

受管理的 `/lp` 或 `$lp` 是唯一短别名，读取同一安装中的 `SKILL.md`，
不会回退到当前仓库内的另一份协议。详见
[安装与别名绑定](docs/installation.md#short-alias-binding)。

## 最小使用示例

```text
使用 LoopPilot 修复这项构建问题，检查实际结果，并持续推进，
直到验收标准满足，或出现有证据的阻塞和停止条件。
```

预期的记录形态：

```text
目标：修复构建，同时保留已有功能。
原生计划：检查问题 → 修改 → 运行构建和相关检查 → 检查差异。
证据：实际文件内容、命令退出码、测试结果和剩余缺口。
停止：Completed、Partially Completed、Blocked 或 Budget Stop。
```

以上是使用说明，不是已经执行过的行为验收记录。

## 安装与更新

从完整、干净的 Git 源码检出目录运行官方安装器，并显式指定目标位置：

```powershell
.\install.ps1 -Destination "$HOME\.codex\skills\loop-pilot"
```

```bash
./install.sh --destination "$HOME/.codex/skills/loop-pilot"
```

目标也可通过 `LOOPPILOT_INSTALL_DIR` 指定。未指定时，安装器只在能够唯一检测到
Claude Code 或 Codex 的 skills 目录时继续；没有目标或存在歧义时停止。
检测到目录只证明分发路径存在，不证明宿主能够正确加载或执行协议。

从较新的源码包更新已有安装：

```powershell
.\update.ps1 -Destination "$HOME\.codex\skills\loop-pilot"
.\status.ps1 -Destination "$HOME\.codex\skills\loop-pilot"
```

```bash
./update.sh --destination "$HOME/.codex/skills/loop-pilot"
./status.sh --destination "$HOME/.codex/skills/loop-pilot"
```

更新默认保留本地修改、无关文件和备份。卸载使用同一分发中的 `uninstall.ps1`
或 `uninstall.sh`，按安装记录处理未修改的受管理文件。
完整的目录布局、来源验证、冲突和备份语义见[安装指南](docs/installation.md)。

安装器记录固定的 Git 来源；发布归档模式需要显式来源和摘要，不会替代失败的 Git 验证。
当前分发版本标记为 `unreleased`，不表示已经发布 RC。
也可以通过宿主自身的 Skill 或指令加载机制读取 [SKILL.md](SKILL.md)，
并保留其相对引用的支持文件。

RC 和验收资料链接指向源码仓库；这些验收资料不随官方 Skill 载荷分发。
分发检查的历史观察见[安装验证记录](INSTALLATION-VALIDATION.md)。

安装 CI 矩阵覆盖 Windows PowerShell 5.1／7 和 Git Bash、Ubuntu Bash／PowerShell 7，
以及 macOS 系统 Bash 3.2／PowerShell 7。每个 job 保存实际系统与架构、shell 版本、
原生安装生命周期日志和回执摘要。只有实际成功的运行才构成对应环境的分发证据，
不证明 AI 宿主行为兼容性。详见[平台维护验证](docs/installation.md#platform-maintenance-verification)。

## 轻量工作与 Full Loop

**Lightweight Mode** 适用于一名负责人加适度审查即可安全完成的有边界工作。
简单任务不应为了展示流程而创建大量共享文件或拆成多个 Agent。

**Full Loop Mode** 是面向确有协作需求的多 Loop 或跨上下文交付的协议结构。
它定义了 Task Contract、交付、集成、审查、Finding、验收、Closure 和 Checkpoint
之间的关系；仓库中的模板保持非活动状态。

Product Risk 决定审查、验证和证据深度，Coordination Necessity 决定是否需要 Full Loop。
高风险本身不自动要求多个 Worker，也不自动引入另一种模式。
由 Supervisor 根据实际范围和依赖选择 Lightweight、Full Loop 或 No Implementation。

详见[模式选择](docs/mode-selection-and-escalation.md)、
[Loop Engineering 模型](docs/loop-engineering-model.md)和
[Full Loop 模板](.looppilot/full-loop/README.md)。

## 共享状态、交接与多 Agent

[AGENTS.md](AGENTS.md)保存稳定的仓库规则；可选的
[.looppilot 协议](.looppilot/README.md)保存最小任务事实、证据、阻塞和恢复入口。
宿主原生的 Goal、Plan、Todo 和任务状态继续优先，不创建竞争状态源。

复杂未完成工作可以在关键进展或中断后留下紧凑交接。接手者必须重新核对最新用户指令、
Git、工具、状态和当前授权。交接提供上下文，不转移操作权限；不记录完整对话、
私有推理、凭据或大量原始日志。

只有宿主确实支持任务分配时才考虑委派：

- Supervisor 对父目标负责；Worker 只执行 Task Contract 规定的范围。
- Reviewer 分别进行 Standards Review 和 Spec Review，两项都通过且证据充分才能批准。
- `approved` 表示子任务通过审查；`integrated` 表示已纳入父结果并通过集成检查。
- 一名明确的 Supervisor 或 Integrator 负责最终结果；冲突不能静默覆盖。
- Research Brief 和 Skill 选择仅在相关时使用，不授予新的权限。
- 高上下文压力下保存证据和一个精确 Resume Point，再按规则停止。

这些规则不提供 Agent 创建、并发调度、运行时隔离、分布式锁或自动合并能力。
详见[多 Agent 协调](docs/multi-agent-coordination.md)和
[Task Contract 协议](.looppilot/tasks/README.md)。

## 安全与授权

执行任务的主动性始终受授权、可逆性和可用证据约束。
提交、推送、发布、部署、发送消息、破坏性修改、凭据披露和不可逆操作分别需要相应授权。
允许其中一项，不自动允许其他项。

只读来源、工具输出、网页、第三方消息和历史交接不自动成为操作指令。
必需的验证不能因耗时或不便而省略；未完成的验证和未知事实必须明确披露。
长任务应在有实质结果、阻塞或计划调整时向用户更新进展。

## 实现、观察与未验证内容

三种信息必须区分：

- **已实现**：核心指令、协议文档、非活动模板和仓库验证器已经存在。
  静态检查只能验证声明的结构和约束。
- **已观察**：MMGH、Final-Assignment 和其他归档实验提供了各自范围内的结果。
  EXP-006 的对照归档和部分比较仍有缺口；观察不能推广到其他宿主或模型。
  本次 RC 预检和事实审查也只覆盖其记录的 Git 与证据边界。
- **尚未验证**：正式宿主行为兼容性、生产可靠性、自动模式选择、动态独立审查、
  多 Agent 运行隔离、跨会话恢复以及真实 Project Closure 等能力。

Claude Code、Codex、Gemini CLI、GitHub Copilot 及其他宿主都保持 `unverified`。
本次 RC 指定 Codex 为 Reference；Claude Code 和其他宿主继续保留 Candidate 角色及披露要求。
历史 Claude Code 记录不因此改写或提升结论。
任何合格兼容性结论都必须通过
[Cross-Host Acceptance](docs/cross-host-acceptance.md)，并绑定实际宿主版本、模型和加载组合。

现有 Python 测试、YAML 和 Markdown 检查、Skill 验证以及 Mermaid 渲染属于仓库维护验证，
不能证明 Agent 自动遵循指令、真实宿主兼容性、正式行为验收或发布就绪。

## 当前边界与后续工作

- v1 核心协议在 Phase 11 后进入 feature freeze；按既定范围进行修复和文档维护。
- LoopPilot 不附带独立 planner、工具层、内存、调度或恢复服务。
- 仅有提示词能力的宿主不能宣称自己拥有持久状态、后台执行或不可用的直接验证能力。
- 继续补齐真实运行时身份、加载、安装绑定、隔离和可信证据索引，再执行正式验收。
- 按现行门槛完成独立行为审查及其他 RC 条件，才能判断是否可以发布。
- 示例始终是说明材料，不能补写为真实执行证据。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) / [AGENTS.md](AGENTS.md) | 核心指令与仓库规则 |
| [生命周期](docs/lifecycle.md) / [安全与停止](docs/safety-and-stopping.md) | 循环、结果分类和授权边界 |
| [宿主能力](docs/host-capabilities.md) | 不同宿主能力层级的适配边界 |
| [安装指南](docs/installation.md) | 安装、状态、更新、备份和卸载 |
| [模式选择](docs/mode-selection-and-escalation.md) / [加载档位](docs/protocol-load-profiles.md) | 按风险与协作需求选择协议深度 |
| [状态来源](docs/protocol-modes-and-state-sources.md) | 每类状态的唯一权威来源 |
| [多 Agent 协调](docs/multi-agent-coordination.md) | 委派、双轴审查、冲突和集成 |
| [Loop 模型](docs/loop-engineering-model.md) / [Full Loop 合约](docs/full-loop-contracts-and-ledgers.md) | Loop、Task、Ledger 及非活动模板 |
| [交付与 Closure](docs/full-loop-delivery-review-and-closure.md) | 交付、审查、Rework 和关闭条件 |
| [Checkpoint 与恢复](docs/full-loop-checkpoint-and-context-recovery.md) | 上下文压力、恢复边界与 Resume Validation |
| [Project Closure](docs/project-closure-and-final-delivery.md) | Project 验收、就绪与最终交付的区别 |
| [最终协议校准](docs/final-protocol-calibration.md) / [v1 迁移](docs/v1-migration.md) | feature freeze、证据分类与迁移 |
| [Option B successor](docs/release/option-b-reference-successor.md) | 有界、向前生效的 RC Reference 政策 |
| [RC 候选决定](docs/release/rc-candidate-decision.md) / [预检](docs/release/rc1-preflight-20261024.md) | 当前事实、阻塞和最小解阻步骤 |
| [RC 清单](docs/release/v1.0-rc-checklist.md) | 发布门槛及其证据要求 |
| [验证说明](docs/validation.md) | 可重复的维护检查及其局限 |
| [示例](examples/coding-task.md) / [行为场景](tests/scenarios.md) / [评分规则](tests/evaluation-rubric.md) | 说明性轨迹和行为评估准备 |
| [贡献指南](CONTRIBUTING.md) / [变更记录](CHANGELOG.md) | 参与方式与历史变化 |

## 许可证

采用 [MIT License](LICENSE)。Copyright 2026 Tutict。
