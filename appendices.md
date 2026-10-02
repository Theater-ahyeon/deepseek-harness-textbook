# 附录：基础与术语随用随查

## A｜最小 TypeScript 速查

类型描述数据形状，语句描述运行行为。下面都是教学示意，帮助阅读，不是可直接安装到 DSH 的插件。

```ts
type Result = { accepted: boolean }
const item = { name: '读取工具', count: 1 }
const count = item.count
async function submit(): Promise<Result> {
  return { accepted: true }
}
```

`type` 声明类型别名；对象用花括号组织属性；点号访问属性；`async` 返回异步结果；`Promise<Result>` 说明兑现后的值符合 Result。不能根据名称把 accepted 当作整个任务完成。

```ts
type Options = { offset?: number }
const offset = options.offset ?? 1
const all = [...existing, added]
```

问号表示可缺省，`??` 只在左值为 null 或 undefined 时取右值，展开运算符生成包含既有元素的新数组。它们不自动深拷贝所有嵌套对象；需要看项目明确的复制和冻结步骤。

```ts
try {
  await action()
} catch (error) {
  report(error)
} finally {
  release()
}
```

try/catch 区分普通与异常路径，finally 用于两种情况下都执行的收尾。finally 中也可能失败；真正的实现需要确定收尾失败与原结果的关系，不能只因写了 finally 就声称所有资源绝对已释放。

`for await` 消费异步序列；`signal` 传递取消；`import type` 引入类型信息；`export` 允许其他模块引用。出现泛型时，先看它约束哪个输入和输出，再决定是否要读全部类型推导。

## B｜核心术语对照

| 中文 | 源码标识或英文 | 在本项目的用途 |
| --- | --- | --- |
| 智能体运行框架 | Harness | 组织请求、能力与过程 |
| 会话 | Session | 保存事实并派生用途视图 |
| 轮次 | turn | 驱动的一段推进边界，可无步骤 |
| 步骤 | step | 组织模型请求与成功后的工具阶段 |
| 尝试 | attempt | 一次模型请求尝试，失败可在同一步恢复 |
| 收件箱 | inbox | 待领取输入与进入目标 |
| 提示词组装 | assemble | 按贡献与作用域形成材料 |
| 提供方 | provider | 兑现某项能力契约的具体实现 |
| 运行配置 | profile | 组合声明、配置层与实际插件树 |
| 组合包 | bundle | 分发配置条目及相应挂载材料 |
| 投影 | projection | 从事实整理特定用途的状态 |
| 当前表层 | surface | 当前消息表示所采用的节点与规则 |
| 临时流片段 | chunk | 请求进行中的片段，不自动等于提交消息 |
| 快照 | snapshot | 一个游标处的可观察状态 |
| 刷新屏障 | flush | 等待提供方兑现相应刷新契约 |
| 回放 | replay | 用已知响应重走真实工程过程 |
| 词元 | token | 模型处理与计量单位，不等于字符或行 |

## C｜一条任务的职责地图

入口控制器检查并接纳请求；收件箱保存输入；驱动领取并组织步骤；提示、指令与历史形成请求材料；模型生成文字或工具提议；工具服务检查准入并分派；具体提供方完成动作；会话记录事实；模型继续使用结果；客户端观察并显示；产物检查判断业务质量。

这段地图表示职责关系，不保证每次任务都会用技能、压缩、MCP 或子代理。是否存在、是否启用、是否实际调用，需要不同证据。正常轮次结束也不自动证明产物准确。

## D｜证据的读法

代码说明已实现的分支；文档说明职责与使用约定；测试源码说明作者怎样检查行为；真实执行记录说明一次配置下实际发生什么。它们互补，不能互相冒充。本书基于固定提交的静态检查，没有运行项目测试或真实模型任务。

可选证据附录中的代码片段带实际文件、行号和固定提交链接。正文无需阅读这些片段即可理解。片段为解释一个结论而省略邻近代码，不保证能单独运行。全部原文和源码保留在 source，修改或深入时回到完整定义，尤其检查注册、绑定、消费、取消和收尾。

## E｜继续阅读原项目

项目架构先看 [架构说明](source/docs/architecture.zh.md)，插件概念看 [Cordis 入门](source/docs/cordis-primer.zh.md)，过程关系看 [轮次与步骤生命周期](source/docs/agent-lifecycle.zh.md)，工具边界看 [工具流水线](source/docs/tool-execution-pipeline.zh.md)，验证方式看 [测试指南](source/docs/testing.zh.md)。逐章材料见 [参考索引](reference-index.md)。

正文已经解释核心运行链以及官方目录中 63 项子系统的功能、协作与主要边界，包括可选执行、语音、定时、团队与 SDK 载体。深入修改项目时，精确 API/配置字段、每个平台沙箱内部、所有后端实现与发布矩阵仍需查相应版本手册；这些细节不作为本教材阅读前提。
