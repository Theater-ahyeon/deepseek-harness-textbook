# 计算与源码实验补充

第十七章评价示例新增可复算的逐项输入与本地 `calculations` 工具。输出保留 Decimal 计算结果、公式、单位、输入文件哈希和正文使用的整数舍入值。数据类型明确标为教学假设。

编写并运行 `examples/source-experiments.ts`，直接调用固定快照的读取窗口函数和 Inbox 实现。检查结果保存到 `examples/source-experiment-results.json`；计算工具再统计记录数量并绑定结果文件哈希。实际执行使用 Node 与 tsx，没有启动 Host 或调用模型。

原十九章叙事与技术结论保留。第十六、十七章增加结果入口，分享包增加 `examples/`。语法、术语索引、本地链接、源节选与原文哈希随构建重新核对。
