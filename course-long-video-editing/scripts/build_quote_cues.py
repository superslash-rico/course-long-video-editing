"""Build quote cues from explicit real word anchors; no estimated fallback or fuzzy correction."""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
sys.dont_write_bytecode=True
from validate_quote import validate

def normalized(text):return ''.join(c.casefold() for c in str(text) if unicodedata.category(c)[0] in 'LN')
def normalize_tokens(data,unit):
 scale={'seconds':1,'ms':.001,'us':.000001}[unit];tokens=data.get('tokens')
 if tokens is None:tokens=[t for u in data.get('utterances',[]) for t in u.get('tokens',[])]
 if not tokens:raise ValueError('No actual word tokens')
 chars=[];clock=[]
 for token in tokens:
  text=str(token.get('text',''))
  if token.get('hidden') or token.get('deleted') or token.get('kind')=='silence' or re.fullmatch(r'\[\d+(?:\.\d+)? seconds silent\]',text):continue
  start,end=token.get('start'),token.get('end')
  if not isinstance(start,(int,float)) or not isinstance(end,(int,float)) or not 0<=start<end:raise ValueError('Invalid word time')
  for c in normalized(text):chars.append(c);clock.append((start*scale,end*scale))
 return ''.join(chars),clock
def build(transcript,requests,unit):
 text,clock=normalize_tokens(transcript,unit);out=[]
 for request in requests:
  rows=request['rows'];start=request['sourceSeconds'][0];end=request['sourceSeconds'][1];cues=[];provenance=[]
  for row,r in enumerate(rows):
   needle=normalized(r['anchor']);matches=[];at=0
   if not needle:raise ValueError('Empty speech anchor')
   while (at:=text.find(needle,at))>=0:
    a,b=clock[at][0],clock[at+len(needle)-1][1]
    if start<=a and b<=end:matches.append((a,b))
    at+=1
   if len(matches)!=1:raise ValueError('Anchor missing or ambiguous in its source window: '+r['anchor'])
   a,b=matches[0];cues.append({'row':row,'from':0,'to':len(r['display'].encode('utf-16-le'))//2,'start':a-start,'end':b-start});provenance.append({'display':r['display'],'actualSpeechAnchor':r['anchor'],'sourceSeconds':[a,b]})
  values={'text':'\n'.join(r['display'] for r in rows),'cues':json.dumps(cues,ensure_ascii=False),'keywords':request.get('keywords',''),'seconds':end-start}
  errors=validate(values)
  if errors:raise ValueError('; '.join(errors))
  if any(c['end']>values['seconds']-.35 for c in cues):raise ValueError('Leave enough time after speech for the actual exit, or choose a different quote window')
  out.append({'id':request['id'],'values':values,'sourceSeconds':request['sourceSeconds'],'speechEvidence':provenance,'textRelationship':'display is an editorial condensation; do not imply verbatim quotation'})
 return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--transcript',required=True,type=Path);p.add_argument('--requests',required=True,type=Path);p.add_argument('--time-unit',choices=['seconds','ms','us'],required=True);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 try:
  if a.output.exists():raise ValueError('Output exists; preserve it or choose a new version')
  out=build(json.loads(a.transcript.read_text()),json.loads(a.requests.read_text()),a.time_unit);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'quotes':out},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'ok':True,'quotes':len(out),'output':str(a.output),'scope':'Measured word timing, not factual or visual approval'},ensure_ascii=False));return 0
 except (OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
