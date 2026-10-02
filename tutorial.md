# 深入理解 DeepSeek Harness

## 从微内核底座到工业级工程落地

> 中文项目教材重构完整版 · 含 Cordis 理论奠基专题章 · 2026-10-03 · 深度源码解析 · 附源码级面试问答
> 基于官方固定基准提交 `639ed015397290b3745d163aafe02ffee4aa3f84` (dsh@0.2.0-rc.2)
> 理论依托：DeepSeek-AI & 北京大学论文《A Programming Paradigm for Spatiotemporal Composability》(arXiv:2608.25512)

---

## 全书目录与知识演进树

- [第 1 章｜智能体基座：Harness 架构全貌与微内核装配](#chapter-01)
- [第 2 章｜运行循环：从任务接入到轮次收敛的控制流](#chapter-02)
- [第 3 章｜上下文装配：提示词、技能发现与动态视野](#chapter-03)
- [第 4 章｜历史管理：长程上下文压缩与溢出防护](#chapter-04)
- [第 5 章｜事实真源：事件溯源、持久化与故障恢复](#chapter-05)
- [第 6 章｜工具执行管线：准入、单调守卫与审批流](#chapter-06)
- [第 7 章｜编码能力与运行环境：文件 I/O、Shell 与语义检索](#chapter-07)
- [第 8 章｜多端交互与状态同步协议：RPC 命令提交与增量事件流](#chapter-08)
- [第 9 章｜评估、度量与确定性回放验证：从 Bad Case 到回归资产](#chapter-09)
- [第 10 章｜多智能体协作：会话分支 Fork、团队编排与冲突防御](#chapter-10)
- [理论专题章｜时空可组合性与 Cordis 原理：DeepSeek Harness 微内核的理论奠基](#chapter-11)

---


<a id="chapter-01"></a>

# 第 1 章｜智能体基座：Harness 架构全貌与微内核装配

在终端或网页中输入“读取项目的 `package.json` 并分析其构建脚本”后，屏幕会在数秒内输出结构化解析。直觉上容易以为是大语言模型直接打开了本地磁盘文件；但大语言模型（LLM）受操作系统沙箱与进程边界隔离，无法直接执行磁盘 I/O。真正驱动这一闭环的，是在底层调度全局状态的中枢运行框架——智能体架构（Harness）。

本章直接解构工业级 Harness 的内部拓扑，剖析庞大工程如何依托微内核底座、轻量依赖注入和严格的生命周期契约组合运转。

---

## 1.1 为什么自研 Agent 终将走向 Harness：从脚本循环到工程契约

在探索 DeepSeek Harness（简称 DSH）的具体源码前，必须先厘清一个根本问题：**为什么不能仅用一个简单的 Python 或 Node.js 循环脚本来运行 Agent？**

初学者手写的 Agent 往往是一个直白的代码片段：

```typescript
// 教学示意：朴素脚本循环的脆弱模型
while (taskNotFinished) {
  const response = await llm.chat(history);
  if (response.toolCall) {
    const result = await executeTool(response.toolCall);
    history.push({ role: 'tool', content: result });
  } else {
    break;
  }
}
```

简单的 `while` 循环适合编写演示脚本，但在生产工程中会立刻暴露四项结构性缺陷：

1. **输入与并发冲突**：模型耗时流式输出时，用户若输入“停止，先看另一个文件”，单线程循环要么阻塞无法接收，要么强行打断破坏上下文。系统必须提供区分排队、步骤打断与静默注入的**收件箱契约**。
2. **状态与崩溃恢复**：任务执行至第 8 步时，若宿主进程遭遇 OOM 崩溃或网络断开，内存中的数组瞬间归零。系统必须将运行事实持久化为**不可变追加事件日志（Event Sourcing）**，才能支持重连与故障恢复。
3. **权限与防御穿透**：模型若遭遇恶意 Prompt 注入并提议执行危险删除命令，脚本若直接调用执行会导致不可逆破坏。系统必须在工具调用与物理执行之间构筑**准入门禁（Admission）、单调守卫（Guard）、人工审批（Approval）与沙箱隔离（Sandbox）**防线。
4. **模块高内聚解耦**：编码助手集成了文件系统、持久终端、上下文压缩、语义检索与多端同步等能力。将这些逻辑硬编码在一起会导致代码迅速失控。

因此，**Harness 的本质不是大模型包装器，而是维护模型、工具、历史与环境协作不变量的操作系统微内核**。它确保外部环境抖动或模型产生幻觉时，系统仍能在可控、可追溯且可恢复的工程边界内运转。

---

## 1.2 源码全景透视：500+ 个 package 是如何被组织起来的

DeepSeek Harness 在基准版本（`commit 639ed015397290b3745d163aafe02ffee4aa3f84`，`dsh@0.2.0-rc.2`）下，根目录由 `pnpm` workspace 管理，划分出了极其严密的模块层级：

```
source/
├── apps/               # 终端应用入口：web、desktop、cli
├── native/system/      # 原生系统能力：本地文件系统与进程桥接
├── packages/           # 核心业务体系（包含 480+ 个原子包）
│   ├── api/            # 外部接入层：session-controller（命令控制器、历史查询）
│   ├── core/           # 运行时核心：agent、agent-loop、session、tools、system-prompt
│   ├── compaction/     # 历史治理：compaction-basic（压缩事务与稳定断言）
│   ├── interaction/    # 人机交互：user-approval（权限审批）、ask-user
│   ├── session/        # 状态持久化：session-persistence-jsonl、session-query
│   ├── tools/          # 具体物理工具：tool-fs、tool-shell、tool-web-search
│   └── eval/           # 评估体系：回放测试、断言套件与度量收集
└── vendor/cordis/      # 微内核底层依赖（Cordis 4.0.4 框架源码）
```

仓库目录看似庞大，但遵循统一的设计原则：**极简内核 + 声明式服务注册**。

DSH 没有臃肿的全局单例，也不使用深层类继承。每个子包都是一个**插件（Plugin）**，它向容器注册**服务（Service）**或监听**生命周期事件（Event）**。驱动组件协同的底层引擎是 `vendor/cordis`。

---

## 1.3 微内核的心脏：Cordis 4.0.4 依赖注入与服务生命周期

Cordis 是一个轻量级依赖注入与生命周期管理元框架。DSH 基准版本将其锁定在 `4.0.4`。

### 1.3.1 Context：基于 Proxy 的动态 IoC 容器

Cordis 的核心是 `Context`（上下文对象）。在 `source/vendor/cordis/src/context.ts` 中可以看到：

```typescript
// 真实源码摘录：source/vendor/cordis/src/context.ts 第 35-42 行
/**
 * Root and child dependency containers for Cordis plugins.
 *
 * A context is a proxy: normal property reads go through the service resolver,
 * while `extend()`, `isolate()`, and `intercept()` create scoped child
 * contexts without mutating their parent.
 */
export class Context { ... }
```

Cordis 在运行时使用 JavaScript `Proxy` 封装 `Context`。插件访问 `ctx.tools` 或 `ctx.sessions` 时，Proxy 会将属性读取拦截并分发给内部的服务解析器（Service Resolver）。

因此，**服务不需要在编译期硬编码组装，插件只需通过字符串键名声明依赖即可获取对应服务**。

### 1.3.2 声明式依赖注入：`static inject` 与 `ctx.plugin`

在 DSH 中挂载一个功能模块，采用的是优雅的依赖声明模式。以核心调度服务 `AgentLoop` 为例（`packages/core/agent-loop/src/index.ts`）：

```typescript
// 真实源码摘录：source/packages/core/agent-loop/src/index.ts 第 330-331 行
export class AgentLoop extends Service implements AgentFactory {
  static inject = ['agents', 'sessions', 'llm', 'tools', 'systemPrompt', 'sessionProjections']
  ...
}
```

`static inject` 声明了硬性依赖契约：Cordis 容器只有在声明的 6 个服务全部就绪后，才会激活 `AgentLoop`。若容器尚未加载 `llm` 或 `tools`，Cordis 会保持 `AgentLoop` 处于挂起状态，直到前置服务齐备，从而消除了因异步加载顺序不同导致的空指针风险。

---

## 1.4 服务注册与作用域隔离：Context、Service 与 Effect 机制

理解了 Cordis 的基本原理，我们进一步追踪服务如何在 DSH 中声明并管理自己的生命周期。

### 1.4.1 Service 基类与全局挂载

在 DSH 中，长期驻留的子系统通常继承自 Cordis 的 `Service` 基类（`vendor/cordis/src/service.ts`）：

```typescript
// 教材新增实践示例：符合 DSH 规范的最小服务定义
import { Service, Context } from '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Context {
    myMetrics: MyMetricsService
  }
}

export class MyMetricsService extends Service {
  constructor(ctx: Context) {
    // 调用 super 并传入当前 Context 和在 ctx 上挂载的属性名 'myMetrics'
    super(ctx, 'myMetrics', true)
  }

  recordOperation(name: string) {
    this.ctx.logger.info(`Operation recorded: ${name}`)
  }
}
```

当通过 `ctx.plugin(MyMetricsService)` 加载该类后，Cordis 自动将其实例绑定到 `ctx.myMetrics` 上，容器内的所有其他插件立即可以通过类型安全的提示直接访问该服务。

### 1.4.2 作用域隔离（Isolate）与子上下文（Fork）

在单进程同时承载多个智能体会话或多工作区的场景下，最忌讳的是不同会话的私有配置或临时工具发生串扰。

Cordis 提供了精妙的隔离机制（`symbols.isolate`）：
- **根上下文（Root Context）**：承载全局不变的系统级服务（如底层文件读写驱动、持久化数据库连接）。
- **分支上下文（Fork / Scoped Context）**：通过 `ctx.extend()` 或 `ctx.isolate()` 派生。子上下文继承父级的服务，但子级注册的私有工具、局部事件监听器在销毁时，父级和兄弟上下文完全不受影响。

### 1.4.3 生命周期与 Effect 自动资源回收

自研 Agent 最容易在长时间运行中发生内存泄漏或子进程悬挂。DSH 借助 Cordis 的 `ctx.effect()` 保证了资源的严密闭环：

```typescript
// 真实机制说明：生命周期 Dispose 与 Effect 绑定
ctx.effect(() => {
  // 1. 注册某些系统资源，例如文件监听器或后台定时轮询
  const timer = setInterval(() => checkStatus(), 1000)

  // 2. 返回清理函数（Disposer）
  return () => {
    clearInterval(timer)
  }
})
```

当该上下文绑定的会话被注销（`session.dispose()`）时，Cordis 会沿着依赖树递归调用所有由 `ctx.effect` 注册的清理函数。这就保证了不管是正在运行的 PTY 终端子进程，还是未完成的文件读写流，都能被百分之百安全释放，杜绝了孤儿进程的产生。

---

## 1.5 贯穿案例启动：微内核就绪与拓扑初始化

为了将全书各章的理论与代码紧密连接，我们将以一个典型的真实工业任务贯穿全书：
> **贯穿业务案例**：用户指派智能体——“排查并修复仓库中跨平台路径反斜杠 `\` 的兼容性缺陷，并通过单元测试验证”。

### 1.5.1 启动时的拓扑构建

当宿主服务拉起时，DSH 顶层入口（`packages/api/session-controller/src/index.ts`）执行初始化：

```
[启动主进程]
     │
     ▼
创建 Cordis Root Context
     │
     ├─► ctx.plugin(SessionStore)         // 挂载会话元数据管理服务
     ├─► ctx.plugin(SessionPersistence)   // 挂载 JSONL 存储引擎
     ├─► ctx.plugin(ToolsRuntime)         // 挂载工具注册与准入流水线
     ├─► ctx.plugin(AgentRegistry)        // 挂载智能体注册表与工厂
     ├─► ctx.plugin(LlmRuntime)           // 挂载大模型路由与适配器
     └─► ctx.plugin(SessionCommandController) // 暴露外部 RPC 控制入口
```

此时，所有服务完成注入与自检，系统进入完全停稳的监听状态。智能体并不预先建立死循环，而是静默等待用户指令的抵达。

---

## 1.6 本章小结

1. **Harness 的定位**：Harness 不是简单的 Prompt 拼接脚本，而是保障大模型在受控沙箱、不可变事件、收件箱调度与持久化边界内安全运行的工业级运行框架。
2. **模块解耦核心**：DSH 底层构建于 Cordis 4.0.4 之上，通过基于 Proxy 的 `Context` 与声明式 `static inject` 彻底消除了模块间的直接紧耦合。
3. **安全与生命周期**：Cordis 的 `isolate` 作用域隔离防止了会话间的数据污染，而 `ctx.effect()` 清理机制则构成了防止底层进程与文件描述符泄漏的关键屏障。

---

## 本章面试问答

### Q1 · 面试官：市面上有很多简易的 Agent 脚本，甚至几十行代码就能跑通 ReAct 循环，为什么 DSH 要引入像 Cordis 这样复杂的微内核框架？

**回答**：
简易脚本把上下文组装、模型通信、工具执行和状态存储强耦合在一个单体循环中。在玩具 Demo 中可行，但在工业场景下，系统面临多模型切换、跨平台工具扩展、细粒度权限准入以及多会话隔离等挑战。DSH 引入 Cordis 4.0.4，将每个能力解耦为独立的 Service，通过 `static inject` 实现声明式依赖装配，通过 `symbols.isolate` 实现了多会话与多智能体的沙箱隔离，并利用 `ctx.effect` 保证了异步资源的自动回收。

**原理**：
本质是“控制反转（IoC）”在智能体工程中的落地。框架将运行规则固化为不可变的基础设施，各个插件只需专注实现自己的业务语义（如文件读取或代码高亮），极大降低了系统的圈复杂度与长期维护成本。

**追问**：如果一个插件声明的依赖服务在容器中不存在，系统会发生什么？
**应答要点**：Cordis 不会直接抛出未定义异常崩溃，而是将依赖未满足的插件保持在未激活（Inactive）状态，直至该服务被其他插件注册提供；若直至启动结束仍缺失，则可通过诊断树排查未满足的 Service 依赖。

---

### Q2 · 面试官：在多租户或多会话环境下，Harness 是如何保证一个会话中的配置或状态不会污染另一个会话的？

**回答**：
在 Cordis 微内核中，系统并非为每个会话创建完全隔离的独立 Node.js 进程，而是通过 `Context.extend()` 和 `symbols.isolate` 派生会话级的子上下文（Scoped Context）。子上下文对服务的读取可以回溯至 Root Context，但对局部状态的写操作（如覆盖当前会话的模型参数、注册当前会话私有的动态 Skill 工具）只记录在当前 Context 分支上，兄弟会话完全不可见。

**原理**：
原型链代理拦截与作用域分级管理。保证了共享重量级全局服务（网络连接池、持久化驱动）的同时，在轻量级的内存层实现了逻辑状态的零泄漏。

**追问**：当会话结束（Disposed）时，这些局部注册的监听器和内存对象如何被回收？
**应答要点**：通过 Cordis 的 `Fiber` 与 `ctx.effect` 机制，会话销毁会沿着派生树向下递归触发 Disposer 清理函数，自动解绑所有事件监听并清空局部 Map，避免事件监听器累积导致的内存泄漏。


---

<a id="chapter-02"></a>

# 第 2 章｜运行循环：从任务接入到轮次收敛的控制流

装配好宿主服务与微内核底座后，系统进入静默待命状态。此时用户发出贯穿案例的首条指令：“排查并修复仓库中跨平台路径反斜杠 `\` 的兼容性缺陷，并通过单元测试验证”。

从用户提交请求到界面输出最终报告，系统内部经历了严密的状态跃迁。智能体不能来一条输入就直接请求一次大模型，必须维护可预测的状态机。

本章沿真实源码调用链剖析 DSH 的核心运行循环（Agent Loop），重点解构入口处的**幂等接纳契约**、收件箱的**三态输入调度**，以及系统状态机在**轮次（Turn）**、**步骤（Step）**与**尝试（Attempt）**之间的严格分层。

---

## 2.1 任务入口拦截：SessionCommandController 的幂等接纳契约

所有来自客户端（Web RPC、Desktop IPC 或 CLI）的交互指令，第一站都必须越过会话命令控制器 `SessionCommandController`（`source/packages/api/session-controller/src/commands.ts`）。

### 2.1.1 为什么必须解耦“接纳”与“完成”

在同步 Request-Response 模式下，服务端通常阻塞等待任务完成才返回结果。但智能体任务属于典型的**长程异步任务（Long-running Asynchronous Task）**：排查并修复代码通常涉及多次模型推理与多次物理编译运行，耗时可达数分钟。

若网关层长时间阻塞连接，前端极易遭遇网关超时（Gateway Timeout）；若网络卡顿导致用户连续双击提交，缺乏拦截机制会导致后台并发启动两套相互冲突的任务，从而破坏工作区代码。

因此，DSH 在入口处确立了严格的**接纳契约（Admission Contract）**：`prompt` 方法仅负责**校验入参、幂等排重、构造不可变消息并推入收件箱**；完成这些步骤后立即向客户端返回 `{ accepted: true }`，整体耗时通常在 20ms 以内。

### 2.1.2 源码精读：`SessionCommandController.prompt`

我们直接查看 `source/packages/api/session-controller/src/commands.ts` 中第 311–377 行的真实代码实现：

```typescript
// 真实源码摘录：source/packages/api/session-controller/src/commands.ts 第 311-377 行（关键片段）
async prompt(request: SessionPromptRequest): Promise<SessionPromptValue> {
  // 1. 内容有效性校验：必须包含非空白字符或有效附件
  if (!hasPromptContent(request.content)) {
    throw new RemoteError('gateway/bad-request', 'prompt content must include non-whitespace text or an attachment', {})
  }

  // 2. 客户端时区规范化校验
  const clientTimeZone = request.clientTimeZone === undefined
    ? undefined
    : canonicalClientTimeZone(request.clientTimeZone)
  if (request.clientTimeZone !== undefined && clientTimeZone === undefined) {
    throw new RemoteError('session/invalid-time-zone', 'clientTimeZone must be UTC or a valid IANA Area/Location name', { value: request.clientTimeZone })
  }

  // 3. 解析目标 Agent 实例
  const agent = await this.resolveAgent(request.sessionId)

  // 4. 关键幂等检查：校验当前 requestId 是否已被处理或正在队列中
  if (hasPromptRequest(agent, request.requestId)) return { accepted: true }

  const source: MessageSource = {
    kind: 'user',
    rpcId: request.requestId,
    ...(clientTimeZone === undefined ? {} : { clientTimeZone }),
  }

  // 5. 多模态与附件准入
  const hasImage = request.content.some(part => part.type === 'image')
  const admit = async (): Promise<SessionPromptValue> => {
    try {
      ...
      const message: UserMessage = createUserMessage({ content, source })
      
      // 6. 根据调用模式将消息排入对应收件箱队列
      if (request.mode === 'steer') agent.steer(message)
      else agent.followup(message)
      
      binding.commit()
    } catch (error) {
      ...
    }
    return { accepted: true }
  }

  return hasImage ? this.agents.serializeImageAdmission(agent, admit) : admit()
}
```

### 2.1.3 幂等检查的双重防线：`hasPromptRequest`

让我们顺着调用链追查原稿中被“虚化”的 `hasPromptRequest` 函数（`commands.ts` 第 602–614 行）：

```typescript
// 真实源码摘录：source/packages/api/session-controller/src/commands.ts 第 602-614 行
function hasPromptRequest(agent: Agent, requestId: SessionRequestId): boolean {
  const matches = (message: UserMessage): boolean => {
    const source = message.source
    return source.kind === 'user' && 'rpcId' in source && source.rpcId === requestId
  }
  // 第一重防线：排查收件箱内存队列（尚未被模型消费的消息）
  if (agent.inbox.nextTurn.some(matches) || agent.inbox.nextStep.some(matches)) return true
  
  // 第二重防线：排查会话历史快照（已经持久化落盘的历史消息）
  return agent.session.snapshotEvents().some((event) => {
    if (event.type !== 'user/message') return false
    const source = event.data.source
    return source.kind === 'user' && 'rpcId' in source && source.rpcId === requestId
  })
}
```

这段源码展示了极高的工程严密性：它不仅扫描了内存收件箱（`nextTurn` 和 `nextStep`），防止请求重复入队；同时还回溯了已经持久化的事件快照。无论网络波动导致客户端在 100 毫秒后重试，还是 5 分钟后因重连机制重发请求，只要携带相同的 `requestId`，控制器都能够准确识别并返回 `{ accepted: true }`，绝不在会话日志中留下一条多余的重复指令。

---

## 2.2 收件箱 Inbox 的三态调度：followup、steer 与 inject 的精确语义

当消息通过 `prompt` 准入后，它被送入了智能体的专属收件箱（Inbox）。

在原稿中，作者遗漏了关键的第三种模式 `inject`，并且未能准确描述 `steer` 在系统不同状态下的分支行为。查阅基准代码 `source/packages/core/agent/src/runtime-types.ts` 第 215–242 行，系统实际上定义了三组语义截然不同的注入方法：

```typescript
// 真实源码接口：source/packages/core/agent/src/runtime-types.ts 第 215-242 行
interface Agent {
  /**
   * 基础派发方法：将带标识的 user 消息路由至收件箱
   * @param message 封装后的用户语义消息
   * @param target 目标队列：'next-turn' 或 'next-step'
   * @param wakeup 是否在投递后主动唤醒驱动器
   */
  send(message: UserMessage, target: InboxTarget, wakeup: boolean): void

  /** 1. 常规下一轮次排队并唤醒驱动 */
  followup(message: UserMessage): void

  /** 2. 提交下一步引导干预，并唤醒驱动 */
  steer(message: UserMessage): void

  /** 3. 静默推入上下文材料，绝不唤醒驱动 */
  inject(message: UserMessage): void
}
```

为了彻底讲透这三者的差异，我们将它们的设计对比梳理如下：

| 调度方法 | 目标队列 (`target`) | 是否唤醒驱动 (`wakeup`) | 驱动空闲（Idle）时的行为 | 驱动运行中（Running）时的行为 | 典型适用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`followup(msg)`** | `next-turn` | **`true`（唤醒）** | 立即启动一个新的 **Turn** 业务轮次 | 保持排队，等待当前 Turn 全部收敛完成后才启动下一轮 | 用户主动提交新的后续任务或常规追问 |
| **`steer(msg)`** | `next-step` | **`true`（唤醒）** | 立即启动新轮次推进 | 在当前正在执行的 **Step 边界**紧急切入，拦截下一次推理方向 | 用户在智能体执行途中喊停或纠偏（“不要改这个文件”） |
| **`inject(msg)`** | `next-step` | **`false`（静默）** | **完全不启动**，消息静止在队列中 | 不打断执行，仅在驱动下一次自行组装 Prompt 时被静默打包 | 系统后台静默更新环境感知、Git 状态变更通知 |

### 2.2.1 为什么必须存在 `inject`？

很多开发者会问：既然都要把材料给模型，为什么不直接 `followup` 或 `steer`？

设想如下场景：当用户正在让智能体排查代码时，后台的文件监控插件检测到某个本地配置文件被外部编辑器修改了。如果插件调用 `followup` 或 `steer`，就会意外强行唤醒原本正在等待网络 I/O 的智能体，或者强行催生一个非预期的轮次；而通过 `inject`，插件可以在完全不惊扰当前运行节拍的前提下，把“外部文件已变更”这一事实妥善存入收件箱。当智能体完成当前步骤并准备组装下一次推理上下文时，这部分事实就会自然而然地浮现在模型的视野中。

---

## 2.3 状态机的三层边界：轮次（Turn）、步骤（Step）与尝试（Attempt）

当收件箱唤醒了调度驱动器 `AgentLoop`（`source/packages/core/agent-loop/`），系统开始进入真正的执行状态机。

工业级 Agent 必须彻底告别朴素的单层循环，在 DSH 中，运行状态被解构为严格嵌套的三层模型：

```
┌────────────────────────────────────────────────────────────────────────┐
│ 业务轮次 (Turn): 由用户输入触发，直到达到任务终止条件 (turn/start -> turn/end) │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ 执行步骤 (Step 1): 单次模型推理及其工具执行 (step/start -> end)  │   │
│   │                                                                │   │
│   │   ┌────────────────────────────────────────┐                   │   │
│   │   │ 模型尝试 (Attempt 1): 遇到超时/网络重试 │                   │   │
│   │   └────────────────────────────────────────┘                   │   │
│   │   ┌────────────────────────────────────────┐                   │   │
│   │   │ 模型尝试 (Attempt 2): 成功获得 ToolCall │                   │   │
│   │   └────────────────────────────────────────┘                   │   │
│   │   ┌────────────────────────────────────────┐                   │   │
│   │   │ 工具管线执行: dispatch(read) -> Result │                   │   │
│   │   └────────────────────────────────────────┘                   │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ 执行步骤 (Step 2): 回填材料后的二次推理并输出最终总结           │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.3.1 轮次（Turn）：面向人类业务的闭环单元

- **定义**：一个 Turn 始于事件 `turn/start`，终于 `turn/end`。它代表人类用户赋予智能体的一段独立业务生命周期。
- **生命周期**：只要模型还在持续提议工具调用（如“读取文件”、“执行搜索”），当前 Turn 就会保持开放（Open Turn）。只有当模型输出纯文字回复、或主动声明任务结束、或遭遇不可恢复的致命错误时，驱动才会发射 `turn/end` 事件并注明结束原因（`completed`、`failed`、`cancelled` 或 `forked`）。

### 2.3.2 步骤（Step）：单次人机交互闭环

- **定义**：一个 Turn 内部包含 1 到 N 个 Step。每个 Step 始于 `step/start`，终于 `step/end`。
- **核心契约**：单步的标准范式是——**组装当前材料 → 发起模型推理 → 模型输出工具提议（Tool Call）或自然语言 → 调度物理工具派发 → 将工具结果以 `tool_result` 追加到会话**。只有当这一整套闭环完成，当前 Step 才算结算。

### 2.3.3 尝试（Attempt）：单步内的故障恢复隔离舱

- **定义**：尝试（Attempt）是对单个模型网络请求的微观封装。
- **关键工程不变量**：当网络闪断、API 触发 429 限流或模型偶发输出格式错误时，驱动在同一步骤内递增 Attempt 计数，并触发可扩展的恢复策略。**Attempt 的失败与重试绝不推进步骤序号（Step Index），也绝不向会话事实日志中写入半途废弃的垃圾步骤事件**。这种设计保证了上层监控和下游持久化看到的状态机步骤永远是干净、单调、确定性递增的。

---

## 2.4 贯穿案例启动：从任务排队到首个工具提议

现在，我们将贯穿案例置入这一运行循环中推演：

1. **入口接纳（0 ms）**：
   - 客户端携带全局唯一 ID `req-path-fix-001` 发送指令：“排查并修复仓库中跨平台路径反斜杠兼容性缺陷”。
   - `SessionCommandController.prompt` 校验文本有效性，时区规范化为 `Asia/Shanghai`。
   - `hasPromptRequest` 核对内存队列与事件历史，确认无重复。
   - 控制器构造带有 `rpcId: 'req-path-fix-001'` 的 `UserMessage`，调用 `agent.followup(message)`。
   - 控制器立即返回 `{ accepted: true }`，前端显示消息已发出。

2. **驱动唤醒与 Turn 开启（15 ms）**：
   - `followup` 主动唤醒了原本静止的 `AgentLoop`。
   - 驱动检测到智能体处于空闲状态，调用会话对象发射底层事件 `turn/start`（`turn: 1`）。系统正式进入第一个开放轮次。

3. **Step 1 初始化与提示词组装（25 ms）**：
   - 驱动发射 `step/start`（`step: 1`），从 `inbox.nextTurn` 中取出该任务消息。
   - 驱动调度上下文服务，将系统规则、工作区信息与该用户消息合并组装（上下文的具体组装机制将在第 3 章展开）。

4. **首次模型推理与 Attempt（40 ms ~ 950 ms）**：
   - 启动 `Attempt 1`，向底层大模型后端发出结构化请求。
   - 模型在这一时刻没有读过任何项目文件，它无法凭空修复代码。因此，模型在 `AssistantMessage` 中给出了一个符合 JSON Schema 的工具调用提议：
     ```json
     {
       "tool_name": "fs_read",
       "arguments": { "path": "src/utils/path.ts" }
     }
     ```

5. **工具派发与步骤收敛（960 ms）**：
   - 驱动拦截到该提议，并不立即结束轮次，而是将其移交给工具安全管线（第 6 章）。
   - 文件工具返回代码文本后，包装为 `tool_result` 回填至会话。
   - 驱动发射 `step/end`（`step: 1`）。此时收件箱无打断指令，且模型尚未给出最终回复，驱动器自动进入 `Step 2`，驱动整项任务向收敛目标继续推进。

---

## 2.5 本章小结

1. **入口接纳契约**：`SessionCommandController.prompt` 严格解耦了接纳与完成。通过 `hasPromptRequest` 对内存收件箱和持久化事件历史的双重扫描，构建了百分之百幂等的防抖防重屏障。
2. **收件箱三态调度**：`followup` 主动唤醒并排入下一轮次，`steer` 针对当前步骤边界紧急干预并唤醒，`inject` 静默推入上下文材料而不扰动驱动节拍。
3. **状态机三层边界**：Turn 负责业务闭环，Step 负责单步人机推理与工具派发，Attempt 负责单步内部的网络容错重试。Attempt 的失败绝不产生孤儿步骤事件。

---

## 本章面试问答

### Q1 · 面试官：用户在前端快速双击了提交按钮，或者因网络波动重发了请求，DSH 在源码层面是如何确保后台不会重复执行两次耗费 Token 的任务的？

**回答**：
DSH 在入口控制器 `SessionCommandController.prompt` 中实现了双重幂等防护函数 `hasPromptRequest(agent, requestId)`：
第一重，它检索目标智能体收件箱中未消费的待办队列 `agent.inbox.nextTurn` 与 `nextStep`，比对消息来源中的 `rpcId`；
第二重，它通过 `agent.session.snapshotEvents()` 扫描底层已经提交的事件快照，检查是否有类型为 `user/message` 且携带相同 `rpcId` 的历史事件。
只要任一防线匹配命中，控制器直接阻断后续入队操作，并立即向客户端返回 `{ accepted: true }` 幂等确认，从而在网关最外层掐断了重复调用的根源。

**原理**：
异步事件驱动系统的“请求排重前置”设计。绝不能等请求进入复杂的 LLM 推理或物理工具执行后才去判断并发，必须在状态机入口处建立基于唯一请求 ID（`rpcId`）的防重屏障。

**追问**：为什么不能只查内存里的 `agent.inbox`，还必须查 `snapshotEvents`？
**应答要点**：因为请求可能已经被 `AgentLoop` 从收件箱取出并正式写入了不可变历史日志（甚至已经开始调用大模型）。如果只查收件箱，取件之后才到达的重试请求就会漏过防线，导致同一个会话产生两条一模一样的用户指令。

---

### Q2 · 面试官：如果智能体在执行耗时很长的编译任务，用户想要中途打断它并发出新指令，应该调用 `followup` 还是 `steer`？为什么？

**回答**：
必须调用 `steer(message)`。
`followup` 会将消息投入 `nextTurn` 队列，它必须等待当前整个 Turn 的所有步骤全部收敛（所有工具执行完且模型输出完成报告）后才会被消费，无法起到即时打断的效果；
而 `steer` 会将消息推入 `nextStep` 队列，并在运行时向驱动发出唤醒信号。正在执行的驱动器会在当前正在进行的 Step 边界（例如当前单次工具执行结束后，或在安全检查点）立即拦截并消费该消息，使模型在下一步推理时优先遵从用户的干预指示。

**原理**：
协作系统中的“边界抢占”语义。长时间运行的系统不能简单采用操作系统级的暴力 `kill` 线程（会导致文件处于半写脏状态），而是通过在有状态边界（Step Boundary）注入 `steer` 引导信号，实现优雅、确定性的协作式打断。


---

<a id="chapter-03"></a>

# 第 3 章｜上下文装配：提示词、技能发现与动态视野

当 `AgentLoop` 驱动器开启一个新的步骤（Step）并准备调用大模型时，它面临一个核心工程挑战：**大语言模型本身既没有跨请求的长期记忆，也无法直接感知宿主操作系统**。模型在当前步骤能够依据的所有信息，完全取决于框架在这一瞬间向其网络接口发送的那个结构化 Payload。

如果无节制地把全部项目文件、所有工具文档和上百轮历史一并塞入，上下文窗口会迅速被撑爆，推理成本呈指数级上升，且大模型极易产生严重的注意力稀释（Lost in the Middle）；反之，如果遗漏了关键的路径规范或环境约束，模型又会给出无法落地的代码。

本章将深入解析 DSH 的上下文装配流水线。我们将剖析系统提示词（System Prompt）的模块化分层构成，解密技能（Skills）的**渐进式披露（Progressive Disclosure）**机理，并明确动态材料挂载的作用域边界。

---

## 3.1 动态组装流水线：模型每一步的材料究竟由谁提供

在朴素的脚本实现中，系统提示词往往是一段在代码里写死的超长模板字符串。但在 DSH 这样承载跨平台、多工具、多插件扩展的框架中，提示词绝不是静态的，而是一座**由多个插件动态申报、按数字顺序稳定拼接的装配流水线**。

在基准版本中，提示词装配中枢由 `packages/core/system-prompt/` 承载，对应的服务是 `SystemPrompt`（`source/packages/core/system-prompt/src/index.ts` 第 405 行）。

```
┌─────────────────────────────────────────────────────────────┐
│ SystemPrompt 服务装配流水线                                 │
│                                                             │
│  [Layer 1: 核心身份]                                        │
│   order: 100 ──► "You are an AI agent powered by DSH..."    │
│                                                             │
│  [Layer 2: 部署前缀]                                        │
│   order: 200 ──► personaPrefix (部署方定制人格)             │
│                                                             │
│  [Layer 3: 宿主与工作区环境]                                │
│   order: 300 ──► OS, cwd, git branch, clientTimeZone       │
│                                                             │
│  [Layer 4: 技能目录摘要 (Skills Summary)]                   │
│   order: 400 ──► <available_skills> (仅包含 Name 与简述)   │
│                                                             │
│  [Layer 5: 工具使用规范]                                    │
│   order: 500 ──► Tool Call 协议与错误重试规则               │
│                                                             │
│  [Layer 6: 部署后缀]                                        │
│   order: 600 ──► personaSuffix (输出格式强制要求)           │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
        输出最终 System Message (放入模型第 0 槽位)
```

### 3.1.1 源码精读：分节注册 `systemPrompt.section`

在 `source/packages/core/system-prompt/src/index.ts` 中，`SystemPrompt` 继承自 Cordis `Service`，并通过分层管理（`ScopedLayers`）允许任意插件向提示词中注入内容：

```typescript
// 真实源码摘录：source/packages/core/system-prompt/src/index.ts 第 454-463 行
section(section: PromptSection): () => void {
  if (!Number.isFinite(section.order)) {
    throw new TypeError(`prompt section "${section.name}" order must be a finite number`)
  }
  return this.layers.effect(
    this.ctx,
    layer => layer.sections.insert(section.name, section),
    { label: 'systemPrompt.section()' },
  )
}
```

每个插件通过调用 `ctx.systemPrompt.section(...)` 注册一个分节（Section），并传入唯一的 `name`、正文 `text` 以及关键的排序权重 `order`。

这种设计的优势在于：**顺序确定性**。无论各插件在微内核中加载完成的先后顺序如何，最终拼接给大模型的 Prompt 文本永远严格按照 `order` 升序排列。排在前面的全局约束不会被后来加载的插件打乱位置，保证了大模型对系统规则感知的绝对稳定性。

---

## 3.2 技能（Skills）的渐进式披露：为什么元数据可见不等于全量加载

在复杂的开发场景中，工程团队往往积累了大量开发规范（如跨平台路径处理规范、数据库迁移准则等）。若将数万字的规范全部预先写入 System Prompt，不仅消耗高昂的 Token 费用，还会严重挤压大模型的有效上下文窗口。

DSH 在 `source/packages/skill/` 体系中采用**技能渐进式披露（Progressive Disclosure）**策略解决该问题。
### 3.2.1 阶段一：引导阶段仅注入技能元数据清单（Summary）

当工作区启动时，本地文件系统技能提供方 `dsh-skill-filesystem`（`packages/skill/skill-filesystem/`）扫描项目中的技能目录。

根据官方规范（`docs/subsystems/skills.zh.md`），DSH 按照以下严格的六级优先级进行本地技能发现：

| 发现优先级 (Rank) | 发现源标识 | 磁盘查找路径 | 覆盖与胜出规则 |
| :--- | :--- | :--- | :--- |
| **100（最高）** | `project-dsh` | `<projectRoot>/.dsh/skills` | 当前项目私有规范，最高优先胜出 |
| **200** | `project-agents` | `<projectRoot>/.agents/skills` | 团队通用规范，次高优先 |
| **300** | `custom` | `Config.customSkillDirs` | 用户显式配置的自定义路径 |
| **400** | `user-dsh` | `<dshHome>/skills` | 当前用户个人全局 DSH 规范 |
| **500** | `user-agents` | `<agentsHome>/skills` | 当前用户全局通用规范 |
| **600（最低）** | `bundled` | `Config.bundledSkillDir` | 系统预置随包分发的内置技能 |

在初次组装提示词时，系统**不读取技能正文（`SKILL.md`）**，仅提取技能名称和简短描述，生成紧凑的 XML 摘要注入 System Prompt：
```xml
<!-- 真实注入 System Prompt 的技能摘要结构 -->
<available_skills>
  <skill>
    <name>path-normalization</name>
    <description>处理 Windows 反斜杠与 POSIX 路径跨平台转换的编码规范与排错指南</description>
  </skill>
  <skill>
    <name>git-commit-helper</name>
    <description>生成符合 Conventional Commits 格式的提交信息</description>
  </skill>
</available_skills>
```

该清单仅占用几十个 Token，足以让模型建立对可用能力的认知索引，在遇到匹配问题时再主动调取技能详情。

### 3.2.2 阶段二：模型触发工具按需加载正文

当大模型在分析任务时，判定当前面临“跨平台路径”问题，它会主动通过工具调用提出加载需求。

DSH 专门提供了一个系统内置工具：`skill`（由 `packages/skill/tool-skill/` 注册）。模型输出以下 Tool Call：

```json
{
  "tool_name": "skill",
  "arguments": {
    "name": "path-normalization"
  }
}
```

框架的工具流水线捕获该调用后，调度 `ctx.skills.get('path-normalization')`，此时才真正从磁盘读取完整的 `SKILL.md` 正文，并作为工具结果（`tool_result`）回填到会话历史中。

这一机制实现了“**目录随时可见、正文按需加载**”，兼顾了能力的广度与上下文窗口的极致精简。

---

## 3.3 动态上下文挂载：文件选区、附件与材料作用域

除了系统级提示词与技能，用户在交互过程中还会上传图片、选中文档片段或引用历史会话。这些材料如何合规地进入模型的视野？

### 3.3.1 材料的作用域（Scope）与可见性控制

在 DSH 中，任何进入上下文的材料都拥有严格的元数据标记：
- **来源（Source）**：标记材料是由用户通过网关显式提交（`kind: 'user'`），还是系统后台静默注入（`kind: 'injected'`），亦或是工具执行的回填（`kind: 'tool'`）。
- **生命周期作用域（Lifetime Scope）**：
  - **单步可见（Step-ephemeral）**：仅在当前推理步骤有效，例如“正在监听的临时网络状态”，不沉淀入持久化会话；
  - **轮次持久（Turn-durable）**：作为当前业务轮次的正式输入（如用户的 prompt 文本）；
  - **会话持久（Session-immutable）**：一旦被写入不可变事件日志，成为未来所有步骤都可以派生读取的真实历史。

---

## 3.4 贯穿案例推进：装配“排查路径缺陷”的首步视野

现在，我们跟随贯穿案例，观察在第 2 章中启动的 `Step 1` 在发起模型网络调用前，上下文装配服务实际交付的数据切片：

1. **环境与工作区上下文注入（Layer 3）**：
   - `SystemPrompt` 注入当前宿主环境信息：
     ```text
     OS: win32 (Windows 10.0.26200 x64)
     CWD: E:/agentcoding/deepseek-harness-learning
     Git Branch: master (Clean)
     ```
   - 这一环境事实极其关键：它明确告知模型当前运行在 **Windows 环境**下，天然存在反斜杠与正斜杠的混用风险。

2. **技能目录呈现（Layer 4）**：
   - 技能发现提供方扫描到 `.dsh/skills/path-normalization/SKILL.md`，将该技能的摘要 `<skill><name>path-normalization</name>...</skill>` 压入候选区。

3. **用户任务原样挂载**：
   - 在 System Prompt 之后，紧随第一条 `UserMessage`：“排查并修复仓库中跨平台路径反斜杠 `\` 的兼容性缺陷，并通过单元测试验证”。

4. **首步推理决策**：
   - 模型在阅读了 System Prompt 后，敏锐捕捉到了两个事实：第一，宿主环境是 Windows；第二，系统提供了一个专门名为 `path-normalization` 的专项技能。
   - 于是，模型在第一步做出的不是盲目瞎猜代码，而是决定先调用工具读取该技能指南与关键文件，确保后续修复方案与规范严格对齐。

---

## 3.5 本章小结

1. **模块化提示词装配**：`SystemPrompt` 服务通过 `section(order, text)` 机制，将身份定义、宿主环境、技能摘要与工具协议解耦为有序分节，确保装配结果的一致性与确定性。
2. **渐进式技能披露**：通过分层排名（Rank 100~600）扫描本地技能，第一阶段只在 Prompt 暴露 Name 与 Description 目录；当模型判定需要时，通过 `skill` 工具按需调取正文，杜绝上下文浪费。
3. **环境感知前置**：宿主环境（操作系统、工作区路径、Git 分支）作为系统事实直接注入上下文，是智能体产出高可靠跨平台代码的前提。

---

## 本章面试问答

### Q1 · 面试官：如果项目中存在很多复杂的规范文档（比如几十个 Skill），一次性全塞进 System Prompt 有什么致命缺陷？DSH 是如何解决的？

**回答**：
一次性全量塞入会导致三大致命缺陷：
1. **Token 成本与延迟暴增**：每个步骤都需要全量传输无用文本，TTFT（首字延迟）急剧增加；
2. **上下文窗口挤占**：过早消耗长文本窗口，导致留给真实代码文件和工具执行结果的配额严重受限；
3. **模型注意力稀释（Lost in the Middle）**：模型在冗长的 Prompt 中极难精准聚焦当前任务的核心指令，容易发生指令遗忘或幻觉。
DSH 采用“渐进式披露”架构：启动时扫描技能目录，Prompt 中仅注入精简的 `<available_skills>` 目录清单（含名称与功能说明）；模型在推理时若发现当前任务涉及特定规范，主动调用内置 `skill` 工具加载对应正文，作为工具结果按需回填，将上下文利用率提升至最高。

**原理**：
“索引与内容分离”的知识检索原则。在元数据层建立全局感知，在内容层实现按需分页加载，符合现代大模型长上下文工程的最优实践。

**追问**：如果在项目根目录和用户根目录下存在两个同名的 Skill，DSH 遵循什么优先级决定胜出方？
**应答要点**：遵循严格的 Rank 优先级。根据官方实现，项目内目录（如 `.dsh/skills`，Rank 100）优先级最高，优先覆盖用户全局目录（如 `<dshHome>/skills`，Rank 400）中的同名技能，确保项目定制规范拥有最高决策权。


---

<a id="chapter-04"></a>

# 第 4 章｜历史管理：长程上下文压缩与溢出防护

随着智能体任务向纵深推进，会话历史开始不可逆转地急剧膨胀。一次包含数十次工具调用、长段命令日志输出与多轮代码修改的长程任务，其上下文累积往往迅速攀升至 50,000 甚至 100,000 个 Token。

此时系统将面临极其严苛的工程瓶颈：即使底层大模型支持超大上下文窗口，单次推理的计算成本与网络延迟也会呈线性上升；更危险的是，长程历史中杂乱的临时日志会形成巨大的注意力噪声，导致模型产生遗忘和幻觉；一旦遇到超出硬件或 API 硬限制的上下文溢出（Context Overflow），系统将直接遭遇致命的 400 异常而中断。

本章将深入剖析 DSH 的长程历史治理体系。我们将精读 `packages/compaction/compaction-basic/` 中的**结构化压缩事务**，揭密防御并发事实覆盖的 **`assertStable` 稳定断言**，并解构超长执行结果外溢落盘的 **`artifact://` Spill 机制**。

---

## 4.1 上下文膨胀困境：Token 成本、注意力稀释与硬截断风险

面对长程历史，简易脚本通常只有两类处理方式：
1. **滑动窗口硬截断（Sliding Window）**：仅保留最近 N 条消息并直接丢弃早期历史。这会导致模型丢失最初用户给出的关键约束（例如“不得引入外部依赖”或“必须兼容 Windows”）。
2. **无状态全量保留**：不做任何清理，直接依赖外部模型上下文窗口。其代价是交互成本骤增，且端到端响应延迟显著恶化。

因此，工业级 Harness 必须具备在保留核心事实、关键约束与因果链的前提下，平滑裁剪历史的**上下文压缩（Compaction）**引擎。

---

## 4.2 结构化压缩事务：从剪枝到摘要生成的阶段控制

在 DSH 中，上下文压缩不是一个简单的字符串拼凑过程，而是一个具有明确状态边界的**受控事务（Compaction Transaction）**。

在基准版本 `source/packages/compaction/compaction-basic/src/region.ts` 中，压缩事务被严格划分为四个阶段：

```
[触发压缩: 达到预防阈值 或 发生溢出恢复]
                    │
                    ▼
阶段 1: 选取候选区间 (selectCompactableRange)
        - 保护最前置的系统指令与前导约束
        - 保护最近开放轮次的有效上下文
        - 选定中间已收敛的历史轮次作为压缩切片
                    │
                    ▼
阶段 2: 异步生成结构化摘要 (Summarization)
        - 提取选定区间内的核心事实、决策与文件状态
        - 提炼为紧凑的结构化 Markdown 摘要
                    │
                    ▼
阶段 3: 并发安全稳定断言 (assertStable 校验)
        - 验证在生成摘要期间，目标区间未发生外部并发修改
        - 若校验失败，立即回滚事务并丢弃该摘要
                    │
                    ▼
阶段 4: 事务提交与闭合 (commitCompactionBody)
        - 写入不可变事件 compaction/start 与 compaction/end
        - 会话派生视图用该摘要替换历史区间
```

### 4.2.1 触发路径的双轨设计：预防路径 vs 溢出恢复路径

DSH 实现了两条触发路径，两者的容错哲学截然不同：
- **预防路径（Pressure Path）**：在每次步骤组装上下文前，若估算当前 Token 接近安全水位线（如达到窗口的 80%），系统提前发起后台压缩。如果预防压缩失败（例如摘要模型超时），系统仅打印警告日志并允许主流程继续尝试。
- **溢出恢复路径（Overflow Recovery Path）**：当网络请求直接抛出模型后端的上下文超限错误（`context_overflow`）时触发。此时属于紧急故障恢复，系统立即执行同步抢救；但为防止程序在不可压缩的死局中死循环，恢复路径受到严格的最大重试次数限制（Max Attempts）。

---

## 4.3 关键并发安全机制：assertStable 稳定断言与提交互斥

在多智能体协同或外部事件驱动的高并发环境中，上下文压缩面临一个极易被忽视的致命陷阱：**并发事实覆盖（Concurrent History Overwrite）**。

时序推演如下：
1. 压缩器在 `T = 0ms` 选取事件序列 `Seq 5 ~ 20` 作为压缩切片，并在后台调用模型生成摘要（通常耗时 2~3 秒）；
2. 在 `T = 1500ms` 时，外部工具或用户干预信号（`steer`）写入新事实，追加到了该区间末尾；
3. 在 `T = 2500ms` 时，摘要模型返回。若系统直接将 `Seq 5 ~ 20` 替换为刚才生成的摘要，在 `T = 1500ms` 追加的新事实就会被**静默抹除**。
为了彻底防御这一并发数据一致性漏洞，DSH 在 `region.ts` 中设计了极其严格的 `assertStable` 断言机制。

### 4.3.1 源码精读：`assertStable` 与提交事务闭合

我们直接审视 `source/packages/compaction/compaction-basic/src/region.ts` 第 210–237 行的真实实现：

```typescript
// 真实源码摘录：source/packages/compaction/compaction-basic/src/region.ts 第 210-237 行
const startEvent = session.append('compaction/start', lifecycle)
const assertStable: StabilityCheck = options.stability === 'whole-surface'
  ? assertWholeSurfaceUnchanged
  : assertSelectedSpanStable
let failure: TransactionFailure | undefined
...
// 异步调用外部大模型生成选定区间的结构化摘要
const summarized = await summarizeCompaction(
  dependencies,
  agent,
  prepared,
  options.sourceCommandId,
  assertStable,
  signal,
)
if (options.owner === null) signal?.throwIfAborted()

// 【关键防线】在正式 commit 之前，再次执行原子级稳定性校验
assertStable(dependencies, session, summarized)
stage = 'commit'

// 校验通过，原子提交压缩产物，更新派生视图
const pending = commitCompactionBody(session, startEvent, summarized)
closing = true
```

`assertStable` 深入对比了压缩起止事件的唯一序列号（`seq`）与内容哈希。如果在异步生成摘要期间，会话历史被插入了任何新事实，`assertStable` 立即抛出异常并中断提交，随后系统发射 `compaction/end` 并标记为取消（`status: 'aborted'`）。

**这种“宁可压缩失败放弃，绝不静默覆盖事实”的防御设计，是工业级 Harness 数据一致性的核心基石**。

---

## 4.4 超长结果的外溢保存：artifact:// 定位符与 Spill 机制

除了长轮次累积，另一种瞬间撑爆上下文的常见元凶是**超长工具输出（Runaway Tool Output）**。例如智能体执行了一条错误的命令输出了 50MB 的日志，或者读取了一个意外庞大的打包文件。

若直接将数万行控制台日志回填进消息历史，单步就会直接导致上下文溢出。DSH 在 `source/packages/core/spill/` 引入了 **外溢定位符机制（Spill Mechanism）**。

### 4.4.1 外溢保存的核心工作流

当工具执行完成并准备生成 `tool_result` 时，内容拦截器检查文本尺寸：
1. **尺寸阈值判定**：若输出内容超过配置阈值（默认通常为 20KB 或 4000 字符），系统触发外溢逻辑；
2. **物理独立落盘**：完整的数据被独立写入专用的持久化存储中，并分配全局唯一的资源 URI，例如 `artifact://spill/tool-call-104.log`；
3. **模型可见截断与定位符回填**：回填到会话历史中的并非全量日志，而是一段精简的结构化片段：
   - 提取文件的前 10 行与末尾 10 行；
   - 中间插入明确的截断提示及外溢定位符 URI；
   - 附带精准的分页指示器（如：`:50-100` 行号选择器）。

```markdown
<!-- 回填给大模型的 Spill 结构示例 -->
[执行日志输出超长，已自动外溢至物理存储]
URI: artifact://spill/npm-test-run.log (总计 14,280 行, 245 KB)

--- [前 5 行预览] ---
> test
> vitest run --reporter=verbose
PASS tests/unit/basic.spec.ts
...
--- [后 5 行预览] ---
FAIL tests/e2e/path-compat.spec.ts:42:15
Expected: "C:\\projects\\app"
Received: "C:/projects/app"
Tests: 1 failed, 28 passed, 29 total
--------------------------------------------------
提示：如需查阅中间具体报错详情，请调用 read 工具并携带行号范围，如 read("artifact://spill/npm-test-run.log:35-50")
```

通过这一机制，大模型既捕获了最终的失败核心摘要（知道了哪一行报错），又避免了被数万行无关日志冲垮窗口，同时还保留了按需精准二次检索全部内容的能力。

---

## 4.5 贯穿案例推进：200KB 测试日志的外溢存盘与定位符回填

现在，我们跟随贯穿案例，见证 Spill 机制如何在真实排查中保卫系统安全：

1. **执行单元测试触发超长日志**：
   - 智能体通过 Shell 工具执行了全量测试套件 `npm run test`；
   - 测试套件输出了覆盖 80 个测试用例的极其冗长的详细日志，体积高达 210 KB（约 55,000 个 Token）；
2. **工具安全管线拦截外溢**：
   - 工具后置处理器检测到输出远超单步安全配额，立即将其截获并写入 `.dsh/artifacts/npm-test-run.log`；
   - 系统生成资源 URI：`artifact://spill/npm-test-run.log`；
3. **紧凑定位符回填至第 2 步**：
   - 智能体在 `Step 2` 接收到的并不是 210KB 的洪流，而是一段仅 300 Token 的精简卡片；
   - 模型清晰地从末尾预览中看到了失败根因：`FAIL tests/path.spec.ts: path.join on Windows expected backslash but got POSIX slash`；
4. **决策推进**：
   - 模型无需为数万行通过日志支付 Token 费用，注意力精准锁定在失败位置，随即发起下一步对 `src/utils/path.ts` 的定向读取与修复。

---

## 4.6 本章小结

1. **长程历史治理双轨制**：预防路径在水位超标前提前瘦身，溢出恢复路径在接口报错后紧急抢救，配合重试次数限制杜绝死循环。
2. **`assertStable` 稳定断言**：在异步摘要完成后、正式提交前执行二次原子校验，彻底防范了压缩期间并发新事实被静默抹除的数据一致性灾难。
3. **`artifact://` Spill 外溢定位**：对失控超长工具输出进行物理旁路落盘，向模型仅回填首尾预览与 URI 定位符，兼顾了信息完整性与窗口安全性。

---

## 本章面试问答

### Q1 · 面试官：在 Agent 长时间运行中，如果上下文压缩（Compaction）只是简单地“在后台异步调用大模型写一段摘要并直接替换旧消息”，在多智能体或异步任务下会产生什么严重的并发 Bug？DSH 是如何解决的？

**回答**：
会产生**并发事实覆盖（Concurrent Event Overwrite）**的严重 Bug。
因为大模型生成摘要是异步且耗时的（通常需要 2~5 秒）。如果在生成摘要期间，用户通过 `steer` 插入了新的纠偏指令，或者后台工具并发写入了一条新的状态事实，而此时异步摘要完成并直接盲目覆盖旧区间，就会将这期间新写入的不可逆事实彻底从模型视野中“抹除”，导致状态撕裂。
DSH 引入了 `assertStable` 稳定断言机制：在摘要模型返回后、正式提交 `commitCompactionBody` 之前，强制原子比对当前会话事件快照的边界序列号与内容哈希。一旦发现区间被外部并发改动，立即抛弃该摘要并中止事务，宁可保留长历史重试，绝不静默丢失并发事实。

**原理**：
乐观并发控制（OCC，Optimistic Concurrency Control）在上下文管理中的应用。将“摘要生成”视为只读计算，将“历史替换”视为原子事务，在提交点验证前置条件，确保事件溯源状态机的线性一致性。

**追问**：如果智能体调用 Bash 执行了一条命令，打印了 10 万行日志，DSH 是如何防止这一单条工具输出直接打爆整个上下文窗口的？
**应答要点**：通过 `artifact://` Spill 外溢机制。工具执行管线在内容序列化时检测阈值，一旦超标立即将全量内容外溢写入独立物理存储，仅向上下文组装层返回包含首尾几行预览的截断卡片与 URI 定位符（如 `artifact://spill/...`），模型后续若需要查看具体行，可通过行号选择器按需二次读取。


---

<a id="chapter-05"></a>

# 第 5 章｜事实真源：事件溯源、持久化与故障恢复

当智能体在长达半小时的复杂重构任务中连续执行了 30 个步骤后，宿主服务器突然断电，或者 Node.js 进程因宿主系统 OOM 瞬间被杀死。数分钟后服务重新拉起，用户在前端刷新了页面。

此时系统会发生什么？
用户之前的任务是彻底灰飞烟灭，还是能够“原地复活”？那段尚未输出完毕的流式文字能不能回来？在进程崩溃那一瞬间正在执行的命令该如何处理？

在朴素的 Agent 实现中，崩溃意味着灾难——因为绝大多数系统将运行状态保存在易失性的内存对象或关系型数据库的可变行（Mutable Rows）中。而 DeepSeek Harness 能够从容应对任意突发崩溃的底层核心，在于它从第一行代码起就确立的架构哲学：**事件溯源（Event Sourcing）与单一事实源（Single Source of Truth）**。

本章我们将深入 `packages/session/session-persistence-jsonl/`，剖析会话不可变事件的**追加流与物理落盘边界**，解构从事件日志零误差重建状态的**投影机制**，并确立工业级系统的**崩溃恢复与迁移契约**。

---

## 5.1 单一事实源哲学：严格区分面向人机的 Message 与不可变的 Event

在进入持久化细节之前，必须在概念上彻底理清原稿曾反复强调的基石：**消息（Message）**与**事件（Event）**的本质差异。

```
┌────────────────────────────────────────────────────────┐
│ 底层事实源: Append-only Event Stream (不可变事件流)     │
│                                                        │
│  [seq: 0] turn/start        (用户发起业务轮次)          │
│  [seq: 1] user/message      (用户输入真实 Payload)     │
│  [seq: 2] step/start        (驱动器开启第 1 步)         │
│  [seq: 3] tool/call         (模型提议调用 fs_read)      │
│  [seq: 4] tool/result       (磁盘物理返回文件内容)      │
│  [seq: 5] step/end          (第 1 步正常结算)          │
│  [seq: 6] assistant/message (模型最终生成的回答文本)    │
│  [seq: 7] turn/end          (轮次收敛闭合)              │
└───────────────────────────┬────────────────────────────┘
                            │ 投影计算 (Projection)
                            ▼
┌────────────────────────────────────────────────────────┐
│ 表层衍生视图 (Derived Views)                            │
│  ├─► 前端渲染: 聊天气泡 (Chat Bubbles)                 │
│  ├─► 模型上下文: System + User + Assistant 消息数组    │
│  └─► 状态监控: 当前运行轮次、耗时与 Token 统计看板      │
└────────────────────────────────────────────────────────┘
```

- **事件（Event）是系统的物理骨架**：它是系统运行过程中发生的不可逆、不可篡改的**客观事实（Immutable Facts）**。事件由底层严格按递增序列号（`seq: 0, 1, 2...`）原子写入，一旦落盘，任何人（包括智能体自身）都不得修改历史事件。
- **消息（Message）只是事件的动态投影**：前端看到的聊天框、模型下一次看到的上下文历史，都不是直接持久化的数据表，而是由只读投影引擎（Projection Engine）扫描事件流后**动态计算生成的中间产物**。

这种设计的巨大优势在于：**无论前端界面如何改版、无论大模型的 Prompt 格式如何演进，底层的事件日志永远保持客观纯净**。系统随时可以从 `seq: 0` 开始重新重放，零误差还原任意历史时刻的完整世界状态。

---

## 5.2 JSONL 存储引擎实现：enqueueLive 内存流与 session/flush 刷盘边界

在 DSH 基准版本中，默认且最高性能的持久化引擎由 `packages/session/session-persistence-jsonl/` 提供。很多初学者误以为调用了 `session.append(...)` 数据就立即安全写到了硬盘上。查阅源码即可发现，事实远非如此简单。

### 5.2.1 性能与安全的权衡：写缓冲区 `enqueueLive`

由于智能体运行过程中事件触发极其频繁（每一步都可能产生数条事件），如果每次发射事件都直接触发操作系统级的同步 `fsync`，磁盘 I/O 延迟将彻底摧毁系统的吞吐能力。

我们精读 `source/packages/session/session-persistence-jsonl/src/storage.ts` 第 534–547 行的核心实现：

```typescript
// 真实源码摘录：source/packages/session/session-persistence-jsonl/src/storage.ts 第 534-547 行
install(ctx: Context): void {
  // 1. 监听全局会话事件：非阻塞推入内存队列
  ctx.on('session/event', (session: Session, event) => {
    this.writers.get(session.id)?.enqueueLive(event, (error) => {
      ctx.logger.warn(`session-persistence: background write for session "${session.id}" failed: ${String(error)}`)
    })
  })

  // 2. 监听落盘等待信号：真正的持久化安全边界
  ctx.on('session/flush', (session: Session) => {
    const writer = this.writers.get(session.id)
    if (writer === null || writer === undefined) return undefined
    return (async () => {
      // 第一阶段：排空内存中所有尚未完成写入的流数据
      await writer.drainLive()
      // 第二阶段：调用操作系统底层 flush，确保物理落盘
      await writer.flush()
    })()
  })
}
```

### 5.2.2 关键工程分界：`append` 返回不等于物理落盘

从源码中可以清晰提炼出写入的两阶段分界：
1. **内存暂存阶段**：`session.append(...)` 发射 `session/event`，持久化写句柄（`JsonlSessionHandle`）通过 `enqueueLive` 将事件推入内存的 `buffered` 数组。此时方法立即同步返回，主业务流程绝不阻塞等待磁盘 I/O。
2. **物理强制刷盘阶段**：只有当外部触发了 `ctx.emit('session/flush', session)` 时，系统才依次执行 `await writer.drainLive()`（等待正在执行的文件流操作结算）并调用底层 `await writer.flush()`（将操作系统页缓存强制刷入物理扇区）。

这一机制明确告诉我们：**`session.append` 的成功返回仅仅代表事件进入了运行时的派发流，只有 `session/flush` 得到兑现后，才标志着该事件具有了绝对的抗断电、抗崩溃安全性**。

---

## 5.3 崩溃与恢复契约：进程崩溃后什么能回来、什么必须丢弃

现在我们可以精确回答本章开头提出的工程命题：**长任务跑到一半进程突然崩溃，用户刷新页面，哪些东西能恢复，哪些永远回不来？**

根据 DSH 的事件溯源契约，系统划分了不可动摇的边界：

### 5.3.1 确定能回来的资产（越过持久化边界的事实）
1. **已提交的会话消息与结构**：所有在崩溃前已经触发 `flush` 并落盘的 `user/message`、`assistant/message` 以及工具调用与结果。
2. **上下文压缩与替换事实**：已经完成并落盘的 `compaction/end` 记录，恢复时直接呈现瘦身后的视图。
3. **已闭合的审批审计记录**：所有成对闭合的 `approval/asked` 与 `approval/decided` 事实。
4. **派生投影状态**：标题、累计 Token 用量、任务总步数均可从完整的事件流重放重新计算。

### 5.3.2 绝对不能回来的数据（未结算的易失性瞬态）
1. **途中正在传输的大模型流式文字（In-flight Streaming Chunks）**：大模型生成到一半、尚未结算为完整 `assistant/message` 的中间字符，随着内存销毁彻底消失。**系统绝不会在恢复时凭空伪造半段截断的回复**。
2. **操作系统的 PTY 终端交互状态**：在宿主中运行的实时 Bash 子进程随着宿主崩溃已经死亡，其虚拟终端的屏幕光标、正在运行的非持久进程无法凭空复活。
3. **未落盘的内存缓冲（Unflushed Buffer）**：在极短的微秒级窗口内尚未越过 `drainLive` 的内存暂存事件。

---

## 5.4 贯穿案例推进：模拟突发崩溃与事件重放修复

现在，我们跟随贯穿案例，推演系统在面临严重崩溃时的自愈过程：

1. **崩溃发生现场**：
   - 智能体在第 2 步中刚刚通过工具读取了 `src/utils/path.ts`，正准备向模型发出第 2 次推理请求以生成修复补丁；
   - 此时，测试脚本执行了 `kill -9`，宿主 Node.js 进程瞬间湮灭。
2. **磁盘状态审视**：
   - 查看项目 `.dsh/sessions/sess-path-001.jsonl`：
     ```json
     {"seq":0,"type":"turn/start","data":{"turn":1}}
     {"seq":1,"type":"user/message","data":{"source":{"kind":"user","rpcId":"req-path-fix-001"},"content":[{"type":"text","text":"排查并修复仓库中跨平台路径反斜杠兼容性缺陷..."}]}}
     {"seq":2,"type":"step/start","data":{"step":1}}
     {"seq":3,"type":"tool/call","data":{"name":"fs_read","callId":"call_01","arguments":{"path":"src/utils/path.ts"}}}
     {"seq":4,"type":"tool/result","data":{"callId":"call_01","content":[{"type":"text","text":"export function normalize(p) { return p.replace(/\\\\/g, '/'); }"}]}}
     {"seq":5,"type":"step/end","data":{"step":1}}
     ```
   - 事件日志精准停留在 `seq: 5`（`Step 1` 正常结算）。
3. **重启与重放恢复（Replay & Repair）**：
   - 宿主服务重新拉起，用户在前端点击该会话；
   - `SessionStore` 读取该 JSONL 文件，由 `SessionRepair` 检测尾部边界：发现 `turn/start` 处于未闭合状态（缺失 `turn/end`）；
   - 系统安全地将状态定位在最近的合法步骤边界（`Step 1` 已完成，材料已在历史中）；
   - 驱动器并不重复去读取文件，而是直接以已落盘的 `tool_result` 为基础，无缝唤起大模型，发起针对 `Step 2` 的修复推导。

---

## 5.5 本章小结

1. **单一事实源**：系统一切状态皆派生自不可变的 JSONL 事件日志。事件是唯一的客观物理真源，消息与气泡均是视图投影。
2. **刷盘分水岭**：`session.append()` 仅完成内存写缓冲（`enqueueLive`），只有 `session/flush` 驱动的 `drainLive()` 与物理 `flush()` 才是抗崩溃的绝对安全线。
3. **恢复哲学**：只有越过落盘边界的事实才能被恢复。内存中未结算的流式碎片应当被果断丢弃，绝不可凭空捏造历史。

---

## 本章面试问答

### Q1 · 面试官：如果智能体在运行中途服务突然崩溃，用户刷新页面后，为什么那半截正在打印的打字机流式文字（Streaming Chunks）没有恢复出来？

**回答**：
这是由 DSH 的**事件溯源与落盘边界契约**决定的。
大模型流式输出的每个 Token 切片属于易失性的传输瞬态（Transient State），并非不可变的会话事实；只有当模型输出完整结束、或发生可重试错误时，系统才会将其封装为一条正式的 `assistant/message` 或错误事件并触发 `flush` 落盘。
在进程崩溃时，未结算的流式片段从未越过持久化边界。事件溯源架构要求“磁盘上的事实序列是系统唯一真源”，任何恢复都必须基于严谨落盘的历史前缀重建。如果系统尝试凭空拼接或猜测恢复半截残缺的流式片段，等于向不可变历史中注入了未经验证的脏数据，将破坏整个状态机的确定性。

**原理**：
分布式系统与事件溯源中的“提交点（Commit Point）”原则。未提交的在途数据在系统崩溃后一律执行回滚丢弃，唯有已提交的不可变日志才具有持久性保证。

**追问**：如果在崩溃那一瞬间，一个外部工具已经修改了本地磁盘上的文件，但在 JSONL 里还没来得及记录 `tool/result`，系统重启后会如何处理？
**应答要点**：此时在事件日志中表现为该工具调用未正常闭合（只有 `tool/call` 而无配对结果）。系统重启后，修复引擎（Repair）会检测到悬挂的工具调用，根据不变量规则，为其合成一条标记为中断失败的 `tool_result`（如 `INTERRUPTED_BY_CRASH`），迫使模型在下一次推理时重新审视当前工作区状态，防止模型误以为物理调用未曾发生。


---

<a id="chapter-06"></a>

# 第 6 章｜工具执行管线：准入、单调守卫与审批流

当大语言模型在推理步骤中输出一段结构化的工具调用提议（Tool Call），例如提议调用 `fs_write` 修改文件，或者提议调用 `shell_exec` 执行清理命令时，框架面临着整个系统最核心的安全防线：**如何确保模型的提议绝对不会越界破坏宿主系统？**

如果框架简单地采用 `eval` 或无条件执行模型返回的 JSON，那么只需一条精巧的提示词注入攻击（Prompt Injection），就能让大模型沦为黑客执行 `rm -rf /` 或窃取私有凭证的提线木偶。

本章我们将深入精读 `packages/core/tools/` 与 `packages/interaction/user-approval/`。我们将解构 DSH 的工具调度总线，剖析 `tools/pre-execute` 瀑布门禁、**`ToolGuard` 单调守卫的不可逆拒绝设计**，以及人工权限审批中 **`approval/asked` 与 `approval/decided` 的强轮次闭合约束**。

---

## 6.1 提议与落地解耦：从模型 Tool Call 结构到物理执行管线

在工程设计上，很多初学者最常犯的错误，就是将“大模型输出工具调用”等同于“工具已经执行”。

在 DSH 中，大模型永远处于**提议方（Proposer）**的地位，它所产生的一切输出在通过安全管线前，仅仅是一串无害的文本。只有通过了层层防御筛选，提议才会被赋予物理执行的权力。

```
大模型输出 Tool Call 提议: { name: "shell_exec", args: { cmd: "rm -rf tmp/" } }
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 工具执行管线 (Tool Execution Pipeline)                      │
│                                                             │
│  [第一道防线: 静态参数校验]                                  │
│   Schema.validate(args) ──► 校验类型与必需字段               │
│                                                             │
│  [第二道防线: 可扩展准入门禁 (Pre-execute Waterfall)]         │
│   tools/pre-execute ──► allow / deny / ask / cancel         │
│                           │                                 │
│                           ▼ 若返回 'ask'                    │
│                 ┌──────────────────────┐                    │
│                 │ 人工权限审批服务     │                    │
│                 │ approval.request()   │                    │
│                 │ (写入 asked & decided)│                    │
│                 └──────────┬───────────┘                    │
│                            │                                │
│                            ▼ 若审批允许                     │
│  [第三道防线: 单调同步守卫 (Monotonic ToolGuard)]            │
│   ctx.tools.guard(exec) ──► 一票否决权 (不可逆转为允许)      │
│                                                             │
│  [第四道防线: 环绕分发与沙箱执行 (Dispatch & Sandbox)]       │
│   tools/execute ──► 超时包装、读写沙箱边界限制、物理 I/O     │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
           生成不可变 tool/result 并回填会话
```

---

## 6.2 可扩展准入门禁：tools/pre-execute 瀑布事件的四种裁决

当工具调用通过了静态 Schema 校验后，进入第一道动态防御：`tools/pre-execute` 瀑布流（Waterfall）。

在 `source/packages/core/tools/src/index.ts` 中，瀑布流允许系统内安装的各类策略插件对本次调用发表意见。每个监听器都可以返回以下四种裁决之一（`PreToolDecision`）：

1. **`allow`（允许）**：该策略认为当前调用安全合规，放行给下一个中间件；
2. **`deny`（拒绝）**：该策略判定当前调用违规（例如试图读取禁止访问的 `.env` 敏感文件），直接阻断执行，并向模型回填结构化错误原因；
3. **`ask`（需要确认）**：该策略判定当前调用属于中高危操作，必须暂停执行并向人类用户发起权限审批；
4. **`cancel`（取消）**：该调用已被外部信号或任务取消指令主动放弃。

---

## 6.3 权限不可逆保证：ToolGuard 单调守卫的数学安全性设计

在支持复杂插件机制的系统中，存在一个极其危险的权限漏洞风险：**监听器重排导致的权限穿透**。

设想如下情况：安全插件 A 检查参数后判定危险，返回了 `deny`；但随后挂载的一个非受信任的第三方插件 B，因为配置粗心或恶意逻辑，在后面的中间件链条中强行返回了 `allow`，从而将原本被拒绝的危险命令放行执行！

为了彻底杜绝此类漏洞，DSH 在 `source/packages/core/tools/src/index.ts` 中引入了一个在类型和算法上都极其精巧的设计——**单调守卫（Monotonic ToolGuard）**。

### 6.3.1 源码精读：`ToolGuard` 类型与单调判定

我们直接查阅 `source/packages/core/tools/src/index.ts` 第 723–731 行的真实源码：

```typescript
// 真实源码摘录：source/packages/core/tools/src/index.ts 第 723-731 行
/**
 * A monotonic execution guard evaluated after every `tools/pre-execute`
 * listener and before the tool body. Returning a reason denies the call;
 * returning `undefined` leaves it unchanged. Because guards have no allow
 * result, listener ordering cannot turn a denial back into permission.
 * @param execution - the identity-protected call after extensible pre-execute policy completed.
 * @returns a final denial reason, or `undefined` to leave the call allowed.
 */
export type ToolGuard = (execution: Readonly<ToolExecution>) => string | undefined
```

请仔细观察 `ToolGuard` 的函数签名：它的返回值类型只能是 `string | undefined`：
- 若返回 `string`：代表**坚决拒绝（Denial Reason）**；
- 若返回 `undefined`：代表**无意见，保持现状**。

**`ToolGuard` 压根没有定义诸如 `true`、`"allow"` 这样的返回值！**

这在数学上构成了一个**单调不增的权限状态机**：Guard 只能执行“单向扣动扳机”的拒绝操作。一旦链条中任何一个 Guard 判定不通过并返回了拒绝理由，后续没有任何 Guard 或插件能够“宣布放行”。这种单调性设计从根本上消除了插件执行顺序不同引发的安全绕过风险。

---

## 6.4 人机协作闭环：approval/asked 与 decided 的强制轮次内成对闭合

当准入门禁裁决为 `ask` 时，控制权移交给用户审批服务（`packages/interaction/user-approval/`）。

很多系统在做审批时，仅仅是在内存中 `await confirm()`。而 DSH 秉持事件溯源与不可变审计的设计，将审批过程提升为**受严格不变量约束的审计事件对（Audit Event Pair）**。

### 6.4.1 源码精读：`approval.request` 与成对事件闭合

我们查阅 `source/packages/interaction/user-approval/src/index.ts` 第 218–228 行及 `invariant.ts`：

```typescript
// 真实源码摘录：source/packages/interaction/user-approval/src/index.ts
// 必须在开放轮次内部发起审批，绝不允许在轮次空隙悬挂
if (trace.openTurn === null) {
  throw new Error('approval.request() outside an open turn: the approval/asked + approval/decided audit pair must be turn-enclosed.')
}

const id = ApprovalRequestId(randomUUID())
// 1. 发射审批询问事件（记录谁被问、什么工具、什么参数）
session.append('approval/asked', { id, toolName: req.toolName, ... })

// 2. 等待人类决定（允许一次、拒绝、取消）
const outcome = await this.promptUser(req)

// 3. 必须发射对应且相同 ID 的决定事件
session.append('approval/decided', { id, outcome })
```

在伴生不变式检查器（`invariant.ts`）中，系统对每次事件追加执行实时断言：
1. **轮次封闭性**：`approval/asked` 和 `approval/decided` 必须全部包含在同一个未结束的 `turn/start` 与 `turn/end` 之间；在轮次之外发起审批，系统直接抛出致命错误，防止重载时留下无法对齐的悬挂审计日志。
2. **一一严格对应**：每一个 `approval/decided` 必须在当前打开的待决集合中找到完全一致的 `ApprovalRequestId`，绝不允许伪造孤儿决定。

---

## 6.5 贯穿案例推进：拦截高危指令 `rm -rf tmp/` 的审批与放行

现在，我们跟随贯穿案例，观察工具管线如何在真实环境中防御高危操作：

1. **模型提议清理临时目录**：
   - 在修复完路径兼容性代码后，模型提议清理构建缓存，输出了工具调用：
     ```json
     {
       "tool_name": "shell_exec",
       "arguments": { "command": "rm -rf ./tmp_cache" }
     }
     ```
2. **准入门禁拦截高危命令**：
   - 工具管线调度 `tools/pre-execute` 瀑布流；
   - 内置安全策略插件识别到命令包含强行删除指令 `rm -rf`，匹配高危操作规则，返回 `{ kind: 'ask', reason: '检测到破坏性文件删除指令，需要人工授权' }`。
3. **审计事件落盘与界面提示**：
   - 审批服务生成唯一审计 ID `ask-9812`；
   - 会话原子追加事件 `approval/asked`，前端界面立即弹出醒目的红色确认卡片，向用户展示命令文本与操作风险；
4. **用户授权与闭合**：
   - 用户点击“仅允许本次执行（Allow Once）”；
   - 审批服务原子追加事件 `approval/decided`（`id: "ask-9812", outcome: "allowed-once"`）；
   - 管线通过 `ToolGuard` 校验后，才将命令交给物理沙箱执行；执行完毕后，回填 `tool_result`，驱动器收敛进入下一阶段。

---

## 6.6 本章小结

1. **提议与执行解耦**：大模型只是提议方，所有工具执行必须无条件经过静态校验、准入门禁、单调守卫和物理沙箱的四层安全过滤。
2. **ToolGuard 单调性**：守卫签名限制为 `string | undefined`，只具备一票否决权，杜绝了后置插件逆转拒绝结果的逻辑越权漏洞。
3. **审批审计成对闭合**：`approval/asked` 与 `approval/decided` 构成了严格的审计单元，且必须在开放轮次（Open Turn）内闭合，保证系统历史的可追溯性。

---

## 本章面试问答

### Q1 · 面试官：如果让你为团队设计一个支持插件扩展的 Agent 工具安全体系，如何防止“某个低优先级的第三方插件意外放行了原本被高优先级安全策略拦截的危险命令”？

**回答**：
必须借鉴 DSH 的**单调守卫（Monotonic Guard）**架构设计。
传统的过滤器链（Filter Chain）中，后置中间件如果返回布尔值（如 `return true`），很容易覆盖前置中间件的判定结果。
DSH 将安全分为两个阶段：
第一阶段是可扩展的 `tools/pre-execute` 瀑布流；
而在瀑布流之后、进入物理分发之前，强制经过一道只读的 `ToolGuard`。
在类型定义上，`ToolGuard` 的签名严格约定为 `(exec) => string | undefined`。它只允许返回拒绝原因字符串，或者返回 `undefined` 表示无意见。由于 Guard 根本没有“允许（Allow）”的表示能力，任何一个 Guard 只要扣动扳机返回拒绝，后续无论挂载多少个插件，都绝不可能把系统状态逆转回放行，从而在数学上锁死了权限穿透的可能。

**原理**：
安全策略的“单调收紧（Monotonic Restriction）”原则。在权限管线中，放行权限应作为基线，各级防御策略只具有单向消减权限的权力，严禁赋予后续节点越级提权的机制。

**追问**：审批事件为什么必须强制在轮次（Turn）内成对闭合？如果允许跨轮次审批会有什么隐患？
**应答要点**：如果允许跨轮次审批，一旦系统在等待用户决策时遭遇断电或刷新，未闭合的 `approval/asked` 会变成悬挂在会话历史中的“无头僵尸数据”。在事件重放和审计时，系统无法判定该授权究竟属于哪一次用户任务，极易引发旧授权被错误应用到新任务的重放攻击漏洞。


---

<a id="chapter-07"></a>

# 第 7 章｜编码能力与运行环境：文件 I/O、Shell 与语义检索

在前面的章节中，我们已经完整走通了智能体的中枢调度架构：从 Cordis 微内核装配、收件箱状态机驱动、上下文提示词与技能发现，一直到工具安全准入与单调守卫。

然而，对于一个定位为 **Coding Agent** 的系统而言，中枢调度必须在宿主操作系统上生根落地。大语言模型如何精准修改一个包含数千行代码的文件而绝不引发“覆盖式污染”？当模型需要执行耗时数分钟的单元测试或构建任务时，系统如何管理长时间驻留的 Shell 虚拟终端并捕获退出码？面对跨越上百个文件的大型仓库，模型又如何借助语义检索与 LSP 符号索引定位调用链？

本章我们将深入 `packages/fs/`、`packages/subprocess/` 与代码导航体系，剖析基于**唯一匹配与差异投影的受控文件修改**、**PTY 虚拟终端与异步 Shell 会话**，以及**跨文件语义感知的工程落地**。

---

## 7.1 受控文件系统（tool-fs）：基于唯一匹配与原子替换的安全编辑

在朴素的智能体开发中，最粗糙的文件写入方式是让大模型直接输出整个文件的全部内容，然后直接调用 `fs.writeFile` 覆盖覆盖写入。

这种做法在工业级编码场景下具有毁灭性：
1. **Token 浪费极其严重**：若一个文件有 3,000 行，仅仅修改其中的 1 行代码，模型必须重新生成整整 3,000 行，带来极高的计费成本与漫长的等待延迟；
2. **静默抹除并发改动**：在漫长的全量生成过程中，人类工程师在本地编辑器中微调了另一处代码，模型的盲目覆盖会直接抹杀人类的劳动成果；
3. **幻觉截断灾难**：受大模型最大输出长度（Max Output Tokens）的物理硬限制，长文件写到一半常遭遇截断，导致源代码文件直接损坏。

### 7.1.1 源码精读：`tool-fs` 的 `edit` 精准替换机制

DSH 在 `source/packages/fs/tool-fs/src/edit.ts` 中实现了优雅且严密的原子局部替换。

```typescript
// 真实源码摘录：source/packages/fs/tool-fs/src/edit.ts 第 18-56 行
interface EditInput {
  filePath: string
  oldString: string
  newString: string
  replaceAll: boolean
}

export function parseEditArgs(args: { file_path: string; old_string: string; new_string: string; replace_all?: boolean }): EditInput {
  // 1. 约束校验：路径非空、old_string 非空
  if (args.file_path.trim().length === 0) throw new Error('file_path must be a non-empty string')
  if (args.old_string.length === 0) throw new Error('old_string must be a non-empty string')
  // 2. 杜绝无意义编辑：old_string 与 new_string 必须不同
  if (args.old_string === args.new_string) throw new Error('old_string and new_string must differ')
  
  return {
    filePath: args.file_path,
    oldString: args.old_string,
    newString: args.new_string,
    replaceAll: args.replace_all ?? false,
  }
}
```

### 7.1.2 唯一匹配原则（Unique Match Principle）

在底层执行时，`ctx.fs.editText` 强制遵循**唯一匹配断言**：
- 模型提议修改时，必须提供目标代码的原文本片段（`old_string`）以及替换后的新片段（`new_string`）；
- 框架扫描文件全文：若 `old_string` 在文件中**出现了 0 次**，系统立即报错抛出 `STRING_NOT_FOUND`，提示模型其记忆已陈旧，迫使模型重新读取最新文件；
- 若 `old_string` 在文件中**匹配到多处（> 1 次）**且 `replace_all` 为 `false`，系统立即拒绝并报错 `AMBIGUOUS_MATCH`，防止发生误替换，迫使模型提供包含更多上下文的更长锚点；
- 只有当 `old_string` 在文件中**严格精准匹配唯一一次**时，系统才执行原子级原地替换。

这种设计将修改的 Token 消耗从全量数千行骤降至十几行的局部 Diff，并提供了确定性的抗误修改保证。

---

## 7.2 进程与持久终端（tool-shell）：PTY 状态保持与异步长任务

修改完代码后，智能体必须能够运行编译器或测试用例。

在传统的服务端架构中，执行系统命令往往调用简单的 `child_process.exec()`。但在编码智能体中，这会遭遇以下致命问题：
1. **彩色输出与终端控制符丢失**：编译器输出的 ANSI 颜色、进度条（如 Vite 或 Vitest）在普通 pipe 管道中容易丢失或变成乱码；
2. **交互式卡死**：某些命令中途会等待交互输入（如 `Are you sure? (y/n)`），若没有虚拟终端，进程将无限挂起；
3. **环境与工作区状态丢失**：用户先执行 `cd packages/core`，下一次再执行 `npm test` 时，普通子进程因为每次独立派生，无法保持工作目录与环境变量。

### 7.2.1 PTY 虚拟终端与长命令生命周期

DSH 在 `source/packages/subprocess/` 中集成了真正的伪终端（PTY，Pseudo Terminal）子系统：
- **持久终端会话（Persistent Terminal Session）**：支持维持长期的 Shell 会话，保留 `cwd`、环境变量与历史命令栈；
- **异步日志流式观察**：命令启动后，系统返回唯一的终端会话 ID，支持实时流式广播 stdout/stderr 输出；
- **取消与信号传递**：当用户在界面点击停止时，框架向 PTY 进程组发送 `SIGINT` 或 `SIGTERM`，确保其派生的所有子进程被干净利落地级联终止。

---

## 7.3 跨文件代码感知：LSP 符号跳转与静态引用链

在拥有数百个模块的复杂工程中，仅靠逐个文件猜测路径去阅读代码，效率极低且容易迷失。

DSH 将语言服务器协议（LSP，Language Server Protocol）深度整合为核心服务：
- **跳转到定义（Goto Definition）**：大模型可以通过 `lsp_definition` 工具，精确定位某个函数或类型在磁盘上的绝对声明位置；
- **查找所有引用（Find References）**：在重构公共接口前，主动查询整个工作区有哪些调用方依赖该符号，从而评估改动的影响面。

---

## 7.4 贯穿案例推进：实施代码补丁并执行单元测试验证

现在，我们跟随贯穿案例，见证编码工具链如何在真实环境中完成代码修复：

1. **精准定位缺陷源码**：
   - 智能体通过前文阅读的测试日志，锁定了 `src/utils/path.ts`；
   - 模型先调用 `fs_read` 获取了文件内容，发现了以下有缺陷的代码：
     ```typescript
     // src/utils/path.ts 原始有缺陷片段
     export function buildNormalizedPath(base: string, sub: string): string {
       return `${base}/${sub}`.replace(/\\/g, '/')
     }
     ```
   - 在 Windows 环境下，当 `base` 包含盘符（如 `C:\projects`）时，强制替换为 POSIX 斜杠会导致后续调用 Node 原生 API 时出现断言不一致。

2. **调用 `edit` 实施局部原子补丁**：
   - 模型向工具管线提交 `edit` 工具调用：
     ```json
     {
       "tool_name": "fs_edit",
       "arguments": {
         "file_path": "src/utils/path.ts",
         "old_string": "export function buildNormalizedPath(base: string, sub: string): string {\n  return `${base}/${sub}`.replace(/\\\\/g, '/')\n}",
         "new_string": "export function buildNormalizedPath(base: string, sub: string): string {\n  return path.normalize(path.join(base, sub))\n}"
       }
     }
     ```
   - 框架解析参数，验证 `old_string !== new_string`，在文件中匹配到唯一目标段落，执行原子写回，并生成结构化 Diff 记录。

3. **在 Shell 终端中启动测试验证**：
   - 补丁应用后，模型在终端中启动测试命令：
     ```json
     {
       "tool_name": "shell_exec",
       "arguments": {
         "command": "npx vitest run tests/e2e/path-compat.spec.ts"
       }
     }
     ```
   - PTY 虚拟终端捕获输出流，测试框架报告：
     ```text
     ✓ tests/e2e/path-compat.spec.ts (1 test passed)
     Test Files  1 passed (1)
          Tests  1 passed (1)
       Duration  320ms
     ```
   - 工具管线捕获进程正常退出码 `exitCode: 0`，回填成功的 `tool_result`，智能体收敛进入任务完结总结。

---

## 7.5 本章小结

1. **受控文件修改**：`tool-fs` 的 `edit` 机制放弃了危险的全量重写，确立了基于 `old_string` 的**唯一匹配原则**，兼顾了极致的 Token 经济性与防并发篡改安全性。
2. **PTY 终端与状态保持**：通过集成虚拟终端（PTY），解决了长任务卡死、ANSI 乱码和跨命令环境丢失的问题，为 Coding Agent 提供了与专业工程师完全一致的终端执行环境。
3. **闭环验证哲学**：代码修改必须配对物理测试运行。只有观察到进程退出码 `exitCode === 0`，才能宣告技术修改的真实完成。

---

## 本章面试问答

### Q1 · 面试官：在让大模型修改源代码时，为什么 DSH 坚决不使用“让模型全量输出新文件并覆盖写入”的方案？

**回答**：
全量重写存在三大致命硬伤：
1. **Token 浪费极其严重**：若一个文件包含 2000 行，哪怕只修改一个字符，模型也必须生成完整 2000 行，导致极其高昂的 Token 费用和漫长的端到端延迟；
2. **大模型最大输出长度限制（Max Output Tokens）截断**：一旦源文件过长，模型生成中途触及输出配额硬上限，文件尾部会被直接腰斩，造成源代码物理损毁；
3. **并发覆盖人类修改**：在模型思考生成的十几秒内，本地编辑器如果被修改过其他行，全量写回会静默抹去人类的未提交代码。
DSH 采用基于唯一匹配的局部 `edit` 机制：模型必须提供待替换的 `old_string` 与新代码 `new_string`。框架在底层严格断言 `old_string` 在文件中仅精准出现一次才执行替换，兼顾了成本控制与绝对的防错安全性。

**原理**：
最小权限与精确语义契约。在代码修改中，修改的范围越聚焦、锚点越精确，系统的确定性和可审计性就越高。

**追问**：如果 `old_string` 在文件中匹配到了多次，系统会发生什么？
**应答要点**：在 `replace_all` 为 `false` 的默认情况下，框架会立即抛出 `AMBIGUOUS_MATCH` 异常拒绝执行，并将报错回填给模型，要求模型补充更多上下文代码以提供全局唯一的查找锚点，防止误替换无关代码。


---

<a id="chapter-08"></a>

# 第 8 章｜多端交互与状态同步协议：RPC 命令提交与增量事件流

在构建实际生产可用的 AI 编程智能体时，核心调度中枢通常运行在本地守护进程或远端服务器上，而真正与人类工程师直接打交道的，是 VS Code 插件、Web 控制台或终端 TUI 客户端。

当一个修复任务需要持续运行数分钟，模型连续执行了数十次工具调用并生成了大量文件 Diff 时：
- 前端如何向后端提交任务，并实现毫秒级输入回显（Optimistic Echo）？
- 当网络发生微小抖动、或者用户在移动办公中合上笔记本盖子再次唤醒时，客户端如何做到**无感增量重连（Resilient Reconnect）**，既不全量拉取数万行历史日志，又绝不丢失中间产生的实时事件？
- 面对复杂的多端并发访问（例如 Web 端与 CLI 终端同时挂载在同一个会话上），系统如何保证视图展示的单调性与绝对有序？

本章我们将深入精读 `packages/api/session-controller/`，解构**命令提交（RPC Mutation）与状态观察（Observable Query）的彻底解耦**，剖析**快照（Snapshot）加游标（Cursor）事件增量流协议**，以及客户端确定性合并算法 `mergeOrderedBaseline`。

---

## 8.1 架构解耦：命令提交（RPC）与事件增量订阅（Reactive Stream）的读写分离

在传统的 Web 开发中，最简单的 API 往往采用 Request-Response 模式：客户端发起 `POST /api/chat`，然后在这个长连接 HTTP 请求中等待服务端将所有操作执行完毕并一次性返回结果。

对于 Coding Agent 而言，这种模式在工程上是完全不可行的：
1. **连接极度脆弱**：一个涉及读写文件、运行单元测试的任务往往持续数分钟，长连接 HTTP 请求极易受网络中间代理超时（Gateway Timeout 504）或 TCP 拥塞重置影响而中断；
2. **缺乏状态可观测性**：在长达数分钟的等待中，客户端无法得知智能体当前究竟卡在哪个步骤；
3. **多端状态脱节**：如果用户在 VS Code 插件里发起了一个任务，在打开的 Web 浏览器端根本无法感知该任务的存在，更无法协同。

### 8.1.1 CQRS 读写分离架构

DeepSeek Harness 在 `source/packages/api/session-controller/` 中采用了严格的 **CQRS（Command Query Responsibility Segregation，命令查询职责分离）** 架构。

```
┌────────────────────────────────────────────────────────┐
│ 客户端 (Web / VS Code / TUI / Electron)                │
│                                                        │
│  [写通道: 命令式 RPC]       [读通道: 增量反应流]          │
│   SessionCommand.prompt()     Snapshot + Event Stream  │
└────────────┬───────────────────────────▲───────────────┘
             │                           │
  1. 提交任务 │ (无状态短请求)             │ 3. 实时推送不可变事件
  (带有 rpcId)│                           │ (seq: 10, 11, 12...)
             ▼                           │
┌────────────────────────────┐           │
│ SessionCommandController   │           │
│ (命令网关与幂等校验)        │           │
└────────────┬───────────────┘           │
             │                           │
  2. 调度执行 │ 写入事实流                 │
             ▼                           │
┌────────────────────────────────────────┴───────────────┐
│ 底层事实源: Immutable Session Event Log (JSONL)         │
└────────────────────────────────────────────────────────┘
```

- **命令通道（Command Channel）**：采用无状态的短请求 RPC（如 `SessionCommand.prompt`、`SessionCommand.stop`）。客户端提交任务后，服务端仅做参数格式校验与幂等排重，推入会话收件箱（`Inbox`）后便立即返回成功，绝不在该 RPC 请求中阻塞等待大模型推理；
- **查询与观察通道（Query / Reactive Stream）**：客户端通过独立的持久长连接（如 WebSocket 或 Server-Sent Events / SSE）挂载到会话的增量事件总线上。服务端按照事件序列号（`seq`）向客户端单向广播物理事件。

这种彻底的读写解耦，使得客户端的渲染逻辑变成了单纯的“事件驱动投影机”：**界面看到的不是命令的直接返回值，而是不可变事件流在客户端内存中的投影呈现**。

---

## 8.2 快照基线与游标协议：Snapshot + Cursor 断线重连机制

当网络断开重连时，客户端最关心的问题是：**我从哪一步开始补齐数据？**

如果每次重连都全量拉取完整的 JSONL 事件日志，当会话历史达到数万条事件时，序列化、网络传输和客户端反序列化的开销将导致界面严重掉帧甚至白屏。

DSH 制定了清晰的**快照基线与游标增量协议（Snapshot + Cursor Protocol）**：

### 8.2.1 客户端状态机与游标管理

在 `source/packages/api/session-controller/src/client/contract/snapshot.ts` 中，客户端维系着轻量的连接状态：

```typescript
// 真实契约定义：source/packages/api/session-controller/src/client/contract/snapshot.ts
export interface SessionClientState {
  /** 客户端当前已消费并确认的最高物理事件序号 */
  lastObservedSeq: number
  /** 会话打开生命周期状态 */
  openState: 'cold' | 'loading' | 'open' | 'error'
  /** 本地乐观回显数组（未落盘前内存可见） */
  pendingSubmissions: PendingSubmission[]
}
```

1. **初始冷启动（Cold Start）**：
   - 客户端连接服务端，传入 `offset = 0`；
   - 服务端返回会话元数据快照（`SessionSnapshot`），包含会话创建时间、当前轮次信息以及近期的事件切片；
   - 客户端记录已消费的最大事件序列号 `lastObservedSeq = N`。
2. **正常事件流式消费**：
   - 服务端按序下发 `seq: N+1`、`seq: N+2` 的增量事件；
   - 客户端每次收到合法事件，单调递增其本地游标：`lastObservedSeq = event.seq`。
3. **断线与增量补偿（Reconnect & Catch-up）**：
   - 当网络中断数秒后重新握手时，客户端在连接握手包中携带自己的游标参数：`sinceSeq = client.lastObservedSeq`；
   - 服务端直接从持久化底层（`storage.read(offset: sinceSeq + 1)`）只截取该游标之后的增量事件流切片下发；
   - 客户端接收并无缝补齐缺失的空隙，瞬间恢复至实时最新状态，网络传输字节数达到理论极限的最小化。

---

## 8.3 客户端确定性保序算法：mergeOrderedBaseline

在多端并发（例如两个浏览器 Tab 访问同一个会话）或者增量事件切片与本地乐观回显合并时，极易出现列表项乱跳、闪烁或相对顺序错乱的严重 UI 体验问题。

DSH 在 `source/packages/api/session-controller/src/client/ordered-baseline.ts` 中提供了一个极具参考价值的通用合并函数：**`mergeOrderedBaseline`**。

### 8.3.1 源码精读：保持既有顺序的权威合并算法

```typescript
// 真实源码摘录：source/packages/api/session-controller/src/client/ordered-baseline.ts 第 11-43 行
export function mergeOrderedBaseline<T>(
  current: readonly T[],
  baseline: readonly T[],
  keyOf: (value: T) => unknown,
): T[] {
  const baselineByKey = new Map<unknown, T>()
  for (const value of baseline) baselineByKey.set(keyOf(value), value)

  // 1. 保留客户端已有的显示顺序，更新对应项的最新服务端数据
  const merged = current
    .map(value => baselineByKey.get(keyOf(value)))
    .filter((value): value is T => value !== undefined)
  const mergedKeys = new Set(merged.map(keyOf))

  // 2. 将服务端新出现、客户端尚不知晓的项，精准插入到最邻近的已知项之前
  for (let index = 0; index < baseline.length; index++) {
    const value = baseline[index]
    if (value === undefined || mergedKeys.has(keyOf(value))) continue
    let insertion = merged.length
    for (let following = index + 1; following < baseline.length; following++) {
      const candidate = baseline[following]
      if (candidate === undefined) continue
      const known = merged.findIndex(item => keyOf(item) === keyOf(candidate))
      if (known !== -1) {
        insertion = known
        break
      }
    }
    merged.splice(insertion, 0, value)
    mergedKeys.add(keyOf(value))
  }
  return merged
}
```

该算法的工程价值在于：**在服务端权威数据（Baseline）与客户端已渲染顺序（Current）发生差异时，绝对不粗暴重置列表，而是以最小侵入性保持客户端用户视觉焦点的不变性**。

---

## 8.4 贯穿案例推进：前端 Diff 实时卡片渲染与断线重连验证

现在，我们将前几章在服务端执行的跨平台路径修复案例，映射到多端协同的前端体验中：

1. **用户在 Web 端提交任务**：
   - 用户在输入框中按下回车，前端生成客户端请求 ID `req-path-fix-001`；
   - 前端立即在对话流中压入一条 `PendingSubmission`（乐观回显），用户瞬间看到自己的输入气泡，体验零延迟；
   - 客户端调用 `SessionCommand.prompt()` RPC，服务端通过 `hasPromptRequest` 排重并接收入库。
2. **事件流实时投射 Diff 卡片**：
   - 服务端执行到第 7 章的代码修改时，发射事件（`tool/result` 携带 `presentationMeta`，包含标准化的 `FileDiff` 结构）：
     ```json
     {
       "seq": 6,
       "type": "tool/result",
       "data": {
         "callId": "call_edit_01",
         "content": [
           {
             "type": "text",
             "text": "The file src/utils/path.ts has been updated."
           }
         ],
         "meta": {
           "diffs": [
             {
               "path": "src/utils/path.ts",
               "oldText": "export function buildNormalizedPath(base: string, sub: string): string {\n  return `${base}/${sub}`.replace(/\\\\/g, '/')\n}",
               "newText": "export function buildNormalizedPath(base: string, sub: string): string {\n  return path.normalize(path.join(base, sub))\n}"
             }
           ]
         }
       }
     }
     ```
   - 前端增量消费到 `seq: 6`，将该事件动态投影为带有绿色/红色高亮的代码 Diff 卡片，实时呈现给用户。
3. **断线与重连增量补偿**：
   - 在测试命令运行期间，用户合上笔记本电脑屏幕 10 秒；
   - 重新打开时，WebSocket 连接重新建立，前端握手包声明 `sinceSeq: 6`；
   - 服务端仅推送后续产生的 `seq: 7`（测试命令输出）与 `seq: 8`（`turn/end` 轮次结束）；
   - 前端调用 `mergeOrderedBaseline`，在不破坏已有气泡布局的前提下，无缝填入测试成功标记与终结总结。

---

## 8.5 本章小结

1. **读写解耦（CQRS）**：任务提交走轻量无状态短 RPC，状态观察走持久化不可变事件流，消除了长连接任务易超时的工程弊端。
2. **游标断线补偿**：依靠单调递增的物理序列号 `seq`，客户端在重连时只需上报 `sinceSeq` 游标，即可实现高能效的增量修补。
3. **保序平滑合并**：`mergeOrderedBaseline` 算法在权威同步与用户视觉稳定性之间取得了精妙平衡，杜绝了多端同步时的列表跳动与闪烁。

---

## 本章面试问答

### Q1 · 面试官：如果让你设计一个支持 Web、VS Code 插件和 CLI 多端协同的 AI 编码助手，你会如何设计前后端的数据同步协议，以防止网络重连时的性能灾难？

**回答**：
必须放弃传统的“每次重连全量拉取会话详情”方案，采用类似 DSH 的 **CQRS 读写分离 + Snapshot + Cursor（快照与游标）增量流协议**：
1. **写通道**：所有操作（发送消息、停止、审批）均通过带有唯一 `requestId` 的无状态轻量 RPC 提交，服务端只负责准入排重与入库，立即返回 ACK，不阻塞等待长任务完成；
2. **读通道**：多端客户端通过长连接订阅后端的不可变事件流（Event Stream），服务端每一条事件严格携带单调自增的整型序号 `seq`；
3. **断线恢复**：客户端本地维系已消费的最高序号 `lastObservedSeq`。当网络发生抖动或重连时，客户端向服务端发送 `sinceSeq = lastObservedSeq`；服务端仅从持久化文件中切片检索该游标之后的增量事件流推送给前端；
4. **客户端合并**：结合 `mergeOrderedBaseline` 算法，在保持客户端当前已呈现顺序的前提下将服务端权威数据安全织入，兼顾极低的带宽消耗与平滑的 UI 渲染。

**原理**：
分布式系统中的增量日志同步（Log-based Catch-up Replication）与客户端反应式投影（Reactive Projection）。将状态同步的复杂度从粗暴的全量序列化降低为轻量的游标追踪。

**追问**：用户发送消息后，如果立刻等待服务端事件落盘并广播才渲染消息气泡，会有明显的卡顿感，DSH 是如何解决这个首字延迟体验问题的？
**应答要点**：DSH 引入了 `PendingSubmission` 机制（乐观本地回显）。在 RPC 请求刚刚发出的同步瞬间，客户端内存中直接构造一个临时的待决提交对象塞入渲染流水线，前端立即呈现出用户的消息气泡。当后续服务端权威的 `user/message` 事件顺着事件流推送到达时，客户端通过配对的 `requestId` 将乐观占位项原子替换为真实不可变事件，从而实现 0 毫秒的极致输入交互体验。


---

<a id="chapter-09"></a>

# 第 9 章｜评估、度量与确定性回放验证：从 Bad Case 到回归资产

在传统的 Web 服务中，单元测试和集成测试具有极强的确定性：给定输入 $A$，断言输出必定是 $B$。
然而，在基于大语言模型的智能体（Agent）工程中，开发者每天都在遭遇**非确定性（Non-deterministic）的梦魇**：
1. **模型输出的概率漂移**：同一个 Prompt 在温度为 0 时仍可能因服务商底层硬件算子调度产生微小输出差异；
2. **测试成本与耗时失控**：如果在 CI/CD 流水线中每次跑全量回归测试都要真实调用远程的大模型 API，不仅成本极其高昂，单次构建动辄耗时数十分钟甚至数小时，还极易遭遇供应商 API 429 限流或网络抖动；
3. **评估口径混乱**：很多团队对智能体质量的评估停留在主观打分或模糊的“体感”，缺乏精准量化的工程指标。

本章我们将深入精读 `packages/test-support/llm-replay/` 与评估体系，解构智能体工程落地的**四大硬核量化度量口径**，剖析**确定性无模型回放测试体系（Deterministic Replay Testing）**，以及核心断言算法 **`assertConsumed`**。

---

## 9.1 智能体工程的四大硬核度量口径：拒绝玄学“体感”

要想科学改进智能体架构，必须首先建立可统计、可对齐、无歧义的量化评估体系。DSH 在生产实践中确立了四大核心度量维度：

```
┌────────────────────────────────────────────────────────┐
│ 智能体性能与质量评估四维矩阵 (Evaluation Quadrant)      │
├──────────────────────────┬─────────────────────────────┤
│ 1. 任务完结率 (Pass Rate) │ 2. 步骤收敛比 (Step Ratio)   │
│   最终物理单测/Lint 验证   │   实际消耗步数 / 理论最优    │
│   是否 100% 成功通过      │   步数，衡量是否存在无意义   │
│                          │   循环探索与无效试错         │
├──────────────────────────┼─────────────────────────────┤
│ 3. 工具拒识率 (Guard Rate)│ 4. 显存/Token 膨胀率        │
│   高危/违规/格式错误工具  │   (Context Inflation)       │
│   调用在准入阶段被拦截的  │   长任务推进过程中每轮上下文 │
│   百分比 (安全基线)      │   Token 增长斜率与外溢效率   │
└──────────────────────────┴─────────────────────────────┘
```

1. **真实任务完结率（Pass Rate / Ground Truth Verification）**：
   - 拒绝大模型自我评价（“我认为我做完了”），必须以**物理操作系统的确定性验证为唯一准则**（如真实的测试套件退出码 `exitCode === 0` 或编译器零错误）。
2. **步骤收敛比（Step Convergence Ratio）**：
   - 公式：$\text{Step Ratio} = \frac{\text{实际执行 Step 数}}{\text{基准最优 Step 数}}$。
   - 若智能体完成一个任务花费了 25 步，而基准专家轨迹仅需 4 步，说明系统在上层规划、Prompt 引导或工具错误回填时存在严重的“瞎猜乱撞”现象。
3. **工具拒识率与安全审计率（Guard & Denial Rate）**：
   - 统计在任务运行期间，模型生成的工具调用被静态 Schema 拦截、被 `tools/pre-execute` 阻断、或被单调 `ToolGuard` 否决的频次。低拒识率证明系统 Prompt 对工具契约的约束清晰，模型幻觉参数少。
4. **上下文膨胀斜率（Context Inflation Slope）**：
   - 监控任务从 Step 1 推进到 Step N 时，单步输入 Token 的增长曲线。优秀的系统在触发 Compaction 压缩和 Spill 外溢后，斜率应保持平缓收敛，而非无限制指数级爆炸。

---

## 9.2 无模型确定性回放：llm-replay 插件架构与原理

为了在 CI/CD 中以零 API 成本、毫秒级速度运行成百上千个测试场景，DSH 开发了高度精密的 **`llm-replay`** 测试底座。

### 9.2.1 捕获与回放闭环

```
[真实开发/生产环境]
用户输入 ──► 驱动执行 ──► 真实调用 DeepSeek API ──► 生成不可变 JSONL 轨迹
                                                        │
                                                        ▼ (抽取为可复用资产)
[CI/CD 确定性回归测试环境]
JSONL 轨迹 ──► deriveReplayScript() ──► 生成 Replay 脚本 Fixture
                                              │
                                              ▼ (拦截 llm/stream 瀑布流)
新版代码启动 ──► LlmRuntime ──► llm-replay 插件 ──► 毫秒级返回录制好的 Chunks (零外部 API)
                                              │
                                              ▼
                                    assertConsumed() 校验
```

在测试环境中，测试套件并不真正连接远程模型，而是通过 Cordis 插件系统挂载 `installLlmReplay`：
- 它在 `ctx.llm` 的瀑布流（Waterfall）最前端注入一个 Mock 拦截器；
- 真实运行时发起的每一次 `stream()` 调用，都会按照会话 ID（`sessionId`）与调用序号，严格匹配录制脚本中的下一个预设响应（Chunk 序列）；
- 测试耗时从数分钟骤降至 **100 毫秒以内**，彻底消除了网络超时与 API 费用。

---

## 9.3 核心断言算法：assertConsumed 如何杜绝测试“假阳性”

在回放测试中，存在一个极其隐蔽却极度危险的 bug：**测试假阳性（False Positive）**。

例如：原本的复杂任务需要调用 3 次大模型（读代码 → 改代码 → 跑测试）。某次开发者重构了状态机代码，引入了一个静默提前退出的 bug，导致智能体只调用了 1 次模型就草草结束了轮次。
如果测试用例仅仅断言 `expect(agent.status).toBe('idle')`，由于智能体没有报错，测试居然会**显示绿色通过**！

为了彻底杜绝此类测试虚假通过，DSH 在 `source/packages/test-support/llm-replay/src/index.ts` 中设计了极其严格的断言工具：**`assertConsumed`**。

### 9.3.1 源码精读：`assertConsumed` 校验逻辑

我们精读 `source/packages/test-support/llm-replay/src/index.ts` 第 1106–1118 行的真实源码：

```typescript
// 真实源码摘录：source/packages/test-support/llm-replay/src/index.ts 第 1106-1118 行
dispose,
assertConsumed(): void {
  const problems: string[] = []
  
  // 1. 检查录制的脚本是否全部被活体会话认领绑定
  if (nextScript < scripts.length) {
    problems.push(`${scripts.length - nextScript} recorded script(s) never bound to a live session`)
  }
  
  // 2. 检查每个会话内部预设的模型调用是否被完全且精准消费完毕
  for (const session of boundSessions.values()) {
    if (session.nextCall < session.script.calls.length) {
      problems.push(
        `session "${session.id}" live-underrun: consumed ${session.nextCall}/${session.script.calls.length} recorded calls`,
      )
    }
  }

  // 3. 存在任何欠消费 (Underrun) 立即抛出明确异常，判测试失败
  if (problems.length > 0) {
    throw new Error(`LLM replay script was not fully consumed:\n- ${problems.join('\n- ')}`)
  }
}
```

`assertConsumed` 确立了铁一般的契约：
- **欠消费立即报错（Live-underrun Error）**：如果录制了 3 次调用，实际只执行了 2 次，报错形如 `consumed 2/3 recorded calls`，明确指出哪一次调用被静默遗漏；
- **会话悬挂报错**：如果有录制好的脚本文件从未被任何子会话认领，立即判定场景驱动的会话拓扑与基准不符。

---

## 9.4 贯穿案例推进：将跨平台修复沉淀为不可变回归测试资产

现在，我们把第 1 到第 8 章历经千锤百炼跑通的“跨平台路径修复”案例，固化为一套永久的回归测试资产：

1. **生产轨迹提取**：
   - 取出已完成的 `.dsh/sessions/sess-path-001.jsonl` 文件；
   - 调用工具脚本 `deriveReplayScript(jsonlPath)`，自动解析事件流中的 `turn/start`、`step/start` 以及对应的模型请求和响应块，剔除动态时间戳与易失字段，生成确定性的测试脚本 `tests/fixtures/path-fix.replay.json`。
2. **编写确定性回归测试用例**：
   ```typescript
   // 真实项目级回归测试示范
   it('regression: fix cross-platform path bug deterministically', async () => {
     const ctx = new Context()
     // 1. 安装微内核与 LLM 回放插件
     const replayHandle = await installLlmReplay(ctx, {
       fixturePath: 'tests/fixtures/path-fix.replay.json'
     })
     
     // 2. 派发与当年线上完全相同的输入任务
     const session = await ctx.agent.createSession()
     await session.prompt('排查并修复仓库中跨平台路径反斜杠兼容性缺陷')
     
     // 3. 核心断言：断言模型调用被 100% 精准消费，不多也不少
     replayHandle.assertConsumed()
     
     // 4. 物理断言：断言代码文件被正确修改
     const fileContent = await readFileSync('src/utils/path.ts', 'utf8')
     expect(fileContent).toContain('path.normalize')
   })
   ```
3. **CI/CD 流水线效益**：
   - 该测试在单核 GitHub Actions 节点上运行仅耗时 **85 毫秒**；
   - 以后任何工程师在重构微内核调度、修改收件箱状态机或重写 Prompt 装配逻辑时，一旦意外破坏了现有的修复调用链，该测试将在 1 秒内精准红灯阻断合入！

---

## 9.5 本章小结

1. **客观度量口径**：智能体评估必须建立在以物理运行结果（ExitCode、Pass Rate）、收敛比和 Token 膨胀斜率为核心的四大硬核指标上，杜绝玄学主观打分。
2. **确定性回放架构**：通过 `llm-replay` 将真实的不可变 JSONL 轨迹转换为无模型的测试脚本，消除了回归测试的网络不稳定性与高昂 API 费用。
3. **`assertConsumed` 严密防线**：通过对脚本认领和调用次数的完整性校验，彻底消除了智能体测试中“静默少走步骤却假阳性通过”的重大隐患。

---

## 本章面试问答

### Q1 · 面试官：大模型输出具有天然的随机性与概率漂移，你们是如何在 CI/CD 流水线中对智能体系统做高可靠、低成本的自动化回归测试的？

**回答**：
我们坚决不在 CI/CD 中直接调用真实的外部大模型 API，而是借鉴 DSH 的 **`llm-replay` 确定性录制回放与 `assertConsumed` 严格断言体系**：
1. **真实轨迹录制**：在本地开发或排错时，将成功解决复杂 Bug 的真实运行日志（不可变 JSONL）通过脚本转换为结构化的 Replay Fixture；
2. **流水线无模型回放**：在 CI 环境下，使用 Cordis 插件向框架注入 `llm-replay` 中间件，拦截底层 `llm/stream` 瀑布流。当框架发起推理请求时，回放器毫秒级回填预录制好的响应切片，完全脱离外部网络，单用例执行耗时从数分钟降至几十毫秒；
3. **防假阳性断言**：在测试用例退出（Teardown）阶段，强制调用 `assertConsumed()`。它会精确比对录制的调用次数与实际发生次数，如果智能体由于代码 bug 发生了少调用（Underrun）或多调用（Overrun），断言立即报错红灯，彻底杜绝了静默提前退出却误判测试通过的“假阳性”缺陷。

**原理**：
自动化测试中的契约模拟（Contract Virtualization）与完整性断言。通过固定外部随机依赖的物理边界，将大语言模型的概率黑盒转化为具备 100% 确定性的白盒状态机测试。

**追问**：如果智能体代码重构后，Prompt 的微小措辞变了，回放测试会不会全部崩溃报废？
**应答要点**：DSH 的回放解析器支持模式匹配与动态占位符注入（例如 `{{fromRequest:<regex>}}`）。对于系统 Prompt 中包含的动态时间戳、易失性 RPC ID 等字段，回放脚本会将其参数化并抽取为上下文模式，使得回放测试在校验核心逻辑流（如工具调用序列和业务收敛）的同时，具备对无关文本微调的容忍度。


---

<a id="chapter-10"></a>

# 第 10 章｜多智能体协作：会话分支 Fork、团队编排与冲突防御

在单智能体（Single Agent）架构中，所有的规划、编码、测试和文档生成都由同一个 Agent 在一个连续的上下文主干中串行执行。
然而，当工程任务的规模与复杂度上升到一定层级时，单智能体架构将不可避免地撞上物理墙壁：
1. **上下文窗口与注意力极限**：当多模块重构任务产生数万行阅读代码与数百行测试输出时，单一上下文不仅成本激增，模型的注意力机制（Needle in a Haystack）也极易发生退化，导致前后逻辑自相矛盾；
2. **串行执行效率低下**：在面对“主分支继续推进核心业务重构，同时需要另一个子任务去探查多平台环境兼容性并编写测试套件”时，串行排队将成倍延长交付等待时间；
3. **实验性探索的污染风险**：开发者常常希望智能体尝试一种激进的重构方案，如果失败了能够干净利落地回滚，而不希望失败的试错代码和无效报错永远污染主干历史。

为了攻克这些瓶颈，智能体系统必须演进到**多智能体（Multi-Agent）与会话分支（Session Fork）**的高阶协同体系。

本章我们将深入精读 `packages/core/session/src/fork.ts` 与多代理编排体系，解构会话分叉的物理底层机制 **`buildForkSeed`**，剖析基于**信箱（Mailbox）机制的异步通信**，以及多代理协作中必须筑起的**上下文膨胀与死锁防御墙**。

---

## 10.1 会话分支的物理底层：buildForkSeed 源码解密与断口修补

在操作系统中，`fork()` 系统调用通过 Copy-On-Write 机制复制当前进程地址空间；在 Git 中，分支创建是在特定 Commit 节点打上指针。

而在以**不可变追加事件流（Append-only Event Log）**为核心的 DSH 中，创建一个全新的子会话或实验分支，底层究竟发生了什么？

### 10.1.1 源码精读：`buildForkSeed` 算法

我们精读 `source/packages/core/session/src/fork.ts` 第 21–30 行的核心实现：

```typescript
// 真实源码摘录：source/packages/core/session/src/fork.ts 第 21-30 行
export function buildForkSeed(events: readonly SessionEvent[], boundary: SessionSeqType): SessionEvent[] {
  // 1. 严格切取父会话从 seq: 0 到 boundary 的事件前缀
  const prefix = events.slice(0, boundary + 1)
  
  // 2. 注入法定继承标记事件: session/end-seed
  prefix.push({
    type: 'session/end-seed',
    seq: SessionSeq(boundary + 1),
    time: events[boundary]!.time,
    data: { inherited: true },
  })
  
  // 3. 运行修补逻辑: 为断口处可能悬挂的打开步骤/轮次合成伪闭合事件
  return prefix.concat(openTurnClosers(prefix, { kind: 'forked' }))
}
```

### 10.1.2 断口状态的合成修补（Synthetic Tail Patching）

这段代码揭示了 DSH 在事件工程上的极高严谨性：
1. **法定继承边界（Inherited Cut）**：父会话的历史在 `boundary` 处被干净截断，紧接着被盖上戳记 `session/end-seed`。从这一刻起，子会话拥有了与父会话完全隔离的独立生命周期，后续子会话产生的任何新事件，其序列号将从 `boundary + 2` 开始独立累加，父子互不干扰；
2. **悬挂步骤自动修补（`openTurnClosers`）**：如果在分叉的那一瞬间，父会话刚好处于某个打开的 Step（例如父会话刚发出了一个工具调用提议，尚未收到结果），直接复制会导致子会话的历史处于未闭合的非法状态！
   `openTurnClosers(prefix, { kind: 'forked' })` 会自动扫描断口：若发现悬挂的 `tool/call`，它会为子会话合成一条标记为 `{ kind: 'forked' }` 的人工 `tool_result`，并紧随其后生成 `step/end` 与 `turn/end`。
   这样一来，子会话在诞生的第一毫秒，其历史就满足了**结构完整性不变量（Structural Invariant）**，智能体驱动器可以在一个确定且干净的基座上立即开启新的轮次。

---

## 10.2 多代理协作通信模式：严格限制直接状态侵入的 Mailbox 机制

当主智能体（Parent Agent）派生出专门负责单元测试的子智能体（Tester Agent）后，它们之间该如何通信？

很多初学者容易采用“共享内存”的方式：让子 Agent 直接读取甚至修改父 Agent 的上下文数组。这种做法在多 Agent 协同中是绝对的灾难——它会迅速引发**竞态条件（Race Conditions）**与上下文严重污染。

DSH 确立了基于 **Mailbox（信箱）** 的离散消息通信拓扑：

```
┌────────────────────────────────────────────────────────┐
│ 主协调智能体 (Parent Coordinator Agent)                 │
│  - 拥有主干会话历史 (Master Session Log)               │
│  - 下发结构化委托任务                                   │
└────────────┬───────────────────────────▲───────────────┘
             │                           │
  1. 派生并投递任务 (Delegate)            │ 3. 收信并整合成果 (Report)
  (带有明确边界与预期 Schema)              │ (结构化汇报，过滤冗长中间过程)
             ▼                           │
┌────────────────────────────────────────┴───────────────┐
│ 子智能体信箱队列 (Child Subagent Mailbox)               │
└────────────────────────────┬───────────────────────────┘
                             │
                  2. 独立沙箱中执行思考与工具调用
                             ▼
┌────────────────────────────────────────────────────────┐
│ 专业子智能体 (Specialized Subagent, 如 Tester/Doc)       │
│  - 拥有完全隔离的独立分支会话 (Forked Session Log)      │
│  - 疯狂试错、产生上百步测试与阅读日志 (不污染主干)      │
└────────────────────────────────────────────────────────┘
```

- **隔离性**：子 Agent 运行在自己独立的沙箱与分叉会话中，它在探查过程中产生的大量临时文件读取、编译报错和试错日志，全部留在子会话日志里；
- **汇聚性**：子 Agent 完工后，通过信箱向主 Agent 回复一份高度提炼的**结构化报告（Structured Deliverable）**。主 Agent 只需消费最终报告，即可将外部协作成果纳入主线，主干上下文保持极高密度与纯净度。

---

## 10.3 协同并发防御：上下文倍增成本控制与死锁防范

引入多智能体协同并不是免费的午餐，在工程落地时必须时刻警惕两大风险：

### 10.3.1 上下文与 Token 倍增陷阱（Context Explosion）
- 如果盲目为每个细小任务都 Fork 一个完整会话，由于每个子 Agent 都继承了父会话的历史前缀，系统并发调用大模型的 Token 消耗将呈倍数级爆炸；
- **防御准则**：在创建子会话时，应当结合第 4 章的压缩机制。如果子任务仅关注局部模块，系统应在 Fork 前对历史前缀执行**定向瘦身（Projection Pruning）**，仅将与子任务相关的上下文切片传递给子智能体。

### 10.3.2 循环等待与死锁防范（Deadlock Prevention）
- 严禁设计 Agent A 等待 Agent B 的结果、而 Agent B 又反向等待 Agent A 授权的“双向同步阻塞等待”拓扑；
- **防御准则**：在调度层面强制要求**有向无环图（DAG，Directed Acyclic Graph）**的单向通信流；对于跨代理的消息投递，强制设定超时（Timeout）与自动降级熔断机制。

---

## 10.4 贯穿案例推进：分叉派生多平台兼容性测试子智能体

现在，我们将贯穿案例推向多 Agent 协同的高潮：

1. **主智能体发起协同委托**：
   - 主智能体在完成了 `src/utils/path.ts` 的核心逻辑修复后，需要验证该修复在 Linux、macOS 和 Windows 混合路径下的极端边界兼容性，并生成补充测试用例；
   - 为了防止测试编写的反复试错污染主会话历史，主智能体提议启动一个专门的 `compat-tester` 子智能体。
2. **执行 `buildForkSeed` 建立隔离分支**：
   - 框架截取当前会话至 `seq: 8` 的事件前缀，调用 `buildForkSeed`；
   - 自动注入 `session/end-seed` 并修补尾部，生成 ID 为 `sess-path-child-tester` 的独立子会话；
3. **子智能体在隔离分支中完成验证**：
   - 子智能体在自己的分叉会话中连续执行了 6 个 Step：尝试了包含盘符冒号、UNC 共享路径、相对路径嵌套等 8 种极端测试用例；
   - 在这个过程中产生了一次语法报错并由子 Agent 自行修正；
   - 子智能体收敛，生成测试全部通过的最终总结。
4. **主干信箱接收报告并闭环合入**：
   - 子智能体将提炼后的有效测试用例文件 `tests/e2e/path-compat-matrix.spec.ts` 作为交付物投递回主智能体的 Mailbox；
   - 主智能体接纳成果，在主干会话中向用户宣布：“路径反斜杠兼容性缺陷已修复，且多平台矩阵极端用例已由子智能体验证完毕，测试 100% 通过！”
   - 全书业务案例至此迎来最终圆满收敛。

---

## 10.5 本章小结

1. **`buildForkSeed` 分支基石**：会话分叉不是指针浅复制，而是通过 `session/end-seed` 确立继承边界，并通过 `openTurnClosers` 强制修补断口悬挂步骤，确保子会话历史不变量。
2. **Mailbox 离散通信**：多 Agent 协作拒绝共享内存污染，主子智能体通过结构化信箱进行单向任务委托与成果汇报。
3. **协同工程红线**：必须时刻防范历史全量继承带来的 Token 爆炸，并通过有向无环拓扑与超时机制杜绝代理间死锁。

---

## 本章面试问答

### Q1 · 面试官：在基于事件溯源（Event Sourcing）的系统中，如果让你实现会话的 Fork（分支创建），在数据结构和状态机上有哪些关键的边界问题必须处理？

**回答**：
必须解决两大核心问题：**继承切片隔离性**与**断口状态机闭合性**（正如 DSH 中的 `buildForkSeed` 实现）：
1. **继承边界切断**：子会话截取父会话从 `0` 到指定 `boundary` 的不可变事件前缀后，必须在尾部追加一条法定分界标记（如 `session/end-seed`）。后续子会话产生的任何新事件，必须从 `boundary + 2` 起使用全新独立的序列号，保证父子两条事件流物理隔离，子会话的后续写入绝不污染或回溯父会话；
2. **悬挂步骤（In-flight Turn/Step）的伪闭合修补**：分叉操作可能发生在父会话的任意时刻。如果在分叉瞬间，父会话刚好发起了一个工具调用尚未返回结果（悬挂的 `tool/call`），若直接切断，子会话的历史就会违背“调用与结果必须成对出现”的强不变量。系统必须在断口处合成一条具有特定语义（如 `{ kind: 'forked' }`）的假 `tool_result`，并紧随补齐 `step/end` 与 `turn/end`，确保子会话拥有一个合法的状态机起点。

**原理**：
日志分叉中的因果一致性（Causal Consistency）与状态机结构完整性校验。分叉不是粗暴的截取，而是建立在新合法基线上的确定性生命周期演进。

**追问**：多 Agent 协作时，很多团队发现随着子 Agent 数量增多，Token 费用不仅没有减少，反而成倍激增，且各个 Agent 之间容易发生死锁，如何从架构上进行防御？
**应答要点**：
- **Token 激增防御**：子 Agent Fork 父会话时绝不能盲目继承全部冗长历史，必须结合上下文压缩与视野投影，只将与子任务相关的上下文切片注入子 Agent；
- **死锁防御**：通信架构必须遵循单向的有向无环图（DAG），子 Agent 只能通过离散的 Mailbox 向主 Agent 异步汇报提炼后的结构化结果，严禁出现 Agent 之间互等对方状态释放的双向阻塞拓扑，并对所有跨代理交互强制配置超时降级熔断。


---

<a id="chapter-11"></a>

# 专题章｜时空可组合性与 Cordis 原理：DeepSeek Harness 微内核的理论奠基

> **学术溯源**：本章基于 DeepSeek-AI 与北京大学研究团队发表的核心理论论文：  
> 《A Programming Paradigm for Spatiotemporal Composability》（Shi, Zhang, Cui, 2026，arXiv:2608.25512 [cs.PL]）。  
> 该论文奠定了 DeepSeek Harness 底层微内核 `vendor/cordis` 的数理基础与核心计算模型。

在前面的章节中，我们已经见证了 DeepSeek Harness 如何利用微内核装配调度智能体的各项能力。然而，一个更深层的理论问题摆在每一位系统架构师面前：
**为什么传统插件系统（如 VS Code 插件、Webpack Loader、Spring 容器）在面临复杂智能体的动态演进与热插拔时，总是难以避免内存泄漏、依赖悬挂或状态撕裂？**
为什么一个插件卸载后，往往必须重启整个 Node.js 进程才敢保证环境纯净？

本章将跳出单纯的工程 API，深入 Cordis 论文的数理内核，全面解构**时空可组合性（Spatiotemporal Composability）**这一全新编程范式，剖析**可逆效果追踪（Revertible Effects）**与**响应式副效果消解（Reactive Coeffects）**的数学公理，并阐明其如何让 DeepSeek Harness 实现零重启动态热重构与安全自愈。

---

## 1. 核心困境：动态组合系统为何总是“穿着插件外衣的重启系统”

论文在引言中开宗明义地指出：现代软件系统（特别是自演进的智能体 Harness）要求系统具备在**运行时动态重构（Dynamic Recomposition）**的能力。

但在现存的工程实践中，绝大多数声明自己支持“热插拔”的系统，本质上都是**伪可组合系统**：
1. **时间维度（Temporal）的不可逆性**：插件加载时执行了若干副作用（如注册了事件监听器、启动了子进程定时器、向全局单例挂载了中间件）。当用户调用“卸载插件”时，开发者手写的 `unload()` 函数往往百密一疏——遗漏了一个事件回调解绑或未终止一个后台 Timer，导致内存泄漏并永久污染宿主环境。
2. **空间维度（Spatial）的脆弱耦合**：组件之间的依赖解析往往是静态的或一次性的。当被依赖的基础服务（例如底层模型适配器 `model`）发生热升级或被替换时，依赖它的上层组件（如协调调度器 `orchestrator`）无法自动感知并重绑，最终因持有陈旧无效的句柄而抛出不可逆的崩溃。

论文提出的断言振聋发聩：**“一个缺乏时间可逆性与空间响应性保证的系统，仅仅是一个穿着插件外衣、本质上依赖全量重启的脆弱系统。”**

---

## 2. 时空可组合性的双重正交保证

为终结这一困局，Cordis 建立了两个正交的理论支柱，统称为**时空可组合性**：

```
┌────────────────────────────────────────────────────────┐
│ 时空可组合性体系 (Spatiotemporal Composability)        │
├──────────────────────────┬─────────────────────────────┤
│ 时间可组合性 (Temporal)    │ 空间可组合性 (Spatial)       │
│ 卸载组件能够【完全回滚】其    │ 组件显式【声明依赖】，运行时   │
│ 所有副作用。每个副作用自带    │ 【响应式】自动消解依赖。服务   │
│ 逆操作，运行时自动逆序执行。 │ 提供者的生命周期长于消费者。   │
└──────────────────────────┴─────────────────────────────┘
```

### 2.1 时间可组合性（Temporal Composability）：副作用自带逆元
在 Cordis 的理论范式中，所有的状态变更（Mutation）在类型签名上被约束为：
$$\text{state} \to \text{state} \times (\text{state} \to \text{state})$$
即：**每一次操作不仅产生新状态，还必须显式返回撤销该操作的逆函数（Inverse Function）**。
- `open()` 必须返回 `close`；
- `register()` 必须返回 `unregister`；
- `spawn()` 必须返回 `kill`。

运行时维系一个逆操作累加器（Inverse Accumulator）。卸载组件时，系统严格按照**后进先出（LIFO，Last-In-First-Out）**的数学顺序依次执行逆操作。**组件作者严禁手写卸载逻辑，卸载过程完全由装载时记录的逆元链条自然派生得出**。

### 2.2 空间可组合性（Spatial Composability）：响应式依赖图
组件不再主动探寻外部环境，而是通过静态声明其依赖契约（Coeffects）。
当声明的所有前置依赖全部激活时，组件自动激活；一旦某个关键前置依赖撤离，依赖该服务的下游组件**自动、级联地进入卸载流程**，杜绝“空指针调用已撤离服务（Use-After-Provider-Gone）”的非法态。

---

## 3. 数学契约：三元组形式化定义与 Fiber 计算模型

论文将系统中的每一个能力单元形式化地定义为一个标准组件（Component）：

$$C = \langle \text{inject}, \text{provide}, \text{apply} \rangle$$

1. **`inject`（副效果规范 / Coeffects）**：该组件激活所**必需**的有类型服务集合（$\mathcal{K}_{\text{req}}$）；
2. **`provide`（提供集 / Provisions）**：该组件装载后向系统容器**暴露**的有类型服务集合（$\mathcal{K}_{\text{prov}}$）；
3. **`apply`（有证副作用函数 / Witnessed Effect Function）**：组件被激活时执行的物理逻辑。

```typescript
// 理论契约映射至 TypeScript 的标准形式
interface Component {
  /** 空间维度：声明所需的类型化服务依赖 (Coeffects) */
  inject: Key<unknown>[]
  /** 空间维度：声明对外提供的类型化服务 (Provisions) */
  provide: Key<unknown>[]
  /** 时间维度：执行操作并把逆元推入累加器 (Revertible Effects) */
  apply(ctx: Context, config: unknown): void
}
```

### 3.1 Fiber：轻量级组件执行线程
在 Cordis 中，组件（Component）是静态的蓝图，而 **Fiber** 是组件在特定上下文中的动态运行时实例。
每个 Fiber 拥有独立的派生上下文、生命周期阶段（Lifecycle State）与逆元累加栈。当一个组件被多次实例化（例如多个沙箱实例）时，系统为每一个实例派生一个专属的 Fiber。

---

## 4. 核心执行状态机：惯性、退避与原子卸载

论文第 4 节严密形式化了组件 Fiber 的四态生命周期转换模型：

```
           mount
INACTIVE ─────────► LOADING ─────────► ACTIVE
   ▲                   │                  │
   │    目标变化       │                  │ 依赖撤离 / 销毁
   │    (惯性降落)     ▼                  ▼
   └─────────────── UNLOADING ◀───────────┘
         逆序执行完毕
```

1. **`INACTIVE`（就绪未激活）**：组件尚未装配，持有 0 个副作用，对系统状态没有任何污染；
2. **`LOADING`（分步装载中）**：
   - 副作用以迭代器（Effect Iterator）的方式逐步执行，并将逆元压入栈；
   - **惯性原则（Inertia Principle）**：如果装载过程中途收到取消信号，当前正在执行的单步操作**必须完整着陆（Land）**，绝不在执行途中野蛮杀死，然后再安全流转至 `UNLOADING`；
3. **`ACTIVE`（已激活）**：所有副作用执行完毕，对外正式发布 `provide` 声明的服务，供下游组件绑定；
4. **`UNLOADING`（级联卸载中）**：
   - **第一步：先停止提供服务**（Stop Providing）。组件立即从提供者注册表中注销，迫使所有下游消费者立即开始响应式卸载；
   - **第二步：保持接口可读，等待依赖排空**。在下游消费者尚未全部撤退前，当前组件的资源（如连接池、文件句柄）依然保持可读，允许消费者在自己的卸载过程中归还资源；
   - **第三步：逆序执行逆元栈**。待下游完全撤离后，严格按 LIFO 顺序清退自身所有副作用，最终回到 `INACTIVE`。

---

## 5. 交换律与独立性：提供者的契约责任

在多插件并发运行的复杂系统中，最棘手的问题是：**在组件 A 记录逆元与执行逆元之间，组件 B 改变了系统状态，A 的逆元还能安全执行吗？**

论文在第 5 节通过抽象代数给出了深刻的理论解答：

1. **效果独立性（Independence）**：
   设操作 $f$ 和 $g$ 分别产生逆元 $f^{-1}$ 和 $g^{-1}$。若 $f$ 与 $g$ 满足交换律（Commutative），即 $f \circ g = g \circ f$，且两者的逆元执行顺序不影响最终观测结果，则称两者独立。
   **独立的组件可以按任意顺序卸载，无需受严格入栈顺序绑架**。
2. **Key 的交换律职责属于提供者（Provider's Obligation）**：
   - 例如，**工具注册表（Tool Registry）**是一个典型的交换 Key：工具 A 和工具 B 以任意顺序注册或注销，系统观测到的工具集是完全等价的；
   - 而**中间件管道（Middleware Pipeline）**则是一个非交换 Key（顺序敏感）。对于非交换 Key，必须通过外层拓扑（如显式依赖声明）来约束加载与卸载次序。
3. **观测等价性（Observational Equivalence $\simeq$）**：
   状态恢复并不追求物理内存地址的逐比特还原，而是追求**任何外部观察者均无法察觉到差异**。内存释放不要求还原堆碎片分布，只要资源已脱离占用即视为完全逆转。

---

## 6. 在 DeepSeek Harness 中的终极映射

DeepSeek Harness 的整体架构完全是 Cordis 论文参考架构（Reference Architecture）的高阶工程兑现：

```
                    ┌──────────────────────────┐
                    │ deepseek-ai/cordis 4.0.4 │
                    │ (时空可组合性微内核基座)   │
                    └─────────────┬────────────┘
                                  │ 派生根上下文 (Root Context)
                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │  DeepSeek Harness 核心架构映射                          │
      ├──────────────────────┬─────────────────────────────────┤
      │ 论文理论抽象          │ DSH 生产包落地                   │
      ├──────────────────────┼─────────────────────────────────┤
      │ Model Broker         │ packages/core/agent-default-model│
      │ Tool Registry (可交换)│ packages/core/tools              │
      │ Session Log (单向外发)│ packages/session/session-jsonl   │
      │ Isolation Realm      │ ctx.isolate() 沙箱边界隔离      │
      │ Orchestration Loop   │ packages/core/agent-loop         │
      │ Hot Module Swap      │ packages/boot/hmr (基于逆元回滚) │
      └──────────────────────┴─────────────────────────────────┘
```

1. **热模块替换（HMR）零残留**：在开发或生产动态更新 Prompt 策略或工具代码时，DSH 直接卸载旧模块的 Fiber，由逆元自动排空事件与连接，新 Fiber 无缝顶替，绝不需要重启 Node 进程；
2. **会话沙箱物理隔离**：利用论文中的 `ctx.isolate()`，每个 Agent 或子任务在属于自己的 Realm 派生树中运行，修改被严格局限在当前子树，子树销毁时所有状态随上下文丢弃自然蒸发。

---

## 7. 本章小结

1. **时空双重保证**：时间可组合性保证任何副作用可逆且逆操作由系统逆序自动派生；空间可组合性保证组件间依赖关系响应式更新与有向无环清退。
2. **拒绝伪插件设计**：依赖全量重启来维护纯净性的系统不是现代插件系统。Cordis 确立了无需重启的动态重构数学规范。
3. **架构底层基石**：理解了 Cordis 的时空可组合性，就彻底读懂了 DeepSeek Harness 在高并发、长程运行和复杂多 Agent 协同下保持高内聚、零污染与故障自愈的理论根源。

---

## 本章面试问答

### Q1 · 面试官：你们系统基于 Cordis 微内核构建，请问 Cordis 核心论文提出的“时空可组合性（Spatiotemporal Composability）”究竟解决了微内核插件架构的什么痛点？

**回答**：
传统的插件架构（如 VS Code 扩展或 Spring 体系）普遍存在两大痛点：
一是**时间维度的不可逆**：插件在 `activate()` 时注册了大量监听器、定时器或修改了全局状态，但在卸载时，开发者手写的 `deactivate()` 容易遗漏清理代码，导致必须全量重启应用才能恢复干净环境；
二是**空间维度的悬挂崩溃**：当某个底层依赖服务发生热更新或被卸载时，上层依赖它的消费者无法感知，容易因持有陈旧句柄发生空指针崩溃。

Cordis 论文从数学上提出了时空可组合性解决方案：
1. **时间可组合性（Temporal）**：任何操作必须被约束为“产生新状态并返回自身的逆元函数（Inverse）”。卸载时由框架的逆元累加器按后进先出（LIFO）自动逆序回滚，无需手写销毁逻辑，确保副作用 100% 干净反转；
2. **空间可组合性（Spatial）**：引入响应式副效果（Reactive Coeffects）。组件通过 `inject` 声明类型化契约，底层服务撤离时，框架自动、级联地卸载依赖它的消费者，保证提供者的生命周期严格长于消费者，从根源上消除了悬挂调用与内存泄漏。

**原理**：
抽象代数中的可逆映射（Invertible Maps）与范畴论中的副效果消解（Coeffect Resolution）。将运行时的动态组装提升为由类型系统和状态机保证的严格数学演算。

**追问**：在插件卸载（`UNLOADING`）过程中，Cordis 为什么要求“先停止提供自身服务，但在下游彻底清退前依然保持资源可读”？
**应答要点**：
这是为了防止“释放后使用（Use-After-Free）”的破坏性竞争。如果提供者立即销毁物理资源（如直接关闭数据库连接池），依赖它的消费者在接收到卸载通告并执行自我清理时，往往需要向连接池归还正在使用的连接，直接销毁会导致消费者报错崩溃。Cordis 的两阶段卸载契约保证：先在逻辑上声明自己不再接纳新请求，等待所有已挂载的消费者优雅退场并归还资源后，最后才物理执行逆元销毁底层资源，从而实现系统级的确定性优雅停机。


---
