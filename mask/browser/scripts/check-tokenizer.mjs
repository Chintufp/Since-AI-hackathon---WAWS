import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import init,{BrowserTokenizer} from '../public/tokenizer/mask_tokenizer.js';
await init({module_or_path:await readFile(new URL('../public/tokenizer/mask_tokenizer_bg.wasm',import.meta.url))});
const current=JSON.parse(await readFile(new URL('../public/models/current.json',import.meta.url)));
const base=new URL(`../public/models/${current.manifest}`,import.meta.url);
const manifest=JSON.parse(await readFile(base));
const tokenizer=new BrowserTokenizer(await readFile(new URL('tokenizer.json',base),'utf8'),manifest.pad_id,512,64);
const cases=JSON.parse(await readFile(new URL('../.cache/validation/tokenizer-cases.json',import.meta.url)));
for(const [i,c] of cases.entries()) {
  const result=JSON.parse(tokenizer.encode(c.text,c.pair??undefined,c.windowed));
  assert.deepEqual(result,c.expected,`Tokenizer mismatch at case ${i}`);
}
console.log(`Exact Python/WASM token IDs, masks, pairs and Unicode offsets: ${cases.length}/${cases.length}`);
