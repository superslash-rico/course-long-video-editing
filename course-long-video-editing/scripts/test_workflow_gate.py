"""Synthetic filesystem regressions for version/evidence gates, not taste tests."""
import unittest,tempfile,json,hashlib,struct,zlib,copy,io
from pathlib import Path
import workflow_gate as w

def png(path,color):
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 row=b'\x00'+bytes(color)*640
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',640,360,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(row*360))+chunk(b'IEND',b''))

class Gate(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.t=Path(self.tmp.name);self.old=(w.ROOT,w.BASE);self.root=self.t/'skill';self.root.mkdir();w.ROOT=self.root;w.BASE=self.root/'assets/examples/quality-baseline';w.BASE.mkdir(parents=True)
  files={'SKILL.md'}|{p for paths in w.STAGES.values() for p in paths}|{'references/source-annotation-and-camera-acceptance.md','assets/components/course-stage/camera.js','assets/components/course-stage/stage.tsx','assets/components/course-stage/source-document.tsx'}
  files|={'assets/components/course-stage/source-credit.tsx','assets/components/course-stage/source-credit-layout.js','assets/components/course-stage/scene.css','assets/components/course-stage/scene.js'}
  for name in files:p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('Synthetic fixture '+name)
  w.write(self.root/'PACKAGE.json',{'version':'1.6.0-test'})
  examples=[]
  for index,rid in enumerate(['E01','E03','E04']):
   clip=w.BASE/(rid+'.mp4');clip.write_bytes(('synthetic hash-only clip '+rid).encode());phases=[]
   for i,label in enumerate(['whole','detail','hold_end','return']):
    f=w.BASE/(rid+'-'+label+'.png');png(f,[20+index*10,20+i*20,60]);phases.append({'phase':label,'file':f.name,'sha256':w.sha(f)})
   examples.append({'id':rid,'name':rid,'file':clip.name,'sha256':w.sha(clip),'roles':['concept'] if rid=='E03' else ['evidence','exercise'],'phases':phases,'goals':['test'],'contactSheet':phases[0]['file']})
  w.write(w.BASE/'manifest.json',{'roles':{'mixed':['E01','E03'],'evidence':['E01'],'concept':['E03'],'exercise':['E04']},'examples':examples})
  self.current=[]
  for i in range(4):p=self.t/f'capture-{i}.png';png(p,[100+i*20,90,130]);self.current.append(str(p))
  self.source=self.t/'current.tsx';self.source.write_text('current-source-v1')
 def tearDown(self):w.ROOT,w.BASE=self.old;self.tmp.cleanup()
 def good(self):
  session=w.prepare('animation','mixed',self.t/'session');review=w.read(self.t/'session/review.json');self.review=self.t/'session/review.json';self.lock=self.t/'session/stage-lock.json'
  review['referenceObservations']=[{'referenceId':r['id'],'viewingStatus':'motion-and-frames','evidenceFile':self.current[0],'observation':'Synthetic observation for contract testing only','application':'Synthetic application for contract testing only'} for r in session['references']]
  review['scenes']=[{'id':'source','understandingGoal':'read a real paragraph','usesRealSource':True,'referenceIds':['E01'],'representative':True,'audited':True,'auditEvidence':self.current[0]},{'id':'method','understandingGoal':'explain a process','usesRealSource':False,'referenceIds':['E03'],'representative':True,'audited':True,'auditEvidence':self.current[1]}]
  for scene in review['scenes']:scene['sourceCredit']={'present':True,'anchor':'screen-bottom-left','coordinateSpace':'screen','audited':True,'auditEvidence':self.current[0]}
  review['sourceInstances']=[{'id':'source-1','sceneId':'source','sourceAvailable':True,'annotationOnOriginal':True,'audited':True}]
  for sid,rid in [('source','E01'),('method','E03')]:
   c=w.comparison(self.lock,rid,self.t/('compare-'+sid),sid,[str(self.source)],frames=self.current)
   review['comparisons'].append({'file':c['comparison'],'verdict':'pass','findings':'Synthetic contract result, no aesthetic claim'})
  out=self.t/'output.bin';out.write_bytes(b'Synthetic output identity only');review['finalOutput']={'file':str(out),'sha256':w.sha(out)}
  w.write(self.review,review);return review
 def test_subtitles_prepare_without_any_reference_library(self):
  (w.BASE/'manifest.json').unlink();r=w.prepare('subtitles','mixed',self.t/'subtitles');self.assertEqual(r['references'],[]);self.assertFalse(any('animation-production' in p for p in r['requiredReading']))
 def test_prepared_session_is_not_viewed_or_passed(self):
  w.prepare('animation','mixed',self.t/'session');r=w.check(self.t/'session/review.json','before-batch');self.assertFalse(r['ok']);self.assertEqual(r['aestheticApproval'],'not-determined-by-script')
 def test_reference_corruption_refused(self):
  (w.BASE/'E01.mp4').write_bytes(b'changed')
  with self.assertRaises(ValueError):w.prepare('animation','mixed',self.t/'session')
 def test_existing_output_never_overwritten(self):
  w.prepare('animation','mixed',self.t/'session')
  with self.assertRaises(ValueError):w.prepare('animation','mixed',self.t/'session')
 def test_no_work_files_inside_skill(self):
  with self.assertRaises(ValueError):w.prepare('subtitles','mixed',self.root/'work')
 def test_complete_contract_still_does_not_claim_aesthetics(self):
  self.good();r=w.check(self.review,'review');self.assertTrue(r['ok'],r);self.assertEqual(r['aestheticApproval'],'not-determined-by-script')
 def test_changed_component_invalidates_policy_lock(self):
  self.good();(self.root/'assets/components/course-stage/stage.tsx').write_text('new mechanism');self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_new_standard_version_invalidates_old_lock(self):
  self.good();w.write(self.root/'PACKAGE.json',{'version':'1.6.1-test'});self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_changed_reference_manifest_invalidates_lock(self):
  self.good();m=w.read(w.BASE/'manifest.json');m['revision']='new reference guidance';w.write(w.BASE/'manifest.json',m);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_source_edit_invalidates_comparison(self):
  self.good();self.source.write_text('new source after old render');self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_capture_replacement_invalidates_comparison(self):
  d=self.good();c=w.read(d['comparisons'][0]['file']);Path(c['frames'][-1]['file']).write_bytes(b'replaced');self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_output_replacement_invalidates_review(self):
  d=self.good();Path(d['finalOutput']['file']).write_bytes(b'changed');self.assertFalse(w.check(self.review,'review')['ok'])
 def test_needs_repair_never_hidden_by_other_passes(self):
  d=self.good();d['comparisons'][0]['verdict']='needs-repair';w.write(self.review,d);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_late_source_instance_without_in_place_annotation_refused(self):
  d=self.good();d['sourceInstances'].append({'id':'late-exercise','sceneId':'source','sourceAvailable':True,'annotationOnOriginal':False,'audited':True});w.write(self.review,d);self.assertFalse(w.check(self.review,'review')['ok'])
 def test_missing_source_instance_refused(self):
  d=self.good();d['sourceInstances']=[];w.write(self.review,d);self.assertFalse(w.check(self.review,'review')['ok'])
 def test_unavailable_source_needs_honest_limitation(self):
  d=self.good();d['sourceInstances'][0].update(sourceAvailable=False,annotationOnOriginal=False,limitation='Login prevents a usable screenshot; retain speech and source note');w.write(self.review,d);self.assertTrue(w.check(self.review,'review')['ok'])
 def test_static_frames_do_not_prove_dynamic_reference_viewing(self):
  d=self.good();d['referenceObservations'][0]['viewingStatus']='frames-only';w.write(self.review,d);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_scene_source_classification_explicit(self):
  d=self.good();del d['scenes'][0]['usesRealSource'];w.write(self.review,d);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_final_scene_pixels_required(self):
  d=self.good();del d['scenes'][1]['auditEvidence'];w.write(self.review,d);self.assertFalse(w.check(self.review,'review')['ok'])
 def test_duplicate_still_frames_rejected(self):
  w.prepare('animation','mixed',self.t/'session')
  with self.assertRaises(ValueError):w.comparison(self.t/'session/stage-lock.json','E01',self.t/'bad','source',[str(self.source)],frames=[self.current[0]]*4)
 def test_invalid_image_bytes_rejected(self):
  w.prepare('animation','mixed',self.t/'session');bad=self.t/'not-image.png';bad.write_bytes(b'not an image')
  with self.assertRaises(ValueError):w.comparison(self.t/'session/stage-lock.json','E01',self.t/'bad','source',[str(self.source)],frames=[str(bad)]*4)
 def test_reference_frames_cannot_be_new_lesson_evidence(self):
  s=w.prepare('animation','mixed',self.t/'session');frames=[q['absoluteFile'] for q in s['references'][0]['phases']]
  with self.assertRaises(ValueError):w.comparison(self.t/'session/stage-lock.json','E01',self.t/'bad','source',[str(self.source)],frames=frames)
 def test_representatives_cover_both_classes_when_present(self):
  d=self.good();d['scenes'][1]['representative']=False;w.write(self.review,d);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_source_credit_cannot_move_into_main_reading_area(self):
  d=self.good();d['scenes'][0]['sourceCredit']['anchor']='middle-left';w.write(self.review,d);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_source_credit_cannot_use_world_coordinates(self):
  d=self.good();d['scenes'][0]['sourceCredit']['coordinateSpace']='world';w.write(self.review,d);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_real_source_cannot_omit_credit(self):
  d=self.good();d['scenes'][0]['sourceCredit']={'present':False};w.write(self.review,d);self.assertFalse(w.check(self.review,'before-batch')['ok'])
 def test_credit_position_requires_actual_review_evidence(self):
  d=self.good();d['scenes'][0]['sourceCredit']['auditEvidence']='missing.png';w.write(self.review,d);self.assertFalse(w.check(self.review,'review')['ok'])
 def test_absent_optional_concept_credit_is_explicit(self):
  d=self.good();d['scenes'][1]['sourceCredit']={'present':False};w.write(self.review,d);self.assertTrue(w.check(self.review,'review')['ok'])
 def test_changed_source_credit_defaults_invalidates_old_review(self):
  self.good();(self.root/'assets/components/course-stage/source-credit-layout.js').write_text('changed credit defaults');self.assertFalse(w.check(self.review,'before-batch')['ok'])

def main():
 stream=io.StringIO();r=unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(Gate));out={'ok':r.wasSuccessful(),'testsRun':r.testsRun,'failures':[str(t)+': '+s for t,s in r.failures+r.errors],'scope':'Synthetic filesystem/identity fixtures only. No real playback, visual taste, decoding or user approval claim.'};print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
