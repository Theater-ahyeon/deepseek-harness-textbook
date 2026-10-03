/** 调用固定快照的真实函数；只替代 Session/Projection 服务接缝，不启动 Host。 */
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { buildWindow } from '../source/packages/fs/tool-fs/src/read-render.ts'
import { ReactLoopInbox, inboxProjectionDefinition } from '../source/packages/core/agent-loop/src/inbox.ts'
import { createUserMessage } from '../source/packages/llm/llm/src/index.ts'

const cases: { id: string; observation: object }[] = []
const root = fileURLToPath(new URL('../', import.meta.url))
const caps = { offset: 2, limit: 2, maxLineLength: 100, maxBytes: 1000 }
const window = await buildWindow(['one\r\n', 'two\r', '\nthree\nfour'], caps, 'fixture.txt')
assert.deepEqual(window.lines, [{number:2,text:'two'},{number:3,text:'three'}])
assert.equal(window.totalLines,4)
assert.equal(window.truncatedByBytes,false)
cases.push({id:'E01-window-and-chunk-boundary',observation:window})

let scannedChunks = 0
async function* chunks() { for (const text of ['alpha\nbeta\n','gamma\ndelta']) { scannedChunks++; yield text } }
const bounded = await buildWindow(chunks(), {...caps,offset:1,limit:10,maxBytes:5}, 'bytes.txt')
assert.deepEqual(bounded.lines,[{number:1,text:'alpha'}])
assert.equal(bounded.truncatedByBytes,true)
assert.equal(bounded.totalLines,4)
assert.equal(scannedChunks,2)
cases.push({id:'E02-byte-cap-keeps-scanning',observation:{...bounded,scannedChunks}})

const unicode = await buildWindow(['中文\na'], {...caps,offset:1,limit:10,maxBytes:4}, 'unicode.txt')
assert.deepEqual(unicode.lines,[])
assert.equal(unicode.truncatedByBytes,true)
assert.equal(unicode.totalLines,2)
cases.push({id:'E03-utf8-byte-cap',observation:unicode})

const empty = await buildWindow([''], {...caps,offset:1}, 'empty.txt')
assert.deepEqual(empty,{lines:[],totalLines:0,truncatedByBytes:false})
await assert.rejects(buildWindow(['one\ntwo'],{...caps,offset:9},'eof.txt'),{code:'FS_NOT_FOUND'})
cases.push({id:'E04-empty-and-past-eof',observation:{empty,outOfRangeError:'FS_NOT_FOUND'}})

// 使用真实 Inbox 投影处理 append 事件；替身只负责将事件交给投影。
let state = inboxProjectionDefinition.init()
const events: object[] = []
const notices: { type: string; data: object }[] = []
const projections = { stateOf: () => state }
const session = {
  id: 'book-inbox',
  append(type: string,data: object) {
    const event = {type,data,seq:events.length+1}
    state=inboxProjectionDefinition.apply(state,event)
    events.push(event)
    return event
  },
}
const dispatch = { emit: (type: string,data: object) => notices.push({type,data}) }
const inbox = new ReactLoopInbox(projections,session,dispatch)
const message = (text: string) => createUserMessage({content:[{type:'text',text}],source:{kind:'user'}})
const turn1=message('第一个任务'),turn2=message('第二个任务'),step1=message('当前步骤补充一'),step2=message('当前步骤补充二')
inbox.append('next-turn',turn1);inbox.append('next-turn',turn2);inbox.append('next-step',step1);inbox.append('next-step',step2)
assert.deepEqual(inbox.claim('next-step',1).map(m=>m.id),[step1.id,step2.id])
assert.deepEqual(inbox.nextTurn.map(m=>m.id),[turn1.id,turn2.id])
assert.deepEqual(inbox.nextStep,[])
const first=inbox.claim('next-turn',2)
assert.deepEqual(first.map(m=>m.id),[turn1.id])
assert.deepEqual(inbox.nextTurn.map(m=>m.id),[turn2.id])
cases.push({id:'E05-inbox-boundary-selection',observation:{stepClaims:2,turnClaims:first.length,pendingTurns:inbox.nextTurn.length}})

const before=events.length
assert.throws(()=>inbox.append('next-step',turn2),/already pending/)
assert.equal(events.length,before)
assert.deepEqual(inbox.nextStep,[])
assert.deepEqual(inbox.nextTurn.map(m=>m.id),[turn2.id])
cases.push({id:'E06-inbox-rejects-duplicate-before-append',observation:{eventsBefore:before,eventsAfter:events.length,pendingTurns:inbox.nextTurn.length}})

const inputs=['source/packages/fs/tool-fs/src/read-render.ts','source/packages/core/agent-loop/src/inbox.ts']
const source=inputs.map(path=>({path,sha256:createHash('sha256').update(readFileSync(root+path)).digest('hex')}))
const result={sourceCommit:'639ed015397290b3745d163aafe02ffee4aa3f84',method:'actual source functions; simulated Session/Projection persistence seam; no Host or model calls',runtime:{node:process.version,executor:'tsx'},source,cases}
writeFileSync(root+'examples/source-experiment-results.json',JSON.stringify(result,null,2)+'\n')
console.log(JSON.stringify({experimentCases:cases.length,passed:cases.map(c=>c.id)}))
