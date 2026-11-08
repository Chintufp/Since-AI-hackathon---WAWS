"""Compare complete old/new Base pipelines on fixed dev, fresh and demo cases."""
import argparse,gc,hashlib,json,os,socket,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
os.environ['HF_HUB_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
import torch
from mask.ml.privacy_v1.bundle import load_model
from mask.ml.privacy_v1.engine import Protector
from mask.ml.privacy_v1 import section_evaluation as evaluation
from mask.ml.privacy_v1.annotation.tools import read
from mask.ml.privacy_v1.section_quick_checks import check_fresh
from mask.ml.privacy_v1.inspect_campaign import cells
from mask.ml.privacy_v1.tables import protect_table
from mask.ml.privacy_v1.data import digest
from mask.web.server import ModelService

PHASE=''
class ProgressProtector(Protector):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.checked=0
 def protect_text(self,*args,**kwargs):
  result=super().protect_text(*args,**kwargs);self.checked+=1
  if self.checked%10==0:print(json.dumps({'phase':PHASE,'records_completed':self.checked}),flush=True)
  return result
evaluation.Protector=ProgressProtector

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')

def main():
 global PHASE
 p=argparse.ArgumentParser();p.add_argument('--old',type=Path,required=True);p.add_argument('--new',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4)
 split=ROOT/'mask/ml/privacy_v1/data/section-split-20261108-v1'
 fresh_file=Path(__file__).with_name('fresh-inputs.json');fresh=json.loads(fresh_file.read_text())
 fixture_root=ROOT/'mask/ml/privacy_v1/data/training-2026-11-07/adapter-fixtures'
 fixtures=json.loads((fixture_root/'manifest.json').read_text())['fixtures']
 gallery=json.loads((ROOT/'demo/web-examples.json').read_text())['examples']
 run={'source_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'device':'cpu','threads':4,'torch':torch.__version__,'fresh_inputs_sha256':digest(fresh_file),'models':{},'files':{str(path.relative_to(ROOT)):digest(path) for path in [split/'dev.authored.jsonl',split/'supplemental-dev.authored.jsonl',fixture_root/'manifest.json']},'limitations':['Dev sets previously used for model selection; fresh diagnostic labels authored in this task, not an independent human audit.','Each complete pipeline uses its published default behavior; differences include both weights and versioned inference logic.','No live provider request, deployed-browser inference, threshold change or default-model update.']}
 with patch.object(socket,'socket',side_effect=AssertionError('Network disabled during inference')):
  for name,path in [('old',args.old),('new',args.new)]:
   target=args.output/name;target.mkdir();started=time.perf_counter();model=load_model(path,'cpu');load_seconds=time.perf_counter()-started
   run['models'][name]={'path':str(path),'manifest_sha256':digest(path/'manifest.json'),'model_id':model.model_id,'load_seconds':load_seconds,'section_mode':Protector(model).section_mode}
   print(json.dumps({'model':name,'phase':'loaded','seconds':round(load_seconds,2)}),flush=True)
   for label,file in [('original-dev','dev.authored.jsonl'),('supplemental-dev','supplemental-dev.authored.jsonl')]:
    PHASE=name+':'+label;report=evaluation.evaluate_rows(model,read(split/file));write(target/(label+'.json'),report)
    print(json.dumps({'phase':PHASE,'counts':report['counts'],'latency':report['latency_seconds']}),flush=True)
   output=[];counts={}
   for row in fresh:
    report=check_fresh(model,[row]);output.extend(report['outputs'])
    for key,val in report['counts'].items():counts[key]=counts.get(key,0)+val
    print(json.dumps({'phase':name+':fresh','id':row['id'],'counts':report['counts']}),flush=True)
   write(target/'fresh.json',{'evaluation_role':'fresh_diagnostics_frozen_before_inference','counts':counts,'outputs':output})
   engine=Protector(model);app=ModelService(engine);demo_outputs=[]
   for file in ['personal-health-message.txt','corporate-support-message.txt']:
    text=(ROOT/'demo'/file).read_text();task=text.split('\n')[0].strip();before=time.perf_counter();preview=app.preview(text,task,client=file)
    demo_outputs.append({'id':file,'text':text,'task':task,'preview_seconds':time.perf_counter()-before,'preview':preview})
   write(target/'video-demos.json',demo_outputs)
   outputs=[]
   for row in gallery:
    result=engine.protect_text(row['text'],row['intended_use'])
    outputs.append({'id':row['id'],'text':row['text'],'task':row['intended_use'],'expected':row['expected_protected_text'],'actual':result.protected_text,'exact_match':result.protected_text==row['expected_protected_text'],'result':result.as_dict()})
   write(target/'gallery.json',outputs)
   outputs=[]
   for fixture in fixtures:
    source=fixture_root/fixture['file'];assert digest(source)==fixture['sha256']
    dest=target/'tables'/('protected-'+source.name)
    row={'file':source.name,'task':fixture['intended_use'],'before':cells(source)}
    try:
     row['report']=protect_table(engine,source,dest,fixture['intended_use']);row['after']=cells(dest)
     expected=fixture.get('expected_cells',{})|fixture.get('unchanged_cells',{})
     if fixture.get('expected_file'):expected=cells(fixture_root/fixture['expected_file'])
     row['expected']=expected;row['mismatches']={c:{'expected':v,'actual':row['after'].get(c)} for c,v in expected.items() if row['after'].get(c)!=v}
     row['round_trip']=True
    except Exception as error:row['error']=type(error).__name__+': '+str(error)
    outputs.append(row)
    print(json.dumps({'phase':name+':table','file':row['file'],'mismatches':len(row.get('mismatches',{})),'error':row.get('error')}),flush=True)
   write(target/'adapters.json',outputs)
   write(target/'metadata.json',run['models'][name]);del app,engine,model;gc.collect()
 write(args.output/'run.json',run)
 print('COMPARISON COMPLETE '+str(args.output),flush=True)

if __name__=='__main__':main()
