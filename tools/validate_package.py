#!/usr/bin/env python3
"""Validate planning artifacts using Python >=3.11, without external packages.
Schema support is intentionally the subset used in this package, not a general JSON Schema engine.
"""
from pathlib import Path
import json, re, sys, hashlib, datetime, copy, tomllib, subprocess
import xml.etree.ElementTree as ET
from source_inventory import HASH_MODE, INVENTORY_EXCLUSIONS, inventory_bytes, source_paths
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(ok,msg):
 checks.append({'check':msg,'passed':bool(ok)})
def matches_type(value,kind):
 return {'object':lambda:isinstance(value,dict),'array':lambda:isinstance(value,list),'string':lambda:isinstance(value,str),'integer':lambda:isinstance(value,int) and not isinstance(value,bool),'boolean':lambda:isinstance(value,bool),'null':lambda:value is None}[kind]()
def validate(value,schema,path='$'):
 errors=[]
 types=schema.get('type')
 if types and not any(matches_type(value,t) for t in (types if isinstance(types,list) else [types])):return [path+': wrong type']
 if 'const' in schema and (value!=schema['const'] or type(value)!=type(schema['const'])):errors.append(path+': const mismatch')
 if 'enum' in schema and value not in schema['enum']:errors.append(path+': enum mismatch')
 if isinstance(value,dict):
  for key in schema.get('required',[]):
   if key not in value:errors.append(path+': missing '+key)
  props=schema.get('properties',{})
  for key,v in value.items():
   if key in props:errors+=validate(v,props[key],path+'.'+key)
   elif schema.get('additionalProperties') is False:errors.append(path+': extra '+key)
 if isinstance(value,list):
  if schema.get('uniqueItems') and len({json.dumps(x,sort_keys=True) for x in value})!=len(value):errors.append(path+': duplicate item')
  for i,v in enumerate(value):errors+=validate(v,schema.get('items',{}),path+f'[{i}]')
 if isinstance(value,str):
  if len(value)<schema.get('minLength',0):errors.append(path+': too short')
  if len(value)>schema.get('maxLength',float('inf')):errors.append(path+': too long')
  if 'pattern' in schema and not re.search(schema['pattern'],value):errors.append(path+': pattern mismatch')
  if schema.get('format')=='date-time':
   try:
    parsed=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    if parsed.tzinfo is None:errors.append(path+': timezone missing')
   except ValueError:errors.append(path+': invalid datetime')
 if isinstance(value,(int,float)) and not isinstance(value,bool):
  if value<schema.get('minimum',-float('inf')):errors.append(path+': below minimum')
  if value>schema.get('maximum',float('inf')):errors.append(path+': above maximum')
 return errors
def source_files():
 return source_paths(ROOT)
sources=source_files()
for file in (f for f in sources if f.suffix=='.json'):
 try:json.loads(file.read_text(encoding='utf-8'));check(True,'JSON parses: '+str(file.relative_to(ROOT)))
 except Exception as e:check(False,str(e))
config=tomllib.loads((ROOT/'config/node.example.toml').read_text(encoding='utf-8'))
schema=json.loads((ROOT/'schemas/configuration/node.schema.json').read_text(encoding='utf-8'))
check(not validate(config,schema),'example config matches supported schema subset')
for field,mutate in [('plaintext',lambda c:c['privacy'].update(allow_plaintext_remote=True)),('privacy_disabled',lambda c:c['privacy'].update(require_private_remote=False)),('bad_limit',lambda c:c['resources'].update(max_concurrent_tasks=0)),('unknown',lambda c:c.update(unknown=True))]:
 bad=copy.deepcopy(config);mutate(bad);check(bool(validate(bad,schema)),'negative configuration rejected: '+field)
es=json.loads((ROOT/'schemas/logging/event.schema.json').read_text(encoding='utf-8'))
fixture={'schema_version':1,'time':'2026-10-17T21:00:00Z','work_id':'WORK-0001','run_id':'schema-test-only','role':'testing','event':'started','summary':'Schema test fixture, not observed product activity','evidence':[]}
check(not validate(fixture,es),'event schema fixture accepted')
bad=copy.deepcopy(fixture);bad['event']='invented_success';check(bool(validate(bad,es)),'unknown event rejected')
bad=copy.deepcopy(fixture);bad['secret']='not-a-real-secret';check(bool(validate(bad,es)),'unknown event payload field rejected')
for f in (f for f in sources if f.suffix=='.jsonl'):
 for line in f.read_text(encoding='utf-8').splitlines():
  if line.strip():check(not validate(json.loads(line),es),'event record: '+str(f.relative_to(ROOT)))
for f in (f for f in sources if f.suffix=='.md'):
 text=f.read_text(encoding='utf-8')
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
  if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
  dest=(f.parent/target.split('#')[0]).resolve()
  check(dest.exists(),'relative link '+str(f.relative_to(ROOT))+' -> '+target)
# Role and work consistency
for name in ['architecture','research','brainstorming','protocol','android','desktop-node','learning','security','testing','mathematical-modeling','pair-programming','pr-review','qwen-research-deputy','orchestrator']:
 check((ROOT/'agents'/f'{name}.md').exists(),'role exists: '+name)
for brief in ROOT.glob('work/WORK-*/brief.md'):
 check(bool(re.search(r'^Status: (not_started|in_progress|blocked|verified)$',brief.read_text(encoding='utf-8'),re.M)),'valid work status: '+brief.parent.name)
 for dep in set(re.findall(r'WORK-\d{4}',brief.read_text(encoding='utf-8').split('## Objective')[0])):
  check(any(ROOT.glob('work/'+dep+'-*/brief.md')),'dependency resolves '+dep)
for f in (f for f in sources if f.suffix=='.puml'):
 t=f.read_text(encoding='utf-8');check(t.count('@startuml')==1 and t.count('@enduml')==1,'PlantUML delimiters: '+f.name)
ns={'b':'http://www.omg.org/spec/BPMN/20100524/MODEL','bpmndi':'http://www.omg.org/spec/BPMN/20100524/DI'}
for f in (f for f in sources if f.suffix=='.bpmn'):
 tree=ET.parse(f);els=list(tree.iter());ids=[e.attrib['id'] for e in els if 'id' in e.attrib];idset=set(ids)
 check(len(ids)==len(idset),'BPMN unique IDs')
 for el in els:
  for attr in ['sourceRef','targetRef','attachedToRef','bpmnElement']:
   if attr in el.attrib:check(el.attrib[attr] in idset,'BPMN reference '+el.attrib[attr])
  if el.tag.endswith(('incoming','outgoing')):check(el.text in idset,'BPMN flow reference '+str(el.text))
 check(bool(tree.findall('.//bpmndi:BPMNShape',ns)) and bool(tree.findall('.//bpmndi:BPMNEdge',ns)),'BPMN contains editor layout')
# Draft proto balance/number checks; no protoc compiler is assumed.
proto=(ROOT/'schemas/protocol/v1/session.proto').read_text(encoding='utf-8')
check(proto.count('{')==proto.count('}'),'proto draft brace balance (not protoc validation)')
manifest_file=ROOT/'MANIFEST.json'
if manifest_file.exists():
 manifest=json.loads(manifest_file.read_text(encoding='utf-8'))
 hash_mode=manifest.get('hash_mode','raw')
 check(hash_mode in ('raw',HASH_MODE),'supported source inventory hash mode')
 for entry in manifest['files']:
  f=ROOT/entry['path'];check(f.is_file() and hash_mode in ('raw',HASH_MODE) and hashlib.sha256(inventory_bytes(f,hash_mode)).hexdigest()==entry['sha256'],'manifest '+entry['path'])
 listed={e['path'] for e in manifest['files']}
 actual={f.relative_to(ROOT).as_posix() for f in sources if f.is_file() and f.name not in INVENTORY_EXCLUSIONS}
 check(listed==actual,'manifest completeness')
report={'status':'passed' if all(x['passed'] for x in checks) else 'failed','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'limits':['This command does not build or test product code','No ML benchmark or cryptographic security proof','PlantUML source delimiter checks only, not rendered','BPMN XML/reference/layout checks, not full XSD validation','Proto structural sketch check, not protoc compilation','Schema validator covers only keywords used in this package']}
if '--write-report' in sys.argv:
 (ROOT/'PACKAGE-VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[x for x in checks if not x['passed']],'limits':report['limits']},ensure_ascii=False,indent=2))
sys.exit(0 if report['status']=='passed' else 1)
