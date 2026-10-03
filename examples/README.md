# 计算与源码验证记录

这里保存教材写作时使用的计算输入、计算工具、断言代码和实际输出。读者可以直接看结果；运行代码用于复核，不作为课程练习。

## 第十七章：复算评价示例

`metrics-input.json` 保存同一组任务在甲、乙方案下的逐项通过标记和用量。它是教学假设数据，不是 DeepSeek Harness 的实测性能。

`calculations.py` 是本地 `calculations` 工具，用 Python `Decimal` 计算通过率、用量变化、百分点、相对增幅和通过任务的分摊用量。每个输出都附原公式、单位与输入文件哈希。表达式仅接受数字、已声明变量和四则运算。

```sh
python examples/calculations.py
python examples/verify-calculations.py
```

结果见 [calculation-results.json](calculation-results.json)。验证代码同时检查配对任务身份、十进制精度、非法表达式和零分母。

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
