"""Summarize the fixed comparison without selecting or changing model settings."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
P=ROOT/'results'
def read(path):return json.loads(path.read_text())
summary={'scope':{'per_model':{'frozen_dev_messages':130,'fresh_diagnostic_messages':12,'video_messages':2,'gallery_messages':6,'spreadsheet_fixtures':16},'fresh_independent_sources':8,'inference_network_disabled':True,'production_default_changed':False},'models':{},'paired_regressions':{},'browser':read(ROOT/'browser-compatibility.json')}
for name in ('old','new'):
 summary['models'][name]={}
 for split in ('original-dev','supplemental-dev'):
  r=read(P/name/(split+'.json'));summary['models'][name][split]={'counts':r['counts'],'latency_seconds':r['latency_seconds']}
 f=read(P/name/'fresh.json');byid={r['id']:r for r in f['outputs']};inputs={r['id']:r for r in read(ROOT/'fresh-inputs.json')}
 switch=[]
 for a,b in [('fresh-health-employer','fresh-health-clinician'),('fresh-boiler-engineer','fresh-boiler-budget'),('fresh-incident-engineering','fresh-incident-commercial')]:
  left,right=byid[a],byid[b];quote=inputs[a]['expected_removed'][0]
  switch.append({'drop_case':a,'keep_case':b,'correct':quote not in left['missed_expected_sections'] and quote in (right['result']['protected_text'] or '') and not any(r['identifier_misses'] or r['lost_expected_facts'] for r in [left,right])})
 summary['models'][name]['fresh']={'counts':f['counts'],'checked_fact_targets':sum(len(x['expected_preserved']) for x in inputs.values()),'app_supported':sum(x['real_app_supported'] for x in f['outputs']),'app_engine_equal':sum(x['real_app_protected_text']==x['result']['protected_text'] for x in f['outputs']),'correct_task_pairs':sum(x['correct'] for x in switch),'task_pairs':switch,'benign_control_unchanged':byid['fresh-benign-technical']['no_edit'],'unknown_reply_alias_preserved':all('[PERSON_999]' in x['locally_restored_reply'] for x in f['outputs'])}
 a=read(P/name/'adapters.json');summary['models'][name]['adapters']={'total':len(a),'round_trips':sum(x.get('round_trip',False) for x in a),'exact_matches':sum(not x.get('mismatches') and 'error'not in x for x in a),'failures':[{'file':x['file'],'mismatches':x.get('mismatches'),'error':x.get('error')} for x in a if x.get('mismatches') or x.get('error')]}
 g=read(P/name/'gallery.json');summary['models'][name]['gallery']={'total':len(g),'exact_matches':sum(x['exact_match'] for x in g)}
 videos=read(P/name/'video-demos.json');summary['models'][name]['videos']=[{'id':x['id'],'seconds':x['preview_seconds'],'status':x['preview']['status'],'change_count':x['preview']['change_count']} for x in videos]
for split in ('original-dev','supplemental-dev'):
 a=read(P/'old'/(split+'.json'));b=read(P/'new'/(split+'.json'));byid={r['id']:r for r in b['outputs']}
 def issues(report,key):return {(r['id'],x['start'],x['end']) for r in report['outputs'] for x in r[key]}
 rows={}
 for key in ('identifier_misses','lost_required_facts','false_removals'):
  old,new=issues(a,key),issues(b,key)
  rows[key]={'fixed':len(old-new),'new':len(new-old),'persistent':len(old&new),'new_examples':[{'id':i,'task':byid[i]['task'],'quote':byid[i]['text'][start:end]} for i,start,end in sorted(new-old)]}
 summary['paired_regressions'][split]=rows
(ROOT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
# Share a directly inspected working context switch, with all source text and no manual rewriting.
examples=[]
for name in ('old','new'):
 for row in read(P/name/'fresh.json')['outputs']:
  if row['id'] in ('fresh-health-employer','fresh-health-clinician','fresh-incident-engineering','fresh-incident-commercial'):
   examples.append(f"## {name}: {row['id']}\n\nTask: {row['task']}\n\n```text\n{row['result']['protected_text']}\n```\n")
(ROOT/'context-examples.md').write_text('# Actual task-dependent outputs\n\nFresh synthetic diagnostics; these exact messages were not in the training release.\n\n'+'\n'.join(examples))
print(json.dumps({'new_fresh':summary['models']['new']['fresh'],'old_tables':summary['models']['old']['adapters']['exact_matches'],'new_tables':summary['models']['new']['adapters']['exact_matches'],'new_fact_loss_regressions':summary['paired_regressions']['supplemental-dev']['lost_required_facts']['new']},indent=2))
