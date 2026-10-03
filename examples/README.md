# 计算与源码验证记录

这里保存教材写作时使用的计算输入、计算工具、断言代码和实际输出。读者可以直接看结果；运行代码用于复核，不作为课程练习。

## 复算全书数值示例

`metrics-input.json` 保存请求材料的字节组成、压缩前后的区域大小、时间线、计数类别和逐项任务用量。它是教学假设数据，不是 DeepSeek Harness 的实测性能。

`calculations.py` 是本地 `calculations` 工具，用 Python `Decimal` 计算请求材料总量、重复规则的增幅、压缩区域的减少量，以及通过率、用量变化、百分点、相对增幅和通过任务的分摊用量。每个输出都附原公式、单位与输入文件哈希。表达式仅接受数字、已声明变量和四则运算。

```sh
python examples/calculations.py
python examples/verify-calculations.py
```

结果见 [calculation-results.json](calculation-results.json)。验证代码同时检查配对任务身份、十进制精度、非法表达式和零分母。

| 章节 | 算例 | 输出键前缀 |
| --- | --- | --- |
| 3 | turn、step、attempt 与 Tool Call 的计数 | C3 |
| 4 | 返回窗口的末行与剩余行数 | C4 |
| 5 | 消息、工具调用与事件的不同计数 | C5 |
| 6 | 重复规则加入前后的材料体积 | C6 |
| 7 | 按需获取 Skill 与全部获取的字节差 | C7 |
| 8 | 压缩区域与后续请求的字节差 | C8 |
| 9 | 尝试、退避与总耗时 | C9 |
| 11 | 请求、实际执行与成功结果的计数 | C11 |
| 13 | 启动、并发子任务与汇合的简化耗时 | C13 |
| 14 | 快照之后的预期序号与缺口 | C14 |
| 15 | 页面出现、业务可用与中间等待的耗时 | C15 |
| 17 | 通过率、token、百分点和相对增幅 | A、B、token、pass、relative |

## 第三、四章：运行真实源码函数

[source-experiments.ts](source-experiments.ts) 直接导入固定快照中的 `buildWindow`、`ReactLoopInbox` 与 Inbox 投影。实际运行使用 Node 和 tsx；结果记录 Node 版本、源码哈希、输入条件与断言后的观察。

| 记录 | 输入条件 | 实际检查的行为 |
| --- | --- | --- |
| E01 | 分块 CRLF 文本，指定行窗口 | 行号与内容正确，跨块换行不多出一行 |
| E02 | 输出字节上限很小 | 返回窗口受限，但继续扫描并得到完整总行数 |
| E03 | 中文字符占用超过字节上限 | 按 UTF-8 字节限制输出 |
| E04 | 空文件与越过文件末尾的 offset | 空文件正常返回，越界抛出 FS_NOT_FOUND |
| E05 | 同时存在 next-step 和 next-turn 输入 | 步骤边界领取全部步骤输入；轮次边界另外只领一个任务 |
| E06 | 把已等待的任务重复插入另一队列 | 在写入事件之前拒绝，等待状态不变 |

Inbox 实验中的 Session、Projection 查询和通知接口使用轻量替身；事件折叠与队列方法使用真实源码。实验未启动 Host，未发送模型请求，未运行上游测试套件。

制作环境已安装依赖，在 PowerShell 中运行：

```powershell
$env:TSX_TSCONFIG_PATH = (Resolve-Path source/tsconfig.base.json).Path
node --import ./source/node_modules/tsx/dist/loader.mjs examples/source-experiments.ts
python examples/calculations.py
```

源码快照不附带 `node_modules`。上述命令需要快照原有依赖已安装。实际结果可直接查阅 [source-experiment-results.json](source-experiment-results.json)，源文件和固定版本记录可在[实现证据](../evidence.html)中对照。
