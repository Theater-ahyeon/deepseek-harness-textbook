"""Update the built sharing archive to exactly match the final reviewed artifacts."""
import hashlib
import json
import os
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'DeepSeek-Harness-中文教材完整版.zip'
TEMP=DEST.with_suffix('.reviewed.tmp')
prefix='DeepSeek-Harness-中文教材/'
review={'browser':'Microsoft Edge','delivery':'file URL; offline HTML','chapter_navigation_count':10,'inline_svg_count':40,'desktop_viewport_width':1912,'mobile_viewport_width':390,'mobile_document_scroll_width':375,'mobile_diagram_scroll_width':760,'broken_images':0,'notes':'Desktop preface and mobile first diagram visually inspected; not every browser tested'}
validation=json.loads((ROOT/'validation.json').read_text(encoding='utf-8'))
validation['browser_review']=review
(ROOT/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
changed=0
with zipfile.ZipFile(DEST) as old,zipfile.ZipFile(TEMP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as new:
    for info in old.infolist():
        data=old.read(info.filename)
        relative=info.filename.removeprefix(prefix)
        # The unmodified source was already hash-checked; only student artifacts changed.
        if not relative.startswith('source/'):
            current=(ROOT/relative).read_bytes()
            if current!=data:
                data=current
                changed+=1
        new.writestr(info,data)
with zipfile.ZipFile(TEMP) as z:
    if z.testzip():raise SystemExit('ZIP integrity check failed')
    names=z.namelist()
    if len(names)!=len(set(names)):raise SystemExit('Duplicate ZIP entries')
    for name in ['tutorial.md','reader.html','validation.json','source-excerpts.md','excerpt-manifest.json']:
        if z.read(prefix+name)!=(ROOT/name).read_bytes():raise SystemExit('Archive differs: '+name)
os.replace(TEMP,DEST)
report=json.loads((ROOT/'share-manifest.json').read_text(encoding='utf-8'))
report.update({'zip_bytes':DEST.stat().st_size,'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'final_artifact_sync':'passed','updated_entries':changed})
(ROOT/'share-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
