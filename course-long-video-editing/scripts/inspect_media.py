"""Inspect actual export streams and optionally decode audio/video. Requires discovered ffprobe/ffmpeg."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
def inspect(path,ffprobe):
 data=json.loads(subprocess.check_output([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(path)]))
 return {'durationSeconds':float(data['format']['duration']),'bytes':int(data['format']['size']),'streams':[{k:s.get(k) for k in ['codec_type','codec_name','profile','width','height','pix_fmt','avg_frame_rate','nb_frames','color_space','color_transfer','color_primaries','sample_rate','channels']} for s in data['streams']]}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=Path);p.add_argument('--ffprobe');p.add_argument('--ffmpeg');p.add_argument('--decode',action='store_true');p.add_argument('--width',type=int);p.add_argument('--height',type=int);p.add_argument('--fps',type=float);p.add_argument('--transfer');a=p.parse_args();probe=a.ffprobe or shutil.which('ffprobe');ff=a.ffmpeg or shutil.which('ffmpeg')
 if not probe or (a.decode and not ff):print(json.dumps({'ok':None,'state':'not-run','reason':'ffprobe/ffmpeg not available; use native metadata and record missing independent check'}));return 3
 try:
  out=inspect(a.file,probe);errors=[];v=next((s for s in out['streams'] if s['codec_type']=='video'),None)
  if any(x is not None for x in [a.width,a.height,a.fps,a.transfer]) and v is None:errors.append('expected video stream is absent')
  if v:
   for k,want in [('width',a.width),('height',a.height),('color_transfer',a.transfer)]:
    if want is not None and v[k]!=want:errors.append('actual '+k+' differs from expected')
   if a.fps is not None:
    n,d=map(float,v['avg_frame_rate'].split('/'))
    if abs(n/d-a.fps)>1e-6:errors.append('actual output fps differs')
  decoded=False
  if a.decode:subprocess.run([ff,'-v','error','-xerror','-i',str(a.file),'-f','null','-'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);decoded=True
  print(json.dumps({'ok':not errors,'errors':errors,**out,'AVDecoded':decoded,'scope':'Codec/color/fps/duration and decoder errors only; not continuous viewing or listening approval'},ensure_ascii=False,indent=2));return 0 if not errors else 2
 except (OSError,ValueError,KeyError,subprocess.CalledProcessError) as e:print(json.dumps({'ok':False,'error':str(e),'decodeFailure':True},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
