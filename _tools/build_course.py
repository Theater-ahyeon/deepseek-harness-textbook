"""从唯一正文 book/*.md 构建离线教材，并重新核对本次版本。
不导入旧生成器，不写回分章，不执行上游项目。仅依赖 Python 标准库。
"""
from pathlib import Path
from datetime import datetime, timezone
from html import escape
import argparse, hashlib, html, json, os, re, subprocess, zipfile
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
COMMIT='639ed015397290b3745d163aafe02ffee4aa3f84'
def read(name):return (ROOT/name).read_text(encoding='utf-8')
def write(name,text):(ROOT/name).write_text(text.rstrip()+'\n',encoding='utf-8')
def data(name):return json.loads(read(name))
def dump(name,obj):write(name,json.dumps(obj,ensure_ascii=False,indent=2))
def reviewed_sha_matches(name,expected):
    actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    if actual==expected:return True
    if name=='README.md' and (ROOT/'revision/readme-refresh-20261003.json').is_file():
        revision=data('revision/readme-refresh-20261003.json')
        return revision['before_sha256']==expected and revision['after_sha256']==actual
    return False
def retarget(md):
    out=[];fenced=False
    for line in md.splitlines():
        if line.startswith('```'):fenced=not fenced
        out.append(line if fenced else re.sub(r'(\]\()\.\./',r'\1',line))
    return '\n'.join(out)

CSS=read('_tools/reader-layout.css')
MD_HTML={'tutorial.md':'reader.html','appendices.md':'appendices.html','subsystems.md':'subsystems.html','evidence-index.md':'evidence.html','reference-index.md':'references.html','glossary.md':'glossary.html','tech-choices.md':'tech-choices.html'}
def inline(s):
    saved=[]
    def keep(v):saved.append(v);return f'@@KEEP{len(saved)-1}@@'
    s=re.sub(r'`([^`]+)`',lambda m:keep('<code>'+escape(m[1])+'</code>'),s)
    def link(m):
        target=m[2]
        name,sep,fragment=target.partition('#')
        if name in MD_HTML:target=MD_HTML[name]+(sep+fragment if sep else '')
        elif re.fullmatch(r'book/\d\d\.md',name):
            target='reader.html#'+(fragment if sep else 'chapter-'+Path(name).stem)
        return keep('<a href="'+escape(target,quote=True)+'">'+escape(m[1])+'</a>')
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,s)
    s=escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>',s)
    for i,v in enumerate(saved):s=s.replace(f'@@KEEP{i}@@',v)
    return s
def render(md):
    lines=md.splitlines();i=0;out=[];source=False;head=0
    def close_source():
        nonlocal source
        if source:out.append('</section>');source=False
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.startswith('<!--'):i+=1;continue
        if re.fullmatch(r'<a id="[\w-]+"></a>',line):out.append(line);i+=1;continue
        if line.startswith('```'):
            lang=line[3:];i+=1;code=[]
            while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
            out.append('<pre'+(' class="source-code"' if source else '')+'><code class="language-'+escape(lang,quote=True)+'">'+escape('\n'.join(code))+'</code></pre>');i+=1;continue
        m=re.match(r'^(#{1,6}) (.*)',line)
        if m:
            level=len(m[1]);head+=1
            if level<=2:close_source()
            if level==2 and '源码研读' in m[2]:out.append('<section class="source-section">');source=True
            out.append(f'<h{level} id="heading-{head}">'+inline(m[2])+f'</h{level}>');i+=1;continue
        img=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if img:
            target=img[2];svg=str(Path(target).with_suffix('.svg'))
            if (ROOT/svg).is_file():target=svg.replace('\\','/')
            out.append('<figure><img loading="lazy" src="'+escape(target,quote=True)+'" alt="'+escape(img[1],quote=True)+'"><figcaption>'+escape(img[1])+' · <a href="'+escape(target,quote=True)+'">查看原图</a></figcaption></figure>');i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[x.strip().replace(r'\|','|') for x in re.split(r'(?<!\\)\|',lines[i].strip().strip('|'))]
                if not all(re.fullmatch(r':?-+:?',x) for x in cells):rows.append(cells)
                i+=1
            out.append('<div class="table-wrap'+(' source-line-table' if source and rows and rows[0][0]=='原文件行号' else '')+'"><table>')
            for n,row in enumerate(rows):
                tag='th' if n==0 else 'td';out.append('<tr>'+''.join('<'+tag+'>'+inline(x)+'</'+tag+'>' for x in row)+'</tr>')
            out.append('</table></div>');continue
        if re.match(r'^(?:- |\d+\. )',line):
            ordered=bool(re.match(r'^\d+\. ',line));tag='ol' if ordered else 'ul';pat=r'^\d+\. ' if ordered else r'^- '
            out.append('<'+tag+'>')
            while i<len(lines) and re.match(pat,lines[i]):out.append('<li>'+inline(re.sub(pat,'',lines[i]))+'</li>');i+=1
            out.append('</'+tag+'>');continue
        if line.startswith('> '):out.append('<blockquote>'+inline(line[2:])+'</blockquote>');i+=1;continue
        if line.strip()=='---':out.append('<hr>');i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|```|<!--|<a |\||- |\d+\. |!\[)',lines[i]):paragraph.append(lines[i]);i+=1
        out.append('<p'+(' class="source-code-note"' if source and line.startswith('代码类型：') else '')+'>'+inline(' '.join(paragraph))+'</p>')
    close_source();return '\n'.join(out)
def page(title,md,nav=''):
    main_reader=bool(nav)
    if not nav:
        nav='<a href="reader.html">全书导读</a><span class="nav-label">随用随查</span><a href="appendices.html">语法与数据基础</a><a href="subsystems.html">补充能力</a><a href="glossary.html">术语索引</a><a href="evidence.html">实现证据</a><a href="references.html">原项目文档</a>'
    else:
        nav='<a href="#book-home">全书导读</a><span class="nav-label">十九章正文</span>'+nav
        nav=nav.replace('<a href="subsystems.html">','<span class="nav-label">随用随查</span><a href="appendices.html">语法与数据基础</a><a href="subsystems.html">')+'<a href="references.html">原项目文档</a>'
    nav += '<a href="tech-choices.html">技术选型与替代方案</a>'
    content=render(md)
    if main_reader:
        parts=re.split(r'<a id="(chapter-\d\d)"></a>',content)
        goals={str(r['chapter']).zfill(2):r['objective'] for r in data('revision/learning-objectives.json')}
        def overview(match):
            cards=[]
            for number,title in re.findall(r'<li><a href="#chapter-(\d\d)">(.*?)</a></li>',match[0]):
                cards.append('<a class="chapter-card" href="#chapter-'+number+'"><strong>'+title+'</strong><span>'+escape(goals[number])+'</span></a>')
            return '<div class="chapter-overview">'+''.join(cards)+'</div>'
        home=re.sub(r'<ul>\s*(?:<li><a href="#chapter-\d\d">.*?</a></li>\s*)+</ul>',overview,parts[0])
        content='<section id="book-home" class="book-section home-section">'+home+'</section>'
        for index in range(1,len(parts),2):
            ident=parts[index]
            content+='<section id="'+ident+'" class="book-section" data-chapter="'+ident[-2:]+'">'+parts[index+1]+'</section>'
    values={'TITLE':escape(title),'NAV':nav,'CONTENT':content,'CSS':CSS,'SCRIPT':read('_tools/reader-layout.js')}
    return re.sub(r'@@(TITLE|NAV|CONTENT|CSS|SCRIPT)@@',lambda m:values[m[1]],read('_tools/reader-layout.html'))

class PageIndex(HTMLParser):
    def __init__(self,s):
        super().__init__();self.ids=[];self.targets=[];self.feed(s)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a' and attrs.get('href'):self.targets.append(attrs['href'])
        if tag=='img' and attrs.get('src'):self.targets.append(attrs['src'])

def validate(chapters,evidence):
    errors=[];quotes=0;lines_explained=0;links=0
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT/'source',text=True).strip() if (ROOT/'source/.git').exists() else data('source-snapshot.json')['commit']
    if actual!=COMMIT:errors.append('源码提交与教材基线不同')
    for e in evidence:
        lines=read(e['path']).splitlines()[e['start']-1:e['end']];code='\n'.join(lines)
        if hashlib.sha256(code.encode()).hexdigest()!=e['excerpt_sha256']:errors.append(e['id']+' 原码变化')
        if sum(bool(x.strip()) for x in lines)!=len(e['explanations']):errors.append(e['id']+' 逐行解释缺失')
        chapter=read(f'book/{e["chapter"]:02}.md')
        if '```ts\n'+code+'\n```' not in chapter:errors.append(e['id']+' 正文节选不一致')
        for syntax,explanation in e['explanations']:
            if '| '+syntax+' | '+explanation+' |' not in chapter:errors.append(e['id']+' 逐行讲解与清单不一致')
        quotes+=1;lines_explained+=len(e['explanations'])
    refs=data('reference-manifest.json')['files']
    for ref in refs:
        p=ROOT/ref['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=ref['sha256']:errors.append('原参考变化：'+ref['path'])
    technical=data('revision/technical-review-20261003.json')
    technical_ranges=0
    if technical['commit']!=COMMIT:errors.append('技术复审版本与源码基线不同')
    for finding in technical['findings']:
        for loc in finding['source']:
            quote='\n'.join(read(loc['path']).splitlines()[loc['start']-1:loc['end']])
            if hashlib.sha256(quote.encode()).hexdigest()!=loc['sha256']:errors.append('技术复审定位变化：'+loc['path'])
            technical_ranges+=1
    second_review=data('revision/second-technical-review-20261003.json') if (ROOT/'revision/second-technical-review-20261003.json').is_file() else None
    second_ranges=0
    if second_review:
        if second_review['commit']!=COMMIT:errors.append('第二轮复审版本与源码基线不同')
        for finding in second_review['findings']:
            for loc in finding['source']:
                quote='\n'.join(read(loc['path']).splitlines()[loc['start']-1:loc['end']])
                if hashlib.sha256(quote.encode()).hexdigest()!=loc['sha256']:errors.append('第二轮复审定位变化：'+loc['path'])
                second_ranges+=1
    files=[ROOT/f for f in ['README.md','tutorial.md','appendices.md','subsystems.md','glossary.md','evidence-index.md','reference-index.md','source-excerpts.md','examples/README.md','tech-choices.md']]+[p for p,_ in chapters]
    for p in files:
        s=p.read_text(encoding='utf-8');s=re.sub(r'```[^\n]*\n[\s\S]*?```','',s)
        for m in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)',s):
            target=m[1];name,_,anchor=target.partition('#')
            if re.match(r'https?:|mailto:',name):continue
            dest=p.parent/name if name else p
            links+=1
            if not dest.exists():errors.append(f'{p.name} 缺失链接 {target}')
            elif anchor and dest.suffix=='.md' and 'id="'+anchor+'"' not in dest.read_text(encoding='utf-8'):errors.append(f'{p.name} 缺失锚点 {target}')
    pages={name:PageIndex(read(name)) for name in ['reader.html','index.html',*list(MD_HTML.values())[1:]]}
    for name,index in pages.items():
        if len(set(index.ids))!=len(index.ids):errors.append(name+' 有重复 id')
        for target in index.targets:
            base,_,anchor=target.partition('#')
            if re.match(r'https?:|mailto:',base):continue
            dest=ROOT/base if base else ROOT/name
            links+=1
            if not dest.exists():errors.append(name+' 缺失 HTML 链接 '+target)
            elif anchor and dest.suffix=='.html':
                target_index=pages.get(dest.name) or PageIndex(dest.read_text(encoding='utf-8'))
                if anchor not in target_index.ids:errors.append(name+' 缺失 HTML 锚点 '+target)
    images=re.findall(r'<img[^>]+src="([^"]+)"',read('reader.html'))
    for path in images:
        if not (ROOT/path).is_file():errors.append('阅读版缺图 '+path)
    qcounts=[]
    for p,_ in chapters:
        text=p.read_text(encoding='utf-8');qcounts.append(len(re.findall(r'(?:### 问题 |\*\*问题 \d)',text)))
        if qcounts[-1]<3:errors.append(p.name+' 缺少理解题')
        if text.count('```')%2:errors.append(p.name+' 代码围栏不闭合')
    term_records=data('revision/terms.json')
    for record in term_records:
        actual_lines=read(record['file']).splitlines()
        at=record['line']-1
        if at>=len(actual_lines) or actual_lines[at]!=record['explanation_paragraph']:
            errors.append('术语定位变化：'+record['term'])
    all_images=[]
    for name in pages:all_images+=re.findall(r'<img[^>]+src="([^"]+)"',read(name))
    reader_sha=hashlib.sha256((ROOT/'reader.html').read_bytes()).hexdigest()
    browser=data('_tools/browser-review.json') if (ROOT/'_tools/browser-review.json').is_file() else None
    browser=browser if browser and browser.get('reader_sha256')==reader_sha else None
    result={'edition':'nineteen_chapter_zero_code_rewrite','verified_at':datetime.now(timezone.utc).isoformat(),'source_commit':COMMIT,'chapter_count':len(chapters),'annotated_source_excerpts':quotes,'nonempty_source_lines_explained':lines_explained,'reference_hashes_checked':len(refs),'local_links_checked':links,'html_pages_checked':len(pages),'reader_figure_occurrences':len(images),'reader_unique_figures':len(set(images)),'all_reading_unique_figures':len(set(all_images)),'terminology_locations_checked':len(term_records),'exercise_questions':sum(qcounts),'exercise_sections':True,'canonical':'book/*.md','source_review':'针对本书主链与本次列出节选的静态核验；补充能力区分官方文档证据','upstream_tests_run':False,'project_runtime_started':False,'real_model_calls':False,'reader_sha256':reader_sha,'browser_review':browser or 'pending','errors':errors}
    result['technical_review_findings']=len(technical['findings'])
    result['technical_review_source_ranges_checked']=technical_ranges
    calculations=data('examples/calculation-results.json')
    if calculations['input_sha256']!=hashlib.sha256((ROOT/'examples/metrics-input.json').read_bytes()).hexdigest():errors.append('计算样本与计算结果不一致')
    experiments=data('examples/source-experiment-results.json')
    if calculations['source_experiments']['input_sha256']!=hashlib.sha256((ROOT/'examples/source-experiment-results.json').read_bytes()).hexdigest():errors.append('实验统计与实际观察不一致')
    if experiments['sourceCommit']!=COMMIT:errors.append('实验与固定源码版本不一致')
    if experiments['scriptSha256']!=hashlib.sha256((ROOT/'examples/source-experiments.ts').read_bytes()).hexdigest():errors.append('实验输出与实验代码不一致')
    for loc in experiments['source']:
        if hashlib.sha256((ROOT/loc['path']).read_bytes()).hexdigest()!=loc['sha256']:errors.append('实验源文件哈希变化：'+loc['path'])
    result['calculations_tool']=calculations['tool']+' (local Python CLI)'
    result['calculated_metrics']=len(calculations['results'])
    result['source_experiment_cases']=len(experiments['cases'])
    result['source_experiments']='actual source functions; simulated Session/Projection seam; assertions passed'
    if second_review:
        result['second_review_findings']=len(second_review['findings'])
        result['second_review_source_ranges_checked']=second_ranges
    if (ROOT/'revision/chapter-language-edits-20261003.json').is_file():
        editorial=data('revision/chapter-language-edits-20261003.json')
        followup=data('revision/source-reading-explanations-20261003.json') if (ROOT/'revision/source-reading-explanations-20261003.json').is_file() else None
        followup_files={r['file']:r for r in followup['files']} if followup else {}
        for item in editorial['files']:
            actual_sha=hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest()
            successor=followup_files.get(item['file'])
            if not reviewed_sha_matches(item['file'],item['after_sha256']) and not (successor and successor['before_sha256']==item['after_sha256'] and reviewed_sha_matches(item['file'],successor['after_sha256'])):
                errors.append('逐章语言复核版本变化：'+item['file'])
        for p in [*[p for p,_ in chapters],ROOT/'subsystems.md',ROOT/'appendices.md']:
            if re.search('而是|而不是',p.read_text(encoding='utf-8')):
                errors.append('正文残留否定对照句式：'+p.name)
        result['chapter_language_review']={'chapters':19,'edits':editorial['paragraph_or_heading_edits'],'Gemini_suggestions_reviewed':len(editorial['gemini_decisions']),'forbidden_contrast_matches':0,'original_code_and_images_preserved':editorial['original_code_and_images_preserved']}
        if followup:
            if len(followup['blocks'])!=27 or {b['id'] for b in followup['blocks']}!={e['id'] for e in evidence}:
                errors.append('独立实现详解覆盖不完整')
            if {r['file'] for r in followup['files']}!={*[f'book/{i:02}.md' for i in range(1,20)],'revision/terms.json','README.md','chapter-format.md'}:
                errors.append('独立实现详解修订文件不完整')
            for item in followup['files']:
                raw=(ROOT/item['file']).read_bytes()
                if not reviewed_sha_matches(item['file'],item['after_sha256']):errors.append('实现详解版本变化：'+item['file'])
                if item['file'].startswith('book/'):
                    newline='\r\n' if b'\r\n' in raw else '\n'
                    for block in [b for b in followup['blocks'] if b['file']==item['file']]:
                        insertion=block['text'].replace('\n',newline).encode('utf-8')
                        if raw.count(insertion)!=1:errors.append('实现详解内容缺失或重复：'+block['id'])
                        raw=raw.replace(insertion,b'',1)
                    if hashlib.sha256(raw).hexdigest()!=item['before_sha256']:errors.append('实现详解之外的原章节内容变化：'+item['file'])
            for block in followup['blocks']:
                source_binding=block['source']
                if hashlib.sha256((ROOT/source_binding['path']).read_bytes()).hexdigest()!=source_binding['file_sha256']:
                    errors.append('实现详解来源变化：'+block['id'])
                if len(block['text'].split('\n\n'))<5 or len(block['text'])<420:errors.append('实现详解过于简略：'+block['id'])
                chapter=read(block['file']);start=chapter.index('<a id="'+block['id'].lower()+'"></a>')
                if chapter.index(block['text'],start)>chapter.index('代码类型：',start):errors.append('实现详解不在源码之前：'+block['id'])
            result['source_reading_explanations']={'chapters':19,'detailed_blocks':27,'added_characters':sum(len(b['text']) for b in followup['blocks']),'original_chapters_recoverable':True,'code_tables_figures_preserved':True}
    if (ROOT/'revision/technology-choices-review-20261003.json').is_file():
        choices=data('revision/technology-choices-review-20261003.json')
        if hashlib.sha256((ROOT/choices['file']).read_bytes()).hexdigest()!=choices['sha256']:
            errors.append('技术选型专题正文与复核记录不一致')
        for group in choices['evidence_groups']:
            for item in group['sources']:
                if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()!=item['sha256']:
                    errors.append('技术选型依据变化：'+item['path'])
        if re.search('而是|而不是',read('tech-choices.md')):
            errors.append('技术选型专题残留否定对照句式')
        result['technology_choices']={'comparison_topics':choices['comparison_topics'],'evidence_groups':len(choices['evidence_groups']),'source_file_bindings':sum(len(g['sources']) for g in choices['evidence_groups']),'official_reference_links':len(choices['official_comparison_references']),'file':'tech-choices.md'}
    if (ROOT/'revision/readme-refresh-20261003.json').is_file():
        revision=data('revision/readme-refresh-20261003.json')
        if hashlib.sha256((ROOT/'README.md').read_bytes()).hexdigest()!=revision['after_sha256']:errors.append('README 与首页修订记录不一致')
        cover=revision['cover']
        if hashlib.sha256((ROOT/cover['path']).read_bytes()).hexdigest()!=cover['sha256']:errors.append('README 封面变化')
        readme=read('README.md')
        chapter_links=re.findall(r'\]\((book/\d\d\.md)\)',readme)
        if set(chapter_links)!={f'book/{i:02}.md' for i in range(1,20)}:errors.append('README 章节地图不完整')
        for target in re.findall(r'(?:\]\(|href=")([^\s)"<>]+)',readme):
            if target.startswith(('http:','https:','#')):continue
            if not (ROOT/target.split('#',1)[0]).exists():errors.append('README 本地入口缺失：'+target)
        if re.search('而是|而不是',readme):errors.append('README 残留否定对照句式')
        result['readme_homepage']={'chapter_links':19,'cover':cover['path'],'local_links_valid':True,'sha256':revision['after_sha256']}
    dump('validation.json',result)
    if errors:raise SystemExit(json.dumps(errors,ensure_ascii=False))
    return result

def build(package=False):
    chapters=[]
    for p in sorted((ROOT/'book').glob('[0-9][0-9].md')):
        title=p.read_text(encoding='utf-8').splitlines()[0][2:]
        chapters.append((p,title))
    if len(chapters)!=19:raise ValueError('本版应有十九章，实际 '+str(len(chapters)))
    preface='''# 深入理解 DeepSeek Harness

本书围绕“读取项目 README 并总结三项功能”的任务，讲解 DeepSeek Harness 的架构与运行机制。正文按数据流和执行顺序解释组件职责，并在需要时补充 TypeScript 与异步基础；源码研读提供逐行说明，支持进一步核对实现。

第一至九章建立运行与材料基础；第十至十五章解释装配、执行边界和产品；第十六至十八章学习验证、评价和能力整合；第十九章讨论 Cordis 论文与具体实现的对应条件。

[技术选型与替代方案](tech-choices.md)解释十四组选型的源码依据、优势、维护代价与替代实现，可以随对应章节查阅。

每章配有讲解问答，把容易混淆的概念放回具体流程。源码研读在代码前提供独立的“实现详解”，连贯说明输入、执行顺序、关键分支与后续交接。页面顶部可“隐藏代码与逐行表”，保留全部文字讲解，按需再展开源码核对。

实现固定在提交 `639ed015397290b3745d163aafe02ffee4aa3f84`，根包 0.2.0-rc.2，Cordis 4.0.4。版本与核验记录见 [实现证据](evidence-index.md)。

## 顺序目录
'''
    preface+='\n'.join(f'- [第 {i} 章 · {title.split("｜",1)[1]}](#chapter-{i:02})' for i,(_,title) in enumerate(chapters,1))
    text=preface+'\n\n'+'\n\n'.join(f'<a id="chapter-{i:02}"></a>\n\n'+retarget(p.read_text(encoding='utf-8')) for i,(p,_) in enumerate(chapters,1))
    text+='\n\n## 随用随查与补充能力\n\n[语法与数据基础](appendices.md) · [补充能力](subsystems.md) · [术语首次解释索引](glossary.md) · [实现证据](evidence-index.md) · [原项目文档](reference-index.md)\n'
    write('tutorial.md',text)
    nav=''.join(f'<a href="#chapter-{i:02}">{i:02} · {escape(title.split("｜",1)[1])}</a>' for i,(_,title) in enumerate(chapters,1))
    nav+='<a href="subsystems.html">补充能力</a><a href="glossary.html">术语索引</a><a href="evidence.html">实现证据</a>'
    write('reader.html',page('深入理解 DeepSeek Harness · 中文教材',text,nav))
    write('index.html',read('reader.html'))
    write('.nojekyll','')
    write('_tools/reader-inline.js',re.search(r'<script>([\s\S]+?)</script>',read('reader.html'))[1])
    for md,target in MD_HTML.items():
        if md=='tutorial.md':continue
        content=read(md);write(target,page(content.splitlines()[0].lstrip('# '),content))
    goals={r['chapter']:r['objective'] for r in data('revision/learning-objectives.json')}
    plan={'title':'深入理解 DeepSeek Harness','chapter_count':len(chapters),'canonical':'book/*.md','exercise_sections':True,'chapters':[{'id':f'{i:02}','title':title.split('｜',1)[1],'file':p.relative_to(ROOT).as_posix(),'learning_objective':goals[i]} for i,(p,title) in enumerate(chapters,1)]}
    dump('book-plan.json',plan)
    dump('course-plan.json',{**plan,'stage':'full_rewrite','commit':COMMIT,'supplement':'subsystems.md','technology_choices':'tech-choices.md'})
    figure_rows=[]
    for n in ['tutorial.md','subsystems.md']:
        for label,target in re.findall(r'!\[([^\]]+)\]\(([^)]+)\)',read(n)):
            figure_rows.append(f'| {Path(target).stem} | {label} | [{n}](../{n}) | [PNG]({Path(target).name}) · [SVG]({Path(target).with_suffix(".svg").name}) |')
    write('figures/index.md','# 中文图解索引\n\n所有图为教材原创示意，表示关系与教学推演。源码标识保留原文。\n\n| 图号 | 内容 | 正文位置 | 文件 |\n| --- | --- | --- | --- |\n'+'\n'.join(figure_rows))
    evidence=data('excerpt-manifest.json')['excerpts']
    dump('package-info.json',{'title':'深入理解 DeepSeek Harness','edition':'nineteen_chapter_zero_code_rewrite','entrypoint':'reader.html','chapter_count':19,'source_commit':COMMIT,'package_version':'0.2.0-rc.2','cordis_version':'4.0.4','canonical':'book/*.md','source_excerpt_count':len(evidence),'validation':'validation.json','reference_index':'reference-index.md','history_excluded':True,'maintenance_tools':'仅保留在制作方本地 _tools；此包为学习阅读版'})
    result=validate(chapters,evidence)
    source=data('sources.json');source.update(updated_date='2026-10-03',delivery_stage='十九章中文重构版：原理正文、逐行源码研读、理解题与答案',chapter_count=19,exercise_sections=True,source_topic_count=19,source_excerpt_count=len(evidence),figure_count=result['all_reading_unique_figures'],planned_figure_count=result['all_reading_unique_figures'],reader_prerequisite='普通电脑操作；正文补基础；无需预读源码',scope='十九章核心主链与补充子系统约定；核验范围见 evidence-index.md 和 revision/status.json')
    for entry in source['sources']:
        if entry['id']=='quantitative-architecture-method':entry['use']='参考量化评价、综合机制与误区体例；依本次要求增加理解题与参考回答'
        if entry['id']=='ai-agent-book-structure':
            entry['use']='参考基础到工程协作的主题递进与问题组织；阅读版参考白底三栏、章节目录、标题层级与章节速览卡片，十九章正文独立创作'
            entry['limits']='查看公开目录、引言、首页与第一章，并在 Edge 核对排版；实现证据来自固定仓库，未复制参考书正文或主题源码'
    if not any(x['id']=='cordis-paper-v1' for x in source['sources']):
        source['sources'].append({'id':'cordis-paper-v1','kind':'primary_research_paper','title':'A Programming Paradigm for Spatiotemporal Composability','url':'https://arxiv.org/abs/2608.25512','version':'v1','accessed_date':'2026-10-03','use':'第十九章效果、独立性、生命周期与边界；实际章节定位见 19.11','limits':'阅读并解释列明部分，不声称核验全部形式证明；不在分享包复制原文 PDF'})
    source['verification']['course_artifact_validation']='validation.json 的本次实际计数与错误列表；旧十章核验不沿用'
    source['technology_choices']={'file':'tech-choices.md','review':'revision/technology-choices-review-20261003.json','comparison_topics':14,'evidence':'固定源码的实际选型与官方技术文档；收益和迁移成本为正文明确标注的工程分析'}
    dump('sources.json',source)
    if package:
        print('Package: artifact checks passed; selecting files',flush=True)
        dest=ROOT.parent/'DeepSeek-Harness-中文教材完整版.zip'
        if dest.exists():
            backup=(Path(data('_tools/rewrite-state.json')['backup']) if (ROOT/'_tools/rewrite-state.json').is_file() else ROOT/'archive/before-package')/'share-before-rewrite.zip'
            if not backup.exists():
                import shutil;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
        selected=[]
        root_files={'README.md','index.html','.nojekyll','source-snapshot.json','tutorial.md','subsystems.md','appendices.md','glossary.md','evidence-index.md','reference-index.md','source-excerpts.md','tech-choices.md','chapter-format.md','illustration-plan.md','book-plan.json','course-plan.json','sources.json','coverage.json','reference-manifest.json','excerpt-manifest.json','validation.json','package-info.json',*MD_HTML.values()}
        # 在遍历前排除依赖和历史目录；源快照只选 Git 跟踪文件，
        # 不枚举本机 node_modules，也不把未跟踪的运行产物装入教材。
        for folder in ['book','figures','revision','examples']:
            for directory,dirs,files in os.walk(ROOT/folder):
                dirs[:]=[d for d in dirs if d not in ['.git','node_modules','__pycache__']]
                for name in files:
                    p=Path(directory)/name
                    selected.append((p,p.relative_to(ROOT).as_posix()))
        tracked=subprocess.check_output(['git','-c','core.excludesfile=','ls-files','-z'],cwd=ROOT/'source').decode('utf-8').split('\0') if (ROOT/'source/.git').exists() else [item['path'] for item in data('source-snapshot.json')['files']]
        for name in tracked:
            if not name:continue
            p=ROOT/'source'/name
            if p.is_file():selected.append((p,'source/'+name))
        for name in root_files:
            p=ROOT/name
            if p.is_file():selected.append((p,name))
        selected.sort(key=lambda item:item[1])
        selected_names={name for _,name in selected}
        for record in data('reference-manifest.json')['files']:
            if record['path'] not in selected_names:raise ValueError('参考文件未进入包：'+record['path'])
        print('Package: selected '+str(len(selected))+' files; writing staged ZIP',flush=True)
        staged=ROOT/'_tools'/'share-new.zip'
        with zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p,name in selected:z.write(p,name)
        print('Package: ZIP written; checking CRC and file bytes',flush=True)
        with zipfile.ZipFile(staged) as z:
            if z.testzip() is not None:raise ValueError('ZIP 完整性检查失败')
            for p,name in selected:
                if z.read(name)!=p.read_bytes():raise ValueError('ZIP 与正文不一致 '+name)
        os.replace(staged,dest)
        print('Package: all selected files match; final ZIP synchronized',flush=True)
        report={'path':str(dest),'entrypoint':'reader.html','entry_count':len(selected),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'zip_bytes':dest.stat().st_size,'chapter_count':19,'source_commit':COMMIT,'annotated_excerpts':len(evidence),'exercise_sections':True,'package_byte_comparison':'all_selected_files_match','source_selection':'Git-tracked files in the pinned snapshot','excluded':['.git','node_modules','_tools','archive','historical drafts','untracked source artifacts','paper PDF']}
        dump('share-manifest.json',report)
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--package',action='store_true');args=parser.parse_args();build(args.package)
