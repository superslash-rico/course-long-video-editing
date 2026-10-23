"""Exercise failure boundaries and useful invariants of the portable helpers. No app/account access."""
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.dont_write_bytecode=True
import course_checks as c
from build_quote_cues import build
from bind_instance import bind
from build_demo_plan import build as build_demo

class Checks(unittest.TestCase):
 def setUp(self):
  self.plan={'paragraphs':[{'id':'p1'},{'id':'p2'}],'decisions':[{'paragraphId':'p1','treatment':'animation','reason':'explain a visible process'},{'paragraphId':'p2','treatment':'presenter','reason':'retain a personal reflection'}],'scenes':[{'id':'s1','timelineSeconds':[10,20],'mode':'full-frame','understandingGoal':'understand the check','visibleChange':'the same note changes state','wholeDesign':'two related parts on one sheet','shots':[{'at':0,'until':3},{'at':3.4,'until':9.5}]}],'quotes':[]}
  self.state={'canvas':[1920,1080,60],'durationSeconds':60,'sourceTranscriptHash':'recorded-source-digest','captionCards':[{'id':'c1','text':'已确认的字幕','seconds':[1,2]}],'items':[{'key':'voice','kind':'voice','source':'source-a','sourceSeconds':[0,60],'timelineSeconds':[0,60],'gainDb':0}]}
  self.tokens={'tokens':[{'text':'先核对','start':.2,'end':.7},{'text':'[0.20 seconds silent]','start':.7,'end':.9},{'text':'再判断','start':.9,'end':1.4}]}
  self.requests=[{'id':'q1','sourceSeconds':[0,2],'rows':[{'display':'先核对','anchor':'先核对'},{'display':'再判断','anchor':'再判断'}]}]
 def test_complete_coverage(self):self.assertTrue(c.plan(self.plan)['ok'])
 def test_missed_paragraph_rejected(self):self.plan['decisions'].pop();self.assertFalse(c.plan(self.plan)['ok'])
 def test_actual_quote_overlap_rejected(self):self.plan['quotes']=[{'id':'q','timelineSeconds':[19,22]}];self.assertFalse(c.plan(self.plan)['ok'])
 def test_nonoverlapping_display_not_deleted_by_broad_idea(self):self.plan['quotes']=[{'id':'q','timelineSeconds':[20.1,22],'semanticCandidateSeconds':[15,22]}];self.assertTrue(c.plan(self.plan)['ok'])
 def test_shot_outside_scene_rejected(self):self.plan['scenes'][0]['shots'][1]['until']=11;self.assertFalse(c.plan(self.plan)['ok'])
 def test_camera_hold_overlap_rejected(self):self.plan['scenes'][0]['shots'][1]['at']=2;self.assertFalse(c.plan(self.plan)['ok'])
 def test_whole_missing_rejected(self):self.plan['scenes'][0].pop('wholeDesign');self.assertFalse(c.plan(self.plan)['ok'])
 def test_offset_mapping(self):self.assertTrue(c.mapping({'mapping':[{'sourceSeconds':[0,60],'timelineSeconds':[4,64]}]})['ok'])
 def test_mapping_rate(self):self.assertTrue(c.mapping({'mapping':[{'sourceSeconds':[5,15],'timelineSeconds':[20,25],'rate':2}]})['ok'])
 def test_mixed_units_rejected(self):self.assertFalse(c.mapping({'mapping':[{'sourceSeconds':[0,60000000],'timelineSeconds':[4,64]}]})['ok'])
 def test_overlap_mapping_rejected(self):self.assertFalse(c.mapping({'mapping':[{'sourceSeconds':[0,3],'timelineSeconds':[4,7]},{'sourceSeconds':[6,9],'timelineSeconds':[6,9]}]})['ok'])
 def test_full_caption_pagination(self):self.assertTrue(c.captions({'cards':[{'id':'a','text':'字幕','seconds':[0,1]}],'totalCount':1,'paginationComplete':True,'visibleCaptionTrackCount':1})['ok'])
 def test_duplicate_caption_page_rejected(self):self.assertFalse(c.captions({'cards':[{'id':'a','text':'字幕','seconds':[0,1]}]*2,'totalCount':2,'paginationComplete':True,'visibleCaptionTrackCount':1})['ok'])
 def test_partial_caption_read_rejected(self):self.assertFalse(c.captions({'cards':[{'id':'a','text':'字幕','seconds':[0,1]}],'totalCount':100,'paginationComplete':False,'visibleCaptionTrackCount':1})['ok'])
 def test_duplicate_visible_caption_tracks_rejected(self):self.assertFalse(c.captions({'cards':[{'id':'a','text':'字幕','seconds':[0,1]}],'totalCount':1,'paginationComplete':True,'visibleCaptionTrackCount':2})['ok'])
 def test_original_speech_unchanged(self):self.assertTrue(c.protection(self.state,copy.deepcopy(self.state),{})['ok'])
 def test_overlay_cannot_change_voice_even_if_declared(self):
  after=copy.deepcopy(self.state);after['items'][0]['gainDb']=-3;self.assertFalse(c.protection(self.state,after,{'expectedChanges':{'voice':{'gainDb':-3}}})['ok'])
 def test_explicit_audio_stage_change(self):
  after=copy.deepcopy(self.state);after['items'][0]['gainDb']=-3;self.assertTrue(c.protection(self.state,after,{'stage':'authorized-audio-edit','expectedChanges':{'voice':{'gainDb':-3}}})['ok'])
 def test_expected_new_sfx(self):
  after=copy.deepcopy(self.state);after['items'].append({'key':'sfx1','kind':'sfx','gainDb':-10});self.assertTrue(c.protection(self.state,after,{'allowedAddedItems':['sfx1']})['ok'])
 def test_unexpected_new_audio_rejected(self):
  after=copy.deepcopy(self.state);after['items'].append({'key':'sfx1','kind':'sfx'});self.assertFalse(c.protection(self.state,after,{})['ok'])
 def test_presenter_copy_audio_rejected(self):
  after=copy.deepcopy(self.state);after['items'].append({'key':'copy','kind':'presenter-copy','sourceAudioEnabled':True,'deriveCaptions':False});self.assertFalse(c.protection(self.state,after,{'allowedAddedItems':['copy']})['ok'])
 def test_silent_presenter_copy(self):
  after=copy.deepcopy(self.state);after['items'].append({'key':'copy','kind':'presenter-copy','sourceAudioEnabled':False,'deriveCaptions':False,'linkedAudibleAudioKeys':[]});self.assertTrue(c.protection(self.state,after,{'allowedAddedItems':['copy']})['ok'])
 def test_picture_flag_does_not_prove_no_linked_sound(self):
  after=copy.deepcopy(self.state);after['items'].append({'key':'copy','kind':'presenter-copy','sourceAudioEnabled':False,'deriveCaptions':False,'linkedAudibleAudioKeys':['duplicate-audio']});self.assertFalse(c.protection(self.state,after,{'allowedAddedItems':['copy']})['ok'])
 def test_added_speech_rejected_in_overlay(self):
  after=copy.deepcopy(self.state);after['items'].append({'key':'duplicate-audio','kind':'voice'});self.assertFalse(c.protection(self.state,after,{'allowedAddedItems':['duplicate-audio']})['ok'])
 def test_transcript_change_detected(self):
  after=copy.deepcopy(self.state);after['sourceTranscriptHash']='different';self.assertFalse(c.protection(self.state,after,{})['ok'])
 def test_actual_source_material_record(self):self.assertTrue(c.materials({'materials':[{'id':'m','source':'source page','identity':'real-page','boundary':'prediction is not validation','state':'used','usedIn':['s1'],'productionFile':'crop.png'}]})['ok'])
 def test_import_not_actual_usage(self):self.assertFalse(c.materials({'materials':[{'id':'m','source':'source page','identity':'real-page','boundary':'short excerpt','state':'used'}]})['ok'])
 def test_generated_evidence_rejected(self):self.assertFalse(c.materials({'materials':[{'id':'m','source':'generation record','identity':'generated-illustration','boundary':'illustration','state':'collected','evidenceClaim':True}]})['ok'])
 def test_measured_quote_cues(self):self.assertEqual(len(build(self.tokens,self.requests,'seconds')[0]['speechEvidence']),2)
 def test_silence_placeholder_not_words(self):
  request=[{'id':'q','sourceSeconds':[0,2],'rows':[{'display':'先核对，再判断','anchor':'先核对再判断'}]}];self.assertAlmostEqual(json.loads(build(self.tokens,request,'seconds')[0]['values']['cues'])[0]['end'],1.4)
 def test_word_time_microseconds(self):
  for t in self.tokens['tokens']:t['start']=round(t['start']*1000000);t['end']=round(t['end']*1000000)
  self.assertAlmostEqual(json.loads(build(self.tokens,self.requests,'us')[0]['values']['cues'])[1]['start'],.9)
 def test_ambiguous_anchor_rejected(self):
  self.tokens['tokens'].append({'text':'先核对','start':1.45,'end':1.5})
  with self.assertRaises(ValueError):build(self.tokens,self.requests,'seconds')
 def test_missing_anchor_rejected(self):
  self.requests[0]['rows'][0]['anchor']='不存在的原话'
  with self.assertRaises(ValueError):build(self.tokens,self.requests,'seconds')
 def test_quote_exit_handle(self):
  self.requests[0]['sourceSeconds'][1]=1.5
  with self.assertRaises(ValueError):build(self.tokens,self.requests,'seconds')
 def test_utf16_not_codepoint_length(self):
  t={'tokens':[{'text':'AI','start':.2,'end':.8}]};q=[{'id':'q','sourceSeconds':[0,2],'rows':[{'display':'AI🙂','anchor':'AI'}]}];self.assertEqual(json.loads(build(t,q,'seconds')[0]['values']['cues'])[0]['to'],4)
 def test_effective_values_preserve_false_zero_empty(self):
  self.assertTrue(c.bindings({'properties':[{'key':'a','defaultValue':True},{'key':'b','defaultValue':1},{'key':'c','defaultValue':'title'}],'overrides':{'a':False,'b':0,'c':''},'expected':{'a':False,'b':0,'c':''}})['ok'])
 def test_omitted_default_not_mismatch(self):self.assertTrue(c.bindings({'properties':[{'key':'a','defaultValue':1}],'overrides':None,'expected':{'a':1}})['ok'])
 def test_unknown_property_detected(self):self.assertFalse(c.bindings({'properties':[{'key':'a','defaultValue':1}],'overrides':{'oldUnknown':2}})['ok'])
 def test_bound_duration_not_default_six(self):self.assertEqual(bind({'seconds':6},2595,60)['propertyOverrides']['seconds'],43.25)
 def test_bound_duration_requires_actual_fps(self):
  with self.assertRaises(ValueError):bind({'seconds':6},480,0)
 def test_shorter_instance_requires_new_camera(self):
  with self.assertRaises(ValueError):bind({'cameraJSON':json.dumps([{'at':0,'until':24}])},480,60)
 def test_bound_overrides_keep_zero_false_and_empty(self):
  out=bind({'seconds':6,'strength':1},480,60,{'strength':0,'flag':False,'label':''});self.assertEqual(out['effectiveValues'],{'seconds':8,'strength':0,'flag':False,'label':''})
 def test_copy_scene_from_other_cwd_and_keep_original(self):
  script=Path(__file__).resolve().parent/'create_scene.py';root=script.parents[1];original=(root/'assets/components/course-stage/defaults.json').read_bytes()
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'new scene';p=subprocess.run([sys.executable,str(script),'--output',str(out),'--title','新片任务'],cwd=tmp,capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertTrue((out/'background.js').exists());self.assertEqual(json.loads((out/'defaults.json').read_text())['title'],'新片任务');self.assertEqual((root/'assets/components/course-stage/defaults.json').read_bytes(),original)
   q=subprocess.run([sys.executable,str(script),'--output',str(out),'--title','不可覆盖'],cwd=tmp,capture_output=True,text=True);self.assertEqual(q.returncode,2);self.assertEqual(json.loads((out/'defaults.json').read_text())['title'],'新片任务')
 def demo_maps(self):
  return ({key:f'{i:010x}' for i,key in enumerate(['html','remotion','background','identity','quote','whoosh','settle'],1)},{key:f'{i:010x}' for i,key in enumerate(['base','overlay','sfx'],21)})
 def test_demo_uses_fresh_ids_and_actual_fps(self):
  assets,tracks=self.demo_maps();out=build_demo(Path(__file__).resolve().parents[1],assets,tracks,30);self.assertEqual(out['durationFrames'],1380);self.assertEqual(len(out['adds']),11);self.assertEqual(out['adds'][1]['durationFrames'],240);self.assertEqual(out['adds'][1]['propertyOverrides']['seconds'],8);self.assertEqual(out['adds'][0]['assetId'],assets['html'])
 def test_demo_scales_canvas_placements(self):
  assets,tracks=self.demo_maps();out=build_demo(Path(__file__).resolve().parents[1],assets,tracks,60,3840,2160);self.assertEqual(out['adds'][3]['left'],240);self.assertEqual(out['adds'][3]['width'],2304)
 def test_demo_rejects_unimplemented_aspect(self):
  assets,tracks=self.demo_maps()
  with self.assertRaises(ValueError):build_demo(Path(__file__).resolve().parents[1],assets,tracks,60,1080,1920)

def main():
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks);buffer=io.StringIO();run=unittest.TextTestRunner(stream=buffer,verbosity=1).run(suite)
 out={'ok':run.wasSuccessful(),'testsRun':run.testsRun,'failures':[str(t)+': '+s for t,s in run.failures+run.errors],'scope':'Synthetic records and temporary filesystem. No aesthetic, actual transcript accuracy, listening, native rendering or second-computer claim.'};print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out['ok'] else 2
if __name__=='__main__':raise SystemExit(main())
