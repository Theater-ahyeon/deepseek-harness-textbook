"""Synchronize completed Chinese explanatory-edition metadata and entry points."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return (ROOT/name).read_text(encoding="utf-8")

def write(name, value):
    (ROOT/name).write_text(value, encoding="utf-8")

def save(name, value):
    write(name, json.dumps(value, ensure_ascii=False, indent=2)+"\n")

plan = json.loads(read("course-plan.json"))
for chapter in plan["chapters"]:
    for entry in chapter["read"]:
        entry[2] = entry[2].replace("createMcpToolDef", "createMcpToolDefinition") if entry[2] == "createMcpToolDef" else entry[2]
        if entry[2] == "dispatch":
            entry[2] = "dispatchToolBody"
last = plan["chapters"][-1]
last["sections"] = ["读取工具的插件生命周期", "模型参数与内部输入", "规范结果、文本与展示元数据", "准入后执行与取消", "已有能力的完整闭环"]
last["measure"] = "通过已有读取工具说明规范值、模型文本与持久展示数据的不同用途，不布置实现任务。"
last["criterion"] = "正文解释实际工具的输入、执行、结果与呈现，使用固定版本源码复核。"
plan["exercise_sections"] = False
save("course-plan.json", plan)

figures = json.loads(read("figures/figure-data.json"))
for figure in figures:
    if figure["id"] == "F18A":
        figure["tag"] = "扩展生命周期示意"
        figure["nodes"][0][0] = "读取工具的既有契约"
    if figure["id"] == "F18B":
        figure["tag"] = "已有读取工具的契约对照"
save("figures/figure-data.json", figures)
write("chapters/18.md", read("chapters/18.md").replace("F18A：新工具注册后复用既有准入与结果链", "F18A：读取工具注册后复用既有准入与结果链"))

sources = json.loads(read("sources.json"))
sources["delivery_stage"] = "中文项目讲解完整版：18 章正文、36 张原创中文图、54 段原码、附录、原项目证据与离线阅读版"
sources["figure_count"] = 36
sources["source_excerpt_count"] = 54
sources["exercise_sections"] = False
sources["updated_date"] = "2026-10-03"
for source in sources["sources"]:
    if source["id"] == "quantitative-architecture-method":
        source["use"] = "参考量化评价、Putting It All Together 与误区体例，面向初学者改编；按用户要求不设置练习"
sources["verification"]["course_artifact_validation"] = "validation.json：核验全文与单章、36 图、54 段原码、本地链接、离线 HTML、附件哈希及固定提交；不是执行上游测试"
save("sources.json", sources)

write("README.md", """# 从一条任务学会 DeepSeek Harness

中文项目讲解完整版，适合只了解少量大模型与编程概念的初学者。先讲整体过程，遇到 TypeScript、异步与网络概念时补基础。18 章以“读取 README 并总结”为线索，配有 36 张原创中文图示、54 段原码节选与原项目参考文档；不设置练习。

**直接开始：[离线图文阅读版](reader.html)。** 在浏览器中打开，无需联网即可阅读全部正文和图示。左侧目录可按 01—18 章顺序跳转。

- [完整 Markdown 教材](tutorial.md)：适合在支持 Markdown 的编辑器中阅读。
- [单章目录](chapters/)：可以按章转发，需保留关联附件目录。
- [术语与语法附录](appendices.md)：随用随查，不必预先背诵。
- [原项目文档与证据索引](reference-index.md)：按章对照官方文档、源码和测试旁证。
- [图示目录](figures/index.md)：PNG 便于阅读，SVG 可继续编辑。

讲解依据固定在官方仓库提交 `639ed015397290b3745d163aafe02ffee4aa3f84`，根包版本 `0.2.0-rc.2`。`source/` 保留原始文档、源码、测试及 MIT 许可，课程正文在仓库外撰写。正文依据静态源码核验；本次未运行项目、上游测试或付费模型实验。

**转交方法：分享整个文件夹或交付 ZIP，解压后打开 `reader.html`。** 保留 `source/`、`figures/` 和 `chapters/` 的位置，参考链接便可继续使用。仅发送 `tutorial.md` 会缺少图和原始证据。ZIP 不包含 `.git/`、编写脚本与历史提纲。

编写体例见 [chapter-format.md](chapter-format.md)，配图方法见 [illustration-plan.md](illustration-plan.md)。版本来源见 [sources.json](sources.json)，文档核验见 [validation.json](validation.json)。正文深入解释既定 18 章路线，更多可选功能的范围说明见附录。
""")

write("chapter-format.md", """# 章内体例：从现象走到可核验的解释

这是已展开完整版的写作体例。按用户要求，只讲解项目，不设置练习、答题或评分。

参考《计算机体系结构：量化研究方法》的机制分析、取舍、量化评价、综合案例与误区组织方式；参考《图解大模型》先建立直觉、再用图解释机制的方法。章节文字与图稿均重新创作。方法来源：[Elsevier 介绍](https://shop.elsevier.com/books/computer-architecture/hennessy/978-0-12-811905-1)、[公开目录](https://shop.elsevier.com/books/computer-architecture/hennessy/978-0-12-383872-8)、[图解大模型作者网站](https://www.llm-book.com/)。

每章按以下顺序展开，具体小节标题结合项目内容调整：

| 顺序 | 讲解内容 |
| --- | --- |
| X.0 | 从具体场景提出本章的问题，交代确实需要的前置概念 |
| X.1 | 先看主图 FXXA，用中文标签建立材料与职责的直觉 |
| X.2 | 跟随入口、调用、等待、分支与结果解释完整主链 |
| X.3 | 补本章需要的类型、异步、注册、进程等基础 |
| X.4 | 三段精选原码与完整阅读路线，交代源码输入、输出与省略上下文 |
| X.5 | 用完整讲解的分析示例说明取舍、计数或比较口径 |
| X.6 | 在 FXXB 中增加条件或边界，将机制放回完整任务 |
| X.7 | 用反例和限定条件解释常见误读 |
| X.8 | 小结因果关系，附原项目文档与测试源码旁证 |

中文用于正文、图名、图注与主要标签；真实类型、函数、事件、路径和原码保留原样。第一次出现的术语说明中文职责。原文优先链接项目已有中文版，不改写官方附件。

每章必须形成从开始到结果的闭合解释，讲清至少一个条件分支。调用关系、事件通知、网络传输与持久化分开说明；接纳、开始、成功、失败、取消各有相应边界。只有接口时不推定所有提供方行为。

源码节选来自固定提交，行号与内容写入 [excerpt-manifest.json](excerpt-manifest.json)。每段同时附本地完整文件与固定提交链接。章节引用文件哈希见 [reference-manifest.json](reference-manifest.json)。测试旁证只说明断言方式，未执行时不表述为本机通过。

分析示例中的拟定数字标明教学假设，不声称项目实测。量化章节区分请求接纳时间、首个可见输出时间、完成时间、轮次/步骤/尝试/工具调用数、词元估计与提供方报告；业务质量、失败与取消也进入比较口径。回放通过不能直接证明模型质量提高。

读者无需先学完整 TypeScript、React、Electron 或 Cordis。源码用于支撑中文讲解，附录提供基础速查。完整教材入口见 [tutorial.md](tutorial.md)。
""")

index = read("reference-index.md")
index = index.replace("本教材正文将由作者重新解释", "本教材正文已由作者重新解释").replace("教材提纲", "完整教材").replace("课程原创图解与例题", "课程原创图解与分析示例")
index = index.replace("综合案例：沿扩展点设计一个可验证的小工具", last["title"])
index = index.replace("怎样把全书的机制合起来，为一个只读能力写出实现位置、契约和验证方案？", last["question"])
index += "\n[excerpt-manifest.json](excerpt-manifest.json) 逐段记录 54 段原码的文件、行号与 SHA-256；[validation.json](validation.json) 记录教材附件检查。分享包保留完整原始源码目录（不含 Git 元数据），便于在离线环境查阅原文上下文。\n"
write("reference-index.md", index)

illustration = read("illustration-plan.md")
illustration = illustration.replace("状态：已完成原创图示方案和 36 张图的分镜规划；尚未绘制整套成图。", "状态：36 张原创中文图已全部绘制，分别提供 SVG 与 PNG。实际文件和缩略目录见 [图示目录](figures/index.md)。下文保留设计理由与分镜说明。")
illustration = illustration.replace("## 5. 后续绘制与检查", "## 5. 成图与检查")
illustration = illustration.replace("最终优先交付可修改的 SVG，另导出 PNG", "已交付可修改的 SVG，并导出 PNG")
illustration = illustration.replace("字体、间距及窄屏阅读在完整成图阶段再做视觉验证。", "SVG 与 PNG 均做结构和尺寸检查，并抽查代表图的字体、间距与流程标注；离线阅读版在窄屏允许横向查阅图示。")
write("illustration-plan.md", illustration)

gallery = ["# 原创中文图示目录\n", "每章两张图。PNG 用于普通 Markdown 阅读，SVG 用于缩放与继续修改。所有图均为结构示意、源码推演或明确标注的教学假设；没有项目实测数据。\n"]
for figure in figures:
    fid=figure["id"]
    gallery.append(f'## {fid}｜{figure["title"]}\n\n![{figure["title"]}]({fid}.png)\n\n[可修改 SVG]({fid}.svg) · [对应章节](../chapters/{fid[1:3]}.md)\n')
write("figures/index.md", "\n".join(gallery))
print("Completed-edition metadata and entry points synchronized")
