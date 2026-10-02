"""Package the authorized local textbook and unmodified upstream references."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'DeepSeek-Harness-中文教材完整版.zip'
validation=json.loads((ROOT/'validation.json').read_text(encoding='utf-8'))
if validation['errors']:raise SystemExit('Validation failed; package not written')
validation['browser_review']={'browser':'Microsoft Edge','delivery':'file URL; offline HTML','chapter_navigation_count':10,'inline_svg_count':40,'desktop_viewport_width':1912,'mobile_viewport_width':390,'mobile_document_scroll_width':375,'mobile_diagram_scroll_width':760,'broken_images':0,'notes':'Desktop preface and mobile first-diagram screenshots inspected; not every browser tested'}
(ROOT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
selected=[]
for name in ['README.md','tutorial.md','reader.html','appendices.md','chapter-format.md','illustration-plan.md','reference-index.md','source-excerpts.md','sources.json','book-plan.json','course-plan.json','reference-manifest.json','excerpt-manifest.json','coverage.json','validation.json']:
    selected.append(ROOT/name)
for folder in ['book','chapters','figures','source']:
    selected.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts)
selected=sorted(set(selected))
total=sum(p.stat().st_size for p in selected)
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in selected:archive.write(p,'DeepSeek-Harness-中文教材/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(DEST) as archive:
    bad=archive.testzip()
    if bad:raise SystemExit('ZIP integrity failure: '+bad)
    if len(archive.infolist())!=len(selected):raise SystemExit('ZIP entry count differs')
    required=['reader.html','tutorial.md','source/LICENSE','book/01.md','book/10.md','figures/F22A.png','source-excerpts.md']
    for name in required:
        if 'DeepSeek-Harness-中文教材/'+name not in archive.namelist():raise SystemExit('ZIP required artifact missing: '+name)
    if any('/.git/' in name for name in archive.namelist()):raise SystemExit('Git metadata accidentally included')
report={'path':str(DEST),'entry_count':len(selected),'uncompressed_bytes':total,'zip_bytes':DEST.stat().st_size,'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'integrity_check':'passed','source_commit':validation['source_commit'],'entrypoint':'DeepSeek-Harness-中文教材/reader.html','chapter_count':10,'figure_count':40,'source_excerpts':60,'subsystems_explained':63,'exercise_sections':False,'includes_original_source':True,'excludes':['.git','course authoring tools','historical outlines']}
(ROOT/'share-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
