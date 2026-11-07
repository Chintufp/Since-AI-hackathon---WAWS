// Make an allowlisted static deployment. Never copy the checkout or .env files.
import {cp,mkdir,readFile,writeFile,rm,readdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const destination=path.join(root,'out/netlify');
await rm(destination,{recursive:true,force:true});await mkdir(destination,{recursive:true});
await cp(path.join(root,'dist'),destination,{recursive:true,filter:file=>!['models','qa','qa.html'].includes(path.basename(file))});
await mkdir(path.join(destination,'models'),{recursive:true});
const config=JSON.parse(await readFile(path.join(root,'public/app-config.json'),'utf8'));
config.modelPointer='/models/current.json';
config.relayURL=process.env.MASK_RELAY_URL||null;
const manifest=process.env.MASK_MODEL_MANIFEST;
if(!manifest?.startsWith('https://'))throw new Error('Set MASK_MODEL_MANIFEST to the verified HTTPS manifest URL.');
if(config.relayURL&&!config.relayURL.startsWith('https://'))throw new Error('Relay requires HTTPS.');
await writeFile(path.join(destination,'app-config.json'),JSON.stringify(config,null,2)+'\n');
await writeFile(path.join(destination,'models/current.json'),JSON.stringify({manifest},null,2)+'\n');
const env=await readFile(path.join(root,'.env.local'),'utf8').catch(()=> '');
const secret=env.split('\n').find(x=>x.startsWith('ANTHROPIC_API_KEY='))?.split('=').slice(1).join('=').trim().replace(/^['"]|['"]$/g,'');
async function audit(directory){
  for(const entry of await readdir(directory,{withFileTypes:true})){
    const file=path.join(directory,entry.name);
    if(entry.name.startsWith('.env'))throw new Error('Environment file in static output.');
    if(entry.isDirectory())await audit(file);
    else if(secret&&(await readFile(file)).includes(Buffer.from(secret)))throw new Error('Credential detected in deployment.');
  }
}
await audit(destination);
console.log('Deployment staged; no environment files or API key in static output.');
