"""Build a reviewable demo placement plan using newly imported asset/track IDs. Never calls an app."""
import argparse
import json
import math
import re
from pathlib import Path
ID=re.compile(r'(?:[0-9a-f]{10}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',re.I)
def build(root,assets,tracks,fps=60,width=1920,height=1080):
 if not isinstance(fps,(int,float)) or not math.isfinite(fps) or fps<=0:raise ValueError('Read the actual positive project fps')
 if width<=0 or height<=0 or abs(width/height-16/9)>1e-6:raise ValueError('This gallery is a 16:9 example; redesign other aspect ratios')
 config=json.loads((root/'assets/examples/portable-workflow/demo-config.json').read_text());sx=width/1920;sy=height/1080
 for key in ['html','remotion','background','identity','quote','whoosh','settle']:
  if not isinstance(assets.get(key),str) or not ID.fullmatch(assets[key]):raise ValueError('Supply the current imported asset ID for '+key)
 for key in ['base','overlay','sfx']:
  if not isinstance(tracks.get(key),str) or not ID.fullmatch(tracks[key]):raise ValueError('Supply the current created track ID for '+key)
 if len(set(assets.values()))!=len(assets):raise ValueError('Demo roles require their separately imported assets')
 def graphic(role,a,b,x,y,w,h,values=None):
  item={'type':'motion-graphic','assetId':assets[role],'trackId':tracks['base' if role in ['html','remotion','background'] else 'overlay'],'startFrame':round(a*fps),'durationFrames':round((b-a)*fps),'left':x*sx,'top':y*sy,'width':w*sx,'height':h*sy}
  if values:item['propertyOverrides']=values
  return item
 adds=[graphic('html',0,24,0,0,1920,1080,{'seconds':24}),graphic('remotion',24,32,0,0,1920,1080,config['remotionValues']),graphic('background',32,46,0,0,1920,1080),graphic('identity',32,38,120,520,1152,460.8,{'seconds':6,'name':'Rico','identity':'超级斜杠创始人'}),graphic('quote',38,46,70,100,1296,837,config['quoteValues'])]
 for e in config['soundEvents']:
  role='whoosh' if e['file'].endswith('soft-whoosh.wav') else 'settle';seconds=.52 if role=='whoosh' else .22
  adds.append({'type':'audio','assetId':assets[role],'trackId':tracks['sfx'],'startFrame':round(e['startSeconds']*fps),'durationFrames':round(seconds*fps),'sourceIn':0,'decibelAdjustment':e['gainDb']})
 return {'fps':fps,'canvas':[width,height],'durationFrames':round(46*fps),'adds':adds,'scope':'Example placement fields for the recorded Desktop native contract; inspect the current tool schema before applying. Pass current project/timeline IDs separately. No mutation performed.'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assets',required=True,type=Path);p.add_argument('--tracks',required=True,type=Path);p.add_argument('--fps',required=True,type=float);p.add_argument('--width',type=int,default=1920);p.add_argument('--height',type=int,default=1080);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
 try:
  if a.output.exists():raise ValueError('Output exists; choose a new version')
  out=build(Path(__file__).resolve().parents[1],json.loads(a.assets.read_text()),json.loads(a.tracks.read_text()),a.fps,a.width,a.height);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'ok':True,'items':len(out['adds']),'durationFrames':out['durationFrames'],'output':str(a.output)},ensure_ascii=False));return 0
 except (OSError,ValueError,TypeError,KeyError) as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
