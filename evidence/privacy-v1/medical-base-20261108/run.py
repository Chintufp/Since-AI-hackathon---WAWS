"""Run the unchanged synthetic medical demo through the new local Base bundle."""
import argparse,gc,hashlib,json,os,socket,sys,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
os.environ['HF_HUB_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
import torch
from mask.ml.privacy_v1.bundle import load_model
from mask.ml.privacy_v1.engine import Protector
from mask.web.server import ModelService


def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 args=p.parse_args();torch.set_num_threads(4)
 source=ROOT/'demo/personal-health-message.txt';text=source.read_text()
 cases=[('browser_first_line',text.split('\n')[0].strip()),('backend_message_only',None),('specific_intended_task','Explain what cetirizine is used for and how it relates to the runny nose and sneezing recorded at the most recent visit.')]
 started=time.perf_counter()
 with patch.object(socket,'socket',side_effect=AssertionError('Network disabled for this local inference check')):
  model=load_model(args.model,'cpu');loaded=time.perf_counter()-started;engine=Protector(model);app=ModelService(engine)
  print(json.dumps({'phase':'model_loaded','seconds':round(loaded,2),'model_id':model.model_id,'section_mode':engine.section_mode}),flush=True)
  outputs=[]
  for name,task in cases:
   start=time.perf_counter();preview=app.preview(text,task,client=name);elapsed=time.perf_counter()-start
   effective_task=text if task is None else task
   result=engine.protect_text(text,effective_task).as_dict()
   assert preview['protected_text']==result['protected_text']
   output=preview['protected_text'];checks={}
   if output is not None:
    checks={
     'name_removed':'Alex Bennett' not in output,
     'email_removed':'alex.bennett@example.com' not in output,
     'patient_number_removed':'PT-482071' not in output,
     'dob_removed':'14 June 1995' not in output,
     'medicine_retained':'Medication prescribed: Cetirizine.' in output,
     'symptoms_retained':'Reason: Runny nose and frequent sneezing.' in output,
     'itching_reason_removed':'Persistent itching around the anus.' not in output,
     'itchy_quote_removed':'My ass is really itchy, especially at night.' not in output,
     'wrist_details_removed':all(s not in output for s in ('Left wrist pain','Wrist sprain')),
    }
   row={'condition':name,'task':task,'effective_task':effective_task,'preview_seconds':elapsed,'checks':checks,'result':result,'application_status':preview['status'],'application_preview_matches_engine':True}
   outputs.append(row)
   print(json.dumps({'condition':name,'seconds':round(elapsed,2),'checks':checks,'status':preview['status'],'protected_text':output},ensure_ascii=False),flush=True)
 report={'source_file':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(text.encode()).hexdigest(),'source_words':len(text.split()),'model_path':str(args.model),'model_manifest_sha256':hashlib.sha256((args.model/'manifest.json').read_bytes()).hexdigest(),'device':'cpu','threads':4,'model_load_seconds':loaded,'source':text,'outputs':outputs,'limitations':['Synthetic training-demo diagnostic, not held-out validation.','No live browser or provider API was exercised; browser task extraction is reproduced through the matching Python pipeline.','Specific task changes only the task field; source medical record is unchanged.']}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 with args.output.open('x') as f:json.dump(report,f,indent=2,ensure_ascii=False);f.write('\n')
 print('Saved '+str(args.output),flush=True)

if __name__=='__main__':main()
