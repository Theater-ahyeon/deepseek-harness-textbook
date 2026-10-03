from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
records=json.loads((root/'revision/terms.json').read_text(encoding='utf-8'))
for r in records:r['line']=(root/r['file']).read_text(encoding='utf-8').splitlines().index(r['explanation_paragraph'])+1
(root/'revision/terms.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=['# 术语解释与回查索引','本索引定位实际解释段落。章内定义与当时的例子一起阅读，索引不代替正文；基础词的进一步展开可能在后续章节。','| 术语 | 解释位置 |\n| --- | --- |']
for r in records:
    loc=f'[第 {r["explanation_chapter"]} 章](reader.html#chapter-{r["explanation_chapter"]:02})' if 'explanation_chapter' in r else '[补充能力](subsystems.html)'
    rows.append(f'| {r["term"]} | {loc}，{r["file"]} 第 {r["line"]} 行 |')
(root/'glossary.md').write_text('\n\n'.join(rows[:2])+'\n\n'+'\n'.join(rows[2:])+'\n',encoding='utf-8')
print('explanation locations synchronized')
