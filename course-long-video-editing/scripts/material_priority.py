# -*- coding: utf-8 -*-
"""Check material provenance/freshness and actual PNG alpha, not visual quality."""
import argparse, hashlib, json, struct, zlib
from pathlib import Path

def digest(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def checked(row,base,errors,label):
 if not isinstance(row,dict) or not row.get('file') or not row.get('sha256'):
  errors.append(label+': file/sha256 required');return None
 p=(base/row['file']).resolve()
 if not p.is_file():errors.append(label+': missing file');return None
 if digest(p)!=row['sha256']:errors.append(label+': changed file');return None
 return p

def png_alpha(p):
 """Decode 8-bit noninterlaced RGBA/GA PNG filters, without optional packages."""
 b=Path(p).read_bytes()
 if not b.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Expected PNG bytes')
 pos=8;chunks=[];info=None
 while pos+12<=len(b):
  n=struct.unpack('>I',b[pos:pos+4])[0];typ=b[pos+4:pos+8];data=b[pos+8:pos+8+n]
  if len(data)!=n:raise ValueError('Truncated PNG')
  if zlib.crc32(typ+data)&0xffffffff!=struct.unpack('>I',b[pos+8+n:pos+12+n])[0]:raise ValueError('PNG checksum mismatch')
  if typ==b'IHDR':info=struct.unpack('>IIBBBBB',data)
  elif typ==b'IDAT':chunks.append(data)
  pos+=12+n
  if typ==b'IEND':break
 if not info:raise ValueError('Missing PNG IHDR')
 w,h,depth,color,compression,filter_method,interlace=info
 if not w or not h or w*h>25000000:raise ValueError('PNG size outside audit bounds')
 if depth!=8 or color not in (4,6) or interlace or compression or filter_method:
  raise ValueError('Use a verified 8-bit noninterlaced RGBA/GA cutout PNG for alpha audit')
 step=4 if color==6 else 2;stride=w*step
 raw=zlib.decompress(b''.join(chunks))
 if len(raw)!=(stride+1)*h:raise ValueError('PNG decoded size mismatch')
 prev=bytearray(stride);hist=[0]*256
 def paeth(a,b,c):
  v=a+b-c;aa=abs(v-a);bb=abs(v-b);cc=abs(v-c)
  return a if aa<=bb and aa<=cc else b if bb<=cc else c
 for y in range(h):
  off=y*(stride+1);mode=raw[off];row=bytearray(raw[off+1:off+1+stride])
  if mode>4:raise ValueError('Invalid PNG filter')
  for x in range(stride):
   a=row[x-step] if x>=step else 0;up=prev[x];ul=prev[x-step] if x>=step else 0
   add=0 if mode==0 else a if mode==1 else up if mode==2 else (a+up)//2 if mode==3 else paeth(a,up,ul)
   row[x]=(row[x]+add)&255
  for a in row[step-1::step]:hist[a]+=1
  prev=row
 lo=next(i for i,n in enumerate(hist) if n);hi=next(i for i in range(255,-1,-1) if hist[i])
 return {'width':w,'height':h,'alphaMin':lo,'alphaMax':hi,'transparentFraction':hist[0]/(w*h)}

def template():
 return {'schemaVersion':2,'researchReceipts':[],'assets':[],'scenes':[],
 'receiptShape':{'id':None,'query':None,'sourceUrl':None,'accessedDate':None,'result':'collected|unavailable|unsuitable','evidence':{'file':None,'sha256':None}},
 'assetShape':{'id':None,'tier':'real|generated|code','role':'evidence|illustration|logic|label|relation','file':None,'sha256':None,'sourceUrl':None,'rightsAndBoundary':None,'generationRecord':None,'visualReview':None,'fullBackgroundException':None},
 'sceneShape':{'id':None,'goal':None,'researchIds':[],'assetIds':[],'realAssessment':None,'generatedAssessment':None,'codeReason':None,'cameraPlan':{'opening':None,'detail':None,'hold':None,'return':None,'perspectiveAndDepth':None,'motionPurpose':None}},
 'scope':'Assistant fills actual records. Template fields are not evidence, aesthetic approval or a required generation quota.'}

def check_plan(plan_path,required_scene_ids=None):
 path=Path(plan_path).resolve();base=path.parent;d=json.loads(path.read_text());errors=[];audits=[]
 if d.get('schemaVersion')!=2:errors.append('Material plan schemaVersion must be 2')
 def indexed(rows,label):
  by={x.get('id'):x for x in rows}
  if len(by)!=len(rows) or any(not k for k in by):errors.append(label+': unique nonempty IDs required')
  return by
 receipts=indexed(d.get('researchReceipts',[]),'researchReceipts')
 if not receipts:errors.append('Actual real-material online research receipts required')
 for rid,r in receipts.items():
  if not all(r.get(k) for k in ['query','sourceUrl','accessedDate']):errors.append(str(rid)+': real query/source/date missing')
  if r.get('result') not in ['collected','unavailable','unsuitable']:errors.append(str(rid)+': explicit actual availability required')
  checked(r.get('evidence'),base,errors,str(rid)+': research evidence')
 assets=indexed(d.get('assets',[]),'assets')
 for aid,a in assets.items():
  tier=a.get('tier');role=a.get('role');p=checked(a,base,errors,str(aid))
  if tier not in ['real','generated','code']:errors.append(str(aid)+': unknown material tier')
  if not a.get('rightsAndBoundary'):errors.append(str(aid)+': rights/use boundary missing')
  if tier=='real' and not a.get('sourceUrl'):errors.append(str(aid)+': original source URL or supplied-original provenance required')
  if tier=='generated':
   if role!='illustration':errors.append(str(aid)+': generated media may only be illustration, never evidence')
   checked(a.get('generationRecord'),base,errors,str(aid)+': generation record')
   exception=a.get('fullBackgroundException')
   if exception:
    if not isinstance(exception,dict) or not exception.get('reason'):errors.append(str(aid)+': full background exception requires actual user-request reason')
    else:checked(exception.get('requestEvidence'),base,errors,str(aid)+': explicit background request')
   if p and not exception:
    try:
     alpha=png_alpha(p);audits.append({'id':aid,**alpha})
     if alpha['alphaMin']>=255 or alpha['alphaMax']<=0 or not .001<alpha['transparentFraction']<.995:
      errors.append(str(aid)+': requires real transparent background and visible subject')
    except (ValueError,struct.error,zlib.error) as e:errors.append(str(aid)+': '+str(e))
   if not a.get('visualReview'):errors.append(str(aid)+': actual edge/subject/material visual review missing')
  if tier=='code' and role not in ['logic','label','relation']:errors.append(str(aid)+': code content limited to logic, relation or labels')
 scenes=indexed(d.get('scenes',[]),'scenes')
 if not scenes:errors.append('Material scene inventory required')
 if required_scene_ids and not set(required_scene_ids)<=set(scenes):errors.append('Material plan does not cover all current animation scenes')
 for sid,s in scenes.items():
  ids=s.get('assetIds',[]);rids=s.get('researchIds',[])
  if not s.get('goal') or not s.get('realAssessment') or not s.get('generatedAssessment'):errors.append(str(sid)+': explain actual tier 1 and tier 2 assessment')
  if not rids or not set(rids)<=set(receipts):errors.append(str(sid)+': map actual online research before lower tiers')
  if not ids or not set(ids)<=set(assets):errors.append(str(sid)+': actual usable material bindings required')
  if any(assets.get(a,{}).get('tier')=='code' for a in ids) and not s.get('codeReason'):errors.append(str(sid)+': explain code logic role after tier assessment')
  camera=s.get('cameraPlan',{})
  if not all(camera.get(k) for k in ['opening','detail','hold','return','perspectiveAndDepth','motionPurpose']):errors.append(str(sid)+': complete purposeful spatial camera plan required')
 return {'ok':not errors,'errors':errors,'sceneCount':len(scenes),'assetCount':len(assets),'pngAlphaAudits':audits,'scope':'File/provenance declarations and real alpha only; manually verify authenticity, rights, beauty, source truth and native camera/video motion.'}

def linked_plan(link,base,scene_ids):
 errors=[];p=checked(link,base,errors,'materialPlan')
 if p:
  try:errors+=check_plan(p,scene_ids)['errors']
  except (OSError,ValueError,KeyError,TypeError) as e:errors.append('materialPlan: '+str(e))
 return errors

def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
 a=s.add_parser('check');a.add_argument('--plan',required=True)
 a=s.add_parser('template');a.add_argument('--output',required=True)
 args=p.parse_args()
 try:
  if args.command=='template':
   out=Path(args.output)
   if out.exists():raise ValueError('Preserve existing plan; choose a new version')
   out.write_text(json.dumps(template(),ensure_ascii=False,indent=2)+'\n');result={'ok':True,'file':str(out)}
  else:result=check_plan(args.plan)
 except (OSError,ValueError,KeyError,TypeError) as e:result={'ok':False,'errors':[str(e)]}
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
