"""Generate explicit instance properties from actual duration/fps; no native mutation or guessed timing."""
import argparse
import json
import math
from pathlib import Path
def bind(defaults,duration_frames,fps,overrides=None):
 if not isinstance(defaults,dict) or (overrides is not None and not isinstance(overrides,dict)):raise ValueError('Defaults and explicit overrides must be objects')
 if not isinstance(duration_frames,int) or isinstance(duration_frames,bool) or duration_frames<=0 or not isinstance(fps,(int,float)) or isinstance(fps,bool) or not math.isfinite(fps) or fps<=0:raise ValueError('Actual positive durationFrames and fps are required')
 values={**defaults,**(overrides or {})};seconds=duration_frames/fps;values['seconds']=seconds
 if values.get('cameraJSON'):
  shots=json.loads(values['cameraJSON'])
  if not shots or any(not isinstance(q.get('until'),(int,float)) or not math.isfinite(q['until']) or q['until']>seconds for q in shots):raise ValueError('Re-author the camera plan for the actual interval; do not truncate a longer plan silently')
 return {'durationFrames':duration_frames,'fps':fps,'seconds':seconds,'propertyOverrides':{**(overrides or {}),'seconds':seconds},'effectiveValues':values,'state':'explicit duration binding; still requires native readback and composed start/read/end inspection'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--defaults',type=Path,required=True);p.add_argument('--duration-frames',type=int,required=True);p.add_argument('--fps',type=float,required=True);p.add_argument('--values',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 try:
  if a.output.exists():raise ValueError('Output exists; choose a new version')
  out=bind(json.loads(a.defaults.read_text()),a.duration_frames,a.fps,json.loads(a.values.read_text()) if a.values else None);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'ok':True,'seconds':out['seconds'],'output':str(a.output)},ensure_ascii=False));return 0
 except (OSError,ValueError,TypeError,KeyError) as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
