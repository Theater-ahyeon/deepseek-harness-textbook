# 可选证据附录：原码节选与完整阅读路线

正文已独立解释项目。这份附录用于复核实现，不是读懂教材的前置要求。节选来自固定提交 639ed015397290b3745d163aafe02ffee4aa3f84，保留原码，省略邻近上下文。

<a id="evidence-01"></a>

## 专题 01｜从一句话到一个结果：智能体运行框架究竟做什么


**接纳入口。** 目标被解析后，已识别请求直接返回 accepted；这不是最终回答。

来源：[实际文件](source/packages/api/session-controller/src/commands.ts)，第 329—335 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/commands.ts#L329)。节选保留原码，省略邻近上下文。

```ts
    const agent = await this.resolveAgent(request.sessionId)
    if (hasPromptRequest(agent, request.requestId)) return { accepted: true }
    const source: MessageSource = {
      kind: 'user',
      rpcId: request.requestId,
      ...(clientTimeZone === undefined ? {} : { clientTimeZone }),
    }
```

**输入交接。** 两种方法都调用 send，但目标队列不同；执行细节在第三章。

来源：[实际文件](source/packages/core/agent-loop/src/agent.ts)，第 163—169 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L163)。节选保留原码，省略邻近上下文。

```ts
  followup(input: UserMessage): void {
    this.send(input, 'next-turn', true)
  }

  steer(input: UserMessage): void {
    this.send(input, 'next-step', true)
  }
```

**调用事实。** 这里追加的是工具调用事实，并返回它的序号，结果会与调用关联。

来源：[实际文件](source/packages/core/agent-loop/src/tool-calls.ts)，第 263—266 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/tool-calls.ts#L263)。节选保留原码，省略邻近上下文。

```ts
function appendToolCall(session: Session, turn: number, step: number, block: ToolCallBlock): SessionSeq {
  const event = session.append('tool/call', { turn, step, callId: block.id, name: block.name, arguments: block.arguments })
  return event.seq
}
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/api/session-controller/src/commands.ts](source/packages/api/session-controller/src/commands.ts)，`SessionCommandController.prompt`。输入：用户内容、requestId 与会话；输出/交接：校验后向 Agent 排入输入；输出接纳结果。[固定提交第 311 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/commands.ts#L311)。
2. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`send / followup / steer；turn / step`。输入：已排入的输入；输出/交接：驱动消费输入并组织模型与工具阶段。[固定提交第 154 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L154)。
3. [packages/core/agent-loop/src/tool-calls.ts](source/packages/core/agent-loop/src/tool-calls.ts)，`executeToolCalls`。输入：成功助手消息里的工具调用；输出/交接：产生有序提交的工具调用与结果；后续步骤可读取结果。[固定提交第 60 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/tool-calls.ts#L60)。


<a id="evidence-02"></a>

## 专题 02｜读懂代码：类型与异步等待


**方法签名与校验。** 签名承诺异步接纳值；有效内容检查仍会在运行时失败。

来源：[实际文件](source/packages/api/session-controller/src/commands.ts)，第 311—317 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/commands.ts#L311)。节选保留原码，省略邻近上下文。

```ts
  async prompt(request: SessionPromptRequest): Promise<SessionPromptValue> {
    if (!hasPromptContent(request.content)) {
      throw new RemoteError(
        'gateway/bad-request',
        'prompt content must include non-whitespace text or an attachment',
        {},
      )
```

**排队与返回。** 调用 followup/steer 后返回接纳值，没有等待最终模型总结。

来源：[实际文件](source/packages/api/session-controller/src/commands.ts)，第 363—376 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/commands.ts#L363)。节选保留原码，省略邻近上下文。

```ts
        using binding = this.ctx.fileUploads.bindPrompt(agent, admission.receiptIds, request.requestId)
        if (request.mode === 'steer') agent.steer(message)
        else agent.followup(message)
        binding.commit()
      } catch (error) {
        if (remoteErrorOf(error) !== undefined) throw error
        if (error instanceof AttachmentError) {
          throw new RemoteError('session/attachment-invalid', error.message, { reason: error.code })
        }
        throw new RemoteError('session/agent-busy', 'prompt rejected', { reason: String(error) })
      }
      return { accepted: true }
    }
    return hasImage ? this.agents.serializeImageAdmission(agent, admit) : admit()
```

**注册定义。** register 收到工具定义；对象中的 execute 要等具体调用才执行。

来源：[实际文件](source/packages/fs/tool-fs/src/read.ts)，第 77—84 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L77)。节选保留原码，省略邻近上下文。

```ts
  ctx.tools.register(defineTool({
    name: 'read',
    description: 'Read a UTF-8 text file and return line-numbered content.',
    parameters: {
      file_path: { type: 'string', required: true, description: 'Path to read, resolved by the filesystem backend.' },
      offset: { type: 'number', description: '1-based first line to return. Defaults to 1.' },
      limit: { type: 'number', description: `Maximum number of lines to return. Defaults to ${caps.limit}.` },
    },
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/api/session-controller/src/commands.ts](source/packages/api/session-controller/src/commands.ts)，`SessionCommandController.prompt`。输入：带类型的请求对象；输出/交接：验证分支与接纳结果；转入消息队列。[固定提交第 311 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/commands.ts#L311)。
2. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`send / followup / steer`。输入：输入内容与进入方式；输出/交接：将输入放入 inbox；驱动消费是另一段行为。[固定提交第 154 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L154)。
3. [packages/fs/tool-fs/src/read.ts](source/packages/fs/tool-fs/src/read.ts)，`applyReadTool`。输入：具备工具服务的上下文；输出/交接：注册 read 定义和 execute 回调；此时没有用户文件读取结果。[固定提交第 68 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L68)。


<a id="evidence-03"></a>

## 专题 03｜循环与消息队列：一轮任务为什么需要多步


**进入时点。** 比较 next-turn、next-step 以及最后一个布尔值，理解目标与唤醒。

来源：[实际文件](source/packages/core/agent-loop/src/agent.ts)，第 163—173 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L163)。节选保留原码，省略邻近上下文。

```ts
  followup(input: UserMessage): void {
    this.send(input, 'next-turn', true)
  }

  steer(input: UserMessage): void {
    this.send(input, 'next-step', true)
  }

  inject(input: UserMessage): void {
    this.send(input, 'next-step', false)
  }
```

**轮次与前置拒绝。** 先记录轮次开始，再询问前置决定；拒绝可以发生在模型步骤进入之前。

来源：[实际文件](source/packages/core/agent-loop/src/agent.ts)，第 303—319 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L303)。节选保留原码，省略邻近上下文。

```ts
    const turn = phase.turn + 1
    try {
      this.session.append('turn/start', { turn })
    } catch (error: unknown) {
      this.throwError(error)
    }
    phase.turn = turn
    let turnEnds: TurnEndReason | null = null
    let target: InboxTarget = 'next-turn'
    try {
      while (true) {
        signal.throwIfAborted()
        const step = phase.step + 1
        const decision = await this.preStep(target, { turn, step })
        if (decision.kind === 'reject') {
          turnEnds = { kind: 'blocked' }
          return false
```

**工具与继续。** 没有工具调用时返回完成；否则执行批次并根据 concluded 决定本步继续结果。

来源：[实际文件](source/packages/core/agent-loop/src/agent.ts)，第 530—538 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L530)。节选保留原码，省略邻近上下文。

```ts
        if (finish.kind === 'max-tokens') return { kind: 'max-tokens' }

        const toolCalls = message.content.filter(block => block.type === 'tool-call')
        if (toolCalls.length === 0) return { kind: 'completed' }
        const { concluded } = await executeToolCalls(
          this.loopCtx, turn, step, toolCalls, signal,
          context => this.inbox.splice('next-step', this.inbox.nextStep.length, 0, [context]),
        )
        return concluded ? { kind: 'completed' } : null
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`followup / steer / inject`。输入：输入和进入方式；输出/交接：更新 inbox 并按方式触发驱动。[固定提交第 154 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L154)。
2. [packages/core/agent-loop/src/inbox.ts](source/packages/core/agent-loop/src/inbox.ts)，`mutate`。输入：插入、领取或删除的变更；输出/交接：先更新投影状态，再通知观察者。[固定提交第 198 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/inbox.ts#L198)。
3. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`wakeDriver → kick → turn`。输入：待处理输入；输出/交接：开放轮次并领取输入；进入 preStep。[固定提交第 214 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L214)。
4. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`preStep → step`。输入：被领取的输入与已装配材料；输出/交接：准入后执行步骤；模型成功分支走工具阶段。[固定提交第 267 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L267)。
5. [packages/core/agent-loop/src/tool-calls.ts](source/packages/core/agent-loop/src/tool-calls.ts)，`executeToolCalls`。输入：工具调用批次；输出/交接：完成工具阶段，返回驱动决定继续或停止。[固定提交第 60 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/tool-calls.ts#L60)。


<a id="evidence-04"></a>

## 专题 04｜沿文件读取工具追到底：模型怎样得到材料


**参数解析。** 起始行和数量补默认，非空路径与上限仍有显式检查。

来源：[实际文件](source/packages/fs/tool-fs/src/read.ts)，第 55—60 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L55)。节选保留原码，省略邻近上下文。

```ts
export function parseReadArgs(args: { file_path: string; offset?: number; limit?: number }, maxLimit: number): ReadInput {
  if (args.file_path.trim().length === 0) throw new Error('file_path must be a non-empty string')
  const offset = args.offset === undefined ? 1 : parsePositiveInteger(args.offset, 'offset')
  const limit = args.limit === undefined ? maxLimit : parsePositiveInteger(args.limit, 'limit')
  if (limit > maxLimit) throw new Error(`limit must be less than or equal to ${maxLimit}`)
  return { filePath: args.file_path, offset, limit }
```

**服务与窗口。** 路径先解析；大或大小未知的文件使用流，随后按多项限制构造窗口。

来源：[实际文件](source/packages/fs/tool-fs/src/read.ts)，第 141—152 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L141)。节选保留原码，省略邻近上下文。

```ts
      const { target, info } = await resolveRegularReadTarget(ctx, exec, input.filePath)

      // Stream when the file is large OR size is unknown, so a size-less backend
      // never buffers an arbitrarily large file.
      const chunks = info.size === undefined || info.size >= caps.streamMinSize
        ? await ctx.fs.streamText(target, exec.signal)
        : [await ctx.fs.readText(target, exec.signal)]
      const window = await buildWindow(
        chunks,
        { offset: input.offset, limit: input.limit, maxLineLength: caps.maxLineLength, maxBytes: caps.maxBytes },
        target.displayPath,
      )
```

**规范结果与通知。** 返回的是有边界的结构化值，观察通知另有用途，模型文本由输出契约生成。

来源：[实际文件](source/packages/fs/tool-fs/src/read.ts)，第 154—164 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L154)。节选保留原码，省略邻近上下文。

```ts
      const outcome = {
        path: target.displayPath,
        offset: input.offset,
        lines: window.lines,
        totalLines: window.totalLines,
      }
      // Record the present observation (a no-op when no policy plugin listens). The
      // read already succeeded; an fs/observed listener is contractually a
      // synchronous, side-effect-only recorder.
      ctx.emit('fs/observed', target, { kind: 'present', version: info.version }, exec)
      return outcome
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/fs/tool-fs/src/index.ts](source/packages/fs/tool-fs/src/index.ts)，`apply`。输入：插件配置与注入的工具/文件服务；输出/交接：调用 applyReadTool 注册能力；这是启动前置。[固定提交第 54 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/index.ts#L54)。
2. [packages/fs/tool-fs/src/read.ts](source/packages/fs/tool-fs/src/read.ts)，`parseReadArgs / applyReadTool`。输入：工具定义与模型参数；输出/交接：校验参数，确定 execute 的文件读取与呈现契约。[固定提交第 55 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L55)。
3. [packages/core/agent-loop/src/tool-calls.ts](source/packages/core/agent-loop/src/tool-calls.ts)，`executeToolCalls`。输入：成功消息的工具调用；输出/交接：交给工具服务，按序记录调用和结果。[固定提交第 60 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/tool-calls.ts#L60)。
4. [packages/core/tools/src/index.ts](source/packages/core/tools/src/index.ts)，`prepareExecution → dispatch`。输入：工具名、参数与执行上下文；输出/交接：准入后调用已注册执行体；返回规范结果。[固定提交第 1493 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/tools/src/index.ts#L1493)。


<a id="evidence-05"></a>

## 专题 05｜会话与日志：发生过的事怎样保存和还原


**稳定事件。** 条目包含序号与时间，并经过冻结和约束检查。

来源：[实际文件](source/packages/core/session/src/index.ts)，第 744—752 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/session/src/index.ts#L744)。节选保留原码，省略邻近上下文。

```ts
    const event = deepFreeze({
      type,
      seq: SessionSeq(this.log.length),
      time: Date.now(),
      data: dataSnapshot,
      ...(surfaceMetadataSnapshot as { surfaceOp?: unknown; sourceEventSeqs?: unknown }),
    } as unknown as SessionEvent<T>)
    validateSessionEventData(event, `session event "${type}" at seq ${event.seq}`)
    this.surfaceManager.validateNext(event as SessionEvent)
```

**消息派生。** 当前表层节点产生相应消息；方法返回消息数组副本，不是整份日志。

来源：[实际文件](source/packages/core/session/src/index.ts)，第 869—880 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/session/src/index.ts#L869)。节选保留原码，省略邻近上下文。

```ts
    for (const seq of nodes.slice(this.derivedNodes)) {
      // Surface sequences are built from this.log — seq is always a valid
      // index by construction. The non-null assertion expresses that invariant.
      // oxlint-disable-next-line typescript/no-non-null-assertion
      const msg = this.deriveEventMessage(this.log[seq]!)
      // A surface node is one of the five message-producing types, but an
      // empty-content assistant/message (a max-tokens step that hosts only
      // usage) derives to null and must not enter the transcript.
      if (msg) this.derived.push(msg)
    }
    this.derivedNodes = nodes.length
    return [...this.derived]
```

**事件写入与刷新。** 事件监听排队，flush 监听等待缓冲排空与 writer 刷新。

来源：[实际文件](source/packages/session/session-persistence-jsonl/src/storage.ts)，第 535—546 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-persistence-jsonl/src/storage.ts#L535)。节选保留原码，省略邻近上下文。

```ts
    ctx.on('session/event', (session: Session, event) => {
      this.writers.get(session.id)?.enqueueLive(event, (error) => {
        ctx.logger.warn(`session-persistence: background write for session "${session.id}" failed (buffered events retained): ${String(error)}`)
      })
    })
    ctx.on('session/flush', (session: Session) => {
      const writer = this.writers.get(session.id)
      if (writer === null || writer === undefined) return undefined
      return (async () => {
        await writer.drainLive()
        await writer.flush()
      })()
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/core/session/src/index.ts](source/packages/core/session/src/index.ts)，`Session.append`。输入：新事件；输出/交接：更新内存事实并通知；观察不同消费方。[固定提交第 722 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/session/src/index.ts#L722)。
2. [packages/core/session/src/index.ts](source/packages/core/session/src/index.ts)，`deriveMessages`。输入：事件日志；输出/交接：输出模型消息视图；是派生路径而非落盘步骤。[固定提交第 860 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/session/src/index.ts#L860)。
3. [packages/session/session-projection/src/index.ts](source/packages/session/session-projection/src/index.ts)，`投影注册与事件消费`。输入：会话事件与投影定义；输出/交接：更新可供 stateOf 查询的状态。[固定提交第 199 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-projection/src/index.ts#L199)。
4. [packages/session/session-persistence-jsonl/src/storage.ts](source/packages/session/session-persistence-jsonl/src/storage.ts)，`enqueueLive / flush`。输入：监听到的持久事件；输出/交接：排队写入；flush 等待队列完成，失败有自己的处理。[固定提交第 274 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-persistence-jsonl/src/storage.ts#L274)。


<a id="evidence-06"></a>

## 专题 06｜提示词与项目指令：下一次模型输入怎样形成


**作用域与工具贡献。** 先合并作用域里的贡献，再取得可见工具 schema；参数在组装中被复制。

来源：[实际文件](source/packages/core/system-prompt/src/index.ts)，第 574—590 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/system-prompt/src/index.ts#L574)。节选保留原码，省略邻近上下文。

```ts
    // Scoped sections shadow globals before the deterministic order sort.
    const sectionByName = this.layers.merge(scope, layer => layer.sections)
    const contextByName = this.layers.merge(scope, layer => layer.contexts)
    // Validate order against pre-restriction names while collecting visible schemas.
    const providers = [
      ...this.layers.global.toolProviders.values(),
      ...scopeLayers.flatMap(layer => [...layer.toolProviders.values()]),
    ]
    const collected: ToolSchema[] = []
    const knownNames = new Set<string>()
    for (const provider of providers) {
      const result = provider(context)
      const schemas = result.schemas.map(({ name, description, parameters, deferLoading }): ToolSchema => ({
        name,
        description,
        parameters: structuredClone(parameters),
        ...deferLoading === true ? { deferLoading } : {},
```

**指令消息进入。** 需要的指令材料按进入批次的位置插入，不是简单读文件后直接改系统字符串。

来源：[实际文件](source/packages/context/agent-instructions/src/index.ts)，第 332—340 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/context/agent-instructions/src/index.ts#L332)。节选保留原码，省略邻近上下文。

```ts
    for (const message of pending) agent.inbox.remove(message.id)
    if (desired === undefined || decision.messages.some(message => sameContextPayload(message, desired))) {
      return decision
    }
    // Fold the context right after the claimed batch, so the direct prompt
    // precedes it and the driver-appended runtime context follows it.
    const lastClaimedIndex = decision.messages.findLastIndex(message => messages.includes(message))
    const entered = decision.messages.toSpliced(lastClaimedIndex + 1, 0, desired)
    return { ...decision, messages: entered }
```

**首次提交。** firstAttempt 控制用户消息只在本步第一次提交；后面据日志构造请求。

来源：[实际文件](source/packages/core/agent-loop/src/agent.ts)，第 419—425 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L419)。节选保留原码，省略邻近上下文。

```ts
      if (firstAttempt) {
        for (const message of decision.messages) {
          this.session.append('user/message', message, { surfaceOp: 'append' })
        }
      }
      firstAttempt = false
      const request = this.buildRequest(config, preparedCall, assembly.tools, { turn, step }, startsRequestSeries, signal)
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/core/system-prompt/src/index.ts](source/packages/core/system-prompt/src/index.ts)，`SystemPrompt.section / context / assemble`。输入：注册的有序贡献；输出/交接：产生已渲染组装；先读契约与组装。[固定提交第 405 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/system-prompt/src/index.ts#L405)。
2. [packages/context/agent-instructions/src/index.ts](source/packages/context/agent-instructions/src/index.ts)，`apply → compose`。输入：项目范围与指令文件；输出/交接：贡献对应材料；作为上一项的生产方回查。[固定提交第 84 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/context/agent-instructions/src/index.ts#L84)。
3. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`preStep`。输入：待进入步骤与提示材料；输出/交接：组装及准入后的步骤输入。[固定提交第 267 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L267)。
4. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`prepareRequest → buildRequest`。输入：已准备调用、Session 日志与材料；输出/交接：提交并冻结发给模型的请求。[固定提交第 547 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L547)。


<a id="evidence-07"></a>

## 专题 07｜技能的按需读取：目录可见为什么不等于正文已加载


**摘要列表。** list 返回 snapshot 的摘要，不返回每份完整正文。

来源：[实际文件](source/packages/skill/skill/src/index.ts)，第 470—472 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/skill/src/index.ts#L470)。节选保留原码，省略邻近上下文。

```ts
  async list(options: SkillViewOptions = {}): Promise<SkillSummary[]> {
    return (await this.snapshot(options)).skills
  }
```

**模型工具路径。** 先查可见摘要和模型调用许可，再取得正文；读取失败有明确分支。

来源：[实际文件](source/packages/skill/tool-skill/src/index.ts)，第 133—143 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/tool-skill/src/index.ts#L133)。节选保留原码，省略邻近上下文。

```ts
      const lookup = { cwd: exec.agent?.session.header.cwd, signal: exec.signal, scope: exec.agent }
      const summary = (await ctx.skills.list(lookup)).find(skill => skill.name === args.name)
      if (!summary) {
        throw new Error(`skill "${args.name}" is unknown or no longer available`)
      }
      if (!isModelInvocable(summary)) {
        throw new Error(`skill "${args.name}" is not available for model invocation`)
      }
      const skill = await ctx.skills.get(args.name, lookup)
      if (!skill) {
        throw new Error(`skill "${args.name}" is unknown or no longer available`)
```

**直接用户路径。** 允许用户调用的完整定义变成带 skill-invocation 来源的指令消息。

来源：[实际文件](source/packages/skill/tool-skill/src/index.ts)，第 189—200 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/tool-skill/src/index.ts#L189)。节选保留原码，省略邻近上下文。

```ts
      const skill = await ctx.skills.get(name, lookup)
      signal.throwIfAborted()
      // Unknown names and user-disabled skills stay plain prose: the
      // gesture was never a claim this boundary recognizes. The check sits
      // on the loaded definition — the single lookup that produces what is
      // actually injected.
      if (skill === undefined || !isUserInvocable(skill)) continue
      const source: SkillInvocationSource = { kind: 'skill-invocation', name, form: 'instructions' }
      injections.push(createUserMessage({
        content: [{ type: 'text', text: renderSkillContent(skill) }],
        source,
      }))
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/skill/skill/src/index.ts](source/packages/skill/skill/src/index.ts)，`SkillRegistry.registerProvider / list / get`。输入：提供方与技能名；输出/交接：定义目录与正文契约。[固定提交第 356 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/skill/src/index.ts#L356)。
2. [packages/skill/skill-filesystem/src/index.ts](source/packages/skill/skill-filesystem/src/index.ts)，`FileSystemSkillProvider.list / get`。输入：文件目录或指定名称；输出/交接：返回技能描述或正文；是注册表的具体提供方。[固定提交第 150 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/skill-filesystem/src/index.ts#L150)。
3. [packages/skill/tool-skill/src/index.ts](source/packages/skill/tool-skill/src/index.ts)，`apply；execute`。输入：技能服务及模型给出的名称；输出/交接：先贡献目录，调用时 get 正文并返回工具结果。[固定提交第 77 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/skill/tool-skill/src/index.ts#L77)。


<a id="evidence-08"></a>

## 专题 08｜上下文压缩：让历史变短需要付出什么


**压力触发。** 前置链尝试压缩，失败会记录警告并继续；不能把警告解释成压缩已成功。

来源：[实际文件](source/packages/compaction/compaction-basic/src/index.ts)，第 158—175 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-basic/src/index.ts#L158)。节选保留原码，省略邻近上下文。

```ts
    ctx.on('agent/pre-step', async (
      { agent, signal },
      next,
    ): Promise<PreStepDecision> => {
      if (!signal.aborted) {
        try {
          const result = await this.compactIfNeeded(agent, 'pressure', signal)
          if (result !== null) logResult(result, 'step pressure')
        } catch (error: unknown) {
          if (error instanceof TargetPressureConfigError) {
            if (this.warnedPressureConfigTargets.has(error.targetKey)) return next()
            this.warnedPressureConfigTargets.add(error.targetKey)
          }
          const message = error instanceof Error ? error.message : String(error)
          ctx.logger.warn(`step compaction failed: ${message}; continuing the turn`)
        }
      }
      return next()
```

**区域选择。** 溢出路径在可选剪枝后选择可压缩范围，没有范围则返回 null。

来源：[实际文件](source/packages/compaction/compaction-basic/src/index.ts)，第 294—301 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-basic/src/index.ts#L294)。节选保留原码，省略邻近上下文。

```ts
    if (trigger === 'context-overflow') {
      if (prune !== undefined) {
        prune.pruneSession(agent.session)
        measurement = meter.measure(agent.session)
      }
      const range = selectCompactableRange(agent.session, measurement, 0)
      if (range === null) return null
      return this.compactRegion(range.start, range.end, agent, signal)
```

**稳定性与提交。** 摘要后先检查稳定性，再提交压缩体并闭合；失败路径记录错误结束。

来源：[实际文件](source/packages/compaction/compaction-basic/src/region.ts)，第 232—245 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-basic/src/region.ts#L232)。节选保留原码，省略邻近上下文。

```ts
    if (options.owner === null) signal?.throwIfAborted()
    assertStable(dependencies, session, summarized)
    stage = 'commit'
    const pending = commitCompactionBody(session, startEvent, summarized)
    closing = true
    const endEvent = session.append('compaction/end', lifecycle)
    closed = true
    result = completeCompaction(pending, endEvent)
  } catch (error: unknown) {
    failure = { error, stage: closing ? 'commit' : stage }
    if (!closing) {
      closing = true
      try {
        session.append('compaction/end', { ...lifecycle, error: errorChain(error) })
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/compaction/compaction-basic/src/index.ts](source/packages/compaction/compaction-basic/src/index.ts)，`事件绑定 → compactIfNeeded`。输入：pre-step 或请求错误及上下文条件；输出/交接：判断是否进入压缩流程。[固定提交第 148 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-basic/src/index.ts#L148)。
2. [packages/compaction/compaction-basic/src/region.ts](source/packages/compaction/compaction-basic/src/region.ts)，`区域选择与 compactSurfaceRegion`。输入：可压缩历史区域；输出/交接：确定范围并组织表层替换流程。[固定提交第 117 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-basic/src/region.ts#L117)。
3. [packages/compaction/compaction-basic/src/summarizer.ts](source/packages/compaction/compaction-basic/src/summarizer.ts)，`summarizeWithLlm`。输入：选定历史材料；输出/交接：通过 LLM 取得摘要；由区域流程消费。[固定提交第 120 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/compaction/compaction-basic/src/summarizer.ts#L120)。
4. [packages/core/session/src/index.ts](source/packages/core/session/src/index.ts)，`deriveMessages`。输入：含表层替换事实的日志；输出/交接：重建后续模型使用的消息视图。[固定提交第 860 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/session/src/index.ts#L860)。


<a id="evidence-09"></a>

## 专题 09｜流式输出与重试：一次失败怎样留在同一步里


**绑定调用。** 服务找到 provider 注册并准备适配器调用，再解析和冻结配置。

来源：[实际文件](source/packages/llm/llm/src/index.ts)，第 936—941 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/llm/src/index.ts#L936)。节选保留原码，省略邻近上下文。

```ts
  async prepareCall(config: LlmCallConfig, signal?: AbortSignal): Promise<PreparedLlmCall> {
    const registration = this.registration(config.provider)
    const adapterCall = await registration.adapter.prepareCall(config.provider, config.model, signal)
    const modelInfo = this.normalizeModelInfo(registration, config.model, adapterCall.model)
    const resolved = this.resolveCallWithInfo(config, modelInfo)
    const resolvedConfig = deepFreeze(structuredClone(resolved.config))
```

**片段消费。** 临时流在逐次取消检查中推进，不等同于最终消息提交。

来源：[实际文件](source/packages/core/agent-loop/src/agent.ts)，第 436—443 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L436)。节选保留原码，省略邻近上下文。

```ts
        const stream = preparedCall?.stream(request) ?? this.loopCtx.llm.stream(request)
        signal.throwIfAborted()
        live.start()
        started = true
        for await (const chunk of stream) {
          signal.throwIfAborted()
          live.push(chunk)
        }
```

**重试边界。** 只有错误恢复返回 retry 才 continue 当前尝试循环，否则抛出错误。

来源：[实际文件](source/packages/core/agent-loop/src/agent.ts)，第 505—509 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L505)。节选保留原码，省略邻近上下文。

```ts
          signal.throwIfAborted()
          if (action?.kind !== 'retry') {
            throw new LlmError(finish.failure.message, finish.failure.code, finish.failure)
          }
          continue
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`prepareRequest`。输入：本步的材料与取消信号；输出/交接：进入 LLM prepared call 准备。[固定提交第 547 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L547)。
2. [packages/llm/llm/src/index.ts](source/packages/llm/llm/src/index.ts)，`prepareCall`。输入：模型配置与 signal；输出/交接：找到并绑定 provider；输出调用能力。[固定提交第 936 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/llm/src/index.ts#L936)。
3. [packages/llm/llm-deepseek/src/adapter.ts](source/packages/llm/llm-deepseek/src/adapter.ts)，`DeepSeekAdapter.prepareCall / stream`。输入：配置、材料及已绑定调用；输出/交接：产生模型流；作为具体提供方阅读。[固定提交第 20 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/llm-deepseek/src/adapter.ts#L20)。
4. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`step 与 for-await 分支`。输入：chunks、错误或取消；输出/交接：提交消息或 attempt；失败走 request-error。[固定提交第 398 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L398)。
5. [packages/llm/llm-retry/src/index.ts](source/packages/llm/llm-retry/src/index.ts)，`退避与 recover`。输入：错误及重试上下文；输出/交接：返回重试动作或保留原错误；策略不属于固定循环。[固定提交第 149 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/llm-retry/src/index.ts#L149)。


<a id="evidence-10"></a>

## 专题 10｜插件框架与运行配置：这些部件怎样装成一个应用


**启动入口。** profile 模式把选择、补丁和参数交给共享运行器。

来源：[实际文件](source/apps/cli/src/bin.ts)，第 31—42 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/cli/src/bin.ts#L31)。节选保留原码，省略邻近上下文。

```ts
  switch (invocation.mode) {
    case 'profile': {
      const { runProfile } = await import('./profile-boot.ts')
      try {
        await runProfile({
          environment: loadLayeredEnv('dsh'),
          profile: invocation.profile,
          fromDefaultProfile: invocation.fromDefaultProfile,
          patchFiles: invocation.patches,
          args: invocation.args,
          ...profileOptions,
        })
```

**顺序组合。** 层数组按顺序展开后应用到空条目列表，不是随意改变合并顺序。

来源：[实际文件](source/packages/boot/app-boot/src/profile.ts)，第 731—737 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/boot/app-boot/src/profile.ts#L731)。节选保留原码，省略邻近上下文。

```ts
export function composeEntries(
  layers: readonly PatchOptions[][], warn: (message: string) => void = () => {},
): EntryOptions[] {
  return applyEntryPatches([], structuredClone(layers.flat()), (message: string, ...args: unknown[]) => {
    let index = 0
    warn(message.replace(/%C/g, () => JSON.stringify(args[index++])))
  })
```

**消费者插件。** 文件插件通过上下文服务契约建立工具；具体服务由应用树满足。

来源：[实际文件](source/packages/fs/tool-fs/src/index.ts)，第 54—64 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/index.ts#L54)。节选保留原码，省略邻近上下文。

```ts
export function apply(ctx: Context, config: Config): void {
  // schemastery (Config) has already filled every defaulted field.
  const resolved = config as ResolvedConfig
  assertPositiveInteger('readLimit', resolved.readLimit)
  assertPositiveInteger('readMaxLineLength', resolved.readMaxLineLength)
  assertPositiveInteger('readMaxBytes', resolved.readMaxBytes)
  assertPositiveInteger('readStreamMinSize', resolved.readStreamMinSize)
  applyReadTool(ctx, {
    limit: resolved.readLimit,
    maxLineLength: resolved.readMaxLineLength,
    maxBytes: resolved.readMaxBytes,
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [apps/cli/src/bin.ts](source/apps/cli/src/bin.ts)，`runCli`。输入：CLI 参数；输出/交接：解析启动模式并转入 profile runner。[固定提交第 26 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/cli/src/bin.ts#L26)。
2. [apps/cli/src/profile-boot.ts](source/apps/cli/src/profile-boot.ts)，`runProfile`。输入：profile 名称与 patches；输出/交接：取得 profile 配置，准备运行应用。[固定提交第 244 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/cli/src/profile-boot.ts#L244)。
3. [packages/boot/app-boot/src/profile.ts](source/packages/boot/app-boot/src/profile.ts)，`loadProfile → composeEntries`。输入：profile 和依次叠加的层；输出/交接：输出最终 Cordis entries。[固定提交第 704 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/boot/app-boot/src/profile.ts#L704)。
4. [packages/boot/app-boot/src/index.ts](source/packages/boot/app-boot/src/index.ts)，`boot`。输入：已组合条目；输出/交接：挂载配置树；服务可由插件贡献。[固定提交第 972 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/boot/app-boot/src/index.ts#L972)。


<a id="evidence-11"></a>

## 专题 11｜工具准入与审批：允许执行的决定在哪里发生


**前置与询问。** 先运行前置决策，只有 ask 才进入审批服务路径。

来源：[实际文件](source/packages/core/tools/src/index.ts)，第 1504—1511 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/tools/src/index.ts#L1504)。节选保留原码，省略邻近上下文。

```ts
      const carrier = scopeTarget(this, exec.agent)
      const gate = await this.ctx.waterfall(
        carrier, 'tools/pre-execute', exec,
        () => Promise.resolve<PreToolDecision>({ kind: 'allow' }),
      )
      const askResolution = gate.kind === 'ask'
        ? await this.serviceAsk(exec, gate)
        : { decision: gate, approvalCancelled: false }
```

**审批事实。** 询问与决定成对记录；返回的是本次 outcome。

来源：[实际文件](source/packages/interaction/user-approval/src/index.ts)，第 224—233 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/interaction/user-approval/src/index.ts#L224)。节选保留原码，省略邻近上下文。

```ts
    const id = ApprovalRequestId(randomUUID())
    session.append('approval/asked', {
      id,
      toolName: req.toolName,
      ...req.callId !== undefined ? { callId: req.callId } : {},
      ...req.reason !== undefined ? { reason: req.reason } : {},
    })
    const outcome = await this.decide(req, session)
    session.append('approval/decided', { id, outcome })
    return outcome
```

**真实执行体。** bodyInvoked 与 execute 指出实际进入点；执行抛错被转为工具错误。

来源：[实际文件](source/packages/core/tools/src/index.ts)，第 1578—1587 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/tools/src/index.ts#L1578)。节选保留原码，省略邻近上下文。

```ts
      const tool = this.resolveExecution(exec.name, exec.agent, exec.parent !== undefined)
      if (!tool) throw new ToolNotFoundError(exec.name)
      state.bodyInvoked = true
      const returned = await tool.execute(exec.arguments, exec)
      const result = this.createSuccessResult(exec, tool, returned)
      return isAborted(signal)
        ? toolAbortedResult(result)
        : result
    } catch (error: unknown) {
      return toolErrorResult(error)
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/core/agent-loop/src/tool-calls.ts](source/packages/core/agent-loop/src/tool-calls.ts)，`executeToolCalls`。输入：工具批次；输出/交接：记录调用并交给工具服务。[固定提交第 60 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/tool-calls.ts#L60)。
2. [packages/core/tools/src/index.ts](source/packages/core/tools/src/index.ts)，`prepareExecution`。输入：调用与策略上下文；输出/交接：pre → 可选 ask → guard；进入或跳过工具体。[固定提交第 1493 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/tools/src/index.ts#L1493)。
3. [packages/interaction/user-approval/src/index.ts](source/packages/interaction/user-approval/src/index.ts)，`审批请求`。输入：需要一次回答的审批内容；输出/交接：取得回答并产生相关事实；是 ask 分支的提供方。[固定提交第 215 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/interaction/user-approval/src/index.ts#L215)。
4. [packages/core/tools/src/index.ts](source/packages/core/tools/src/index.ts)，`dispatch 与 post-execute`。输入：获准调用或拒绝结果；输出/交接：执行及后处理，形成模型面对的最终结果。[固定提交第 1564 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/tools/src/index.ts#L1564)。


<a id="evidence-12"></a>

## 专题 12｜外部服务与能力接入：连接成功不等于拥有知识库


**名称包装。** 简单名字直接拼接，其他情况会规范化并添加哈希。

来源：[实际文件](source/packages/mcp/mcp-client/src/tools.ts)，第 81—86 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-client/src/tools.ts#L81)。节选保留原码，省略邻近上下文。

```ts
export function publicToolName(serverName: string, rawName: string): string {
  const joined = `mcp__${serverName}__${rawName}`
  const normalized = joined.replace(INVALID_NAME_CHARS, '_')
  if (normalized === joined && normalized.length <= MAX_PUBLIC_NAME_LENGTH) return normalized
  const hash = createHash('sha256').update(`${serverName}\0${rawName}`).digest('hex').slice(0, HASH_LENGTH)
  return `${normalized.slice(0, MAX_PUBLIC_NAME_LENGTH - HASH_LENGTH - 1)}_${hash}`
```

**远端调用与注册。** 包装回调调用原远端工具名；之后把新定义注册到现有 Tools。

来源：[实际文件](source/packages/mcp/mcp-client/src/tools.ts)，第 138—150 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-client/src/tools.ts#L138)。节选保留原码，省略邻近上下文。

```ts
      call: (args, execution) => client.callTool(
        { name: tool.name, arguments: args },
        { signal: execution.signal, timeout: opts.toolCallTimeoutMs, toolDefinition: tool },
      ),
    }))
  }

  // Phase 2: swap generations.
  for (const dispose of previous.values()) dispose()
  const disposers: ToolDisposers = new Map()
  try {
    for (const [publicName, definition] of definitions) {
      disposers.set(publicName, ctx.tools.register(definition))
```

**工具契约。** 远端说明、参数、输出和执行体进入普通 ToolDefinition 结构。

来源：[实际文件](source/packages/mcp/mcp-client/src/tools.ts)，第 229—236 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-client/src/tools.ts#L229)。节选保留原码，省略邻近上下文。

```ts
  const { name, rawName, description, inputSchema } = options
  const projections = new WeakMap<ToolExecution, PreparedProjection>()
  return {
    name,
    description,
    parameters: inputSchema,
    output: createOutput(rawName, supportedOutputSchema(options.outputSchema)),
    execute: createExecutor(ctx, options, projections),
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/mcp/mcp-client/src/index.ts](source/packages/mcp/mcp-client/src/index.ts)，`apply`。输入：MCP 服务配置；输出/交接：准备连接、发现与能力注册。[固定提交第 154 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-client/src/index.ts#L154)。
2. [packages/mcp/mcp-client/src/connection.ts](source/packages/mcp/mcp-client/src/connection.ts)，`startConnection → connectGeneration`。输入：服务器连接配置；输出/交接：形成连接代次并进入能力发现。[固定提交第 127 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-client/src/connection.ts#L127)。
3. [packages/mcp/mcp-client/src/tools.ts](source/packages/mcp/mcp-client/src/tools.ts)，`publicToolName / syncTools / createMcpToolDef`。输入：服务名与远端工具定义；输出/交接：包装名称和执行体，注册为现有 Tools 能力。[固定提交第 81 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-client/src/tools.ts#L81)。
4. [packages/mcp/mcp-resources/src/index.ts](source/packages/mcp/mcp-resources/src/index.ts)，`资源插件入口`。输入：资源能力与上下文；输出/交接：独立资源接口；对照工具接入，不假定统一 ctx.mcp 服务。[固定提交第 47 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/mcp/mcp-resources/src/index.ts#L47)。


<a id="evidence-13"></a>

## 专题 13｜子代理：拆分任务前先看上下文起点


**运行校验。** Runtime 选择提供方并检查能力、深度与输出契约后启动。

来源：[实际文件](source/packages/subagent/subagent/src/index.ts)，第 559—570 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent/src/index.ts#L559)。节选保留原码，省略邻近上下文。

```ts
  async start(name: string, request: SubagentStartRequest): Promise<SubagentRun> {
    const provider = this.expectProvider(name)
    this.assertCapabilities(provider, request)
    assertSubagentMaxDepth(request.maxDepth)
    if (request.outputSchema !== undefined) assertObjectJsonSchema(request.outputSchema)
    const descriptor = snapshotSubagentDescriptor({
      mode: 'one-shot',
      provider: name,
      ...request.label !== undefined ? { label: request.label } : {},
    })
    const resolved: ResolvedSubagentStartRequest = { ...request, descriptor }
    const run = await provider.start(resolved)
```

**新起点。** 空种子表示不继承父历史，交给共享进程内驱动运行。

来源：[实际文件](source/packages/subagent/subagent-spawn-in-process/src/index.ts)，第 54—59 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent-spawn-in-process/src/index.ts#L54)。节选保留原码，省略邻近上下文。

```ts
  start(request: ResolvedSubagentStartRequest) {
    // Fresh child: no seed. The shared driver mints ids, stamps cwd/lineage/
    // depth, drives the one-shot (including the structured capture when the
    // request carries an outputSchema), and maps the result.
    return startInProcessRun(request, {})
  }
```

**完成前缀。** 最后一个 turn/end 决定种子边界；没有已完成轮次时返回空数组。

来源：[实际文件](source/packages/subagent/subagent-fork-in-process/src/index.ts)，第 48—55 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent-fork-in-process/src/index.ts#L48)。节选保留原码，省略邻近上下文。

```ts
function completedTurnPrefix(parent: Agent): SessionEvent[] {
  // oxlint-disable-next-line typescript/no-deprecated -- Existing Session history read; migration deferred.
  const events = parent.session.snapshotEvents()
  const lastEnd = events.findLast(e => e.type === 'turn/end')
  if (lastEnd === undefined) return []
  // seq === array index (the append contract), so slice up to and including it.
  return events.slice(0, lastEnd.seq + 1)
}
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/subagent/tool-subagent/src/index.ts](source/packages/subagent/tool-subagent/src/index.ts)，`apply；execute；start / startContinuable`。输入：任务与工具配置；输出/交接：请求 Runtime 建立一次性或可继续运行。[固定提交第 313 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/tool-subagent/src/index.ts#L313)。
2. [packages/subagent/subagent/src/index.ts](source/packages/subagent/subagent/src/index.ts)，`SubagentRuntime`。输入：提供方名称与能力要求；输出/交接：校验后分派并管理句柄。[固定提交第 200 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent/src/index.ts#L200)。
3. [packages/subagent/subagent-spawn-in-process/src/index.ts](source/packages/subagent/subagent-spawn-in-process/src/index.ts)，`start`。输入：spawn 请求；输出/交接：建立独立子 Session，进入 in-process driver。[固定提交第 54 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent-spawn-in-process/src/index.ts#L54)。
4. [packages/subagent/subagent-in-process-driver/src/index.ts](source/packages/subagent/subagent-in-process-driver/src/index.ts)，`startInProcessRun`。输入：子 Session 与运行参数；输出/交接：驱动子代理执行并交付运行结果。[固定提交第 104 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent-in-process-driver/src/index.ts#L104)。
5. [packages/subagent/subagent-fork-in-process/src/index.ts](source/packages/subagent/subagent-fork-in-process/src/index.ts)，`completedTurnPrefix`。输入：父历史；输出/交接：作为 fork 分支对照，取得已完成前缀。[固定提交第 47 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/subagent/subagent-fork-in-process/src/index.ts#L47)。


<a id="evidence-14"></a>

## 专题 14｜网页端：提交任务与跟随结果是两条链


**本地提交记录。** 这段建立暂态提交，并协调附件退役；不代表服务器已经完成任务。

来源：[实际文件](source/packages/client/ui-conversation/src/client/service.ts)，第 275—283 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-conversation/src/client/service.ts#L275)。节选保留原码，省略邻近上下文。

```ts
    const submission = session.beginSubmission({
      mode,
      text,
      attachments: pendingAttachments,
      onRetire: (settlement) => {
        this.settleSubmittedAttachments(session.sessionId, attachments, settlement)
        finishRetirement?.(settlement)
      },
    })
```

**上行提交。** 客户端带同一请求标识、目标会话和内容进行远程调用。

来源：[实际文件](source/packages/api/session-controller/src/client/sessions/session.ts)，第 269—277 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/client/sessions/session.ts#L269)。节选保留原码，省略邻近上下文。

```ts
    if (this.address === undefined) {
      const clientTimeZone = resolvedClientTimeZone()
      result = await this.remote.session.prompt({
        requestId: requestId ?? randomUUID() as SessionRequestId,
        sessionId: this.sessionId,
        mode,
        content,
        clientTimeZone,
      }, signal)
```

**连续性检查。** 旧事件可略过，但未来事件跳过预期序号时会报错。

来源：[实际文件](source/packages/api/session-controller/src/history.ts)，第 226—232 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/history.ts#L226)。节选保留原码，省略邻近上下文。

```ts
        const expectedSeq = SessionSeq(nextOffset)
        if (item.event.seq < expectedSeq) continue
        if (item.event.seq !== expectedSeq) {
          throw new RemoteError('gateway/internal', `session event stream skipped seq ${String(expectedSeq)}`, {})
        }
        nextOffset = SessionLogOffset(nextOffset + 1)
        yield entryFor(item.event)
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/client/ui-conversation/src/client/service.ts](source/packages/client/ui-conversation/src/client/service.ts)，`ConversationController.sendSession`。输入：编辑内容与当前会话；输出/交接：本地提交回显，并请求 Client Session.prompt。[固定提交第 229 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-conversation/src/client/service.ts#L229)。
2. [packages/api/session-controller/src/client/sessions/session.ts](source/packages/api/session-controller/src/client/sessions/session.ts)，`Session.prompt`。输入：带 requestId 的提交；输出/交接：经 RPC 到 Host prompt；Host 再进入第 01 章入口。[固定提交第 254 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/client/sessions/session.ts#L254)。
3. [packages/api/session-controller/src/history.ts](source/packages/api/session-controller/src/history.ts)，`SessionHistoryController.follow`。输入：会话与订阅请求；输出/交接：输出初始快照、持久事件及助手流。[固定提交第 120 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/history.ts#L120)。
4. [packages/api/session-controller/src/client/sessions/session.ts](source/packages/api/session-controller/src/client/sessions/session.ts)，`acceptEventChange`。输入：follow 收到的变化；输出/交接：合并客户端会话与提交状态。[固定提交第 646 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/api/session-controller/src/client/sessions/session.ts#L646)。
5. [packages/client/ui-chat/src/client/chat/ChatView.tsx](source/packages/client/ui-chat/src/client/chat/ChatView.tsx)，`ChatView`。输入：会话分组、节点与顺序快照；输出/交接：订阅变化并显示过程。[固定提交第 101 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/client/ui-chat/src/client/chat/ChatView.tsx#L101)。


<a id="evidence-15"></a>

## 专题 15｜桌面端：窗口、页面与宿主服务怎样合作


**启动先后。** 先导航到应用文档，再启动后端；已有文档经 boot 响应继续。

来源：[实际文件](source/apps/desktop/src/main.ts)，第 567—575 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/main.ts#L567)。节选保留原码，省略邻近上下文。

```ts
  const reconcileBackend = (): Promise<void> => {
    startup ??= (async () => {
      await navigateMain(applicationUrl)
      await backend.start(async () => {
        await Promise.all([manager.applyRelease(), prepareHostEnvironment()])
      })
      if (backend.host !== undefined) await openInitialWindow()
      if (backend.host !== undefined) updateJournal?.action('workspace-ready')
      // The existing Web document resumes through the boot IPC response.
```

**宿主消息。** ready、shutdown-complete 与 fatal 分别处理，不是所有消息都是聊天内容。

来源：[实际文件](source/apps/desktop/src/host-process.ts)，第 206—218 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/host-process.ts#L206)。节选保留原码，省略邻近上下文。

```ts
    child.on('message', (message: unknown) => {
      if (!isDesktopHostEvent(message)) {
        this.fail(new Error('dsh desktop host sent an invalid IPC event'))
        child.kill('SIGTERM')
        return
      }
      if (message.type === 'ready') this.readyResolve({ url: message.url, injections: message.injections })
      else if (message.type === 'platform-session') this.onPlatformSession?.(message.session)
      else if (message.type === 'shutdown-complete') {
        if (this.stopping) this.shutdownCompleted = true
        else this.fail(new Error('dsh desktop host acknowledged an unrequested shutdown'))
      }
      else if (message.type === 'fatal') this.fail(new DesktopHostFatalError(message.message, message.diagnostic))
```

**业务转发。** 检查来源后映射路径并适配认证，再执行 HTTP 请求。

来源：[实际文件](source/apps/desktop/src/web-document.ts)，第 77—88 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/web-document.ts#L77)。节选保留原码，省略邻近上下文。

```ts
export async function forwardWebRequest(request: Request, host: string, cookie: string): Promise<Response> {
  const source = new URL(request.url)
  const origin = request.headers.get('origin')
  if (origin !== null && origin !== 'dsh-app://app') return new Response(null, { status: 403 })
  const target = new URL(host)
  target.pathname = source.pathname
  target.search = source.search
  const headers = new Headers(request.headers)
  for (const name of ['host', 'origin', 'cookie', 'sec-fetch-site']) headers.delete(name)
  headers.set('cookie', cookie)
  const init = { method: request.method, headers, body: request.body, signal: request.signal, duplex: 'half', redirect: 'manual' as const }
  const response = await fetch(target, init)
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [apps/desktop/src/main.ts](source/apps/desktop/src/main.ts)，`窗口配置；reconcileBackend（约 567 行）`。输入：启动参数和窗口状态；输出/交接：先加载页面，再调用 Host.start；隔离配置说明边界。[固定提交第 229 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/main.ts#L229)。
2. [apps/desktop/src/host-process.ts](source/apps/desktop/src/host-process.ts)，`DesktopHostProcess.start`。输入：Host 启动配置；输出/交接：spawn 并处理就绪 IPC。[固定提交第 186 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/host-process.ts#L186)。
3. [apps/desktop/src/main.ts](source/apps/desktop/src/main.ts)，`protocol.handle 与 boot 注入`。输入：renderer 请求与启动状态；输出/交接：本地静态资源或转发 Host；把流信息交给页面。[固定提交第 662 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/main.ts#L662)。
4. [apps/desktop/src/web-document.ts](source/apps/desktop/src/web-document.ts)，`forwardWebRequest`。输入：业务 HTTP 请求；输出/交接：来源检查与认证适配后返回响应。[固定提交第 77 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/web-document.ts#L77)。
5. [apps/desktop/src/preload-app.ts](source/apps/desktop/src/preload-app.ts)，`目录选择与 ready 桥`。输入：有限桌面动作；输出/交接：交付受控桌面能力；对照业务网络链。[固定提交第 77 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/apps/desktop/src/preload-app.ts#L77)。


<a id="evidence-16"></a>

## 专题 16｜测试与回放：复现通过究竟证明了什么


**脚本派生。** 缺少 finish 的已录制调用需要额外处理，不自动成为正常回放。

来源：[实际文件](source/packages/test-support/llm-replay/src/index.ts)，第 462—472 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L462)。节选保留原码，省略邻近上下文。

```ts
export function deriveReplayScript(events: SessionEvent[]): ReplayEntry[] {
  const script: ReplayEntry[] = []
  const close = (key: string | undefined, chunks: StreamChunk[]): void => {
    if (chunks.length === 0) return
    if (chunks[chunks.length - 1]?.type !== 'finish') {
      throw new Error(
        `llm-replay: model call ${key} ended without a finish chunk (a thrown stream); `
        + 'this scenario needs a replay.override.json sidecar',
      )
    }
    script.push({ kind: 'chunks', chunks })
```

**接入选择。** providers 配置决定使用 ReplayAdapter 还是 llm/stream 拦截。

来源：[实际文件](source/packages/test-support/llm-replay/src/index.ts)，第 1101—1104 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L1101)。节选保留原码，省略邻近上下文。

```ts
  const providers = config.providers ?? []
  const dispose = providers.length > 0
    ? ctx.llm.registerAdapter(providers.map(provider => provider.id), new ReplayAdapter(providers, replay))
    : ctx.on('llm/stream', (options: GenerateOptions, _next) => replay(options))
```

**消费检查。** 检查未绑定脚本及未消费响应，才能发现流程请求数与录制不一致。

来源：[实际文件](source/packages/test-support/llm-replay/src/index.ts)，第 1107—1115 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L1107)。节选保留原码，省略邻近上下文。

```ts
    assertConsumed(): void {
      const problems: string[] = []
      if (nextScript < scripts.length) {
        problems.push(`${scripts.length - nextScript} recorded script(s) never bound to a live session`)
      }
      for (const [key, state] of bound) {
        if (state.cursor < state.entries.length) {
          const who = key === ANON ? 'the anonymous session' : `session ${key}`
          problems.push(`${who} consumed ${state.cursor}/${state.entries.length} recorded call(s)`)
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/test-support/llm-replay/src/index.ts](source/packages/test-support/llm-replay/src/index.ts)，`deriveReplayScript`。输入：已录制会话；输出/交接：生成模型响应脚本。[固定提交第 462 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L462)。
2. [packages/test-support/llm-replay/src/index.ts](source/packages/test-support/llm-replay/src/index.ts)，`installLlmReplay`。输入：脚本与 provider 配置；输出/交接：安装 ReplayAdapter 或流拦截，固定模型输出。[固定提交第 1031 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L1031)。
3. [packages/core/agent-loop/src/agent.ts](source/packages/core/agent-loop/src/agent.ts)，`step`。输入：固定模型响应与真实循环状态；输出/交接：执行工具和日志流程；由测试断言验证行为。[固定提交第 398 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/core/agent-loop/src/agent.ts#L398)。


<a id="evidence-17"></a>

## 专题 17｜量化评价：同时看质量、时间、用量与失败


**用量投影。** 注册三个相应用量/压力视图，并按需要同步。

来源：[实际文件](source/packages/llm/token-meter/src/index.ts)，第 110—122 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/token-meter/src/index.ts#L110)。节选保留原码，省略邻近上下文。

```ts
  constructor(ctx: Context, config: TokenMeterConfig = {}) {
    super(ctx, 'tokenMeter')
    validateConfigKeys(config)

    ctx.sessionProjections.register(tokenUsageProjectionDefinition)
    ctx.sessionProjections.register(contextPressureProjectionDefinition)
    ctx.sessionProjections.register(contextBreakdownProjectionDefinition)

    // Readers catch up independently, while eager observation bounds ordinary
    // read latency without creating state for sessions no consumer has read.
    ctx.on('session/event', (session) => {
      if (this.states.has(session)) this._sync(session)
    })
```

**遥测观察。** 事件与 flush 触发后端交接；回调如何等待有独立契约。

来源：[实际文件](source/packages/session/session-telemetry/src/coordinator.ts)，第 104—116 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-telemetry/src/coordinator.ts#L104)。节选保留原码，省略邻近上下文。

```ts
      ctx.on('session/event', (session, event) => {
        this.contain(() => {
          this.captureEvent(session, event)
        })
      })
      // Parallel listeners are awaited by the loop at turn end; returning void
      // (not the SDK's flush promise) is the turn-latency contract.
      ctx.on('session/flush', (session) => {
        this.contain(() => {
          this.hintFlush(session)
        })
      })
      ctx.on('agent/error', ({ agent, turn, step, error }) => {
```

**反馈捕获。** 按需模式只由符合条件的实际事件触发对应历史前缀捕获。

来源：[实际文件](source/packages/session/session-telemetry-otel/src/index.ts)，第 218—230 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-telemetry-otel/src/index.ts#L218)。节选保留原码，省略邻近上下文。

```ts
    const coordinator = new SessionTelemetryCoordinator(ctx, backend, {
      capture: 'on-demand',
      includeHistory: true,
    })
    ctx.on('session/event', (session, event) => {
      if (!isFeedback(session, event)) return
      // Only the canonical appended event authorizes this exact prefix.
      // oxlint-disable-next-line typescript/no-deprecated -- Existing Session history read; migration deferred.
      if (session.eventAt(event.seq) !== event) {
        ctx.logger.warn(NON_CANONICAL_EVENT_WARNING)
        return
      }
      coordinator.captureSession(session, event.seq)
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [packages/llm/token-meter/src/index.ts](source/packages/llm/token-meter/src/index.ts)，`TokenMeter 与用量投影`。输入：会话及模型相关事件；输出/交接：更新 tokenUsage / contextPressure / contextBreakdown。[固定提交第 101 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/token-meter/src/index.ts#L101)。
2. [packages/session/session-telemetry/src/coordinator.ts](source/packages/session/session-telemetry/src/coordinator.ts)，`SessionTelemetryCoordinator`。输入：会话生命周期、事件、flush 和错误；输出/交接：交给注册的后端；与用量投影是不同消费路径。[固定提交第 75 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-telemetry/src/coordinator.ts#L75)。
3. [packages/session/session-telemetry-otel/src/index.ts](source/packages/session/session-telemetry-otel/src/index.ts)，`按需捕获与反馈触发`。输入：后端配置与事件；输出/交接：形成 OTel logs 导出；不推断未实现的评测能力。[固定提交第 218 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/session/session-telemetry-otel/src/index.ts#L218)。


<a id="evidence-18"></a>

## 专题 18｜综合案例：已有文件工具如何接入与呈现


**官方最小工具。** name/inject/apply 与参数、输出契约共同组成最小注册形态。

来源：[实际文件](source/docs/cookbook/adding-a-tool.zh.md)，第 14—27 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/cookbook/adding-a-tool.zh.md#L14)。节选保留原码，省略邻近上下文。

```ts
export const name = 'my-tool'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'read_file',
    description: 'Read a file from disk.',          // what the model sees
    parameters: {
      path: { type: 'string', required: true, description: 'Absolute path' },
      limit: { type: 'number' },                     // optional by default
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
```

**真实读取实现。** 已注册执行体使用文件服务，并兑现窗口和取消约定。

来源：[实际文件](source/packages/fs/tool-fs/src/read.ts)，第 137—150 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L137)。节选保留原码，省略邻近上下文。

```ts
    async execute(args, exec) {
      const input = parseReadArgs(args, caps.limit)
      // One stat: absence observation OR type check + size routing + present version.
      // A concurrent write can only make a later guarded mutation fail stale and require reread.
      const { target, info } = await resolveRegularReadTarget(ctx, exec, input.filePath)

      // Stream when the file is large OR size is unknown, so a size-less backend
      // never buffers an arbitrarily large file.
      const chunks = info.size === undefined || info.size >= caps.streamMinSize
        ? await ctx.fs.streamText(target, exec.signal)
        : [await ctx.fs.readText(target, exec.signal)]
      const window = await buildWindow(
        chunks,
        { offset: input.offset, limit: input.limit, maxLineLength: caps.maxLineLength, maxBytes: caps.maxBytes },
```

**可回放展示材料。** 呈现元数据从规范结果提取，不靠回放时再读取文件。

来源：[实际文件](source/packages/fs/tool-fs/src/read.ts)，第 124—132 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L124)。节选保留原码，省略邻近上下文。

```ts
      presentationMeta: (_args, value) => {
        const lang = langFromPath(value.path)
        return {
          path: value.path,
          offset: value.offset,
          lines: value.lines.map(({ number, text }) => ({ number, text })),
          totalLines: value.totalLines,
          ...lang === undefined ? {} : { lang },
        }
```

**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。

1. [docs/cookbook/adding-a-tool.zh.md](source/docs/cookbook/adding-a-tool.zh.md)，`最小工具结构`。输入：能力需求与输入输出契约；输出/交接：确定 name / inject / apply / defineTool 的职责。[固定提交第 1 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/cookbook/adding-a-tool.zh.md#L1)。
2. [packages/fs/tool-fs/src/index.ts](source/packages/fs/tool-fs/src/index.ts)，`apply`。输入：配置与注入服务；输出/交接：以已有文件插件核对注册和生命周期。[固定提交第 54 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/index.ts#L54)。
3. [packages/fs/tool-fs/src/read.ts](source/packages/fs/tool-fs/src/read.ts)，`applyReadTool`。输入：read 的 schema、execute 与呈现；输出/交接：核对真实工具如何兑现契约。[固定提交第 68 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/fs/tool-fs/src/read.ts#L68)。
4. [docs/cookbook/extension-cookbook.zh.md](source/docs/cookbook/extension-cookbook.zh.md)，`扩展点选择`。输入：需要扩展的层；输出/交接：定位能力接口；把 Host 工具与 UI 扩展分开。[固定提交第 1 行](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/docs/cookbook/extension-cookbook.zh.md#L1)。


<a id="book-evidence-08"></a>

## 教材第 8 章：补充实现证据

**调用配置的范围。** 这些字段选择模型与请求选项，不是模型权重。

[本地完整文件](source/packages/llm/llm/src/call-config.ts)，第 21—30 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/llm/src/call-config.ts#L21)。

```ts
 * per call.
 */
export interface LlmCallConfig {
  provider: string
  model: string
  reasoningEffort?: ReasoningEffortId
  temperature?: number
  maxTokens?: number
  stop?: string[]
}
```

**准备并冻结解析配置。** 先找注册适配器，再解析模型与调用配置，复制并冻结。

[本地完整文件](source/packages/llm/llm/src/index.ts)，第 936—944 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/llm/llm/src/index.ts#L936)。

```ts
  async prepareCall(config: LlmCallConfig, signal?: AbortSignal): Promise<PreparedLlmCall> {
    const registration = this.registration(config.provider)
    const adapterCall = await registration.adapter.prepareCall(config.provider, config.model, signal)
    const modelInfo = this.normalizeModelInfo(registration, config.model, adapterCall.model)
    const resolved = this.resolveCallWithInfo(config, modelInfo)
    const resolvedConfig = deepFreeze(structuredClone(resolved.config))
    const context = resolved.context === undefined
      ? undefined
      : deepFreeze(structuredClone(resolved.context))
```

<a id="book-evidence-09"></a>

## 教材第 9 章：补充实现证据

**启用条目的实际变更。** 先检查目标与可写条件，再写 patch、重载并观察当前状态。

[本地完整文件](source/packages/boot/plugin-manager/src/index.ts)，第 425—434 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/boot/plugin-manager/src/index.ts#L425)。

```ts
  setPluginEnabled(id: PluginEntryId, enabled: boolean): Promise<ChangeResult> {
    return this.change(result => this.configure(async () => {
      const row = (await this.listPlugins()).find(item => item.entryId === id)
      if (row === undefined) throw new ManagementFailure('unknown-plugin')
      if (row.readOnlyReason !== undefined) throw new ManagementFailure(row.readOnlyReason)
      await writePluginEnabled(this.profile.patchPath, row.patchId, row.moduleName, enabled)
      result.warnings = await this.reload(enabled ? [row.patchId] : [])
      const current = (await this.listPlugins()).find(item => item.entryId === id)
      return current?.enabled !== enabled && this.ownerContext.get('hmr') !== undefined ? 'overridden' : undefined
    }), { stage: 'enable', target: id, enabled }, 'plugin')
```

**完整消费回放的检查。** 未绑定脚本和未消费调用都会形成问题，不能把提前结束当作完整回归。

[本地完整文件](source/packages/test-support/llm-replay/src/index.ts)，第 1107—1120 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/test-support/llm-replay/src/index.ts#L1107)。

```ts
    assertConsumed(): void {
      const problems: string[] = []
      if (nextScript < scripts.length) {
        problems.push(`${scripts.length - nextScript} recorded script(s) never bound to a live session`)
      }
      for (const [key, state] of bound) {
        if (state.cursor < state.entries.length) {
          const who = key === ANON ? 'the anonymous session' : `session ${key}`
          problems.push(`${who} consumed ${state.cursor}/${state.entries.length} recorded call(s)`)
        }
      }
      if (problems.length > 0) {
        throw new Error(`llm-replay: fixture not fully consumed — ${problems.join('; ')}; the scenario drove fewer model calls than recorded`)
      }
```

<a id="book-evidence-10"></a>

## 教材第 10 章：补充实现证据

**团队成员持久身份。** Session 标识、标签、上下文起点与创建阶段分别记录。

[本地完整文件](source/packages/experimental/agent-team/src/types.ts)，第 47—55 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/experimental/agent-team/src/types.ts#L47)。

```ts
export interface TeamMemberSnapshot {
  readonly id: SessionId
  readonly name: string
  readonly description: string
  readonly provider: string
  readonly context: 'fresh' | 'fork'
  readonly phase: TeamMemberPhase
  readonly error?: string
}
```

**任务完整快照。** 修订、所有者、阻塞关系与路径提示进入任务记录。

[本地完整文件](source/packages/experimental/agent-team/src/types.ts)，第 74—83 行；[固定提交](https://github.com/deepseek-ai/deepseek-harness/blob/639ed015397290b3745d163aafe02ffee4aa3f84/packages/experimental/agent-team/src/types.ts#L74)。

```ts
export interface TeamTaskSnapshot {
  readonly id: TeamTaskId
  readonly revision: number
  readonly subject: string
  readonly description: string
  readonly status: TeamTaskStatus
  readonly ownerId?: SessionId
  readonly blockedBy: TeamTaskId[]
  readonly writeScopes: string[]
}
```
