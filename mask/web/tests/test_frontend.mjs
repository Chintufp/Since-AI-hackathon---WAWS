import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { JSDOM } from 'jsdom';
const html=readFileSync(new URL('../static/index.html',import.meta.url),'utf8');
const script=readFileSync(new URL('../static/app.js',import.meta.url),'utf8');
const examples=JSON.parse(readFileSync(new URL('../../../demo/web-examples.json',import.meta.url),'utf8')).examples;
const flush=()=>new Promise(resolve=>setTimeout(resolve,20));
const result={status:'needs_review',coverage:{complete:true},protected_text:'Hello [PERSON_1]'};
function setup(preview=async()=>({ok:true,json:async()=>result}),motion=false){
  const dom=new JSDOM(html,{url:'http://127.0.0.1:8788',runScripts:'outside-only'}), w=dom.window, calls=[];
  w.matchMedia=()=>({matches:!motion});
  w.fetch=async(path,options)=>{calls.push({path,options}); return path==='/api/preview'?preview():{ok:true,json:async()=>({})};};
  w.eval(script); const $=id=>w.document.getElementById(id);
  const type=value=>{$('message').value=value;$('message').dispatchEvent(new w.Event('input'));};
  return {w,$,type,calls,close:()=>w.close()};
}
test('exactly one visible box and two controls; no auto filtering or provider calls',async()=>{
 const ui=setup();try{
 assert.equal(ui.w.document.querySelectorAll('button').length,2);
 assert.equal(ui.w.document.querySelectorAll('h1,h2,header,footer,input').length,0);
 assert.equal(ui.$('output').hidden,true);ui.type('Hello Emma');await flush();
 assert.equal(ui.calls.filter(x=>x.path==='/api/preview').length,0);
 ui.$('filter').click();await flush();assert.equal(ui.$('message').hidden,true);
 assert.equal(ui.$('output').textContent,result.protected_text);
 assert.equal(ui.calls.some(x=>x.path==='/api/send'),false);
 }finally{ui.close();}
});
test('example link alternates the two supplied complete messages',()=>{
 const ui=setup();try{
 ui.$('example').click();assert.equal(ui.$('message').value,examples[0].text.trimEnd().replace('below?\n\nPATIENT','below?\nPATIENT'));
 ui.$('example').click();assert.equal(ui.$('message').value,examples[1].text.trimEnd());
 ui.$('example').click();assert.match(ui.$('message').value,/Name: Alex Bennett/);
 assert.equal(ui.calls.filter(x=>x.path==='/api/preview').length,0);
 }finally{ui.close();}
});
test('full message is scanned; opening request supplies context',async()=>{
 const ui=setup();try{ui.$('example').click();ui.$('filter').click();await flush();
 const body=JSON.parse(ui.calls.find(x=>x.path==='/api/preview').options.body);
 assert.match(body.text,/wrist pain/);assert.equal(body.task,examples[0].intended_use);
 }finally{ui.close();}
});
test('example change discards obsolete inference',async()=>{
 let resolve;const ui=setup(()=>new Promise(done=>resolve=done));try{
 ui.type('First');ui.$('filter').click();ui.$('example').click();
 resolve({ok:true,json:async()=>result});await flush();
 assert.equal(ui.$('output').hidden,true);assert.match(ui.$('message').value,/Alex Bennett/);
 }finally{ui.close();}
});
test('failed coverage preserves source and exposes retry only in the existing button',async()=>{
 const ui=setup(async()=>({ok:true,json:async()=>({...result,coverage:{complete:false}})}));try{
 ui.type('Original');ui.$('filter').click();await flush();assert.equal(ui.$('message').value,'Original');
 assert.match(ui.$('filter').textContent,/try again/);assert.equal(ui.$('output').hidden,true);
 }finally{ui.close();}
});
test('real edit ranges animate safely, including Unicode and DROP, without HTML execution',async()=>{
 const data={...result,protected_text:'😀 [PERSON_1].',protected_view:{message:[{text:'😀 '},{text:'[PERSON_1]',start:2,end:6,action:'ALIAS'},{text:'.'},{text:'',start:7,end:14,action:'DROP'}]}};
 const ui=setup(async()=>({ok:true,json:async()=>data}),true);try{
 ui.type('😀 Emma. <img>');ui.$('filter').click();await flush();
 assert.ok(ui.$('output').querySelector('.dust'));assert.equal(ui.$('output').querySelector('img'),null);
 await new Promise(resolve=>setTimeout(resolve,850));assert.equal(ui.$('output').textContent,data.protected_text);
 assert.equal(ui.$('message').value,data.protected_text);assert.equal(ui.$('output').querySelector('.dust'),null);
 }finally{ui.close();}
});
