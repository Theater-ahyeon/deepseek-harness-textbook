# 技术选型与替代方案：从项目需求理解架构取舍

DeepSeek Harness 同时承担 Agent 运行、工具执行、插件装配、Session 恢复和产品交互。理解技术选型，需要先确定这些职责，再分析每项技术承担的部分，以及替换后需要重新实现的机制。

本专题比较十四组选型。每节先列出固定源码版本中的实际实现，再分析它对项目的收益、维护代价和替代方案。收益与迁移成本是依据实现结构作出的工程分析，原项目的依赖声明与接口约定作为事实证据。比较使用相同的功能目标，不给不同层次的技术排列总分。

建议在读完第 1 章后阅读总览，学习各章时查阅对应比较；读完第 19 章后，再集中阅读 Cordis、执行模型和生命周期的取舍。

## 选型总览

| 项目需求 | 当前采用的方案 | 主要收益 | 需要承担的代价 | 对应正文 |
| --- | --- | --- | --- | --- |
| 多包协作与跨端契约 | TypeScript、Node.js、ESM | Host 与 Client 共用类型约定，接入 JavaScript 生态 | 编译期类型之外仍需运行时校验，重计算需要安排执行位置 | 第 2、14、15 章 |
| 动态装配与资源管理 | Cordis 插件、服务注入与 effect | 注册项和清理行为归属插件，支持按依赖启停 | 学习作用域、依赖和卸载规则 | 第 10、19 章 |
| 开放任务的逐步执行 | Agent loop、Inbox 与工具调度 | 模型请求、工具执行和事件记录使用同一运行链 | 自行维护轮次、步骤、取消和恢复语义 | 第 3、9、11 章 |
| 可恢复的交互历史 | Session 事件日志、Surface 与 JSONL Provider | 原始事实与派生视图分离，支持恢复和历史继承 | 日志格式、迁移、写入权与 flush 都需治理 | 第 5、8、13 章 |
| 产品数据持久化 | Domain API、JSON 与 SQLite 后端 | 业务结构与介质分离，各领域选择后端 | 版本兼容和跨操作顺序仍由领域维护 | 补充能力 |
| 外部数据校验 | Schemastery、Zod、工具 schema DSL | 配置、领域数据和工具输入分别按契约验证 | 多种 schema 系统需要明确分工 | 第 10、11 章 |
| Host 与 Client 调用 | Typert、Gateway 与生成产物 | 方法、参数、对象身份和流式契约相互对应 | 生成链、codec 与运行时注册增加维护环节 | 第 14、15 章 |
| 多模型接入 | LLM 服务与 Provider，含 pi-ai 适配器 | 核心循环使用统一请求和流式响应入口 | 保留不同模型的能力差异与异常语义 | 第 9 章 |
| 外部工具生态 | MCP 的 stdio 与 Streamable HTTP | 工具和资源使用共同发现、调用约定 | 连接、认证、重连和注册更新需要处理 | 第 12 章 |
| 交互界面与状态 | React、Zustand、Immer、Vite | 状态快照与组件订阅分离，Web 和桌面共享界面基础 | 高频更新、状态归属和订阅清理需要设计 | 第 14、15 章 |
| 桌面产品 | Electron Main、Renderer 与独立 Node Host | 网页界面与 Node 运行环境衔接 | 多进程通信、打包、升级和资源占用 | 第 15 章 |
| 多包构建与发布 | pnpm workspace、tsc、tsdown | 按包管理依赖，区分类型构建与分发产物 | 依赖图、导出条件和构建顺序需要一致 | 第 10 章、补充能力 |
| 可重复验证 | Vitest、模型回放与独立断言 | 稳定复现运行分支，减少测试对在线模型的依赖 | fixture、请求断言与真实评价分别维护 | 第 16、17 章 |
| 程序化工具调用 | 全新 Node 子进程、Host 绑定与 OS 沙箱 | TypeScript 程序组织多项工具，Host 管理执行与清理 | 进程启动、协议、输出预算和平台沙箱 | 补充能力 |

<a id="choice-runtime"></a>
## 1. TypeScript 与 Node.js：统一契约和运行生态

### 项目实际采用什么

根包声明 ESM，使用 pnpm workspace，并要求 Node.js `^22.19.0 || >=24.0.0`。Host 与 Client 分别通过 TypeScript project references 构建。桌面应用使用独立 Node Host，Web 前端也在同一个多包仓库中开发。版本事实见文末 T01、T12 和 T13。

TypeScript 为编译期检查提供依据：服务方法的参数、工具结果和 Session 事件都能在开发时关联到对应类型。它在运行前发现类型不匹配；外部 JSON、模型输出和持久文件则由运行时校验处理。[TypeScript 官方基础文档](https://www.typescriptlang.org/docs/handbook/2/basic-types.html)解释了类型检查与类型擦除的关系。

### 对这个项目的优势与代价

统一语言让 Host 接口、Client 调用和插件声明可以直接共享类型与生成工具。例如 Session 标识类型变化后，相关调用点可以在构建中暴露问题；新增远程方法时，生成器可以同时产出 Host descriptor 与 Client 侧契约。

Node.js 适合组织模型流、网络请求、文件访问和子进程等异步任务。等待 I/O 时，事件循环继续处理其他工作。同步 JavaScript 计算会占用事件循环；添加 `async` 关键字不会把计算移到其他线程。这个机制可在 [Node.js 事件循环说明](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop)中核对。项目通过独立 Host、子进程和 Provider 分工安排执行职责，具体操作的延迟仍取决于实现和输入规模。

### 与替代方案比较

| 方案 | 主要优势 | 替换时需要处理的工作 |
| --- | --- | --- |
| TypeScript + Node.js | Host、Web Client 和插件使用同一语言与包生态 | 保留运行时校验，控制同步重计算，管理原生扩展与分发 |
| Python + asyncio | 直接使用 Python 的模型、数据处理与科研库，支持异步网络和子进程 | 浏览器 Client 仍需 JavaScript；重新连接跨语言类型、事件表示和远程调用契约 |
| 以原生服务承担 Host | 将系统调用和计算集中到原生实现中 | 重新设计与 Client、插件、模型 SDK 的语言边界及构建发布流程 |

[Python asyncio](https://docs.python.org/3/library/asyncio.html)同样提供异步并发、网络与子进程能力。选择 Node.js 的架构收益集中在跨端协作和既有生态；CPU 计算能力要按实际负载单独测量。

<a id="choice-cordis"></a>
## 2. Cordis：把依赖与资源生命周期纳入装配

### 项目实际采用什么

插件声明所需服务，在激活时注册工具、监听器或 Provider，并通过 effect 关联清理行为。profile 选择插件组合，Cordis 依据服务可用性和插件生命周期管理装配。`Context.isolate()` 与 `intercept()` 提供服务作用域和配置干预入口。源码与装配规则见 T02，第 19 章解释对应理论。

### 对这个项目的优势与代价

一个文件工具可能同时贡献工具定义、调用监听器和界面呈现。将这些贡献归属同一插件，可以在卸载时沿已登记的清理路径撤销它们。文件 Provider 变更后，依赖它的部件也能依据服务状态重新安排激活。

这种管理方式减少了各模块自行保存全局注册表和清理列表的重复工作。开发者需要理解服务身份、插件归属、effect 和异步清理。已经交给外部系统的动作，还需要由对应 Provider 管理结果和恢复；资源登记不能撤回已经发生的外部操作。

### 与替代方案比较

| 方案 | 装配方式 | 在相同功能目标下的实现差异 |
| --- | --- | --- |
| 手写模块与注册表 | 启动函数显式创建服务，手动登记与清理 | 初始结构直接；扩展热替换后，需要补齐依赖失效、作用域和撤销顺序 |
| NestJS 模块与依赖注入 | 模块组织 Provider，使用 singleton、request 或 transient 生命周期 | 适合围绕应用模块和请求组织服务；本项目的动态插件树与贡献撤销还需具体设计 |
| Cordis | 按上下文装配插件，关联服务依赖与 effect | 与项目的可替换 Provider 和动态贡献机制相互配合；需要维护完整的资源归属 |

[NestJS 的 injection scopes](https://docs.nestjs.com/fundamentals/injection-scopes)定义了三种 Provider 生命周期。Cordis 的插件上下文、服务隔离和卸载机制解决另一组装配问题，迁移时应逐项映射这些行为。

<a id="choice-loop"></a>
## 3. Agent loop：围绕模型与工具建立连续运行链

### 项目实际采用什么

默认 agent-loop 驱动器创建或恢复 Agent，处理 Inbox、模型流、工具调用和持久历史。工具调度区分可并行与独占调用，并配置并行上限。工具执行经过准入、审批和 guard 等边界，执行结果再进入后续模型请求。事实见 T03、T07。

### 对这个项目的优势与代价

“读取文件再总结”与“搜索多份材料再编辑文档”都可以沿模型请求、工具结果、下一步请求的循环运行。工具集合由插件贡献，任务可以在运行中依据结果继续展开。Session 提供统一记录，使模型、工具和用户界面能够围绕同一执行历史协作。

控制流由项目直接维护，因此轮次与步骤边界、重试、取消、工具顺序和恢复规则都需要明确实现。增加一种驱动方式时，还要保持它与 Session、审批和 Client 事件的约定一致。

### 与 LangGraph 和固定工作流比较

| 方案 | 控制结构 | 更直接表达的需求 | 迁移时的关键工作 |
| --- | --- | --- | --- |
| 项目默认 Agent loop | 模型与工具循环，运行边界进入 Session | 步骤随观察结果继续展开的交互任务 | 将新增控制机制接入现有历史、审批与取消链 |
| LangGraph | 图节点、状态及图的执行机制 | 显式分支、子图、状态检查点与人工中断 | 映射 graph state、thread、checkpoint 与本项目 Session 事件语义 |
| 固定步骤工作流 | 预定义步骤与分支 | 次序清晰的审批、报表或批处理 | 规定失败后重试哪一步、保存什么状态、怎样去重外部动作 |

[LangGraph 官方概述](https://docs.langchain.com/oss/javascript/langgraph/overview)和[持久化说明](https://docs.langchain.com/oss/javascript/langgraph/persistence)介绍了图执行与 checkpoint。图式编排与 Agent loop 可以组合；DeepSeek Harness 也包含工作流扩展。选型首先决定由哪一层维护控制流，再安排状态、工具准入和产品接口。

<a id="choice-session"></a>
## 4. Session 事件日志：保存事实，再构造当前视图

### 项目实际采用什么

`Session.append` 按顺序追加内存事件并发出通知。JSONL 持久化 Provider 在存在对应 writer 时排入写入队列，flush 处理写入结算。Surface 从历史中构造当前可用的消息表示，压缩和 fork 在相应历史约定上运行。append、排队与持久化完成是不同阶段，源码事实见 T04、T05。

### 对这个项目的优势与代价

模型请求的中间状态、工具调用结果和运行结束边界都可以记录为事件。界面投影、模型消息历史与恢复逻辑读取同一组事实，各自形成需要的视图。调查一次失败时，可以追踪接受输入、模型尝试、工具交接与结算的顺序。

事件类型和持久格式必须版本化。恢复需要处理未完成步骤、generation 选择与写入权；长历史需要通过投影、索引或压缩控制读取成本。保存事件历史也要求维护迁移逻辑，确保旧记录能按既定规则恢复。

### 与消息数组、快照和数据库事件表比较

| 方案 | 保存的主体 | 优势 | 为本项目补齐什么 |
| --- | --- | --- | --- |
| 可变 messages 数组 | 当前对话消息 | 最初实现简单，直接构造模型输入 | 增加工具状态、尝试、运行边界、历史变更和中断恢复 |
| 状态 checkpoint | 某个执行位置的状态快照 | 从选定位置恢复状态，便于图或工作流执行 | 明确外部动作是否已完成，以及快照间需要保留的事实 |
| JSONL 事件日志 | 有序事件与版本信息 | 按流保存历史，文件可以随本地 Session 管理 | 顺序、迁移、写入结算和查询索引 |
| 数据库事件表 | 数据库中的有序事件 | 将事件持久化纳入数据库的查询和事务机制 | 实现相同事件语义、序号、写入归属与恢复约定 |

事件模型和存储介质是两个决策。将 JSONL 改成数据库事件表，仍然可以保留事件驱动的 Session；将日志改成单个最新快照，则会改变可观察的历史信息。LangGraph 的 checkpoint 与跨 thread store 也承担不同用途，其区分见[官方持久化文档](https://docs.langchain.com/oss/javascript/langgraph/persistence)。

<a id="choice-storage"></a>
## 5. JSON 与 SQLite：为不同产品数据选择持久介质

### 项目实际采用什么

工作区注册等非 Session 数据通过 storage hub 与 Domain API 访问。JSON 后端支持整 unit 文档和 per-record 文档；SQLite 后端通过 `node:sqlite` 的 `DatabaseSync` 在一个数据库中保存按行组织的 JSON 文档。领域根据配置选择后端。事实见 T06。

### 对这个项目的优势与代价

JSON 文件便于查看结构、复制和排查数据；整 unit 布局每次更新重新发布对应文档，per-record 布局按记录保存。SQLite 适合把较多独立更新放在数据库内，通过单条操作修改记录，避免每次重写整个 unit 文件。这里的 SQLite 后端仍按文档存储值，领域对象没有自动转成任意关系表。

项目后端约定保证每次独立操作的原子性，多个业务操作的顺序由调用方维护。当前 SQLite unit 实现没有为一组领域更新自动开启事务，也没有内部写队列。`DatabaseSync` 操作同步执行，频繁或较大的数据库操作需要检查 Host 的阻塞时间。

### 与 PostgreSQL 等服务型数据库比较

| 方案 | 部署与访问特点 | 在项目中的收益 | 需要处理的成本 |
| --- | --- | --- | --- |
| JSON | 本地文件树，按配置布局保存文档 | 人工检查直接，随本地应用管理 | 文件发布、版本处理及大量更新时的写入成本 |
| SQLite | 嵌入式数据库文件 | 无须另起数据库服务，独立记录更新集中管理 | 写竞争、同步调用和数据库文件生命周期 |
| PostgreSQL 等服务型数据库 | 应用通过连接访问数据库服务 | 集中管理共享数据与多实例访问 | 连接、认证、事务映射、迁移及服务运维 |

[SQLite 官方选型说明](https://www.sqlite.org/whentouse.html)区分了嵌入式数据库与服务型数据库。当前 SQLite 配置默认 WAL，并支持 rollback journal 模式。WAL 的共享内存机制限制了网络文件系统上的部署方式，见[官方 WAL 文档](https://www.sqlite.org/wal.html)；项目源码也为此提供 journalMode 选择。迁移到服务型数据库时，应先实现 StorageBackend 约定，再明确多实例写入权与业务事务。

<a id="choice-schema"></a>
## 6. 类型与 schema：分别约束配置、领域和工具输入

### 项目实际采用什么

本项目包含三种需要区分的 schema 用途：Schemastery 验证插件配置并应用默认值；Zod 定义领域记录等结构，并参与 Typert strict schema；工具系统使用自己的 JSON-value schema DSL 与 JSON Schema 校验约定。源码中的 `import z from '@deepseek-ai/schemastery'` 指向 Schemastery，变量名 `z` 无法单独说明它使用 Zod。事实见 T07、T08。

### 对这个项目的优势与代价

每个入口可以按自己的语义校验。例如插件配置需要默认值，持久记录需要格式版本和明确结构，模型工具参数需要可公开的 JSON Schema 及执行前检查。统一工具 DSL 还能关联参数推导、输入校验和生成的工具声明，减少重复定义。

多套系统增加了学习和维护成本。类型、默认值、输入结构与输出结构需要一致；一些运行时结构也无法直接表达为模型工具可接受的 JSON Schema。扩展节点或生成 codec 时，需要同时核对输入、输出和序列化后的表示。

### 与其他校验方式比较

| 方案 | 契约所在位置 | 优势 | 主要实现工作 |
| --- | --- | --- | --- |
| 仅 TypeScript 类型 | 源文件与构建检查 | 编辑器和编译器可追踪调用关系 | 外部数据入口另加运行时校验 |
| Zod | 代码中的 schema | 关联运行时解析与类型推导 | 管理转换、默认值及 JSON Schema 可表示性 |
| JSON Schema + Ajv | 数据形式的 schema 与编译后的 validator | 可以独立分发 schema，便于多语言边界协作 | 对齐版本、类型生成、默认值和校验选项 |
| 项目的分层 schema | 配置、领域、工具按职责定义 | 让各入口保留对应语义 | 维护多套生成与校验规则，防止边界漂移 |

[Ajv 官方说明](https://ajv.js.org/guide/getting-started.html)解释了从 schema 编译校验函数的方式；[Zod 的 JSON Schema 文档](https://zod.dev/json-schema)列出了转换机制与不可表示类型。换用统一 validator 时，需要先列出配置默认值、工具声明和持久记录校验的差异，再确定如何表达它们。

<a id="choice-rpc"></a>
## 7. Typert：连接服务方法、远程对象与传输

### 项目实际采用什么

Typert 的生成 descriptor 描述服务、方法、参数 codec、对象 lookup、调用作用域和流式结果。请求发送 endpoint 与具名 args，Host 在注册表中解析活对象；取消通过带外 signal 传递。strict codec 使用生成 schema，SRC 路径检查 JSON 安全值。Gateway 分派服务调用，Connection 承担对应传输与响应信封，实时 Remote stream 使用 Gateway 管理的 WebSocket mux。事实见 T08。

### 对这个项目的优势与代价

Client 请求某个 Session 的方法时，只需传递约定的身份值。Host 解析真实对象，保留服务作用域；生成器让客户端声明、Host descriptor 与校验方式相互对应。类型变化、对象身份和流式调用都纳入同一构建链。

生成器、manifest、注册表和 codec 必须一起维护。缺失 lookup Provider 时，身份解析应按不可用处理。跨版本通信还需要兼容策略，构建通过也不能替代运行时的权限判断与数据校验。

### 与 REST、tRPC 和 gRPC 比较

| 方案 | 契约表达 | 对相同需求的实现差异 |
| --- | --- | --- |
| REST + OpenAPI | 路径、HTTP 方法与数据 schema | 接口便于公开；对象 lookup、作用域、取消和双向流需要相应设计 |
| tRPC | TypeScript Router 与推导类型 | 同一 TypeScript 技术栈能共享调用类型；需将项目服务与对象身份映射到 Router |
| gRPC + Protocol Buffers | 服务与消息定义、生成客户端和服务端 | 跨语言代码生成和流式 RPC 契约明确；需安排浏览器接入及领域对象映射 |
| Typert | 项目服务方法、生成 descriptor 与运行时注册 | 与 Cordis 服务、作用域和 Host 对象身份直接配合；维护项目专用生成体系 |

[tRPC 官方文档](https://trpc.io/docs/)和[gRPC 官方介绍](https://grpc.io/docs/what-is-grpc/introduction/)说明了各自的契约形式。上述方案都可以实现经过认证与校验的调用，差别在于契约如何定义、生成及接入项目的服务模型。

<a id="choice-model"></a>
## 8. 模型 Provider：统一调用入口，保留模型差异

### 项目实际采用什么

Agent 通过 LLM 服务选择 Provider 与模型，消费统一的请求及流式结果。仓库包含 pi-ai 适配器和其他模型接入实现；pi-ai 路由使用提供方目录，也允许显式声明路由，结合模型能力、端点和凭据配置形成请求。事实见 T09。

### 对这个项目的优势与代价

更换模型接入方式时，工具调度、Session 和界面仍可以围绕同一组运行事件工作。测试 Provider 也能接入这个边界，使固定响应与实时模型使用相同上层流程。模型配置和凭据处理集中在相应接入层。

不同模型对工具、图片、推理设置和请求格式的支持不同。统一服务需要保留这些能力声明，并转换流式块、错误和用量信息。新增 Provider 后，要核对取消、部分输出、重试和接受时点等细节。

| 方案 | 收益 | 对项目的实现影响 |
| --- | --- | --- |
| 直接调用单一厂商 SDK | 接近该厂商的接口和新增能力 | 上层业务若直接使用厂商对象，需要另加稳定边界才能切换 Provider |
| 多提供方适配库 | 复用路由、模型目录和协议适配 | 仍需对接项目的事件、凭据和错误语义 |
| 项目 LLM 服务 + Provider | 核心运行链保持稳定，接入实现可替换 | 维护公共契约与各模型能力之间的对应关系 |

pi-ai 已作为 Provider 实现的一部分使用。比较“统一模型服务”和“采用某个 SDK”时，需要分别观察架构边界与边界内的实现库。

<a id="choice-mcp"></a>
## 9. MCP：为外部工具和资源采用共同协议

### 项目实际采用什么

MCP 客户端按配置创建 stdio 或 Streamable HTTP transport。stdio 启动服务器子进程并构造传入环境；HTTP 连接配置 URL 与请求头。远端工具注册进入工具链，资源则经过发现和读取接口进入材料链。事实见 T10。

### 对这个项目的优势与代价

外部服务能使用相同的工具和资源约定接入，应用无需为每种服务重新设计发现协议。工具名称、输入结构和资源 URI 按 MCP 消息传递，再映射到项目的注册与调用机制。

连接失败、能力协商、认证、重连和列表更新增加了运行状态。远端工具同样需要经过调用准入；本地执行环境的限制也不能自动覆盖远端服务的资源访问。协议接入与权限执行分别由对应机制承担。

| 方案 | 适合表达的连接 | 实现与维护特点 |
| --- | --- | --- |
| 进程内插件 | 直接访问项目服务的可信模块 | 调用链短，生命周期随插件管理，直接耦合项目 API |
| 自定义 HTTP API | 已有业务服务接口 | 能保留业务语义，需要单独设计工具描述与资源发现 |
| MCP stdio | 由客户端管理的本地服务器进程 | 采用标准消息约定，需管理进程、环境与退出 |
| MCP Streamable HTTP | 独立部署的远端或本地服务 | 采用共同能力协议，需管理 URL、连接与认证 |

[MCP transport 规范](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)定义 stdio 和 Streamable HTTP。Streamable HTTP 使用 HTTP 请求并可承载 SSE；它与本项目 Client 的 WebSocket Remote stream 是不同通信路径。

<a id="choice-ui"></a>
## 10. React、Zustand、Immer 与 Vite：把状态组织和页面呈现分开

### 项目实际采用什么

Web 与桌面界面使用 React。共享 Store 引擎使用 Zustand vanilla、selector 订阅和 Immer，向消费方公开 subscribe 与 snapshot 契约；Store 引擎本身不依赖 React。Web 应用通过 Vite 构建。事实见 T11、T12。

### 对这个项目的优势与代价

Session 历史、流式消息和运行状态先进入 Store，再由组件订阅相应快照。React 负责界面呈现，Store 负责状态更新。共享状态引擎也可以供其他观察端使用，降低业务状态与组件生命周期之间的耦合。

selector 帮助组件选择需要观察的部分，Immer 支持以草稿更新方式生成新的状态。项目还包含按动画帧批量通知的机制，用于安排高频更新。组件更新成本仍由订阅粒度、状态结构和实际事件量决定。分组状态、完整历史和当前快照之间也需要避免重复成为可写的权威来源。

| 方案 | 状态组织方式 | 对项目的迁移影响 |
| --- | --- | --- |
| React + 当前 Store 引擎 | 外部快照与 selector，组件按需订阅 | 保留共享引擎及现有客户端插件接口 |
| React + Redux Toolkit | Store、action 与 reducer 组织状态更新 | 将现有 actions 和 snapshot 契约映射到新的状态接口；Redux Toolkit 同样使用 Immer |
| Vue 或 Svelte 界面 | 使用各自组件与响应式机制 | 重写组件、插槽和生命周期接入，能够继续通过适配器消费既有状态与远程接口 |
| 手写 DOM 与订阅 | 显式更新节点与清理监听器 | 页面较少时实现直接；界面模块增多后需维护自己的组合和更新约定 |

[React 的外部 Store 接口](https://react.dev/reference/react/useSyncExternalStore)说明了 subscribe 与 snapshot 的配合；[Redux Toolkit 的 Immer 说明](https://redux.js.org/toolkit/usage/immer-reducers)表明草稿更新并非某个 Store 独有。Vite 负责开发和构建，状态库负责运行时数据更新，两者承担不同职责。

<a id="choice-desktop"></a>
## 11. Electron 与独立 Node Host：分离桌面外壳和任务运行

### 项目实际采用什么

Electron Main 管理窗口与桌面生命周期，Renderer 加载界面，`DesktopHostProcess.start` 启动独立 Node 子进程。Main 中的窗口配置关闭 nodeIntegration，开启 contextIsolation 与 sandbox。Host 返回服务地址和 injections，界面据此启动业务调用。事实见 T12。

### 对这个项目的优势与代价

Web 界面可以复用到桌面；Main 专注窗口、协议转发和系统集成，Host 承担 Agent 与插件运行。Host 的标准输出、退出和 ready/fatal 通知也形成独立的诊断入口。界面等待后端启动时，可以保留明确的启动状态。

多进程架构要求维护通信、认证、启动握手、退出与重启路径。分发需要携带相应运行环境和界面资源，安装包、内存和启动成本都要实际测量。Renderer 隔离与工具执行沙箱分属不同层次：前者管理页面权限，后者约束执行环境。

| 方案 | 运行结构 | 替换时的关键变化 |
| --- | --- | --- |
| Electron + Node Host | Chromium Renderer、Main 和独立 Host | 复用当前界面与 Node 服务，同时维护多进程和分发 |
| Tauri + Node sidecar 或重写 Host | Core process、系统 WebView 与额外运行服务 | 重做桌面桥接；保留 Node Host 时仍需分发它及其依赖 |
| 纯 Web + 外部 Host | 浏览器页面访问已有服务 | 减少桌面安装工作，重新安排本地文件、进程和系统能力的访问入口 |

[Electron 的进程模型](https://www.electronjs.org/docs/latest/tutorial/process-model)与[Tauri 的进程模型](https://v2.tauri.app/concept/process-model/)给出了各自结构。Tauri 使用系统 WebView；将当前应用换成 Tauri 时，必须一并决定 Node Host 的保留方式，才能估算完整产品的体积和维护工作。

<a id="choice-build"></a>
## 12. pnpm workspace 与分包构建：让能力以包为单位协作

### 项目实际采用什么

workspace 覆盖 vendor、分组 packages、原生系统包、apps 和 website。依赖通过 `workspace:*` 等声明关联。Host 与 Client 使用独立 tsconfig 构建，tsc 执行类型和声明构建，tsdown 生成相应分发产物；Web 产品另由 Vite 构建。workspace 配置还声明依赖安装脚本的允许项。事实见 T13。

### 对这个项目的优势与代价

服务定义、Provider 和 Consumer 可以拆成不同包，产品组合按依赖选用它们。修改公共类型时，项目能沿构建关系检查消费方。分包也让发布导出面与运行入口更明确，帮助控制 Host 代码和 Client 代码的边界。

包数增加后，需要检查循环依赖、导出条件、构建顺序和运行时依赖闭包。开发环境能解析到源码，不代表发布后的包能解析到同一模块。project references、路径映射和打包配置必须与真实发布布局一致。

| 方案 | 管理层次 | 对项目的影响 |
| --- | --- | --- |
| pnpm workspace | 包依赖、本地包关联与安装 | 已与仓库的 workspace 协议和依赖策略结合 |
| npm 或 Yarn workspace | 同仓库多包协作 | 重新核对依赖解析、安装布局、peer dependency 和构建脚本 |
| 单包仓库 | 同一个包内组织全部模块 | 简化最初配置，同时缩小独立发布和组合的边界 |
| Nx、Turborepo 等任务编排 | 构建任务图与缓存 | 可以叠加到包管理之上；还需定义任务输入、输出和失效条件 |

[pnpm workspace](https://pnpm.io/workspaces)与[npm workspace](https://docs.npmjs.com/cli/v11/using-npm/workspaces/)都支持多包协作。包管理、类型构建、bundling 和任务缓存是不同决策，不能只换一个命令就假定所有发布行为等价。

<a id="choice-tests"></a>
## 13. Vitest 与模型回放：分别验证软件行为和任务效果

### 项目实际采用什么

仓库使用 Vitest，设置单元、快照、Web、E2E 与 benchmark 等测试入口。LLM replay 按 Session 分配脚本，并按调用位置消费条目；测试可以在 Provider 层或模型流边界接入回放。事实见 T14。

### 对这个项目的优势与代价

固定响应让工具调度、流式展示、取消和恢复分支能够重复执行。开发者可以明确制造一次工具调用、一次错误或一段部分响应，观察项目怎样处理它们。测试框架再通过断言检查真正关心的状态和数据。

回放位置只说明消费了哪项响应。请求中的 system prompt、工具 schema 或历史消息错误时，按序返回的响应仍可能使测试走完流程；因此请求内容必须独立断言。fixture 也需要随持久格式与行为变化维护。实际模型的工具选择与产物质量，继续通过在线评价和任务样本测量。

| 方案 | 主要验证对象 | 为完整验证补充什么 |
| --- | --- | --- |
| Vitest + 项目回放 | 固定模型响应下的真实运行链 | 请求断言、错误分支、fixture 消费检查和真实任务评价 |
| Jest + 等价替身 | 测试运行与 mock、assertion | 对齐模块、转换、快照和项目测试工具的行为 |
| Node 内置 test runner | Node 原生测试执行 | 配置 TypeScript、DOM 或浏览器测试所需环境，并接入回放 |
| 每次调用在线模型 | 当时的模型和网络表现 | 控制费用、波动与外部副作用，另外保留可重复的软件行为测试 |

[Vitest 官方比较](https://vitest.dev/guide/comparisons)与[Node test runner 文档](https://nodejs.org/api/test.html)介绍各自执行机制。测试框架决定怎样运行断言；回放决定怎样替代外部响应；评价决定怎样衡量任务产物。

<a id="choice-ptc"></a>
## 14. PTC Node 子进程：用程序组织工具，再由 Host 管理执行

### 项目实际采用什么

`ptc-runtime-node` 为每次程序运行创建全新 Node 进程，执行可擦除 TypeScript 程序，通过异步绑定请求 Host 工具。Host 负责沙箱准备、截止时间、输出预算、协议检查和受管清理。直接 Node API 仍能在所选执行限制内使用；嵌套工具调用重新进入工具准入链。事实见 T15。

### 对这个项目的优势与代价

模型可以用一次程序调用组织循环、多项读取或并发工具任务，减少逐次向模型请求下一动作的往返。全新进程提供独立的执行生命周期，Host 能在超时、取消或完成后清理受管进程。绑定保留项目的工具可见性与审批机制。

进程边界增加启动和通信成本。Host 要区分日志与控制帧，限制同时待处理的调用和输出大小，并验证结果是否为无损 JSON。具体文件与网络限制由 OS 沙箱后端实施，运行时需要检查其可用性和约束程度。

| 方案 | 执行机制 | 需要设计的边界 |
| --- | --- | --- |
| 当前 Node 子进程 | 完整 Node 执行环境，OS 沙箱与 Host 绑定 | 进程、平台策略、控制通信及资源清理 |
| `node:vm` 同进程求值 | 在 Node 进程中建立 JavaScript context | 仍需可靠的外部隔离与终止机制；Node 官方明确它不构成安全机制 |
| 受限 JavaScript 引擎 | 嵌入引擎并显式提供宿主能力 | 定义可见 API、计量、取消和逃逸后的隔离边界，核对 Node API 兼容性 |
| Python 子进程 | 使用 Python 程序和工具代理 | 维护解释器分发、绑定协议、结果编码与相同的执行约束 |
| 容器或远端执行服务 | 将程序交给独立运行环境 | 镜像或服务生命周期、文件映射、身份、通信和恢复 |

[Node vm 文档](https://nodejs.org/api/vm.html)明确说明该模块不应用作安全隔离。减少启动开销和改变隔离机制是两个问题，替代运行时需要分别验证工具调用语义、资源约束与清理能力。仓库还包含实验性的 Python PTC 实现，说明这个能力已通过接口与具体运行环境分离。

## 需求变化后，哪些选型需要重新评估

| 新的主要需求 | 优先检查的选择 | 对架构的具体影响 |
| --- | --- | --- |
| 单个本地 Agent，工具数量少 | 插件数量、分包粒度与界面入口 | 可以减少组合和产品层，同时保留工具准入与状态记录 |
| 大量固定业务流程 | 驱动方式与检查点 | 显式定义步骤和分支，再接入相同的工具与历史接口 |
| 多实例共同维护产品数据 | 存储后端与写入权 | 引入共享介质，并设计跨实例协调和事务 |
| 主要依赖 Python 数据处理库 | Host 语言边界或独立计算 Provider | 让计算通过受控接口执行，再确定需要共享哪些类型与事件 |
| 安装包大小是硬指标 | 桌面外壳与 Node Host 分发 | 对完整产品测量体积，包含外壳、Host、原生模块与资源 |
| 流式消息量显著增加 | Store 通知、投影和界面订阅 | 测量事件处理与渲染延迟，调整批处理和订阅粒度 |
| 执行来自多个用户的不可信程序 | 执行隔离、身份与资源计量 | 把运行环境、Host 绑定和租户数据范围一起设计 |

项目的主要组合关系是：TypeScript 连接类型与生成产物，Cordis 连接插件与服务生命周期，Session 连接运行事实与派生视图，Provider 连接公共接口与具体执行环境，Client 通过远程契约观察和操作 Host。替换技术时，先确认这些关系仍由哪一层承担，再比较开发成本、运行成本和维护工作。

## 原项目证据与进一步阅读

本专题固定使用源码提交 `639ed015397290b3745d163aafe02ffee4aa3f84`。下面的材料用于核对实际选型；正文已解释比较所需的机制。

| 编号 | 支持的事实 | 原项目材料 |
| --- | --- | --- |
| T01 | Node 范围、ESM、构建命令与开发依赖 | [根 package.json](source/package.json)、[Host tsconfig](source/tsconfig.host.json)、[Client tsconfig](source/tsconfig.client.json) |
| T02 | Cordis 上下文、插件装配与生命周期 | [Cordis Context](source/vendor/cordis/src/context.ts)、[插件注册与依赖](source/vendor/cordis/src/registry.ts)、[资源生命周期](source/vendor/cordis/src/fiber.ts)、[profile 合成](source/packages/boot/app-boot/src/profile.ts) |
| T03 | 默认 Agent loop 与并行工具上限 | [Agent loop 原文](source/packages/core/agent-loop/README.zh.md)、[Inbox 实现](source/packages/core/agent-loop/src/inbox.ts) |
| T04 | Session 内存事件追加与 Surface | [Session 实现](source/packages/core/session/src/index.ts)、[Session 章节](book/05.md) |
| T05 | JSONL writer 与写入队列 | [持久化实现](source/packages/session/session-persistence-jsonl/src/storage.ts)、[持久化原文](source/docs/subsystems/persistence.zh.md) |
| T06 | Domain、JSON、SQLite、同步连接与单操作原子性 | [存储原文](source/docs/subsystems/storage.zh.md)、[JSON 后端](source/packages/storage/storage-json/src/index.ts)、[SQLite 后端](source/packages/storage/storage-sqlite/src/index.ts)、[SQLite unit](source/packages/storage/storage-sqlite/src/unit.ts)、[SQLite schema](source/packages/storage/storage-sqlite/src/schema.ts) |
| T07 | Schemastery 配置与工具 JSON-value schema DSL | [Schemastery 依赖](source/vendor/schemastery/package.json)、[工具注册表](source/packages/core/tools/src/index.ts)、[工具 schema](source/packages/core/tools/src/schema.ts)、[工具 JSON Schema 校验](source/packages/core/tools/src/json-schema.ts) |
| T08 | Typert descriptor、Zod 与 Gateway 分工 | [Typert 原文](source/docs/subsystems/typert.zh.md)、[协议类型](source/packages/typert/protocol/src/types.ts)、[Typert registry 依赖](source/packages/typert/registry/package.json)、[Gateway](source/packages/api/gateway/src/index.ts) |
| T09 | pi-ai 适配器、路由和模型配置 | [pi-ai 接入实现](source/packages/llm/llm-pi-ai/src/index.ts)、[接入原文](source/packages/llm/llm-pi-ai/README.zh.md) |
| T10 | MCP stdio 与 Streamable HTTP 工厂 | [MCP transport](source/packages/mcp/mcp-client/src/transport.ts)、[MCP 原文](source/packages/mcp/mcp-client/README.zh.md) |
| T11 | React、Zustand、Immer 与 Vite | [Web 依赖](source/apps/web/package.json)、[Store 引擎](source/packages/client/store/src/index.ts)、[Store 契约](source/packages/client/store/src/contract.ts)、[Store 依赖](source/packages/client/store/package.json) |
| T12 | Electron、Node Host 与 Renderer 配置 | [桌面依赖](source/apps/desktop/package.json)、[Host 子进程](source/apps/desktop/src/host-process.ts)、[Main](source/apps/desktop/src/main.ts) |
| T13 | workspace、安装脚本策略和分包构建 | [workspace 配置](source/pnpm-workspace.yaml)、[根构建命令](source/package.json) |
| T14 | Vitest 配置、回放位置与消费检查 | [测试配置](source/vitest.config.ts)、[回放实现](source/packages/test-support/llm-replay/src/index.ts)、[回放原文](source/packages/test-support/llm-replay/README.zh.md) |
| T15 | 新 Node 进程、OS 沙箱、绑定与资源限制 | [Node PTC 原文](source/packages/ptc-runtime/ptc-runtime-node/README.zh.md)、[Node PTC 实现](source/packages/ptc-runtime/ptc-runtime-node/src/index.ts)、[Python PTC 原文](source/packages/experimental/ptc-runtime-python/README.zh.md) |

[全书目录](tutorial.md) · [补充能力](subsystems.md) · [源码与文档证据](evidence-index.md)
