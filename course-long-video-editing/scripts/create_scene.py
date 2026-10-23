"""Copy the portable stage into a new course-owned source folder; never edit installed templates."""
import argparse
import json
import shutil
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--title',required=True);p.add_argument('--kind',choices=['html','remotion','background'],default='html');a=p.parse_args()
 source=Path(__file__).resolve().parents[1]/'assets/components/course-stage';out=a.output.expanduser().resolve()
 try:
  if out.exists():raise ValueError('Output directory exists; choose a new version')
  if out==source.parents[2] or source.parents[2] in out.parents:raise ValueError('Output must be outside the installed skill')
  resource=json.loads((source/'resource.json').read_text())
  if any(not (source/n).is_file() for n in resource['copyFiles']):raise ValueError('Incomplete source kit')
  out.mkdir(parents=True)
  for name in resource['copyFiles']:
   target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/name,target)
  defaults=json.loads((out/'defaults.json').read_text());defaults['title']=a.title;(out/'defaults.json').write_text(json.dumps(defaults,ensure_ascii=False,indent=2)+'\n');(out/'defaults.js').write_text('export const defaults = '+json.dumps(defaults,ensure_ascii=False)+';\n')
  props=json.loads((out/'properties.json').read_text())
  for v in props:v['defaultValue']=defaults[v['key']]
  (out/'properties.json').write_text(json.dumps(props,ensure_ascii=False,indent=2)+'\n');entry={'html':'index.html','remotion':'remotion-example.tsx','background':'background-only.html'}[a.kind]
  record={'entry':entry,'width':1920,'height':1080,'durationSeconds':24,'properties':'background-properties.json' if a.kind=='background' else 'properties.json','state':'copied; author content/timing/whole layout and import into the current native project before use','fixedExampleTimingIsNotNewSpeechTiming':True};(out/'scene-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'ok':True,'entry':str(out/entry),'next':'Replace content and shot times, inspect real source frames, then native import/readback/composite/export'},ensure_ascii=False));return 0
 except (OSError,ValueError,KeyError) as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
