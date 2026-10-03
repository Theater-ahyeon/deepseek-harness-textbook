# 深入理解 DeepSeek Harness

[在线阅读](https://theater-ahyeon.github.io/deepseek-harness-textbook/) · [下载完整教材](https://github.com/Theater-ahyeon/deepseek-harness-textbook/releases/latest) · [GitHub 仓库](https://github.com/Theater-ahyeon/deepseek-harness-textbook)

本书面向具备少量概念基础的读者。十九章围绕“读取 README 并总结”的任务，依次讲解项目架构、运行机制与关键实现。正文完整解释流程，源码节选配有逐行说明，讲解问答梳理易混淆概念。

**开始阅读：[离线图文教材](reader.html)。** 无需联网加载图、字体或脚本；页面顶部可隐藏源码研读，先读完整机制说明。

阅读版采用白底三栏排版：左侧选章，右侧定位小节，正文下方进入下一章。首页提供十九章速览；顶部可离线搜索，按 `/` 也能打开搜索。点击“全文阅读”可连续浏览全书。手机上通过左上角打开目录。排版参考与核验记录见[阅读版说明](revision/reading-layout-20261003.md)。

- [Markdown 全文](tutorial.md)与[分章正文](book/)保持相同编号。
- [补充能力](subsystems.html)解释主线外的材料、存储、执行、产品与运行治理。
- [语法基础](appendices.html)、[术语定位](glossary.html)供回查。
- [实现证据](evidence.html)记录真实节选、路径、版本、行号与核验范围。
- [原项目文档](references.html)作为可选证据。
- [计算与源码验证](examples/README.md)提供 calculations 的输入、输出和实际运行过的断言代码。

正文唯一编辑来源是 book/*.md；构建脚本只汇总和渲染，不覆盖分章。在制作方的本地维护版本中，编辑后运行 _tools/build_course.py，需要同步分享包时使用 --package。旧十章生成入口已停用。archive、chapters 与根目录带书名号的审校报告属于历史资料，不参与新版构建，也不放入新版 ZIP。分享包用于阅读；本地维护工具保留在 _tools。

固定源码提交为 639ed015397290b3745d163aafe02ffee4aa3f84，根包版本 0.2.0-rc.2，Cordis 版本 4.0.4，核验日期为 2026-10-03。源码、参考文档与节选校验记录见 validation.json；数值算例以明确标注的教学输入计算，examples/ 保存实际执行的局部源码验证结果。

给别人学习时发送完整 ZIP，保留目录，解压后打开 reader.html。[本次核验](validation.json)与[版本说明](package-info.json)记录实际版本与范围。[重构记录](revision/changes.md)保留结构和重要事实变更。制作方另在本地 share-manifest.json 保存 ZIP 的最终哈希与逐文件比较结果。

正文与配图保留专有名词，首次出现用中文解释；具体约定见[专有名词使用约定](revision/naming-policy.md)。
