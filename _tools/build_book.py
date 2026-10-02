"""Assemble authored chapters, verified excerpts and an offline reader.

The upstream checkout is read-only. No DSH tests or model requests run here.
"""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
plan_path = ROOT / "course-plan.json"
plan = json.loads(plan_path.read_text(encoding="utf-8"))
specs = json.loads((ROOT / "_tools/excerpt-spec.json").read_text(encoding="utf-8"))
commit = plan["commit"]
online = f"https://github.com/deepseek-ai/deepseek-harness/blob/{commit}/"


def block_replace(text, name, content):
    pattern = rf"<!-- {name}:start -->.*?<!-- {name}:end -->"
    return re.sub(pattern,lambda _:f"<!-- {name}:start -->\n\n{content.strip()}\n\n<!-- {name}:end -->",text,flags=re.S)


chapters=[]
quote_records=[]
for c in plan["chapters"]:
    cid=c["id"]
    path=ROOT/"chapters"/(cid+".md")
    text=path.read_text(encoding="utf-8")
    # User requested project explanation without exercises.
    text=re.sub(rf"\n## {cid}\.8 本章练习\n.*?(?=\n## {cid}\.9)","\n",text,flags=re.S)
    text=text.replace(f"## {cid}.9 小结与参考",f"## {cid}.8 小结与参考")
    text=text.replace("已解例题：","分析示例：")
    text=re.sub(r"\(\.\./figures/(F\d{2}[AB])\.svg\)",r"(../figures/\1.png)",text)
    if cid=="18":
        c["title"]="综合案例：已有文件工具如何接入与呈现"
        c["question"]="已有文件工具怎样兑现输入输出、执行、持久记录和界面呈现契约？"
    excerpts=[]
    for file,start,end,label,explanation in specs[cid]:
        content=(SOURCE/file).read_text(encoding="utf-8").splitlines()
        if not (1<=start<=end<=len(content)):
            raise ValueError(f"Invalid excerpt {file}:{start}-{end}")
        quote="\n".join(content[start-1:end])
        excerpts.append(f"**{label}。** {explanation}\n\n来源：[实际文件](../source/{file})，第 {start}—{end} 行；[固定提交]({online}{file}#L{start})。节选保留原码，省略邻近上下文。\n\n```ts\n{quote}\n```")
        quote_records.append({"chapter":cid,"file":"source/"+file,"start":start,"end":end,"excerpt_sha256":hashlib.sha256(quote.encode()).hexdigest()})
    route=["**完整阅读路线。** 路线区分启动前置、执行主链与提供方对照，不把它们误连为一次同步调用。\n"]
    for i,(file,line,symbol,inp,result) in enumerate(c["read"],1):
        route.append(f"{i}. [{file}](../source/{file})，`{symbol}`。输入：{inp}；输出/交接：{result}。[固定提交第 {line} 行]({online}{file}#L{line})。")
    text=block_replace(text,"evidence","\n\n".join(excerpts)+"\n\n"+"\n".join(route))
    references=["原项目文档用于复核，优先保留已有中文版：\n"]
    for file in c["docs"]:
        references.append(f"- [{file}](../source/{file})")
    if c["tests"]:
        references.append("\n行为旁证为测试源码，未在本次执行：\n")
        for file in c["tests"]:
            references.append(f"- [{file}](../source/{file})")
    references.append("\n[全书参考索引](../reference-index.md) · [术语与语法速查](../appendices.md)")
    text=block_replace(text,"references","\n".join(references))
    text=text.replace("\n\n\n","\n\n")
    path.write_text(text,encoding="utf-8")
    c["status"]="已展开"
    chapters.append((c,text))

plan["stage"]="complete_explanatory_edition"
plan["exercise_sections"]=False
plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

preface="""# 从一条任务学会 DeepSeek Harness

> 中文项目讲解完整版 · 18 章 · 2026-10-03 · 固定提交 639ed015397290b3745d163aafe02ffee4aa3f84

## 这本教材怎样读

先看一条真实职责链，再在需要时补类型、异步、插件和网络基础。全书使用“读取 README.md，说明用途并总结三点”作为教学场景，逐层解释入口、循环、材料、工具、会话、产品与证据。每章提供原创中文图示、完整因果讲解、精选原码、分析示例和原项目参考；没有课后练习或答题要求。

建议按 01—18 顺序阅读。首次读到源码片段时，先跟随中文解释，完整路径可稍后用于复核。部分数字专为解释计数或比较口径而设，均标教学假设，不是 DSH 性能报告。文档和图示无需先安装项目依赖即可阅读。

## 版本与方法

实现依据来自 [官方项目](https://github.com/deepseek-ai/deepseek-harness) 的固定源码副本，根包版本 0.2.0-rc.2，源码提交日期 2026-09-29。原文件、原文和 MIT 许可保留在 [source](source/README.md)。静态源码核验支持已实现流程，不冒充真实运行；本次没有运行 DSH、上游测试或付费模型实验。

章内组织借鉴《计算机体系结构：量化研究方法》的机制、取舍、定量分析与综合案例，方法来源见 [出版社介绍](https://shop.elsevier.com/books/computer-architecture/hennessy/978-0-12-811905-1)。配图参考《图解大模型》的直觉优先表达，公开参考见 [作者网站](https://www.llm-book.com/)；图稿是本课程原创，先画材料再展开机制，没有复制书中的图文。

用户提供的飞书“四板斧”帮助组织材料/能力、编排、评价与产品四个方向，不能替代本项目的实现证据。范围记录见 [sources.json](sources.json)。

## 全书导航

"""
book=[preface]
for c,text in chapters:
    book.append(f'- [{c["id"]}｜{c["title"]}](#chapter-{c["id"]})')
book.append("\n也可使用 [离线图文阅读版](reader.html)，或打开 chapters 中的单章 Markdown。[参考证据索引](reference-index.md)和[附录](appendices.md)随用随查。\n")
part=None
for c,text in chapters:
    if part!=c["part"]:
        part=c["part"]
        book.append(f"\n## {part}\n")
    adjusted=re.sub(r"^(#{1,5}) ",lambda m:"#"+m.group(1)+" ",text,flags=re.M)
    adjusted=adjusted.replace("](../","](")
    book.append(f'\n<a id="chapter-{c["id"]}"></a>\n\n'+adjusted)
book.append("\n## 全书收束\n\n项目的核心不是一个模型接口，而是有范围的材料组织、受控动作、明确状态、可用呈现和相称证据的合作。18 章已覆盖提纲中的核心路线；所有可选后端、OS 沙箱内部、LSP、浏览器/电脑操作、PTC、Jobs、Goal、Schedule、Webhook、Agent Teams、Python SDK、原生扩展、迁移、签名与发布尚未逐项深入，详见附录范围。\n")
book_text="\n".join(book)
(ROOT/"tutorial.md").write_text(book_text,encoding="utf-8")
(ROOT/"excerpt-manifest.json").write_text(json.dumps({"commit":commit,"excerpts":quote_records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Minimal deterministic renderer for the Markdown subset authored in this book.
def inline(text):
    tokens=[]
    def keep(value):
        tokens.append(value)
        return f"@@TOKEN{len(tokens)-1}@@"
    text=re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",lambda m:keep(figure(m.group(2),m.group(1))),text)
    text=re.sub(r"`([^`]+)`",lambda m:keep("<code>"+html.escape(m.group(1))+"</code>"),text)
    def hyperlink(m):
        target=m.group(2)
        if target=="reader.html":target="#top"
        return keep(f'<a href="{html.escape(target,quote=True)}">{html.escape(m.group(1))}</a>')
    text=re.sub(r"\[([^\]]+)\]\(([^)]+)\)",hyperlink,text)
    text=html.escape(text)
    text=re.sub(r"\*\*(.+?)\*\*",r"<strong>\1</strong>",text)
    for i,value in enumerate(tokens):text=text.replace(f"@@TOKEN{i}@@",value)
    return text


def figure(target,alt):
    resolved=ROOT/target
    svg=resolved.with_suffix(".svg")
    if svg.is_file():
        return '<figure>'+svg.read_text(encoding="utf-8")+f'<figcaption>{html.escape(alt)}</figcaption></figure>'
    return f'<img src="{html.escape(target,quote=True)}" alt="{html.escape(alt,quote=True)}"/>'


def render(md):
    lines=md.splitlines(); out=[]; i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith("<!--"):
            i+=1;continue
        if line.startswith('<a id="'):
            out.append(line);i+=1;continue
        if line.startswith("```"):
            lang=line[3:];i+=1;code=[]
            while i<len(lines) and not lines[i].startswith("```"):
                code.append(lines[i]);i+=1
            out.append('<pre><code class="language-'+html.escape(lang)+'">'+html.escape("\n".join(code))+"</code></pre>");i+=1;continue
        h=re.match(r"^(#{1,6}) (.*)",line)
        if h:
            level=len(h.group(1));out.append(f"<h{level}>"+inline(h.group(2))+f"</h{level}>");i+=1;continue
        if line.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].startswith("|"):
                cells=[v.strip() for v in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?",v or " ") for v in cells):rows.append(cells)
                i+=1
            out.append('<div class="table-wrap"><table>')
            for n,row in enumerate(rows):
                tag="th" if n==0 else "td"
                out.append("<tr>"+"".join(f"<{tag}>"+inline(v)+f"</{tag}>" for v in row)+"</tr>")
            out.append("</table></div>");continue
        if re.match(r"^(?:- |\d+\. )",line):
            ordered=bool(re.match(r"^\d+\. ",line));tag="ol" if ordered else "ul";out.append(f"<{tag}>")
            pattern=r"^\d+\. " if ordered else r"^- "
            while i<len(lines) and re.match(pattern,lines[i]):
                out.append("<li>"+inline(re.sub(pattern,"",lines[i]))+"</li>");i+=1
            out.append(f"</{tag}>");continue
        if line.startswith("> "):
            out.append("<blockquote>"+inline(line[2:])+"</blockquote>");i+=1;continue
        para=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r"^(#|```|<!--|<a |\||- |\d+\. )",lines[i]):
            para.append(lines[i]);i+=1
        out.append("<p>"+inline(" ".join(para))+"</p>")
    return "\n".join(out)


nav="".join(f'<a href="#chapter-{c["id"]}"><span>{c["id"]}</span>{html.escape(c["title"])}</a>' for c,_ in chapters)
css="""*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:30px}body{margin:0;background:#f5f7fa;color:#243247;font-family:'Microsoft YaHei','Noto Sans CJK SC',sans-serif;line-height:1.9}aside{position:fixed;left:0;top:0;bottom:0;width:290px;background:#fff;border-right:1px solid #dbe2ec;overflow:auto;padding:28px 20px}aside h2{font-size:20px;margin:0 0 18px}aside a{display:block;color:#4b5c73;text-decoration:none;font-size:13px;line-height:1.6;padding:9px 8px;border-radius:7px}aside a:hover{background:#edf3fa;color:#225fa3}aside span{color:#728ab0;margin-right:9px}main{margin-left:290px;padding:50px 5vw 100px;max-width:1500px}article{max-width:960px;margin:auto;background:white;border:1px solid #e2e7ef;border-radius:12px;padding:48px 56px}h1{font-size:34px;line-height:1.4;margin:0 0 22px}h2{font-size:27px;line-height:1.5;margin:65px 0 20px;border-top:1px solid #dbe2ec;padding-top:28px}h3{font-size:21px;line-height:1.6;margin:32px 0 14px}p{font-size:16px;margin:14px 0}a{color:#2866a5;text-underline-offset:3px;overflow-wrap:anywhere}blockquote{background:#edf3fa;border-left:4px solid #7198c9;margin:22px 0;padding:14px 20px;color:#465d79}code{background:#eef2f7;border-radius:4px;padding:2px 5px;font-family:Consolas,monospace;font-size:.9em}pre{background:#172336;color:#e0e8f3;padding:20px 24px;border-radius:9px;overflow:auto;line-height:1.65}pre code{background:none;padding:0;font-size:13px}figure{margin:25px -18px}figure svg{width:100%;height:auto;display:block}figcaption{color:#64748b;font-size:13px;text-align:center;margin-top:8px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #dce3ed;padding:10px 13px;text-align:left}th{background:#f0f4fa}li{margin:9px 0;font-size:15px}footer{margin-top:50px;font-size:13px;color:#64748b}@media(max-width:1050px){aside{position:static;width:auto;border-bottom:1px solid #dbe2ec;max-height:240px}aside nav{display:grid;grid-template-columns:1fr 1fr}main{margin:0;padding:25px 3vw}article{padding:28px 24px}figure{margin:18px -12px}}@media(max-width:600px){aside nav{display:block}h1{font-size:27px}h2{font-size:23px}p{font-size:15px}article{padding:23px 17px}}@media print{aside{display:none}main{margin:0;padding:0}article{border:0;padding:0;max-width:none}figure{break-inside:avoid}pre{white-space:pre-wrap;background:#f3f5f8;color:#18273b}h2{break-before:page}a{color:inherit}}"""
body=render(book_text)+"<h2>附录</h2>"+render((ROOT/"appendices.md").read_text(encoding="utf-8"))
document=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>从一条任务学会 DeepSeek Harness · 中文项目讲解</title><style>{css}</style></head><body id="top"><aside><h2>从一条任务学会 DSH</h2><p>中文项目讲解 · 18 章</p><nav>{nav}</nav><a href="reference-index.md">原项目证据索引</a><a href="tutorial.md">Markdown 完整版</a></aside><main><article>{body}<footer>固定源码版本 · 原创讲解和图示 · 静态核验，未运行项目实验</footer></article></main></body></html>'
(ROOT/"reader.html").write_text(document,encoding="utf-8")
print(json.dumps({"chapters":len(chapters),"verified_excerpts":len(quote_records),"book_chars":len(book_text),"chinese_characters":len(re.findall(r'[\u4e00-\u9fff]',book_text)),"exercise_sections":False,"offline_reader_bytes":len(document.encode())},ensure_ascii=False))
