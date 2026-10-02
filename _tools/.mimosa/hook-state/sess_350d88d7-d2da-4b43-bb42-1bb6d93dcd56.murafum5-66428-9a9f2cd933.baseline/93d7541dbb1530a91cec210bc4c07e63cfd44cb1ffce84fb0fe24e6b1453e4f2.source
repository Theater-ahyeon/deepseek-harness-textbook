"""Finalize entry points, diagram metadata and reference coverage for the textbook."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(name):return (ROOT/name).read_text(encoding='utf-8')
def write(name,value):(ROOT/name).write_text(value,encoding='utf-8')
def save(name,value):write(name,json.dumps(value,ensure_ascii=False,indent=2)+'\n')

figures=json.loads(read('figures/figure-data.json'))
extras=[
 {'id':'F19A','title':'模型参数与运行框架材料是两层变化','kind':'compare','tag':'职责边界示意','left':['运行时改变','提示、历史与工具结果进入请求','配置选择提供方和模型','不由这条链推定权重更新'],'right':['另行模型训练','训练数据与目标决定更新','优化过程改变模型参数','需要新版本与独立评价证据']},
 {'id':'F20A','title':'运行证据怎样支持版本改进','kind':'flow','tag':'教学分析 · 不是默认自动流水线','nodes':[['记录条件与轨迹','版本、任务、材料与结果','log'],['定位首次偏差','读取、压缩、动作或生成','control'],['选择更新产物','文档、技能、程序或模型','control'],['管理版本变更','验证依赖与实际启用','tool'],['复核工程行为','回放与相应检查','log'],['判断实际任务效果','质量、时间、用量与失败','user']]},
 {'id':'F21A','title':'整个项目的三组合作职责','kind':'columns','tag':'功能地图 · 不表示调用顺序','columns':[['运行与材料','入口、队列、轮次与步骤','会话、提示、技能与压缩','模型路由、附件与历史引用'],['能力与动作','文件、网页与语义导航','Shell、终端、PTC 与沙箱','MCP、子代理、工作流与团队'],['产品与治理','CLI、SDK、网页与桌面','预览、语音、提醒与外部触发','存储、评价、反馈与版本管理']]},
 {'id':'F22A','title':'触发工作与证明工作完成分开观察','kind':'compare','tag':'外部触发边界示意','left':['定时提醒','宿主保存时间与目标会话','到时投递原会话','投递后仍有普通任务过程'],'right':['外部 Webhook','提供方验证交付，规则判断','可创建工作区根会话','runtime 不自带去重和结果跟踪']},
]
figures=[f for f in figures if f['id'] not in {x['id'] for x in extras}]+extras
save('figures/figure-data.json',figures)

for file,heading,addition in [
 ('_tools/book_sections.py','## 8.1 推理调用与参数更新是两种变化','![模型参数与运行框架材料是两层变化](../figures/F19A.png)\n\n图 8A 是职责边界示意。左边改变当前输入与动作，右边需要另行训练；不能从模型在本次任务里纠错推出权重已经更新。'),
 ('_tools/book_sections.py','## 9.1 原始轨迹怎样成为可用证据','![运行证据怎样支持版本改进](../figures/F20A.png)\n\n图 9A 是教学分析链，表示不同证据环节怎样衔接，不宣称项目默认自动完成所有环节。'),
 ('_tools/module_explanations.py','## 1.4 用一张地图认识整个仓库','![整个项目的三组合作职责](../figures/F21A.png)\n\n图 1C 将运行与材料、能力与动作、产品与治理并列呈现。它是功能地图，不是三步执行流程。'),
 ('_tools/module_explanations.py','## 9.7 Schedule 与 Webhook：不是每项任务都由当前页面发起','![触发工作与证明工作完成分开观察](../figures/F22A.png)\n\n图 9B 对照两种触发来源；任一方成功投递都不能证明随后任务已完成。'),
]:
    content=read(file)
    if addition not in content:content=content.replace(heading,heading+'\n\n'+addition)
    write(file,content)

illustration=read('illustration-plan.md').replace('36 张','40 张').replace('## 2. 图的展开顺序','## 2. 图的展开顺序')
illustration+='\n## 完整版新增图示\n\n十章教材保留原核心专题图号，并新增整体地图、模型边界、改进链与外部触发图。\n\n| 图号 | 讲解位置 | 用途 |\n| --- | --- | --- |\n'
for f in extras:illustration+=f'| {f["id"]} | {f["title"]} | {f["tag"]} |\n'
write('illustration-plan.md',illustration)

gallery=['# 原创中文图示目录\n','40 张原创图均提供 PNG 与 SVG。图号保留专题标识，教材按十章阅读；图内教学假设不作为项目实测。\n']
for f in figures:
    fid=f['id']
    gallery.append(f'## {fid}｜{f["title"]}\n\n![{f["title"]}]({fid}.png)\n\n[可修改 SVG]({fid}.svg) · [教材入口](../tutorial.md)\n')
write('figures/index.md','\n'.join(gallery))

source=json.loads(read('sources.json'))
source['title']='深入理解 DeepSeek Harness：从智能体基础到工程协作'
source['chapter_count']=10
source['source_topic_count']=18
source['subsystems_explained']=63
source['figure_count']=40
source['planned_figure_count']=40
source['source_excerpt_count']=60
source['exercise_sections']=False
source['delivery_stage']='十章中文教材完整版，正文独立解释；源码与原文作为可选证据'
source['reader_prerequisite']='少量概念即可；无需预读源码或原项目文档；不要求安装运行'
source['scope']='完整功能架构、核心运行过程与全部已列子系统协作；不穷举配置/API 字段、每个平台后端内部或发布矩阵'
if not any(s['id']=='ai-agent-book-structure' for s in source['sources']):
    source['sources'].append({'id':'ai-agent-book-structure','kind':'user_supplied_open_book','title':'深入理解 AI Agent','url':'https://bojieli.github.io/ai-agent-book/','structure_url':'https://bojieli.github.io/ai-agent-book/book/introduction/','accessed_date':'2026-10-03','use':'十章两部分的主题递进与问题组织；正文重新创作，DSH 实现以固定仓库为证据','limits':'查看公开目录、引言与十章入口/目录；不复制全书，不移植其全部能力主张，不附配套练习'})
source['verification']['course_artifact_validation']='validation.json：十章正文、63 项子系统覆盖、40 张图、60 段可选原码、离线链接和源码哈希；不执行上游项目测试'
save('sources.json',source)

write('README.md','''# 深入理解 DeepSeek Harness

从智能体基础到工程协作的中文项目教材。适合只了解少量概念的初学者，正文独立解释项目，无需先阅读源码或官方文档，不设练习。

**开始阅读：[离线图文阅读版](reader.html)。** 解压后用浏览器打开，即可按第 1—10 章顺序阅读正文与全部图示，无需联网加载图或脚本。

- [完整 Markdown 教材](tutorial.md)：十章全文，分“理解与构建”和“评价、改进与协作”两部分。
- [单章教材](book/)：与全文保持同一章号，适合分章阅读。
- [基础与术语附录](appendices.md)：遇到新概念时查询。
- [图示目录](figures/index.md)：40 张原创中文图，均有 PNG 和可修改 SVG。
- [可选参考证据](reference-index.md)：原项目文档、源码与测试旁证。
- [原码节选附录](source-excerpts.md)：60 段精选原码；可以完全略过而继续学习。

正文整合 18 个核心实现专题，并解释官方子系统目录中 63 项能力的功能、协作和主要边界。原始专题稿在 `chapters/`，内部编号仅供证据维护，不是教材章号。详细配置/API 字段、每个平台后端内部与发布矩阵不逐项穷举。

实现固定在官方提交 `639ed015397290b3745d163aafe02ffee4aa3f84`，根包 `0.2.0-rc.2`。`source/` 保留原仓库、中文文档与 MIT 许可；新正文在其外撰写。静态核验不冒充执行报告，本次未运行项目、上游测试或付费模型实验。

**给别人学习：发送交付 ZIP，保留目录结构，解压后打开 `reader.html`。** 仅转发一个 Markdown 会缺少图片和可选原文；ZIP 不包含 Git 元数据、编写脚本或历史提纲。

写作与参考方法见 [chapter-format.md](chapter-format.md) 和 [illustration-plan.md](illustration-plan.md)。版本、覆盖与核验记录见 [sources.json](sources.json)、[coverage.json](coverage.json)、[validation.json](validation.json)。
''')

format_text=read('chapter-format.md')
format_text=format_text.replace('每章按以下顺序展开，具体小节标题结合项目内容调整：','十章主题主线参考[《深入理解 AI Agent》全书结构](https://bojieli.github.io/ai-agent-book/book/introduction/)。每章先给中文导入，再串联机制与补充能力，最后收束。以下顺序用于核心机制专题，不要求读者阅读任何源码附件：')
format_text=format_text.replace('三段精选原码与完整阅读路线，交代源码输入、输出与省略上下文','正文补足机制解释；原码与阅读路线移至可选证据附录')
format_text=format_text.replace('小结因果关系，附原项目文档与测试源码旁证','小结因果关系；参考原文与测试源码仅作为可选旁证')
format_text=format_text.replace('源码用于支撑中文讲解','源码在附录支撑中文讲解，不作为正文前提')
format_text+='\n正文覆盖完整功能架构与文档化子系统，但不逐字段替代 API 手册或穷举所有平台内部。正文首次出现一个模块时，应解释它解决的问题、输入输出、进入主链的条件与失败/生命周期边界；不能以“见源码”替代这些解释。\n'
write('chapter-format.md',format_text)

appendix=read('appendices.md')
appendix=appendix.replace('每章精选代码片段带实际文件、行号和固定提交链接。','可选证据附录中的代码片段带实际文件、行号和固定提交链接。正文无需阅读这些片段即可理解。')
old='未在正文深入的所有模型与执行后端、OS 沙箱内部、LSP、浏览器/电脑操作、PTC、Jobs、Goal、Schedule、Webhook、Agent Teams、Python SDK、原生扩展、历史迁移、签名和发布，仍是扩展阅读。全书完成的是已明确列出的核心项目路线，不把这些模块列为已经系统讲解。'
appendix=appendix.replace(old,'正文已经解释核心运行链以及官方目录中 63 项子系统的功能、协作与主要边界，包括可选执行、语音、定时、团队与 SDK 载体。深入修改项目时，精确 API/配置字段、每个平台沙箱内部、所有后端实现与发布矩阵仍需查相应版本手册；这些细节不作为本教材阅读前提。')
write('appendices.md',appendix)

plan=json.loads(read('book-plan.json'))
coverage=json.loads(read('coverage.json'))['subsystems']
labels={name:(ROOT/'source/docs/subsystems'/f'{name}.zh.md').read_text(encoding='utf-8').splitlines()[0].lstrip('# ') for group in [coverage] for name in [x['subsystem'] for x in group]}
index=['# 可选证据索引\n','正文已经独立解释项目，这份索引用于复核或深入修改，不是阅读前提。原文、源码、测试和 MIT 许可均保留在固定仓库副本。测试只作源码旁证，本次未执行。\n','固定提交：`639ed015397290b3745d163aafe02ffee4aa3f84`；根包 `0.2.0-rc.2`。\n','## 按新版十章查阅\n','| 教材 | 文档化子系统参考 |\n| --- | --- |']
for c in plan['chapters']:
    refs=[f'[{labels[x["subsystem"]]}]({x["reference"]})' for x in coverage if x['book_chapter']==c['id']]
    index.append(f'| [第 {int(c["id"])} 章：{c["title"]}](tutorial.md#chapter-{c["id"]}) | '+ '<br>'.join(refs)+' |')
index+=['\n## 精选原码与原始专题\n','[60 段原码节选及完整路径](source-excerpts.md)供核对。18 个专题内部编号保留，仅用于维护，教材以十章顺序阅读。\n','| 专题 | 教材所在章 | 完整参考 |\n| --- | --- |']
topics=json.loads(read('course-plan.json'))['chapters']
major_of={tid:int(c['id']) for c in plan['chapters'] for tid in c['topics']}
for t in topics:
    refs=[f'[{Path(p).name}](source/{p})' for p in t['docs']]
    index.append(f'| [专题 {t["id"]}：{t["title"]}](tutorial.md#topic-{t["id"]}) | 第 {major_of[t["id"]]} 章 | '+'<br>'.join(refs)+' |')
index+=['\n## 证据与复用\n','原始文档说明契约，源码说明实现分支，测试源码说明断言方式；真实运行效果需运行证据支持，不能互相替代。教学图与假设数字是本教材原创解释，不作为项目实测。\n','分享包保留完整 source 目录及 [MIT 许可](source/LICENSE)，仅省略 Git 元数据。参考书只保留公开链接与结构方法说明，未打包其正文或插图。\n','[参考文件哈希](reference-manifest.json) · [节选行号与哈希](excerpt-manifest.json) · [覆盖记录](coverage.json) · [教材检查](validation.json)\n']
write('reference-index.md','\n'.join(index))

manifest=json.loads(read('reference-manifest.json'))
selected={x['path'] for x in manifest['files']}
selected.update(x['reference'] for x in coverage)
selected.update(x['file'] for x in json.loads(read('excerpt-manifest.json'))['excerpts'])
selected.update(['source/packages/llm/llm/README.zh.md','source/packages/llm/llm-pi-ai/README.zh.md','source/packages/boot/plugin-manager/README.zh.md','source/packages/experimental/agent-team/README.zh.md'])
manifest['files']=[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'kind':'original_document' if p.endswith('.md') else ('license' if p.endswith('LICENSE') else 'source_or_test')} for p in sorted(selected)]
manifest['scope']='All cited core-topic files, documented subsystem references, supplementary evidence, root README and license; not a hash of every repository file'
save('reference-manifest.json',manifest)
print('Ten-chapter edition metadata, references and four additional diagram specifications synchronized')
