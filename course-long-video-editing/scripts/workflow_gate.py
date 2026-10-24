"""Stage-scoped reading, real reference comparisons and evidence freshness checks.

This does not edit ChatCut and cannot certify aesthetics or prove that a person/AI
watched a film. It refuses incomplete/stale evidence instead of calling it passed.
"""
import argparse,hashlib,json,shutil,subprocess,sys,struct
from pathlib import Path
from html import escape
sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/examples/quality-baseline'
STAGES={
 'intake':['references/project-start-and-file-management.md','references/intake-and-rough-cut.md'],
 'packaging':['references/branding-intro-outro-transitions.md'],
 'subtitles':['references/subtitles.md'],
 'materials':['references/material-research-and-capture.md'],
 'animation':['references/animation-production.md','references/whole-first-design-and-camera.md','references/example-guide.md','references/runtime-and-binding.md'],
 'emphasis':['references/screen-tutorial.md','references/identity-and-quotes.md'],
 'review':['references/quality-and-handoff.md'],
 'maintenance':['references/learning-and-skill-maintenance.md']}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def in_root(name,root):
 p=(root/name).resolve();p.relative_to(root.resolve())
 if not p.is_file():raise ValueError('Missing packaged file: '+str(name))
 return p
def target_dir(path):
 p=Path(path).expanduser().resolve()
 root=ROOT.resolve()
 if p==root or root in p.parents:raise ValueError('Write course evidence outside the installed Skill')
 if p.exists():raise ValueError('Output exists; preserve it and choose a new version')
 p.mkdir(parents=True);return p
def standard(stage,profile='mixed'):
 files=['SKILL.md']+STAGES[stage]
 if stage=='animation' and profile!='concept':files+=['references/source-annotation-and-camera-acceptance.md']
 rows=[{'file':n,'sha256':sha(in_root(n,ROOT)),'characters':len(in_root(n,ROOT).read_text(encoding='utf-8'))} for n in files]
 package=read(ROOT/'PACKAGE.json')
 payload={'skillVersion':package['version'],'stage':stage,'profile':profile,'readings':rows}
 if stage=='animation':
  payload['benchmarkManifestSHA256']=sha(BASE/'manifest.json')
  payload['mechanisms']=[{'file':n,'sha256':sha(in_root(n,ROOT))} for n in ['assets/components/course-stage/camera.js','assets/components/course-stage/stage.tsx','assets/components/course-stage/source-document.tsx','assets/components/course-stage/source-credit.tsx','assets/components/course-stage/source-credit-layout.js','assets/components/course-stage/scene.css','assets/components/course-stage/scene.js']]
 payload['policyHash']=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 return payload
def prepare(stage,profile,output,ids=None):
 s=standard(stage,profile);refs=[]
 if stage=='animation':
  m=read(BASE/'manifest.json');by={r['id']:r for r in m['examples']};chosen=ids or m['roles'][profile]
  if not chosen or len(chosen)!=len(set(chosen)):raise ValueError('Select distinct applicable references')
  for rid in chosen:
   if rid not in by:raise ValueError('Unknown reference: '+rid)
   r=by[rid];p=in_root(r['file'],BASE)
   if sha(p)!=r['sha256']:raise ValueError('Reference clip differs from approved inventory: '+rid)
   frames=[]
   for q in r['phases']:
    f=in_root(q['file'],BASE)
    if sha(f)!=q['sha256']:raise ValueError('Reference frame changed: '+rid+'/'+q['phase'])
    frames.append({**q,'absoluteFile':str(f)})
   refs.append({'id':rid,'name':r['name'],'sha256':r['sha256'],'clip':str(p),'contactSheet':str(in_root(r['contactSheet'],BASE)),'roles':r['roles'],'phases':frames,'goals':r['goals']})
 out=target_dir(output)
 lock={'schemaVersion':1,'standard':s,'references':refs,'state':'prepared-not-viewed','scope':'Paths/hashes are verified, not actual viewing or aesthetic approval.'}
 write(out/'stage-lock.json',lock)
 review={'schemaVersion':1,'session':'stage-lock.json','referenceObservations':[{'referenceId':r['id'],'viewingStatus':'pending','evidenceFile':None,'observation':'','application':''} for r in refs],'scenes':[],'comparisons':[],'sourceInstances':[],'finalOutput':None,'userAestheticApproval':'pending'}
 write(out/'review.json',review)
 return {'ok':True,'skillVersion':s['skillVersion'],'stage':stage,'policyHash':s['policyHash'],'session':str(out/'stage-lock.json'),'requiredReading':[str(ROOT/r['file']) for r in s['readings']],'readingCharacters':sum(r['characters'] for r in s['readings']),'references':refs,'next':'Actually play the selected films and inspect the four states. Record specific observations; render this lesson, compare current pixels, then check. A prepared session is not a visual pass.'}

def video_info(p):
 tool=shutil.which('ffprobe')
 if not tool:raise ValueError('ffprobe unavailable; use --frames with actual native captures instead')
 m=json.loads(subprocess.check_output([tool,'-v','error','-show_streams','-show_format','-of','json',str(p)],text=True))
 v=next((s for s in m['streams'] if s['codec_type']=='video'),None)
 if not v:raise ValueError('Current export has no video stream')
 return {'durationSeconds':float(m['format']['duration']),'width':v['width'],'height':v['height'],'fps':v.get('avg_frame_rate',v.get('r_frame_rate'))}
def image_size(p):
 data=Path(p).read_bytes()
 if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data)>=24:return struct.unpack('>II',data[16:24])
 if data.startswith(b'\xff\xd8'):
  pos=2
  while pos+4<=len(data):
   if data[pos]!=255:pos+=1;continue
   marker=data[pos+1];pos+=2
   if marker in [0xd8,0xd9] or 0xd0<=marker<=0xd7:continue
   length=int.from_bytes(data[pos:pos+2],'big')
   if marker in [0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf] and pos+7<=len(data):
    h,w=struct.unpack('>HH',data[pos+3:pos+7]);return w,h
   if length<2:break
   pos+=length
 raise ValueError('Expected a decodable-size PNG/JPEG capture: '+str(p))
def comparison(session,ref_id,output,scene,sources,video=None,times=None,frames=None):
 session=Path(session).resolve();lock=read(session);s=lock['standard'];now=standard(s['stage'],s['profile'])
 if now['policyHash']!=s['policyHash']:raise ValueError('Rules changed since prepare; create a fresh session for the applicable update')
 ref=next((r for r in lock['references'] if r['id']==ref_id),None)
 if not ref:raise ValueError('Reference was not prepared for this session')
 current_ref=next(r for r in read(BASE/'manifest.json')['examples'] if r['id']==ref_id)
 if sha(in_root(current_ref['file'],BASE))!=ref['sha256']:raise ValueError('Reference clip changed since prepare')
 if not sources:raise ValueError('Declare the actual entry/support/parameter files for freshness checks')
 snapshots=[{'file':str(Path(p).resolve()),'sha256':sha(p)} for p in sources]
 out=target_dir(output);media=None
 if video:
  video=Path(video).resolve();meta=video_info(video)
  if not times or len(times)!=4 or times!=sorted(set(times)) or times[0]<0 or times[-1]>=meta['durationSeconds']:raise ValueError('Provide four distinct ordered clip-local seconds within the current export')
  tool=shutil.which('ffmpeg')
  if not tool:raise ValueError('ffmpeg unavailable; use --frames with actual native captures instead')
  current=[]
  for i,t in enumerate(times):
   f=out/f'current-{i+1}.jpg';subprocess.run([tool,'-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-q:v','2',str(f)],check=True,capture_output=True);current.append(f)
  media={'file':str(video),'sha256':sha(video),**meta,'timesClipLocalSeconds':times}
 else:
  if not frames or len(frames)!=4:raise ValueError('Provide four actual native frame files in whole/detail/hold-end/return order')
  current=[]
  for i,p in enumerate(frames):
   p=Path(p).resolve()
   if p.suffix.lower() not in ['.png','.jpg','.jpeg']:raise ValueError('Native frames must be actual PNG/JPEG files')
   f=out/f'current-{i+1}{p.suffix.lower()}';shutil.copy2(p,f);current.append(f)
 sizes=[image_size(p) for p in current]
 if len(set(sizes))!=1 or any(min(x)<360 or max(x)<640 for x in sizes):raise ValueError('Use consistent, readable actual capture sizes; thumbnails are not sufficient')
 if len({sha(p) for p in current})<3:raise ValueError('Four timestamps do not provide enough distinct scene states; inspect the actual views and reading motion')
 if {sha(p) for p in current} & {q['sha256'] for q in ref['phases']}:raise ValueError('Reference frames cannot stand in for new lesson captures')
 labels=['whole','detail','hold_end','return'];reference=[]
 for i,q in enumerate(ref['phases']):
  src=Path(q['absoluteFile']);f=out/f'reference-{i+1}{src.suffix}'
  if sha(src)!=q['sha256']:raise ValueError('Reference frame differs from the prepared session')
  shutil.copy2(src,f);reference.append(f)
 imgs=[]
 for kind,files in [('样片',reference),('本课',current)]:
  for i,f in enumerate(files):imgs.append(f'<figure><img src="{escape(f.name)}"><figcaption>{kind} · {labels[i]}</figcaption></figure>')
 page='<!doctype html><meta charset="utf-8"><title>样片与本课实际画面对照</title><style>body{background:#100C19;color:#F5EFF8;font:16px/1.6 sans-serif;margin:24px}h1{font-size:24px}section{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}figure{margin:0}img{width:100%;aspect-ratio:16/9;object-fit:contain;background:#000}figcaption{padding:8px}p{max-width:1000px}</style><h1>'+escape(scene)+' · '+escape(ref['name'])+'</h1><p>上行样片，下行本课。实际检查主要阅读单位、前景相机、停留动态、原件批注、条件、遮挡与整体归组；文件齐全不等于视觉通过。</p><section>'+''.join(imgs)+'</section>'
 (out/'comparison.html').write_text(page,encoding='utf-8')
 record={'schemaVersion':1,'sceneId':scene,'referenceId':ref_id,'referenceSHA256':ref['sha256'],'policyHash':s['policyHash'],'sourceSnapshots':snapshots,'currentMedia':media,'frames':[{'file':str(f),'sha256':sha(f),'role':kind,'phase':labels[i]} for kind,files in [('reference',reference),('current',current)] for i,f in enumerate(files)],'view':'comparison.html','scope':'Actual paired image files plus version checks; manual motion/visual judgment required.'}
 write(out/'comparison.json',record)
 return {'ok':True,'comparison':str(out/'comparison.json'),'view':str(out/'comparison.html'),'next':'Open the comparison and actual clip. Record specific findings and repairs in review.json; do not mark complete from this command.'}

def check(review_path,phase):
 review_path=Path(review_path).resolve();d=read(review_path);lock_path=(review_path.parent/d['session']).resolve();lock=read(lock_path);s=lock['standard'];errors=[]
 if s['stage']!='animation':errors.append('Animation check requires an animation session')
 if standard(s['stage'],s['profile'])['policyHash']!=s['policyHash']:errors.append('Stage rules changed; review applies to an older standard')
 refs={r['id']:r for r in lock['references']};observations={r.get('referenceId'):r for r in d.get('referenceObservations',[])}
 for rid,r in refs.items():
  if not Path(r['clip']).is_file() or sha(r['clip'])!=r['sha256']:errors.append('Reference clip missing/changed: '+rid)
  o=observations.get(rid,{})
  if o.get('viewingStatus')!='motion-and-frames':errors.append('Dynamic reference and keyframes not reviewed: '+rid)
  if not o.get('observation') or not o.get('application'):errors.append('Specific reference observation/application missing: '+rid)
  proof=o.get('evidenceFile')
  if not proof or not (review_path.parent/proof).is_file():errors.append('Viewing evidence missing: '+rid)
 scenes=d.get('scenes',[]);by={r.get('id'):r for r in scenes}
 if not scenes or len(by)!=len(scenes) or any(not x for x in by):errors.append('Scene inventory must be nonempty with unique IDs')
 for scene in scenes:
  if not isinstance(scene.get('usesRealSource'),bool):errors.append('Explicit real-source classification missing: '+str(scene.get('id')))
  credit=scene.get('sourceCredit') or {}
  if not isinstance(credit.get('present'),bool):errors.append('Source-credit presence must be explicit: '+str(scene.get('id')))
  if scene.get('usesRealSource') is True and credit.get('present') is not True:errors.append('Real-source scene needs a source credit: '+str(scene.get('id')))
  if credit.get('present') is True:
   if credit.get('anchor')!='screen-bottom-left' or credit.get('coordinateSpace')!='screen':errors.append('Source credit must be fixed to the screen bottom-left: '+str(scene.get('id')))
   if phase=='review':
    proof=credit.get('auditEvidence')
    if credit.get('audited') is not True or not proof or not (review_path.parent/proof).is_file():errors.append('Actual source-credit position audit missing: '+str(scene.get('id')))
  if not scene.get('understandingGoal') or not scene.get('referenceIds') or not set(scene['referenceIds'])<=set(refs):errors.append('Scene lacks goal/applicable reference: '+str(scene.get('id')))
  if scene.get('usesRealSource') is True and not any('evidence' in refs[r]['roles'] for r in scene.get('referenceIds',[]) if r in refs):errors.append('Real-source scene needs a real-source reference: '+str(scene.get('id')))
  if phase=='review':
   if scene.get('audited') is not True:errors.append('Scene not audited: '+str(scene.get('id')))
   proof=scene.get('auditEvidence')
   if not proof or not (review_path.parent/proof).is_file():errors.append('Scene audit pixels/clip evidence missing: '+str(scene.get('id')))
 comparisons=d.get('comparisons',[]);compared=set()
 for item in comparisons:
  p=(review_path.parent/item['file']).resolve();c=read(p);sid=c['sceneId'];compared.add(sid)
  if sid not in by or c['referenceId'] not in by.get(sid,{}).get('referenceIds',[]):errors.append('Comparison not mapped to its scene/reference')
  if c['policyHash']!=s['policyHash'] or c['referenceId'] not in refs or c['referenceSHA256']!=refs.get(c['referenceId'],{}).get('sha256'):errors.append('Stale comparison standard/reference')
  for f in c['sourceSnapshots']+c['frames']+([c['currentMedia']] if c.get('currentMedia') else []):
   if not Path(f['file']).is_file() or sha(f['file'])!=f['sha256']:errors.append('Compared source/output/frame changed: '+f['file'])
  if not c['sourceSnapshots']:errors.append('Comparison missing current source snapshots')
  if item.get('verdict')!='pass' or not item.get('findings'):errors.append('Actual comparison review incomplete or needs repair: '+sid)
 reps={r['id'] for r in scenes if r.get('representative') is True}
 if not reps or not reps<=compared:errors.append('Representative scene comparisons incomplete')
 for kind in [True,False]:
  if any(r.get('usesRealSource') is kind for r in scenes) and not any(r.get('usesRealSource') is kind and r.get('id') in reps for r in scenes):errors.append('Representative scenes must cover each present source/concept class')
 # Every source use is enumerated, including late lesson/recap/exercise instances.
 source_instances=d.get('sourceInstances',[]);instance_ids=[r.get('id') for r in source_instances]
 if len(instance_ids)!=len(set(instance_ids)) or any(not x for x in instance_ids):errors.append('Source instances need unique IDs')
 for scene in scenes:
  if scene.get('usesRealSource') is True and not any(i.get('sceneId')==scene['id'] for i in source_instances):errors.append('Real-source use inventory missing: '+scene['id'])
 for i in source_instances:
  if i.get('sceneId') not in by:errors.append('Unknown source instance scene')
  if i.get('sourceAvailable') is not False and i.get('annotationOnOriginal') is not True:errors.append('Available source is not annotated in place: '+str(i.get('id')))
  if i.get('sourceAvailable') is False and not i.get('limitation'):errors.append('Unavailable source lacks honest limitation')
  if phase=='review' and i.get('audited') is not True:errors.append('Source instance not audited: '+str(i.get('id')))
 if phase=='review':
  out=d.get('finalOutput') or {}
  if not out.get('file') or not Path(out.get('file','')).is_file() or sha(out['file'])!=out.get('sha256'):errors.append('Current final review output missing/changed')
 return {'ok':not errors,'errors':errors,'phase':phase,'sceneCount':len(scenes),'sourceInstanceCount':len(source_instances),'evidenceComplete':not errors,'aestheticApproval':'not-determined-by-script','scope':'Checks version/evidence completeness and declared review results. It cannot prove viewing, good taste, camera strength, source truth or listening quality; inspect real frames and clips.'}

def main():
 p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
 a=subs.add_parser('prepare');a.add_argument('--stage',choices=list(STAGES),required=True);a.add_argument('--profile',choices=['evidence','concept','exercise','mixed'],default='mixed');a.add_argument('--references',nargs='+');a.add_argument('--output',required=True)
 a=subs.add_parser('compare');a.add_argument('--session',required=True);a.add_argument('--reference',required=True);a.add_argument('--scene',required=True);a.add_argument('--output',required=True);a.add_argument('--sources',nargs='+',required=True);g=a.add_mutually_exclusive_group(required=True);g.add_argument('--video');g.add_argument('--frames',nargs=4);a.add_argument('--times',nargs=4,type=float)
 a=subs.add_parser('check');a.add_argument('review');a.add_argument('--phase',choices=['before-batch','review'],default='before-batch')
 args=p.parse_args()
 try:
  if args.command=='prepare':out=prepare(args.stage,args.profile,args.output,args.references)
  elif args.command=='compare':out=comparison(args.session,args.reference,args.output,args.scene,args.sources,args.video,args.times,args.frames)
  else:out=check(args.review,args.phase)
 except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as e:out={'ok':False,'errors':[str(e)],'aestheticApproval':'not-determined-by-script'}
 print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
