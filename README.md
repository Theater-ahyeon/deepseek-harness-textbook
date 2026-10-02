# 深入理解 DeepSeek Harness

从智能体基础到工程协作的中文项目教材。适合只了解少量概念的初学者，正文独立解释项目，无需先阅读源码或官方文档，不设练习。

**开始阅读：[离线图文阅读版](reader.html)。** 解压后用浏览器打开，即可按第 1—19 章顺序阅读正文与全部 40 张原创架构图示，无需联网加载图或脚本。

- [完整 Markdown 教材](tutorial.md)：全 19 章全文，分“核心构建与运行时原理”、“安全、交互、度量与多 Agent”和“理论奠基与数理升华”三部分。
- [单章教材](book/)：与全文保持同一章号（01 ~ 19），适合分章阅读。
- [基础与术语附录](appendices.md)：遇到新概念时查询。
- [图示目录](figures/index.md)：40 张原创中文图，均有 PNG 和可修改 SVG。
- [可选参考证据](reference-index.md)：原项目文档、源码与测试旁证。
- [原码节选附录](source-excerpts.md)：60 段精选原码；可以完全略过而继续学习。

正文整合 18 个核心实现专题与 1 个理论奠基专题，并解释官方子系统目录中 63 项能力的功能、协作和主要边界。

**每章末尾附“本章面试问答”**：全书 19 套追问式面试真题，涵盖源码级事实、核心设计原理、下一层追问与应答要点，末尾另有跨章综合压力问答。

实现固定在官方提交 `639ed015397290b3745d163aafe02ffee4aa3f84`，根包 `0.2.0-rc.2`。`source/` 保留原仓库、中文文档与 MIT 许可；新正文在其外撰写。静态核验不冒充执行报告，本次未运行项目、上游测试或付费模型实验。

**给别人学习：发送交付 ZIP，保留目录结构，解压后打开 `reader.html`。** 仅转发一个 Markdown 会缺少图片和可选原文；ZIP 不包含 Git 元数据、编写脚本或历史提纲。

写作与参考方法见 [chapter-format.md](chapter-format.md) 和 [illustration-plan.md](illustration-plan.md)。版本、覆盖与核验记录见 [sources.json](sources.json)、[coverage.json](coverage.json)、[validation.json](validation.json)。
