# 实现证据索引

固定提交：`639ed015397290b3745d163aafe02ffee4aa3f84`。访问与静态核验日期：2026-10-03。根包：0.2.0-rc.2；Cordis：4.0.4。

正文使用短编号。这里记录路径、原文件行号和节选摘要。代码保持原文；中文解释在代码外，不伪装成上游作者的注释。没有运行项目或上游测试。

<a id="e01a"></a>

## E01A · 接纳时的身份与来源

位置：[source/packages/api/session-controller/src/commands.ts](source/packages/api/session-controller/src/commands.ts)，原文件 329—335 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/commands.ts#L329)。

正文：[第 1 章](book/01.md#e01a)。SHA-256：`df9508f64cab980b1b83d1925420aef67f1d5e618a68ea4f3d1d4de5d93ec29c`。

证据等级：真实实现节选。

<a id="e01b"></a>

## E01B · 工具调用的关联记录

位置：[source/packages/core/agent-loop/src/tool-calls.ts](source/packages/core/agent-loop/src/tool-calls.ts)，原文件 263—266 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/tool-calls.ts#L263)。

正文：[第 1 章](book/01.md#e01b)。SHA-256：`e42f6877041eecfac66444e8b0a3ffa89971ab06c4678e99ef734059752d0a4a`。

证据等级：真实实现节选。

<a id="e02a"></a>

## E02A · async 返回的结果由方法契约决定

位置：[source/packages/api/session-controller/src/commands.ts](source/packages/api/session-controller/src/commands.ts)，原文件 311—318 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/commands.ts#L311)。

正文：[第 2 章](book/02.md#e02a)。SHA-256：`4a725a0a69d39dc0b0f23e6d7b0e693a3b4e92aef3ff17527808685be3954413`。

证据等级：真实实现节选。

<a id="e03a"></a>

## E03A · 领取时组合两类待处理输入

位置：[source/packages/core/agent-loop/src/inbox.ts](source/packages/core/agent-loop/src/inbox.ts)，原文件 109—114 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/inbox.ts#L109)。

正文：[第 3 章](book/03.md#e03a)。SHA-256：`66a316e130d9fab1ede5bc38d0937b8c0621ffba5fffc4cb58d7d841db3cbdaf`。

证据等级：真实实现节选。

<a id="e04a"></a>

## E04A · 参数默认值与错误分支

位置：[source/packages/fs/tool-fs/src/read.ts](source/packages/fs/tool-fs/src/read.ts)，原文件 55—61 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L55)。

正文：[第 4 章](book/04.md#e04a)。SHA-256：`0571fb8c96d3b6a97c6e3a7d5b3354de08ecdb8b5e9357d2bab902b9c068619a`。

证据等级：真实实现节选。

<a id="e04b"></a>

## E04B · 大小信息决定文本取得方式

位置：[source/packages/fs/tool-fs/src/read.ts](source/packages/fs/tool-fs/src/read.ts)，原文件 141—152 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L141)。

正文：[第 4 章](book/04.md#e04b)。SHA-256：`ab938e5af52b8deef090aadda32610976f7dfefcdf1b7f39ab0d1b7db7eb6d7c`。

证据等级：真实实现节选。

<a id="e05a"></a>

## E05A · 事件对象建立与验证

位置：[source/packages/core/session/src/index.ts](source/packages/core/session/src/index.ts)，原文件 744—752 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/session/src/index.ts#L744)。

正文：[第 5 章](book/05.md#e05a)。SHA-256：`90afb132a58060eec1b67c9d255abb66e59fd9f922c1036b90d7e05fee9342b7`。

证据等级：真实实现节选。

<a id="e05b"></a>

## E05B · 后台写入与持久化等待

位置：[source/packages/session/session-persistence-jsonl/src/storage.ts](source/packages/session/session-persistence-jsonl/src/storage.ts)，原文件 535—547 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-persistence-jsonl/src/storage.ts#L535)。

正文：[第 5 章](book/05.md#e05b)。SHA-256：`f5c9f19720259576ec7236da0673f9928813c34560e15146ac4e1f36f4d8459c`。

证据等级：真实实现节选。

<a id="e06a"></a>

## E06A · 项目指令进入本步消息

位置：[source/packages/context/agent-instructions/src/index.ts](source/packages/context/agent-instructions/src/index.ts)，原文件 332—340 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/context/agent-instructions/src/index.ts#L332)。

正文：[第 6 章](book/06.md#e06a)。SHA-256：`dd9106ae23be4e4c05068b73c1c2634dcc2f0a14cb280bf73fc55ab027f0f3ca`。

证据等级：真实实现节选。

<a id="e07a"></a>

## E07A · 读取正文前的可见性和入口检查

位置：[source/packages/skill/tool-skill/src/index.ts](source/packages/skill/tool-skill/src/index.ts)，原文件 133—144 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/tool-skill/src/index.ts#L133)。

正文：[第 7 章](book/07.md#e07a)。SHA-256：`d05d09dbab2d88dab8c9f0f011a7a737c936d026959e78baccb250e19b0cb848`。

证据等级：真实实现节选。

<a id="e08a"></a>

## E08A · 提交前稳定性检查与结束记录

位置：[source/packages/compaction/compaction-basic/src/region.ts](source/packages/compaction/compaction-basic/src/region.ts)，原文件 232—238 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-basic/src/region.ts#L232)。

正文：[第 8 章](book/08.md#e08a)。SHA-256：`b756e27f37f6ff8ae7550878ca0d148e629a06dec762f920ec1324e3302d0115`。

证据等级：真实实现节选。

<a id="e09a"></a>

## E09A · 配置复制与冻结

位置：[source/packages/llm/llm/src/index.ts](source/packages/llm/llm/src/index.ts)，原文件 937—944 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/llm/src/index.ts#L937)。

正文：[第 9 章](book/09.md#e09a)。SHA-256：`6b60157d8a23d05df618d232b37407e5020efd99f46f5468df319e15cb6b6b7d`。

证据等级：真实实现节选。

<a id="e09b"></a>

## E09B · 失败以后是否再尝试

位置：[source/packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，原文件 505—509 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L505)。

正文：[第 9 章](book/09.md#e09b)。SHA-256：`0bae018eab905c1e60649080b17bf0f781c00c780342085b9b703e39849efb1b`。

证据等级：真实实现节选。

<a id="e10a"></a>

## E10A · 配置层与条目补丁的合成

位置：[source/packages/boot/app-boot/src/profile.ts](source/packages/boot/app-boot/src/profile.ts)，原文件 731—738 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/boot/app-boot/src/profile.ts#L731)。

正文：[第 10 章](book/10.md#e10a)。SHA-256：`7d873d19bd8dcfb63585828c757e15379971d03312007e9de06d7f57b7e1b413`。

证据等级：真实实现节选。

<a id="e11a"></a>

## E11A · 准入链与可选询问

位置：[source/packages/core/tools/src/index.ts](source/packages/core/tools/src/index.ts)，原文件 1504—1511 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/tools/src/index.ts#L1504)。

正文：[第 11 章](book/11.md#e11a)。SHA-256：`afd6b6fb67cf8a962d92cf8dabfd063c37c85c858da312d6f087aa075545f5e7`。

证据等级：真实实现节选。

<a id="e11b"></a>

## E11B · 一次审批怎样留下关联记录

位置：[source/packages/interaction/user-approval/src/index.ts](source/packages/interaction/user-approval/src/index.ts)，原文件 224—233 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/interaction/user-approval/src/index.ts#L224)。

正文：[第 11 章](book/11.md#e11b)。SHA-256：`cbf872d82d316b92e21660db7edb1de17da8844194d26bd9194c1936f691f72e`。

证据等级：真实实现节选。

<a id="e12a"></a>

## E12A · stdio 与 HTTP 的不同执行边界

位置：[source/packages/mcp/mcp-client/src/transport.ts](source/packages/mcp/mcp-client/src/transport.ts)，原文件 31—46 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-client/src/transport.ts#L31)。

正文：[第 12 章](book/12.md#e12a)。SHA-256：`f2a51ac6bf584f0d4de856f7afb8674067f4f7adfe9cd5f4feeaaddce2093f7d`。

证据等级：真实实现节选。

<a id="e13a"></a>

## E13A · 进程内 fork 取到哪里

位置：[source/packages/subagent/subagent-fork-in-process/src/index.ts](source/packages/subagent/subagent-fork-in-process/src/index.ts)，原文件 48—55 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent-fork-in-process/src/index.ts#L48)。

正文：[第 13 章](book/13.md#e13a)。SHA-256：`8d3dae537c9af1b72e3974b601386a16ce261f88ae48a12de075acd651f7ba05`。

证据等级：真实实现节选。

<a id="e14a"></a>

## E14A · 跟随时发现重复与缺口

位置：[source/packages/api/session-controller/src/history.ts](source/packages/api/session-controller/src/history.ts)，原文件 226—232 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/history.ts#L226)。

正文：[第 14 章](book/14.md#e14a)。SHA-256：`9829a357f68b3820e455eddb9e7dd627b45163043f44c164f0a86ba6091ef828`。

证据等级：真实实现节选。

<a id="e15a"></a>

## E15A · 真正启动 Host 子进程的位置

位置：[source/apps/desktop/src/host-process.ts](source/apps/desktop/src/host-process.ts)，原文件 188—201 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/host-process.ts#L188)。

正文：[第 15 章](book/15.md#e15a)。SHA-256：`7a2808013c50da9b9f701f08ed1795c88a46bbd3331c1d7913678f85acbe7d17`。

证据等级：真实实现节选。

<a id="e16a"></a>

## E16A · 消费按位置推进

位置：[source/packages/test-support/llm-replay/src/index.ts](source/packages/test-support/llm-replay/src/index.ts)，原文件 1064—1068 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L1064)。

正文：[第 16 章](book/16.md#e16a)。SHA-256：`a9f577f03bad1c79999a054886fe4b39c706d3ea9ebd21097885aaf7bf14e305`。

证据等级：真实实现节选。

<a id="e16b"></a>

## E16B · 有路由时与无路由时的接入

位置：[source/packages/test-support/llm-replay/src/index.ts](source/packages/test-support/llm-replay/src/index.ts)，原文件 1101—1104 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L1101)。

正文：[第 16 章](book/16.md#e16b)。SHA-256：`968a92e55287eecd02b3760e7c273af68cf1f70d968e6eabb239c6e604579b36`。

证据等级：真实实现节选。

<a id="e17a"></a>

## E17A · 三项计量视图的注册

位置：[source/packages/llm/token-meter/src/index.ts](source/packages/llm/token-meter/src/index.ts)，原文件 114—116 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/token-meter/src/index.ts#L114)。

正文：[第 17 章](book/17.md#e17a)。SHA-256：`4c1dad11d5845b97e86d8e5beb6c7143c3fff5f729dd8ea2c05a77ba93247cbf`。

证据等级：真实实现节选。

<a id="e18a"></a>

## E18A · 卡片资料从规范值派生

位置：[source/packages/fs/tool-fs/src/read.ts](source/packages/fs/tool-fs/src/read.ts)，原文件 124—133 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L124)。

正文：[第 18 章](book/18.md#e18a)。SHA-256：`d8cbbfa4de003d804f56f8ff61c5c6a396e9e42e70b1255e12f2163732716aa1`。

证据等级：真实实现节选。

<a id="e19a"></a>

## E19A · 作者提供资源释放逻辑

位置：[source/docs/cordis-tutorial/02-lifecycle-and-effects.zh.md](source/docs/cordis-tutorial/02-lifecycle-and-effects.zh.md)，原文件 20—26 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/cordis-tutorial/02-lifecycle-and-effects.zh.md#L20)。

正文：[第 19 章](book/19.md#e19a)。SHA-256：`9a3763c8b3db919d4392ae0a18e5e08bd0122d8813103c5cd5def14a70fc4664`。

证据等级：仓库官方教程示例，不是生产运行记录。

<a id="e19b"></a>

## E19B · 服务名称作用域隔离

位置：[source/vendor/cordis/src/context.ts](source/vendor/cordis/src/context.ts)，原文件 121—125 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/vendor/cordis/src/context.ts#L121)。

正文：[第 19 章](book/19.md#e19b)。SHA-256：`ce17bf1a2b6cefc62bd332f4151c2ee2f9449f87a7d99e323a5d6c9c78ae4c40`。

证据等级：真实实现节选。

<a id="e19c"></a>

## E19C · 同层资源释放并发等待

位置：[source/vendor/cordis/src/fiber.ts](source/vendor/cordis/src/fiber.ts)，原文件 675—686 行。

版本链接：[固定提交定位](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/vendor/cordis/src/fiber.ts#L675)。

正文：[第 19 章](book/19.md#e19c)。SHA-256：`8268990ba934eb54a88d56e5883118c0eb251a87eca8381b5a201a7f001090aa`。

证据等级：真实实现节选。


<a id="s01"></a>

## S01 · 团队名册、任务板与消息交接

本条是正文行为核验，未额外添加代码块。对应补充能力中 Agent Teams 的完整过程，依据固定提交的真实实现；不等于所有团队路径已运行测试。

| 文件 | 核验对象 | 定位 |
| --- | --- | --- |
| [types.ts](source/packages/experimental/agent-team/src/types.ts) | TeamMemberSnapshot、TeamTaskSnapshot、TeamMessageSnapshot | 成员阶段、任务修订与范围、稳定消息身份 |
| [mailbox.ts](source/packages/experimental/agent-team/src/mailbox.ts) | sendAdmitted、serializeDispatch、dispatchOnce、checkpointDelivered、recoverFor | 先记 queued，同目标交接顺序，目标持久接收后确认，以及恢复 |
| [任务约定](source/docs/subsystems/agent-team.zh.md) | 官方团队契约 | 范围重叠提示与业务完成的限制 |

<a id="s02"></a>

## S02 · 有界工具池、屏障与顺序提交

对应第三章的双工具推演，依据固定提交的 [tool-calls.ts](source/packages/core/agent-loop/src/tool-calls.ts)：executeToolCalls 第 59—103 行建立模型顺序的计划并逐组处理；runGroup 第 126—246 行管理数量上限、结果槽、提交位置、重新分类和取消收尾。特别核对 commitReady、startCall 与 fillPool，区分前置准备、实际执行与结果后处理的顺序。本节为源码行为分析，没有声称双工具例子已运行。


<a id="s03"></a>

## S03 · 工具输出与 Web 卡片的两条路径

对应第十八章。ToolRuntime 构造模型内容与持久 metadata；Session page/follow 下发原始事件；Web Client 按调用身份配对，再按工具名选择 renderer。readCardModel 校验参数、meta 和模型结果格式，生成 ReadBlock 数据。

| 实现入口 | 处理过程 |
| --- | --- |
| [ToolRuntime](source/packages/core/tools/src/index.ts) 第 1831—1853 行 | 规范值快照、输出校验、render 与顶层 presentationMeta |
| [ToolCallTree](source/packages/client/ui-tool/src/client/tool/ToolCallTree.tsx) 第 49—63 行 | 按工具名称分发 keyed slot，缺少 renderer 时使用 GenericToolCard |
| [read-card-model](source/packages/client/ui-tool/src/client/tool/models/read-card-model.ts) | 检查原始调用、窗口 metadata 和文件结果格式，生成卡片数据或返回 null |
| [ReadRow](source/packages/client/ui-tool/src/client/tool/toolviews/read-row.tsx) | 注册 read renderer 并调用 readCardModel |
| [已实施的展示架构决策](source/.agents/notes/implemented/architecture/2026-08-23-client-derived-tool-presentation.zh.md) | 原始 journal、Host 本地 presenter 与 Web renderer 的职责 |
