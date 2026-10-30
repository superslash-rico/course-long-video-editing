"""Failure-boundary tests for missing, stale and mis-timed course evidence."""
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
import lesson_standard as q


class LessonStandard(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.file = self.base / 'actual-local-evidence.txt'
        self.file.write_text('Synthetic contract evidence, not a course or aesthetic pass')
        self.ref = {'file': self.file.name, 'sha256': q.digest(self.file)}
        self.pass_record = {'status': 'pass', 'finding': 'Synthetic fixture for evidence-contract testing', 'evidence': self.ref}
        self.design = {'fullCanvas': True, 'readingUnitComplete': True, 'foregroundCamera': True,
                       'backgroundMode': 'dot-parallax', 'cameraFamily': 'follow-material',
                       'cameraPurpose': 'Follow the same document into its result',
                       'materialTreatment': 'real-source', 'materialReason': 'Read the actual source paragraph',
                       'presenterMode': 'none', 'presenterReason': 'This fixture has no video input'}
        self.animation = {'scenes': [{'id': 's1', 'visualDesign': self.design,
                                     'visualChecks': {k: copy.deepcopy(self.pass_record) for k in q.VISUAL_CHECKS}}],
                          'sourceInstances': [{'id': 'i1', 'sceneId': 's1', 'sourceAvailable': True,
                                               'useKind': 'reading', 'annotationStyle': 'marker-circle', 'coordinateSpace': 'source-pixels'}],
                          'visualSummary': {k: copy.deepcopy(self.pass_record) for k in q.SUMMARY_CHECKS}}
        self.overview = {'status': 'included', 'contentSummary': ['Turn a task into a workflow'],
                         'learningObjectives': ['Draw steps and identify human checks'],
                         'displayText': 'Learn workflows; draw steps and identify human checks.', 'basis': [self.ref],
                         'presentation': {'durationSeconds': 9.5, 'fullTextAtSeconds': 1.8, 'animatedBackground': True,
                                          'typewriter': True, 'soundEffect': True, 'narration': False, 'presenter': False, 'extraFootage': False},
                         'timeline': {'introEnd': 4, 'overviewStart': 4, 'overviewEnd': 13.5, 'bodyStart': 13.5, 'bodyEnd': 100, 'outroStart': 100},
                         'contentReview': self.pass_record, 'readabilityReview': self.pass_record,
                         'timingReview': self.pass_record, 'mappingEvidence': self.ref}

    def tearDown(self):
        self.temp.cleanup()

    def visual(self):
        return q.animation_checks(self.animation, self.base, 'review')

    def overview_errors(self):
        return q.overview_checks({'lessonOverview': self.overview}, self.base)

    def test_actual_complete_visual_contract(self):
        self.assertEqual(self.visual(), [])

    def test_fixed_occlusion_design_refused(self):
        self.design['fullCanvas'] = False
        self.assertTrue(self.visual())

    def test_background_only_camera_refused(self):
        self.design['foregroundCamera'] = False
        self.assertTrue(self.visual())

    def test_missing_dot_proof_refused(self):
        del self.animation['scenes'][0]['visualChecks']['dot-parallax']
        self.assertTrue(self.visual())

    def test_dot_template_cannot_mark_visibility_not_applicable(self):
        self.animation['scenes'][0]['visualChecks']['dot-parallax']['status'] = 'not-applicable'
        self.assertTrue(self.visual())

    def test_actual_full_frame_source_can_explain_background_exception(self):
        self.design.update(backgroundMode='source-full-frame', backgroundReason='Full-frame original recording leaves no exposed animation background')
        self.animation['scenes'][0]['visualChecks']['dot-parallax']['status'] = 'not-applicable'
        self.assertEqual(self.visual(), [])

    def test_stale_actual_pixels_refused(self):
        self.file.write_text('Changed after the recorded review')
        self.assertTrue(self.visual())

    def test_placeholder_card_rejected_as_exercise_material(self):
        self.design['materialTreatment'] = 'placeholder-card'
        self.assertTrue(self.visual())

    def test_authored_document_needs_actual_files(self):
        self.design['materialTreatment'] = 'authored-artifact'
        self.assertTrue(self.visual())
        self.animation['sourceInstances'][0]['authoredArtifact'] = {
            'label': 'self-authored-teaching-example', 'editableSource': self.ref,
            'documentFile': self.ref, 'renderedImage': self.ref}
        self.assertEqual(self.visual(), [])
        self.animation['sourceInstances'][0]['authoredArtifact']['renderedImage'] = {'file': 'absent.png', 'sha256': '0'*64}
        self.assertTrue(self.visual())

    def test_authored_example_cannot_claim_official_identity(self):
        self.animation['sourceInstances'][0]['authoredArtifact'] = {
            'label': 'official-source', 'editableSource': self.ref, 'documentFile': self.ref, 'renderedImage': self.ref}
        self.assertTrue(self.visual())

    def test_reading_marks_need_source_coordinate_system(self):
        self.animation['sourceInstances'][0]['coordinateSpace'] = 'screen'
        self.assertTrue(self.visual())

    def test_uniform_frame_requires_semantic_selection_reason(self):
        self.animation['sourceInstances'][0]['annotationStyle'] = 'semantic-frame'
        self.assertTrue(self.visual())
        self.animation['sourceInstances'][0]['annotationReason'] = 'Original application selection rectangle'
        self.assertEqual(self.visual(), [])

    def test_identity_logo_needs_main_composition_placement(self):
        self.animation['sourceInstances'][0] = {'id': 'logo', 'sceneId': 's1', 'sourceAvailable': True,
                                               'useKind': 'identity', 'identityPlacement': 'top-right-badge'}
        self.assertTrue(self.visual())
        self.animation['sourceInstances'][0]['identityPlacement'] = 'main-subject'
        self.assertEqual(self.visual(), [])

    def test_repetitive_camera_batch_needs_repair_or_teaching_reason(self):
        for sid in ('s2', 's3'):
            extra = copy.deepcopy(self.animation['scenes'][0]);extra['id'] = sid
            self.animation['scenes'].append(extra)
        self.assertTrue(self.visual())
        self.animation['visualSummary']['repetitionRationale'] = 'Continuous follow shot deliberately keeps one document identifiable; local angles and reading beats differ, recorded in scene audit'
        self.assertEqual(self.visual(), [])

    def test_dynamic_presenter_and_coverage_audits_required(self):
        for key in ('presenter-routing', 'animation-coverage'):
            with self.subTest(key=key):
                old = self.animation['visualSummary'].pop(key)
                self.assertTrue(self.visual())
                self.animation['visualSummary'][key] = old

    def test_complete_lesson_overview(self):
        self.assertEqual(self.overview_errors(), [])

    def test_default_template_is_pending_and_not_passed(self):
        self.assertTrue(q.overview_checks({'lessonOverview': q.overview_template()}, self.base))

    def test_ai_declaration_does_not_substitute_for_learning_goals(self):
        self.overview.update(displayText='Voice and appearance were generated by AI.', learningObjectives=[])
        self.assertTrue(self.overview_errors())

    def test_target_text_requires_actual_lesson_basis(self):
        self.overview['basis'] = []
        self.assertTrue(self.overview_errors())

    def test_ten_second_default_and_real_reading_hold(self):
        self.overview['presentation']['durationSeconds'] = 11
        self.assertTrue(self.overview_errors())
        self.overview['presentation']['durationSeconds'] = 9.5
        self.overview['presentation']['fullTextAtSeconds'] = 9.5
        self.assertTrue(self.overview_errors())

    def test_overview_goes_between_intro_and_body(self):
        self.overview['timeline']['bodyStart'] = 4
        self.assertTrue(self.overview_errors())

    def test_nominal_duration_cannot_differ_from_final_timeline(self):
        self.overview['timeline']['overviewEnd'] = 13
        self.assertTrue(self.overview_errors())

    def test_overview_is_text_only_without_new_voice(self):
        self.overview['presentation']['narration'] = True
        self.assertTrue(self.overview_errors())

    def test_user_may_explicitly_override_duration(self):
        self.overview['userOverride'] = {'instruction': 'Use twelve seconds for this lesson overview', 'maxSeconds': 12, 'evidence': self.ref}
        self.overview['presentation']['durationSeconds'] = 12
        self.overview['timeline'].update(overviewEnd=16, bodyStart=16)
        self.assertEqual(self.overview_errors(), [])
        del self.overview['userOverride']['evidence']
        self.assertTrue(self.overview_errors())

    def test_omission_needs_explicit_user_evidence(self):
        self.overview = {'status': 'user-omitted'}
        self.assertTrue(self.overview_errors())
        self.overview['userOverride'] = {'instruction': 'Omit the lesson overview for this excerpt', 'omitOverview': True, 'evidence': self.ref}
        self.assertEqual(self.overview_errors(), [])

    def test_old_timing_mapping_cannot_pass_current_evidence(self):
        self.overview['mappingEvidence'] = {'file': self.file.name, 'sha256': '0'*64}
        self.assertTrue(self.overview_errors())

    def test_nonfinite_or_bool_timeline_refused(self):
        for bad in (float('nan'), float('inf'), True):
            with self.subTest(value=bad):
                self.overview['timeline']['bodyStart'] = bad
                self.assertTrue(self.overview_errors())


    def test_complete_music_evidence(self):
        music={'status':'included','style':'light-electronic-instrumental-without-lyrics','sourceFile':self.ref,'rightsEvidence':self.ref,'mixReview':self.pass_record}
        self.assertEqual(q.music_checks({'courseMusic':music},self.base),[])
        music['mixReview']={'status':'pending'}
        self.assertTrue(q.music_checks({'courseMusic':music},self.base))

    def test_pending_music_and_unlicensed_source_cannot_pass(self):
        self.assertTrue(q.music_checks({'courseMusic':q.music_template()},self.base))
        music={'status':'included','style':'light-electronic-instrumental-without-lyrics','sourceFile':self.ref,'mixReview':self.pass_record}
        self.assertTrue(q.music_checks({'courseMusic':music},self.base))

    def test_music_omission_respects_explicit_user_choice(self):
        self.assertTrue(q.music_checks({'courseMusic':{'status':'user-omitted'}},self.base))
        music={'status':'user-omitted','userOverride':{'instruction':'No background music for this course','omitMusic':True,'evidence':self.ref}}
        self.assertEqual(q.music_checks({'courseMusic':music},self.base),[])


def main():
    stream = io.StringIO()
    r = unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(LessonStandard))
    print(json.dumps({'ok': r.wasSuccessful(), 'testsRun': r.testsRun,
                      'failures': [str(t)+': '+s for t,s in r.failures+r.errors],
                      'scope': 'Synthetic evidence/timing boundaries only; not real aesthetics, readability, playback or user approval.'}, ensure_ascii=False, indent=2))
    return 0 if r.wasSuccessful() else 2


if __name__ == '__main__':
    raise SystemExit(main())
