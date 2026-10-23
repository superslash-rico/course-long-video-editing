"""Read PCM levels without editing media. A gain suggestion is a listening starting point, not approval."""
import argparse
import array
import json
import math
import shutil
import subprocess
from pathlib import Path
def meter(path,ffmpeg,start=0,duration=None):
 cmd=[ffmpeg,'-v','error','-ss',str(start),'-i',str(path)]
 if duration is not None:cmd+=['-t',str(duration)]
 cmd+=['-vn','-ar','48000','-ac','2','-f','f32le','pipe:1'];v=array.array('f');v.frombytes(subprocess.check_output(cmd))
 if not v:raise ValueError('No decoded audio samples')
 peak=max(abs(x) for x in v);active=[x for x in v if abs(x)>peak*.025];rms=math.sqrt(sum(x*x for x in active)/max(1,len(active)));db=lambda n:20*math.log10(max(1e-10,n))
 return {'samplePeakDbFS':db(peak),'activeRmsDbFS':db(rms),'sampleFrames':len(v)//2,'sampleRate':48000,'channels':2,'zeroOrNearSilent':peak<1e-8,'overZeroSamples':sum(abs(x)>1 for x in v),'measurement':'float PCM sample peak and active-sample RMS; not true peak or LUFS'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=Path);p.add_argument('--ffmpeg');p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float);p.add_argument('--voice',type=Path);p.add_argument('--voice-start',type=float,default=0);p.add_argument('--voice-duration',type=float,default=1.2);p.add_argument('--relative-rms-db',type=float,default=-8);p.add_argument('--peak-gap-db',type=float,default=6);p.add_argument('--sfx-peak-ceiling-db',type=float,default=-12);a=p.parse_args();ff=a.ffmpeg or shutil.which('ffmpeg')
 if not ff:print(json.dumps({'ok':None,'state':'not-run','reason':'No ffmpeg; measure with available editor tools and record actual method'}));return 3
 try:
  if a.start<0 or (a.duration is not None and a.duration<=0) or a.voice_start<0 or a.voice_duration<=0:raise ValueError('Invalid audio range')
  sfx=meter(a.file,ff,a.start,a.duration);out={'ok':True,'media':sfx,'editsPerformed':False,'subjectiveListening':'not-performed'}
  if a.voice:
   voice=meter(a.voice,ff,a.voice_start,a.voice_duration)
   if sfx['zeroOrNearSilent'] or voice['zeroOrNearSilent']:
    out.update(voice=voice,suggestedSFXGainDb=None,suggestionScope='Silent source/window: choose a real audible SFX and a speech-active window before calculating gain.');print(json.dumps(out,ensure_ascii=False,indent=2));return 0
   gain=min(voice['activeRmsDbFS']+a.relative_rms_db-sfx['activeRmsDbFS'],voice['samplePeakDbFS']-a.peak_gap_db-sfx['samplePeakDbFS'],a.sfx_peak_ceiling_db-sfx['samplePeakDbFS']);out.update(voice=voice,suggestedSFXGainDb=round(gain,2),suggestionScope='Per-source starting point only. Inspect actual track/clip/ducking and final mix, then listen. Do not change original speech automatically.')
  print(json.dumps(out,ensure_ascii=False,indent=2));return 0
 except (OSError,ValueError,subprocess.CalledProcessError) as e:print(json.dumps({'ok':False,'error':str(e)}));return 2
if __name__=='__main__':raise SystemExit(main())
