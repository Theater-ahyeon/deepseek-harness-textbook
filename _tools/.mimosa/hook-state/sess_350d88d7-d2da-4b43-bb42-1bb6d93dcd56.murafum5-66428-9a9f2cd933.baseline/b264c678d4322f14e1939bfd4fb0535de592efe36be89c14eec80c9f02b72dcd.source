"""Build the outline and reference index from the reviewed chapter plan.

This only writes course artifacts outside source/. It does not run DSH or tests.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
PLAN = json.loads((ROOT / "course-plan.json").read_text(encoding="utf-8"))
if PLAN.get("stage") == "complete_explanatory_edition":
    raise SystemExit("完整版已存在；提纲脚本不允许覆盖正文。请使用 build_book.py。")
COMMIT = PLAN["commit"]
ONLINE = f"https://github.com/deepseek-ai/deepseek-harness/blob/{COMMIT}/"
DOCUMENT_LABELS = {
    "docs/architecture.zh.md": "项目架构原文",
    "docs/agent-lifecycle.zh.md": "智能体轮次与步骤生命周期原文",
    "docs/subsystems/commands.zh.md": "会话命令接口原文",
    "docs/user/develop/basic/tool.zh.md": "工具开发基础原文",
    "docs/subsystems/core.zh.md": "核心循环接口原文",
    "docs/tool-catalog.zh.md": "项目工具目录原文",
    "docs/subsystems/filesystem.zh.md": "文件系统能力原文",
    "docs/persistence-catalog.zh.md": "持久化目录原文",
    "docs/session-format-status.zh.md": "会话格式状态原文",
    "docs/event-producer-consumer.zh.md": "事件生产与消费关系原文",
    "docs/subsystems/skills.zh.md": "技能能力接口原文",
    "docs/subsystems/compaction.zh.md": "上下文压缩接口原文",
    "docs/user/guide/mcp-memory.zh.md": "外部记忆服务接入指南原文",
    "docs/subsystems/llm-streaming.zh.md": "模型流式调用接口原文",
    "docs/cordis-primer.zh.md": "插件框架入门原文",
    "docs/subsystems/boot.zh.md": "启动与装配接口原文",
    "docs/tool-execution-pipeline.zh.md": "工具执行流水线原文",
    "docs/subsystems/approval.zh.md": "审批能力原文",
    "docs/subsystems/mcp.zh.md": "外部能力协议接口原文",
    "docs/subsystems/subagent.zh.md": "子代理接口原文",
    "docs/api-gateway.zh.md": "接口网关原文",
    "docs/subsystems/conversation.zh.md": "会话交互接口原文",
    "docs/subsystems/client-modules.zh.md": "客户端模块原文",
    "apps/desktop/README.zh.md": "桌面应用说明原文",
    "docs/testing.zh.md": "项目测试指南原文",
    "packages/test-support/llm-replay/README.md": "模型回放说明原文（英文）",
    "docs/subsystems/token-meter.zh.md": "词元计量接口原文",
    "docs/subsystems/otel.zh.md": "遥测导出接口原文",
    "docs/subsystems/session-telemetry.zh.md": "会话遥测接口原文",
    "docs/cookbook/adding-a-tool.zh.md": "新增工具操作指南原文",
    "docs/cookbook/extension-cookbook.zh.md": "扩展开发指南原文",
}


def link(path, label=None):
    return f"[{label or DOCUMENT_LABELS.get(path, path)}](source/{path})"


def stable(path, line):
    return f"[固定提交 L{line}]({ONLINE}{path}#L{line})"


header = """# 从一条任务学会 DeepSeek Harness

> 初学者教材提纲 · 2026-10-03 修订 · 当前 18 章均为“大纲”，尚未展开完整正文。

## 读者、目标与贯穿案例

适合只知道少量大模型、智能体（Agent）和编程概念的人。无需先学完 TypeScript、Cordis、React 或 Electron：先解释一条任务如何完成，遇到语法和异步机制时补够用的基础。

正文、标题、示例图标签和图注以中文为主，术语第一次出现补英文对照。真实代码、函数名、事件名和路径保留原样，方便定位；原项目参考文档优先选已有中文版，不改写原文。

全书围绕“读取一个项目的 README.md，说明用途并总结三点”逐层展开。先假设文件存在、read 已启用且调用获准，再加入输入变化、上下文变长、模型失败、工具拒绝、页面刷新等条件。它是教学场景；目前没有运行这次任务或录制实测轨迹。模型是否选择 read 不是本书保证的固定行为。

学完核心路线，应能解释一条任务的输入、材料、执行、状态、呈现与验证；能沿源码找依据；能为一个小能力写契约和验证方案。这里的“完整版教材”指下面已列明的核心路线，不能把尚未覆盖的每个后端和可选模块都称为已讲完。

## 版本与证据边界

官方仓库：https://github.com/deepseek-ai/deepseek-harness 。固定提交 `639ed015397290b3745d163aafe02ffee4aa3f84`，源码日期 2026-09-29，根包版本 `0.2.0-rc.2`。原仓库位于 [source](source/README.md)，原文件未修改。实现结论来自静态源码检查；项目测试作为可阅读的行为旁证，尚未执行。机器上另一版本的 CLI 不作为教材依据。

正文将全部重新撰写，围绕可理解的现象解释机制；原项目文档保留为参考附件。正文、原文、源码和测试的用途见 [证据索引](reference-index.md)，来源记录见 [sources.json](sources.json)。

## 教材体例与配图方法

借鉴《计算机体系结构：量化研究方法》的定量分析、综合案例和误区/习题安排，将一章组织成“现象与图解 → 主链与基础 → 源码证据 → 设计取舍与分析例子 → 综合案例 → 误区与练习”。方法依据见 [Elsevier 第六版介绍](https://shop.elsevier.com/books/computer-architecture/hennessy/978-0-12-811905-1)与[第五版目录](https://shop.elsevier.com/books/computer-architecture/hennessy/978-0-12-383872-8)。

参考《图解大模型》的直觉优先与图示教学方法，先显示材料进出，再逐层展开内部过程。来源为[作者网站](https://www.llm-book.com/)及[官方代码仓库](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models)。图稿采用本课程自己的卡片、色彩和箭头规则；没有复制书中的图文，也不宣称已复刻其精确视觉样式。

完整规则见 [章内体例](chapter-format.md)与 [36 张图的分镜规划](illustration-plan.md)。每章两张规划图，其中主图回答机制，伴随图回答分支或取舍；成图仍待绘制。量化先从计数与时间线开始，后面再讨论预算和多次实验；所有非实测数字都必须标“教学假设”。

## 学习次序

| 部分 | 章节 | 完成后能够解释什么 |
| --- | --- | --- |
| 一：看懂一条任务 | 01—05 | 分工、最小源码阅读、循环、文件材料和会话事实 |
| 二：组织材料并应对失败 | 06—09 | 请求材料、按需技能、压缩、模型流与重试 |
| 三：接入能力并控制边界 | 10—13 | 装配、准入、MCP、子任务起点 |
| 四：把过程变成可用产品 | 14—15 | 发送与订阅、页面恢复、桌面执行环境 |
| 五：用证据评价与扩展系统 | 16—18 | 回放证据、联合评价和能力扩展设计 |

初次阅读按 01→18 顺序。每章先读作者讲解和图解，再按需查看原文与完整源码；参考链接不应成为理解正文的前置任务。第一部分完成后暂停复述完整链；第二、三部分分别检查材料来源和能力边界；最后提交综合案例设计。

飞书《通用Agent设计方法论（四板斧）》用于课程问题组织：场景材料与外部能力落在 06—08、11—12、18；编排与推理融合落在 03、09—10、13；评测与调优落在 16—17；产品承载落在 14—15。它不作为 DSH 实现证据；读取范围仅包括已访问页面的目录及正文，不声称读完其所有子页面。

## 基础知识怎样按需补

| 首次需要的位置 | 补充内容 | 学到什么程度即可继续 |
| --- | --- | --- |
| 01—02 | 输入输出、对象、类型、函数、Promise、async/await | 分得清类型说明与实际行为，知道 await 等待哪个结果 |
| 03 | 队列、状态机、事件通知 | 知道输入何时被领取、谁推动下一步 |
| 04—05 | schema、服务接口、投影、序列化、持久化 | 分得清参数、材料、事实与派生视图 |
| 06—08 | 贡献、按需读取、上下文窗口与摘要 | 追得出模型当前看到材料的来源 |
| 09—10 | 异步迭代、取消、依赖注入、生命周期 | 分得清流片段、最终消息和可替换提供方 |
| 12—15 | 协议、RPC、订阅、进程、IPC、preload | 画得清跨边界的两个通信方向 |
| 16—17 | 断言、回放、样本、单位、比例 | 知道什么检查支持什么结论 |

"""

lines = [header]
part = None
for c in PLAN["chapters"]:
    cid = c["id"]
    if part != c["part"]:
        part = c["part"]
        lines.append(f"# {part}\n")
    lines.extend([
        f'<a id="chapter-{cid}"></a>\n',
        f'## {cid}｜{c["title"]}\n',
        f'**状态：大纲。核心问题：** {c["question"]}\n',
        '**正文小节：**\n'
    ])
    for i, title in enumerate(c["sections"], 1):
        lines.append(f'{i}. {cid}.{i} {title}')
    lines.append(f'\n**任务主链：** {c["chain"]}\n')
    lines.append(f'**在这里补基础：** {c["basics"]}\n')
    lines.append('**源码证据阅读顺序：** 下列路线区分启动前置、执行主链和提供方对照；它们不是把所有条目误连成一次同步调用。\n')
    for i, (path, line, symbol, inp, result) in enumerate(c["read"], 1):
        lines.append(f'{i}. {link(path)}，`{symbol}`；{stable(path,line)}。输入：{inp}。输出/下一步：{result}。')
    lines.extend([
        f'\n**困难条件与分支：** {c["branch"]}\n',
        f'**分析例题规划：** {c["measure"]}\n',
        f'**配图：** F{cid}A 与 F{cid}B；问题、画面和图注见 [分镜表](illustration-plan.md)。\n',
        f'**需要反驳的误解：** {c["misconception"]}\n',
        '**原项目参考文档：** ' + '；'.join(link(p) for p in c["docs"]) + '。\n',
        '**选读行为旁证（未执行）：** ' + ('；'.join(link(p) for p in c["tests"]) if c["tests"] else '本章是源码阅读基础，沿入口契约作静态对照，不额外设置运行作业') + '。\n',
        f'**章末练习规划：** 读图复述一条主链；追踪上述一个分支；完成本章分析例题的邻近变体；用源码证据反驳上述误解。正式题目在正文展开时编写，当前不附标准答案。\n',
        f'**完成标准：** {c["criterion"]}\n',
        f'**本章暂缓：** {c["defer"]}\n'
    ])

lines.append("""# 附录与后续编写安排

## 附录规划

| 附录 | 内容 | 用途 |
| --- | --- | --- |
| A 最小 TypeScript 速查 | 对象/类型、Promise、异步流、可选字段、错误、导入 | 读到不懂的语法时回查，不作开课门槛 |
| B 术语与事件卡片 | Session、turn、step、attempt、tool/result、snapshot、stream | 统一中英文和生命周期含义 |
| C 原项目文档及源码索引 | 按章排列原文、固定提交、实现路线与测试 | 让关键结论可以复核 |
| D 学习记录与故障分析表 | 现象、当前解释、证据、未解问题、验证计划 | 避免把复述术语当成已经掌握 |
| E 实验记录表 | 输入、环境、模型、配置、检查、时间、用量、失败 | 为第 17 章比较准备同一口径 |

当前已完成 C 的索引和文件清单；其余附录是编写规划，尚未完成正文。

## 旧大纲的内容去了哪里

原 12 课大纲保存在 [archive/source-outline-v1.md](archive/source-outline-v1.md)，用于追溯旧路线。此前所有课程都处于提纲阶段，本次没有覆盖已展开课程或学习者笔记。

| 原课 | 新章 | 重组原因 |
| --- | --- | --- |
| 01 任务总览 | 01；新增 02 | 保留分工总览，另补够用的阅读与等待基础 |
| 02 启动装配 | 10 | 先体验服务职责，再理解怎样装配 |
| 03 Session | 05 | 放在循环与工具之后讲事实和视图 |
| 04 AgentLoop | 03 | 先建立驱动的执行骨架 |
| 05 模型与重试 | 09 | 学完材料来源后再讲模型调用可靠性 |
| 06 工具、审批、MCP | 04、11、12 | 文件材料、准入控制、外部协议各有独立问题 |
| 07 Prompt、Skill、压缩 | 06、07、08 | 分开材料组装、正文按需取得和历史替换 |
| 08 子代理 | 13 | 在服务装配与边界之后讨论拆分 |
| 09 Web | 14 | 复用已理解的核心链解释产品过程 |
| 10 Desktop | 15 | 在 Web 的基础上加进程边界 |
| 11 回放、用量与遥测 | 16、17 | 区分工程复现与质量/成本比较 |
| 12 工具扩展与社区对照 | 04、18；社区另列拓展 | 先读现成工具，最后做综合设计，社区版本不混入官方证据 |

## 范围与未覆盖内容

核心路线覆盖官方启动、任务循环、文件读取、Session、提示词/技能/压缩、DeepSeek 适配器与重试、工具审批、MCP、进程内子代理、Web、Desktop、回放、用量/遥测和工具扩展设计。

尚未系统展开所有模型和执行后端、完整系统沙箱、LSP、浏览器/电脑操作、PTC、Jobs、Goal、Schedule、Webhook、实验性 Agent Teams、Python SDK、原生模块、历史格式迁移、签名和发布。社区 dsh-web 可做拓展比较，其源码不随当前官方证据集附送，也不替代官方事实。第三方 RAG/Memory 的部署不列为默认能力。

## 全文展开顺序与完成门槛

按五部分的学习依赖逐章写作，使用 [章内体例](chapter-format.md)。每章补齐原创解释、精选源码、图与图注、完整分析例子、练习、误区和原文引用后，才把状态改为“正文完成”。先完成第一部分并检查能否由初学者独立复述完整任务，再保持相同难度梯度展开后续部分。

全文结束时核对跨章术语、所有图中的边界与箭头、固定版本链接和练习所需知识。实验未执行就保留“待测”；图未绘制就保留“规划”。提供给学生的正式包应有相对链接、配图文件、原文附件、许可和版本说明，不能让学习者从源码清单自行拼出课程。
""")

all_paths = set()
docs = set()
for c in PLAN["chapters"]:
    docs.update(c["docs"])
    all_paths.update(c["docs"])
    all_paths.update(c["tests"])
    for p, n, *_ in c["read"]:
        all_paths.add(p)
        f = SOURCE / p
        if not f.is_file():
            raise ValueError(f"Missing reading: {p}")
        if not 1 <= n <= len(f.read_text(encoding="utf-8").splitlines()):
            raise ValueError(f"Invalid line: {p}:{n}")
all_paths.update(["README.md", "LICENSE"])
for p in all_paths:
    if not (SOURCE / p).is_file():
        raise ValueError(f"Missing reference: {p}")

index = ["""# 原项目文档与证据索引

## 怎样使用这些材料

本教材正文将由作者重新解释，下面原文用于复核。项目原有文档全部保留在 `source/docs/`，各包原 README、源码与测试保留原目录，图片和相对链接的目标也随整仓库保留。不是只截取一句文档当作完整教程，也没有改写原文后冒充官方说明。

证据版本：官方仓库固定提交 `639ed015397290b3745d163aafe02ffee4aa3f84`，根包 `0.2.0-rc.2`。下列是按章精选参考索引；被列入附件不表示已逐行审阅整个文件。关键主链已做静态核验，测试列为可读旁证，未安装依赖或运行项目测试。文档描述与实现冲突时，要在正文指出并以固定版本实际实现为准。

| 材料 | 可以支持什么 | 不能自动支持什么 |
| --- | --- | --- |
| 原项目文档 | 官方描述的职责、契约和使用方式 | 当前机器实际启用哪些插件、一次任务确实成功 |
| 固定版本源码 | 已实现分支、注册、调用和提交边界 | 当前部署状态、实测性能、未经说明的设计动机 |
| 测试源码 | 某个行为被怎样断言 | 本机已经运行通过、业务任务普遍成功 |
| 课程原创图解与例题 | 对机制的解释、可复核的教学推导 | 项目原作者观点或实测数值 |
| 飞书参考 | 四个方向的课程问题组织 | DSH 中某个能力实际存在 |

## 按章阅读原文

先读课程的讲解，再选择下面原文。实现的编号路线和固定提交行号链接集中在 [教材提纲](tutorial.md) 的对应章节。

| 章 | 参考原文 | 查阅目的 |
| --- | --- | --- |
""".rstrip()]
for c in PLAN["chapters"]:
    index.append(f'| [{c["id"]} {c["title"]}](tutorial.md#chapter-{c["id"]}) | '+ '<br>'.join(link(p) for p in c["docs"]) + f' | 复核：{c["question"]} |')
index.append("""
## 可转交的原文附件

当前附件就是完整 `source/` 官方仓库副本。不要只复制几篇 Markdown：项目文档会引用其他文档、包 README、图片和源码。转交整个课程文件夹保留这些关系。`source/.git/` 是版本元数据，课堂阅读不依赖它；未来制作精简分享包时应先核对所选原文的相对链接依赖，再省略开发文件，不能未经核对删除引用目标。

许可保留在 [项目 MIT 许可](source/LICENSE)。课程参考的两本书通过出版社、作者公开页注明方法来源，没有把书籍全文或书中插图放进附件。飞书页只保留引用与读取范围记录，不附未经取得的全文。

## 文件清单与维护

[reference-manifest.json](reference-manifest.json) 记录本提纲实际引用的原文、实现和测试路径、字节大小与 SHA-256，便于检查附件是否缺失或被替换。它不覆盖整仓库，也不代表运行验收；各章具体行为仍需回到源码契约。

以后升级源码时另存新版本并更新提交、路径、符号、行号和清单。原教材与学习记录保留，不把新版本行号直接嫁接到旧链接上。
""")

manifest = {
    "commit": COMMIT,
    "scope": "Only source files referenced by the chapter plan plus root README and license",
    "files": [
        {"path": "source/" + p, "bytes": (SOURCE / p).stat().st_size,
         "sha256": hashlib.sha256((SOURCE / p).read_bytes()).hexdigest(),
         "kind": "original_document" if p in docs or p == "README.md" else "license" if p == "LICENSE" else "source_or_test"}
        for p in sorted(all_paths)
    ]
}
(ROOT / "tutorial.md").write_text("\n".join(lines), encoding="utf-8")
(ROOT / "reference-index.md").write_text("\n".join(index), encoding="utf-8")
(ROOT / "reference-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
print(json.dumps({"chapters":len(PLAN["chapters"]),"planned_figures":len(PLAN["chapters"])*2,"reference_files":len(all_paths),"reference_documents":len(docs)},ensure_ascii=False))
