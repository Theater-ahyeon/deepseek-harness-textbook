"""Validate course artifacts and source citations; do not execute DSH tests."""
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
from PIL import Image

root = Path(__file__).resolve().parents[1]
plan = json.loads((root/'course-plan.json').read_text(encoding='utf-8'))
errors = []
ids = [c['id'] for c in plan['chapters']]
book_plan = json.loads((root/'book-plan.json').read_text(encoding='utf-8'))
figure_data = json.loads((root/'figures/figure-data.json').read_text(encoding='utf-8'))
evidence_text = (root/'source-excerpts.md').read_text(encoding='utf-8')
if ids != [f'{i:02}' for i in range(1,19)]:
    errors.append('Unexpected chapter IDs')
files = [root/p for p in ['README.md','tutorial.md','appendices.md','chapter-format.md','illustration-plan.md','reference-index.md','figures/index.md']]
files += [root/'chapters'/f'{cid}.md' for cid in ids]
files += [root/'book'/f'{c["id"]}.md' for c in book_plan['chapters']]
files += [root/'source-excerpts.md']
local_links=0
book = (root/'tutorial.md').read_text(encoding='utf-8')
for f in files:
    content=f.read_text(encoding='utf-8')
    if re.search(r'\]\((?:[A-Za-z]:[/\\]|file:)', content):
        errors.append(f'Machine-specific link in {f.relative_to(root)}')
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if re.match(r'https?://',target):continue
        local_links+=1
        path,_,fragment=unquote(target).partition('#')
        resolved=(f.parent/path).resolve() if path else f
        if not resolved.exists():errors.append(f'Missing local target: {f.relative_to(root)}: {target}')
        if fragment.startswith(('chapter-','topic-','evidence-','book-evidence-')) and resolved.is_file():
            if f'id="{fragment}"' not in resolved.read_text(encoding='utf-8'):
                errors.append(f'Missing chapter anchor: {target}')
    if f.parent.name=='chapters':
        cid=f.stem
        c=plan['chapters'][int(cid)-1]
        if not content.startswith(f'# {cid}｜{c["title"]}'):errors.append(f'Chapter title differs from plan: {cid}')
        headings=re.findall(r'^## '+cid+r'\.(\d+) ',content,re.M)
        if headings != [str(i) for i in range(9)]:errors.append(f'Incomplete chapter section sequence: {cid}')
        if re.search(r'^#{1,6} .*?(练习|作业|答题|评分)',content,re.M):errors.append(f'Exercise section in chapter {cid}')
        adjusted=re.sub(r'^(#{1,5}) ',lambda m:'#'+m.group(1)+' ',content,flags=re.M).replace('](../','](')
        if f'id="topic-{cid}"' not in book:errors.append(f'Missing explanatory topic: {cid}')
    if f.parent.name=='book':
        cid=f.stem
        c=book_plan['chapters'][int(cid)-1]
        if not content.startswith(f'# 第 {int(cid)} 章｜{c["title"]}'):errors.append(f'Book chapter title differs: {cid}')
        if re.search(r'^#{1,6} .*?(练习|作业|答题|评分)',content,re.M):errors.append(f'Exercise section in book chapter {cid}')
        adjusted=re.sub(r'^(#{1,5}) ',lambda m:'#'+m.group(1)+' ',content,flags=re.M).replace('](../','](')
        if adjusted not in book:errors.append(f'Combined book differs from book chapter {cid}')

figure_text=(root/'illustration-plan.md').read_text(encoding='utf-8')
rows=re.findall(r'^\| (F\d{2}[AB]) \|',figure_text,re.M)
expected={x['id'] for x in figure_data}
if set(rows)!=expected or len(rows)!=40:errors.append('Figure IDs do not match completed book')
for fid in sorted(expected):
    try:
        tree=ET.parse(root/'figures'/f'{fid}.svg')
        if tree.getroot().get('viewBox')!='0 0 1120 760':errors.append(f'Unexpected SVG dimensions: {fid}')
        with Image.open(root/'figures'/f'{fid}.png') as img:
            if img.size!=(1120,760):errors.append(f'Unexpected PNG dimensions: {fid}')
            img.verify()
    except Exception as exc:errors.append(f'Figure parse failed {fid}: {exc}')
    if len(re.findall(r'\]\(figures/'+fid+r'\.png\)',book))!=1:
        errors.append(f'Figure absent or duplicated in book: {fid}')

manifest=json.loads((root/'reference-manifest.json').read_text(encoding='utf-8'))
for entry in manifest['files']:
    f=root/entry['path']
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=entry['sha256']:
        errors.append(f'Reference hash mismatch: {entry["path"]}')
excerpts=json.loads((root/'excerpt-manifest.json').read_text(encoding='utf-8'))
if len(excerpts['excerpts'])!=60:errors.append('Expected 60 verified excerpts')
for entry in excerpts['excerpts']:
    lines=(root/entry['file']).read_text(encoding='utf-8').splitlines()
    quote='\n'.join(lines[entry['start']-1:entry['end']])
    if hashlib.sha256(quote.encode()).hexdigest()!=entry['excerpt_sha256']:
        errors.append(f'Excerpt hash mismatch: {entry["file"]}:{entry["start"]}')
    if f'```ts\n{quote}\n```' not in evidence_text:
        errors.append(f'Excerpt missing or altered in appendix: {entry["file"]}')
    if entry.get('chapter'):
        chapter=(root/'chapters'/f'{entry["chapter"]}.md').read_text(encoding='utf-8')
        if f'```ts\n{quote}\n```' not in chapter:errors.append(f'Core-topic excerpt altered: {entry["chapter"]}')

class ReaderParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.links=[]
        self.svg_count=0
        self.forbidden=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag=='svg':self.svg_count+=1
        if tag=='script' or (tag in ('img','link','iframe') and re.match(r'https?://',a.get('src',a.get('href','')))):
            self.forbidden.append(tag)

parser=ReaderParser()
parser.feed((root/'reader.html').read_text(encoding='utf-8'))
duplicate=[i for i,n in Counter(parser.ids).items() if n>1]
if duplicate:errors.append('Duplicate IDs in reader: '+', '.join(duplicate))
if parser.svg_count!=40:errors.append('Reader does not embed all 40 diagrams')
if parser.forbidden:errors.append('Reader contains scripts or remote dependencies')
for link in parser.links:
    if re.match(r'https?://',link):continue
    path,_,fragment=unquote(link).partition('#')
    if path and not (root/path).exists():errors.append('Reader link missing: '+link)
    if not path and fragment and fragment not in parser.ids:errors.append('Reader anchor missing: '+link)

head=subprocess.run(['git','rev-parse','HEAD'],cwd=root/'source',capture_output=True,text=True,check=True).stdout.strip()
if head!=plan['commit'] or head!=excerpts['commit'] or head!=manifest['commit']:
    errors.append('Source commit differs between artifacts')
diff=subprocess.run(['git','diff','--name-only','HEAD'],cwd=root/'source',capture_output=True,text=True,check=True).stdout.strip()
if diff:errors.append('Tracked source files changed: '+diff)
result={
    'edition':'self_contained_ten_chapter_edition','chapter_count':10,'source_topic_count':len(ids),
    'subsystems_explained':len(json.loads((root/'coverage.json').read_text(encoding='utf-8'))['subsystems']),
    'exercise_sections':False,'source_reading_required':False,'figure_count':40,'figure_formats':['SVG','PNG'],
    'source_excerpts_checked':len(excerpts['excerpts']),'markdown_files_checked':len(files),
    'local_links_checked':local_links,'reader_inline_svg_count':parser.svg_count,
    'reader_local_links_checked':len([x for x in parser.links if not re.match(r'https?://',x)]),
    'reader_remote_runtime_dependencies':False,'reference_hashes_checked':len(manifest['files']),
    'source_commit':head,'tracked_source_changes':bool(diff),'errors':errors,
    'source_review':'static','upstream_tests_run':False,'project_runtime_started':False,
    'visual_review':'Representative diagrams inspected; not every browser or upstream feature tested',
}
(root/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(1 if errors else 0)
