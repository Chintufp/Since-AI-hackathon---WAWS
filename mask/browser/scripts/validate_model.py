"""Generate actual Python references and compare optimized final edits, never targets."""
import copy
import json
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[3]
BROWSER = ROOT / 'mask/browser'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BROWSER / '.tools/python'))
import torch
import onnxruntime as ort
from mask.ml.privacy_v1.bundle import load_model
from mask.ml.privacy_v1.engine import Protector

torch.set_num_threads(4)
reference = load_model(BROWSER / '.cache/reference/deberta-v3-base')
current = json.loads((BROWSER / 'public/models/current.json').read_text())
manifest_path = (BROWSER / 'public/models' / current['manifest']).resolve()
manifest = json.loads(manifest_path.read_text())
options=ort.SessionOptions()
options.intra_op_num_threads=4
session=ort.InferenceSession(str(manifest_path.parent/'model.onnx'),sess_options=options,providers=['CPUExecutionProvider'])

class Network:
    backbone=reference.net.backbone
    def __call__(self, batch, mode):
        out=session.run(None,{x.name:batch[x.name].cpu().numpy() for x in session.get_inputs()})
        return torch.from_numpy(out[0]) if mode=='tag' else tuple(torch.from_numpy(x) for x in out[1:])

optimized=copy.copy(reference)
optimized.net=Network()
records=[json.loads(line) for line in (ROOT/'mask/ml/privacy_v1/data/training-2026-11-07/dev.jsonl').read_text().splitlines()]
for source in ['gallery.outputs.json','fresh.outputs.json']:
    records.extend(json.loads((ROOT/'evidence/privacy-v1/training-2026-11-07/measurements/deberta-v3-base-inspect'/source).read_text()))
records.extend({'id':f'unicode-{i}', 'task':'Summarise this message.', 'text':text} for i,text in enumerate([
    '😀 My name is Émilie Dupont; email: emilie@example.invalid. My salary is 3500 euros.',
    'Name: Jose\u0301 Martin\nEmail: jose@example.invalid\nMy partner has asthma.',
    'Already [PERSON_1]. Name: Jane Smith. Name: Jane Smith. Email: jane@example.invalid.',
    'Name: Anne O’Connor; phone: +358 40 123 4567. My blood pressure is 120/80.',
]))
def stable(result):
    return {k:result[k] for k in ['status','protected_text','protected_task','review_reasons','retained_sensitive','pending_reviews','coverage']}

cases=[]; differences=[]
started=time.monotonic()
for i,r in enumerate(records):
    task=r.get('task') or r['text'].split('\n')[0]
    a=Protector(reference).protect_text(r['text'],task).as_dict()
    b=Protector(optimized).protect_text(r['text'],task).as_dict()
    if stable(a)!=stable(b):
        differences.append({'id':r.get('id',str(i)),'reference':stable(a),'optimized':stable(b)})
    cases.append({'id':r.get('id',str(i)),'text':r['text'],'task':task,'expected':b,'reference':a})
    if i%10==0: print(f'Compared {i+1}/{len(records)} cases',flush=True)
out=BROWSER/'.cache/validation';out.mkdir(parents=True,exist_ok=True)
(out/'cases.json').write_text(json.dumps(cases,ensure_ascii=False))
(out/'quantization-differences.json').write_text(json.dumps(differences,indent=2,ensure_ascii=False))
# Full tokenizer contract: singles, pairs, and overflowing windows.
tokenizer=[]
texts=list(dict.fromkeys([r['text'] for r in records]+['hello ' * 600, '  A\tB\nC\r\nD  ', 'A\u00a0B\u202fC \ufb01 😀']))
for text in texts:
    for windowed in [False,True]:
        kwargs={'max_length':512,'stride':64,'truncation':True,'return_overflowing_tokens':True,'padding':True} if windowed else {}
        enc=dict(reference.tokenizer(text,return_offsets_mapping=True,**kwargs));enc.pop('overflow_to_sample_mapping',None)
        if not windowed:enc={k:[v] for k,v in enc.items()}
        windows=[{k:v[i] for k,v in enc.items()} for i in range(len(enc['input_ids']))]
        tokenizer.append({'text':text,'pair':None,'windowed':windowed,'expected':{'windows':windows}})
for r in records:
    text=r['text']; pair=' [unused0] '+text[:20]+' [unused1] '+text[20:]
    task=r.get('task','Summarise.')+'\n\nType: PERSON'
    enc=dict(reference.tokenizer(task,pair,return_offsets_mapping=True))
    tokenizer.append({'text':task,'pair':pair,'windowed':False,'expected':{'windows':[enc]}})
(out/'tokenizer-cases.json').write_text(json.dumps(tokenizer,ensure_ascii=False))
report={'cases':len(cases),'final_result_differences':len(differences),'seconds':time.monotonic()-started,'model':manifest['id']}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
