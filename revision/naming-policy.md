# 专有名词使用约定

正文用中文讲解，项目名称、组件名、接口名和论文术语保留原文。首次出现时用中文解释它是什么、在哪里参与流程，后续沿用原名称。

- 保留 DeepSeek Harness、Agent、Session、Tool、Inbox、Skill、SkillRegistry、Provider、Surface、Context、Fiber、TokenMeter、SystemPrompt 等名称。
- profile 是项目的运行配置名称，保持源码用法；不统一改成另一个大小写名称。
- 保留 TypeScript、Promise、async、await、MCP、RPC、SDK、CLI、HMR 等名称、缩写与标识符。
- Cordis 论文采用 Spatiotemporal Composability、effect、coeffect、disposer、inverse、witnessed effect function 等原词；中文段落解释它们的含义与证明条件，不另造“副效果”“有证效果函数”之类替代名称。
- 模型上下文指模型本次可使用的材料；Cordis 的 Context 是访问服务与登记资源的对象。两者不混用。
- “请求”“依赖”“函数”“文件路径”等普通说明仍用中文。Tool 的解释可以谈“工具调用”，不要求每一个普通中文词都换成英文。
- 配图保留组件名，动作与关系尽量用中文；源码、路径和原项目文档保持原样。

这项约定落实于当前分章正文、补充说明、术语索引及原创配图，覆盖之前“术语首次补英文、以后中文优先”的写法。
