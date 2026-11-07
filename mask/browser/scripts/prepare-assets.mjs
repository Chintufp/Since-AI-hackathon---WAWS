import { cp, mkdir, readFile, writeFile, access } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
for (const dir of ['public/runtime/pyodide', 'public/runtime/ort', 'public/policy']) await mkdir(path.join(root, dir), {recursive: true});
for (const name of ['pyodide.mjs', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']) {
  await cp(path.join(root, 'node_modules/pyodide', name), path.join(root, 'public/runtime/pyodide', name));
}
for (const name of ['ort-wasm-simd-threaded.mjs', 'ort-wasm-simd-threaded.wasm', 'ort-wasm-simd-threaded.jsep.mjs', 'ort-wasm-simd-threaded.jsep.wasm']) {
  await cp(path.join(root, 'node_modules/onnxruntime-web/dist', name), path.join(root, 'public/runtime/ort', name));
}
for (const name of ['favicon.svg', 'favicon.ico', 'logo.svg', 'logo-dark.svg', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png', 'site.webmanifest', 'styles.css']) {
  await cp(path.join(root, '../web/static', name), path.join(root, 'public', name));
}
await cp(path.join(root, '../public/fonts/InterVariable.woff2'), path.join(root, 'public/font.woff2'));
const examples = JSON.parse(await readFile(path.join(root, '../../demo/web-examples.json'), 'utf8'));
await writeFile(path.join(root, 'public/examples.json'), JSON.stringify(examples.examples.slice(0, 2).map(({id, text, title}) => ({id, text, title}))));
const python = process.env.MASK_BUILD_PYTHON || path.join(root, '../ml/privacy_v1/.venv/bin/python');
execFileSync(python, [path.join(root, 'scripts/prepare_policy.py')], {stdio: 'inherit'});
await access(path.join(root, 'public/tokenizer/mask_tokenizer_bg.wasm'));
await access(path.join(root, 'public/models/current.json'));
console.log('Prepared self-hosted runtimes, tokenizer, policy, font and synthetic inputs.');
