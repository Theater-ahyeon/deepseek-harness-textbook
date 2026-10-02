# 可选证据索引

正文已经独立解释项目，这份索引用于复核或深入修改，不是阅读前提。原文、源码、测试和 MIT 许可均保留在固定仓库副本。测试只作源码旁证，本次未执行。

固定提交：`639ed015397290b3745d163aafe02ffee4aa3f84`；根包 `0.2.0-rc.2`。

## 按新版十章查阅

| 教材 | 文档化子系统参考 |
| --- | --- |
| [第 1 章：Agent 基础：一条任务怎样运转](tutorial.md#chapter-01) | [核心](source/docs/subsystems/core.zh.md)<br>[用户命令](source/docs/subsystems/commands.zh.md) |
| [第 2 章：上下文工程：模型每一步究竟看到什么](tutorial.md#chapter-02) | [系统提示词组装](source/docs/subsystems/system-prompt.zh.md)<br>[Skills](source/docs/subsystems/skills.zh.md)<br>[压缩（compaction）](source/docs/subsystems/compaction.zh.md)<br>[持久附件](source/docs/subsystems/attachment.zh.md)<br>[会话引用](source/docs/subsystems/session-reference.zh.md)<br>[作用域注册](source/docs/subsystems/scope.zh.md)<br>[spill 存储](source/docs/subsystems/spill.zh.md) |
| [第 3 章：记忆与知识：会话记录、材料获取和外部记忆](tutorial.md#chapter-03) | [会话](source/docs/subsystems/session.zh.md)<br>[会话持久化](source/docs/subsystems/persistence.zh.md)<br>[存储](source/docs/subsystems/storage.zh.md)<br>[工作区](source/docs/subsystems/workspace.zh.md)<br>[会话查询](source/docs/subsystems/session-query.zh.md)<br>[会话投影](source/docs/subsystems/session-projection.zh.md)<br>[会话标题](source/docs/subsystems/session-title.zh.md) |
| [第 4 章：工具：从调用契约到受控执行](tutorial.md#chapter-04) | [工具](source/docs/subsystems/tools.zh.md)<br>[文件系统](source/docs/subsystems/filesystem.zh.md)<br>[用户审批](source/docs/subsystems/approval.zh.md)<br>[MCP](source/docs/subsystems/mcp.zh.md)<br>[Web 访问](source/docs/subsystems/web.zh.md)<br>[PTC 运行时](source/docs/subsystems/ptc-runtime.zh.md)<br>[进程沙箱](source/docs/subsystems/sandbox.zh.md)<br>[权限预设](source/docs/subsystems/permission-presets.zh.md) |
| [第 5 章：Coding Agent 与运行框架：插件装配和故障恢复](tutorial.md#chapter-05) | [Profile 管理](source/docs/subsystems/boot.zh.md)<br>[Shell 执行器](source/docs/subsystems/shell.zh.md)<br>[子进程](source/docs/subsystems/subprocess.zh.md)<br>[持久 PTY 会话](source/docs/subsystems/terminal.zh.md)<br>[SSH](source/docs/subsystems/ssh.zh.md)<br>[LSP 导航](source/docs/subsystems/lsp.zh.md)<br>[插件配置表单](source/docs/subsystems/settings.zh.md)<br>[用户凭据](source/docs/subsystems/credentials.zh.md) |
| [第 6 章：交互：网页、桌面与异步观察](tutorial.md#chapter-06) | [Web Client 架构](source/docs/subsystems/web-client.zh.md)<br>[HTTP 服务器](source/docs/subsystems/web-server.zh.md)<br>[Client 模块](source/docs/subsystems/client-modules.zh.md)<br>[客户端资源](source/docs/subsystems/client-resources.zh.md)<br>[Web Client Slots](source/docs/subsystems/slots.zh.md)<br>[右侧 Sidebar](source/docs/subsystems/sidebar-right.zh.md)<br>[Conversation 组装](source/docs/subsystems/conversation.zh.md)<br>[Typert 远程调用](source/docs/subsystems/typert.zh.md)<br>[Office 转 PDF](source/docs/subsystems/office-to-pdf.zh.md)<br>[产出物](source/docs/subsystems/deliverables.zh.md)<br>[语音输入](source/docs/subsystems/voice-input.zh.md)<br>[浏览器操作](source/docs/subsystems/browser-use.zh.md)<br>[计算机操作](source/docs/subsystems/computer-use.zh.md)<br>[用户交互](source/docs/subsystems/user-questions.zh.md) |
| [第 7 章：Agent 评估：回放、质量与工程指标](tutorial.md#chapter-07) | [Token 计量](source/docs/subsystems/token-meter.zh.md)<br>[运行时不变式](source/docs/subsystems/invariants.zh.md)<br>[消息反馈](source/docs/subsystems/feedback.zh.md)<br>[OTel 上报](source/docs/subsystems/otel.zh.md)<br>[产品埋点](source/docs/subsystems/product-telemetry.zh.md)<br>[遥测（telemetry）](source/docs/subsystems/session-telemetry.zh.md) |
| [第 8 章：模型与 Harness：后训练主题在本项目中的边界](tutorial.md#chapter-08) | [LLM（大语言模型）流式输出](source/docs/subsystems/llm-streaming.zh.md) |
| [第 9 章：持续改进：从运行证据到可验证的新版本](tutorial.md#chapter-09) | [同会话目标](source/docs/subsystems/goal.zh.md)<br>[计划模式](source/docs/subsystems/plan.zh.md)<br>[Todo](source/docs/subsystems/todo.zh.md)<br>[宿主级 Schedule](source/docs/subsystems/schedule.zh.md)<br>[Webhook runtime](source/docs/subsystems/webhook.zh.md)<br>[扩展](source/docs/subsystems/extensions.zh.md) |
| [第 10 章：多 Agent 协作：子代理与实验性团队](tutorial.md#chapter-10) | [Subagent](source/docs/subsystems/subagent.zh.md)<br>[Agent Teams](source/docs/subsystems/agent-team.zh.md)<br>[后台任务运行时](source/docs/subsystems/jobs.zh.md)<br>[工作流](source/docs/subsystems/workflow.zh.md) |

## 精选原码与原始专题

[60 段原码节选及完整路径](source-excerpts.md)供核对。18 个专题内部编号保留，仅用于维护，教材以十章顺序阅读。

| 专题 | 教材所在章 | 完整参考 |
| --- | --- |
| [专题 01：从一句话到一个结果：智能体运行框架究竟做什么](tutorial.md#topic-01) | 第 1 章 | [architecture.zh.md](source/docs/architecture.zh.md)<br>[agent-lifecycle.zh.md](source/docs/agent-lifecycle.zh.md) |
| [专题 02：读懂代码：类型与异步等待](tutorial.md#topic-02) | 第 1 章 | [commands.zh.md](source/docs/subsystems/commands.zh.md)<br>[tool.zh.md](source/docs/user/develop/basic/tool.zh.md) |
| [专题 03：循环与消息队列：一轮任务为什么需要多步](tutorial.md#topic-03) | 第 1 章 | [agent-lifecycle.zh.md](source/docs/agent-lifecycle.zh.md)<br>[core.zh.md](source/docs/subsystems/core.zh.md) |
| [专题 04：沿文件读取工具追到底：模型怎样得到材料](tutorial.md#topic-04) | 第 4 章 | [tool-catalog.zh.md](source/docs/tool-catalog.zh.md)<br>[filesystem.zh.md](source/docs/subsystems/filesystem.zh.md) |
| [专题 05：会话与日志：发生过的事怎样保存和还原](tutorial.md#topic-05) | 第 3 章 | [persistence-catalog.zh.md](source/docs/persistence-catalog.zh.md)<br>[session-format-status.zh.md](source/docs/session-format-status.zh.md)<br>[event-producer-consumer.zh.md](source/docs/event-producer-consumer.zh.md) |
| [专题 06：提示词与项目指令：下一次模型输入怎样形成](tutorial.md#topic-06) | 第 2 章 | [architecture.zh.md](source/docs/architecture.zh.md)<br>[agent-lifecycle.zh.md](source/docs/agent-lifecycle.zh.md) |
| [专题 07：技能的按需读取：目录可见为什么不等于正文已加载](tutorial.md#topic-07) | 第 2 章 | [skills.zh.md](source/docs/subsystems/skills.zh.md)<br>[tool-catalog.zh.md](source/docs/tool-catalog.zh.md) |
| [专题 08：上下文压缩：让历史变短需要付出什么](tutorial.md#topic-08) | 第 2 章 | [compaction.zh.md](source/docs/subsystems/compaction.zh.md)<br>[mcp-memory.zh.md](source/docs/user/guide/mcp-memory.zh.md) |
| [专题 09：流式输出与重试：一次失败怎样留在同一步里](tutorial.md#topic-09) | 第 5 章 | [llm-streaming.zh.md](source/docs/subsystems/llm-streaming.zh.md)<br>[agent-lifecycle.zh.md](source/docs/agent-lifecycle.zh.md) |
| [专题 10：插件框架与运行配置：这些部件怎样装成一个应用](tutorial.md#topic-10) | 第 5 章 | [cordis-primer.zh.md](source/docs/cordis-primer.zh.md)<br>[architecture.zh.md](source/docs/architecture.zh.md)<br>[boot.zh.md](source/docs/subsystems/boot.zh.md) |
| [专题 11：工具准入与审批：允许执行的决定在哪里发生](tutorial.md#topic-11) | 第 4 章 | [tool-execution-pipeline.zh.md](source/docs/tool-execution-pipeline.zh.md)<br>[approval.zh.md](source/docs/subsystems/approval.zh.md) |
| [专题 12：外部服务与能力接入：连接成功不等于拥有知识库](tutorial.md#topic-12) | 第 4 章 | [mcp.zh.md](source/docs/subsystems/mcp.zh.md)<br>[mcp-memory.zh.md](source/docs/user/guide/mcp-memory.zh.md) |
| [专题 13：子代理：拆分任务前先看上下文起点](tutorial.md#topic-13) | 第 10 章 | [subagent.zh.md](source/docs/subsystems/subagent.zh.md) |
| [专题 14：网页端：提交任务与跟随结果是两条链](tutorial.md#topic-14) | 第 6 章 | [api-gateway.zh.md](source/docs/api-gateway.zh.md)<br>[conversation.zh.md](source/docs/subsystems/conversation.zh.md)<br>[client-modules.zh.md](source/docs/subsystems/client-modules.zh.md) |
| [专题 15：桌面端：窗口、页面与宿主服务怎样合作](tutorial.md#topic-15) | 第 6 章 | [README.zh.md](source/apps/desktop/README.zh.md)<br>[architecture.zh.md](source/docs/architecture.zh.md) |
| [专题 16：测试与回放：复现通过究竟证明了什么](tutorial.md#topic-16) | 第 7 章 | [testing.zh.md](source/docs/testing.zh.md)<br>[README.md](source/packages/test-support/llm-replay/README.md) |
| [专题 17：量化评价：同时看质量、时间、用量与失败](tutorial.md#topic-17) | 第 7 章 | [testing.zh.md](source/docs/testing.zh.md)<br>[token-meter.zh.md](source/docs/subsystems/token-meter.zh.md)<br>[otel.zh.md](source/docs/subsystems/otel.zh.md)<br>[session-telemetry.zh.md](source/docs/subsystems/session-telemetry.zh.md) |
| [专题 18：综合案例：已有文件工具如何接入与呈现](tutorial.md#topic-18) | 第 4 章 | [adding-a-tool.zh.md](source/docs/cookbook/adding-a-tool.zh.md)<br>[extension-cookbook.zh.md](source/docs/cookbook/extension-cookbook.zh.md) |

## 证据与复用

原始文档说明契约，源码说明实现分支，测试源码说明断言方式；真实运行效果需运行证据支持，不能互相替代。教学图与假设数字是本教材原创解释，不作为项目实测。

分享包保留完整 source 目录及 [MIT 许可](source/LICENSE)，仅省略 Git 元数据。参考书只保留公开链接与结构方法说明，未打包其正文或插图。

[参考文件哈希](reference-manifest.json) · [节选行号与哈希](excerpt-manifest.json) · [覆盖记录](coverage.json) · [教材检查](validation.json)
