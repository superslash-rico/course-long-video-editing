"""Read-only checks on normalized course records. Does not judge aesthetics or edit an app."""
import argparse
import json
import math
import sys
from pathlib import Path
sys.dont_write_bytecode=True
from validate_quote import validate as validate_quote

def finite(n):return isinstance(n,(float,int)) and not isinstance(n,bool) and math.isfinite(n)
def span(v):return isinstance(v,list) and len(v)==2 and all(finite(x) for x in v) and 0<=v[0]<v[1]
def overlap(a,b):return a[0]<b[1] and b[0]<a[1]
def result(errors,**extra):return {'ok':not errors,'errors':errors,**extra}

def plan(data):
 errors=[];paragraphs=data.get('paragraphs',[]);decisions=data.get('decisions',[]);scenes=data.get('scenes',[]);quotes=data.get('quotes',[])
 ids=[p.get('id') for p in paragraphs];covered=[d.get('paragraphId') for d in decisions]
 if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):errors.append('paragraphs require unique nonempty ids')
 if set(ids)-set(covered):errors.append('unreviewed paragraphs: '+', '.join(sorted(set(ids)-set(covered))))
 if set(covered)-set(ids):errors.append('decision references an unknown paragraph')
 for d in decisions:
  if d.get('treatment') not in ['animation','quote','screen','presenter','transition'] or not d.get('reason'):errors.append('each decision needs a treatment and reason')
 for s in scenes:
  if not s.get('id') or not span(s.get('timelineSeconds')):errors.append('each scene needs an id and valid timelineSeconds');continue
  if s.get('mode') not in ['full-frame','local','transparent']:errors.append('scene needs explicit display mode')
  if not s.get('understandingGoal') or not s.get('visibleChange'):errors.append('scene needs understandingGoal and visibleChange')
  if s.get('mode')=='full-frame' and not s.get('wholeDesign'):errors.append('full-frame scene needs planned whole composition')
  dur=s['timelineSeconds'][1]-s['timelineSeconds'][0];prev=None
  for shot in s.get('shots',[]):
   a,b=shot.get('at'),shot.get('until')
   if not finite(a) or not finite(b) or not 0<=a<=b<=dur:errors.append('shot outside its scene');continue
   if prev is not None and a<prev:errors.append('camera reading holds overlap')
   prev=b
 for q in quotes:
  if not span(q.get('timelineSeconds')):errors.append('quote needs valid timelineSeconds');continue
  for s in scenes:
   if span(s.get('timelineSeconds')) and overlap(q['timelineSeconds'],s['timelineSeconds']) and not q.get('overlapJustification'):errors.append('quote overlaps actual animation: '+str(q.get('id'))+'/'+str(s.get('id')))
 return result(errors,paragraphCount=len(ids),decisionCount=len(decisions),sceneCount=len(scenes),quoteCount=len(quotes),scope='Coverage and timing structure only; full-text teaching judgment and frames still require review.')

def materials(data):
 errors=[]
 for m in data.get('materials',[]):
  for k in ['id','source','identity','boundary','state']:
   if not m.get(k):errors.append('material missing '+k)
  if m.get('state') not in ['collected','imported-reference','used','unavailable']:errors.append('invalid material state')
  if m.get('identity') not in ['real-page','real-photo','source-video','self-authored-illustration','generated-illustration']:errors.append('invalid material identity')
  if m.get('state')=='used' and (not m.get('usedIn') or not m.get('productionFile')):errors.append('used material requires productionFile and actual usedIn')
  if m.get('identity') in ['generated-illustration','self-authored-illustration'] and m.get('evidenceClaim') is True:errors.append('illustration cannot claim to be factual evidence')
 return result(errors,scope='Source ledger completeness and use status; source credibility, permission and factual accuracy require human/agent research.')

def mapping(data):
 errors=[];rows=data.get('mapping',[])
 for i,r in enumerate(rows):
  src,dst=r.get('sourceSeconds'),r.get('timelineSeconds');rate=r.get('rate',1)
  if not span(src) or not span(dst) or not finite(rate) or rate<=0:errors.append('invalid source/timeline mapping');continue
  if abs((src[1]-src[0])/rate-(dst[1]-dst[0]))>1e-6:errors.append('mapping duration/rate mismatch')
  if i and span(rows[i-1].get('timelineSeconds')) and dst[0]<rows[i-1]['timelineSeconds'][1]:errors.append('unexpected overlap in body mapping')
 return result(errors,scope='Constant-speed source mapping; variable speed needs an explicit per-frame map or preserved native track.')

def captions(data):
 errors=[];cards=data.get('cards',[]);ids=[x.get('id') for x in cards]
 if not cards:errors.append('no caption cards')
 if len(ids)!=len(set(ids)):errors.append('duplicate caption id or repeated pagination')
 if data.get('totalCount')!=len(cards):errors.append('card count does not match the full paginated total')
 if data.get('paginationComplete') is not True:errors.append('pagination completeness not recorded')
 previous=None
 for c in cards:
  if not isinstance(c.get('text'),str) or not c['text'].strip():errors.append('empty caption card')
  if not span(c.get('seconds')):errors.append('invalid caption time');continue
  if previous and c['seconds'][0]<previous:errors.append('caption overlap or unordered cards')
  previous=c['seconds'][1]
 if data.get('visibleCaptionTrackCount')!=1:errors.append('expected one confirmed visible primary caption track')
 return result(errors,cardCount=len(cards),scope='Card structure/pagination only; spelling, speech meaning and on-screen position require review.')

def protection(before,after,changes):
 errors=[];allowed=changes.get('expectedChanges',{});added=set(changes.get('allowedAddedItems',[]));removed=set(changes.get('allowedDeletedItems',[]));a={x['key']:x for x in before.get('items',[])};b={x['key']:x for x in after.get('items',[])}
 if len(a)!=len(before.get('items',[])) or len(b)!=len(after.get('items',[])):errors.append('duplicate normalized item key')
 for k in ['canvas','durationSeconds','sourceTranscriptHash','captionCards']:
  expected=changes.get('expectedTopLevel',{}).get(k,before.get(k))
  if after.get(k)!=expected:errors.append('protected top-level changed: '+k)
 if set(b)-set(a)!=added:errors.append('added items differ from explicit change plan')
 if set(a)-set(b)!=removed:errors.append('deleted items differ from explicit change plan')
 for key in set(a)&set(b):
  expected={**a[key],**allowed.get(key,{})}
  if b[key]!=expected:errors.append('unexpected item fields changed: '+key)
  if a[key].get('kind')=='voice' and b[key]!=a[key] and changes.get('stage','overlay') in ['overlay','subtitle']:errors.append('overlay/subtitle stage changed original speech: '+key)
 for key in added:
  item=b.get(key,{})
  if item.get('kind')=='voice' and changes.get('stage','overlay') in ['overlay','subtitle']:errors.append('overlay/subtitle stage added a speech track: '+key)
  if item.get('kind')=='presenter-copy' and (item.get('sourceAudioEnabled') is not False or item.get('deriveCaptions') is not False or item.get('linkedAudibleAudioKeys')!=[]):errors.append('new presenter copy duplicates audio/captions or linked sound is unverified: '+key)
 return result(errors,scope='Normalized actual values, not raw serialization; declared changes must name exact resulting values. Does not establish subjective audio or visual quality.')

def quotes(data):
 errors=[]
 for q in data.get('quotes',[]):
  values=q.get('values',q);errors.extend(str(q.get('id','quote'))+': '+s for s in validate_quote(values))
  if finite(q.get('durationSeconds')) and abs(q['durationSeconds']-values.get('seconds',0))>1e-6:errors.append('quote seconds differs from placed item duration')
 return result(errors,scope='UTF-16 cue coverage and time structure; actual word sync and visual layout are separate checks.')

def bindings(data):
 schema=data.get('properties',[]);overrides=data.get('overrides')
 if overrides is None:overrides={}
 if not isinstance(overrides,dict):return result(['overrides must be an object or null'])
 defaults={p['key']:p.get('defaultValue') for p in schema};effective={**defaults,**overrides};errors=[]
 if len(defaults)!=len(schema):errors.append('duplicate property key')
 if set(overrides)-set(defaults):errors.append('unknown override keys require current-schema review')
 for key,value in data.get('expected',{}).items():
  if key not in effective or effective[key]!=value:errors.append('effective property differs: '+key)
 return result(errors,effective=effective,scope='Readback defaults plus saved overrides; an empty native update patch does not clear previously saved values.')

CHECKS={'plan':plan,'materials':materials,'mapping':mapping,'captions':captions,'quotes':quotes,'bindings':bindings}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('check',choices=[*CHECKS,'protection']);p.add_argument('input',type=Path);p.add_argument('--after',type=Path);p.add_argument('--changes',type=Path);a=p.parse_args()
 try:
  data=json.loads(a.input.read_text())
  if a.check=='protection':
   if not a.after or not a.changes:p.error('protection requires --after and --changes')
   out=protection(data,json.loads(a.after.read_text()),json.loads(a.changes.read_text()))
  else:out=CHECKS[a.check](data)
 except (OSError,ValueError,KeyError,TypeError) as exc:out=result([str(exc)])
 print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
