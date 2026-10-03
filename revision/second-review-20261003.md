# 2026-10-03 · 第二轮全书中文与技术复审

这一轮通读十九章、补充能力和语法附录，对二十一份文件完成一百二十七项段落与标题修改。原稿及旧分享包备份于本地 `archive/before-second-review-20261003-090100`。

## 中文表达

将“取得、交出、着陆、实现接纳对象”等生硬措辞改为具体动作，拆开嵌在括号和破折号中的定义。原来只提醒“不能推断”“不等于完成”的句子，改为说明数据由谁处理、下一步何时发生。保留分支条件，并直接写出条件成立后的处理结果。

同步调整流程回顾、源码执行推演和讲解问答。专有名词保留原名，首次定义用中文解释；原码、逐行说明和原项目文档保持原样。

## 技术修正与补充

| 章节 | 修正后的讲解 | 固定源码 |
| --- | --- | --- |
| 2、附录 | Promise.all 全部成功时按传入顺序返回，任一项失败则拒绝；其他已启动操作继续自身流程。 | 基础异步概念，与第十九章逐项捕获错误的 disposer 流程区分。 |
| 3 | next-step 边界领取全部引导输入；next-turn 边界再追加一项普通任务。 | core/agent-loop/src/inbox.ts 的 claim。 |
| 4 | read 保存有限窗口，同时扫描输入统计总行数。 | fs/tool-fs/src/read-render.ts 第 78—142 行。 |
| 6 | 成功工具结果提供触及路径，步骤结束后排队更新项目指令，下一步前置链等待更新完成。 | context/agent-instructions/src/index.ts 第 296—359 行。 |
| 8 | 压缩依次追加开始、摘要、替换消息和结束标记，提交失败时已有事件留在 Session 中。 | compaction/compaction-basic/src/region.ts 第 173—278、471—521 行。 |
| 9 | 消费流时直接抛错，结算尝试后继续抛出；finish 携带失败时才进入对应请求恢复链。 | core/agent-loop/src/agent.ts 第 433—514 行。 |
| 11 | 前置策略和审批形成允许决定后，才检查独立的 guard。 | core/tools/src/index.ts 第 1493—1538 行。 |
| 12 | 同步准备失败保留旧注册；交换阶段发生冲突则清空本轮注册，该服务器留下零项工具。 | mcp/mcp-client/src/tools.ts 第 91—162 行。 |
| 13 | spawn 和 fork 复用创建函数，为各自子任务建立独立 Agent 和 Session。 | subagent-in-process-driver 的 startInProcessRun 与 drivePublishedRun。 |
| 14 | Host 发现事件缺口后结束 follow；客户端 resync 在历史来源地址替换时重建窗口，投影控制流独立重连。 | api/session-controller 的 history.ts 与 client/sessions/session.ts。 |
| 17 | 三组记录标题与配图一致；“总用量÷通过数”解释为含失败消耗的分摊用量。 | 教学案例的算式与图 F17A。 |

本轮新核验的源文件、行范围和 SHA-256 见 [技术记录](second-technical-review-20261003.json)。逐项改写的前后文本见 [编辑记录](second-review-edits-20261003.json)。

## 交付检查

原码节选与原始参考文件按固定提交检查，术语解释段落和索引同步更新。离线阅读版与分享包由当前正文重建，浏览器检查绑定本轮阅读版文件；打包后检查 CRC 并逐文件比较内容。计数及结果见 [validation.json](../validation.json)。

本轮采用本地编辑和静态源码核验，未新增外部模型调用。
