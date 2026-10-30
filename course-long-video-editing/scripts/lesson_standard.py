"""Evidence contracts for lesson packaging and the confirmed animation standard.

Checks declarations, files and timing; cannot certify perception, pedagogy or taste.
"""
from pathlib import Path
import hashlib
import math

VISUAL_CHECKS = ('canvas-clear', 'dot-parallax', 'spatial-camera', 'human-marks',
                 'logo-main-subject', 'real-materials', 'presenter-clearance')
SUMMARY_CHECKS = ('camera-variety', 'presenter-routing', 'animation-coverage')
MARK_STYLES = {'highlighter', 'marker-underline', 'marker-circle', 'hand-bracket',
               'hand-check', 'mixed', 'semantic-frame'}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def checked_file(record, base, errors, label):
    if not isinstance(record, dict) or not record.get('file'):
        errors.append(label + ': file/hash evidence missing')
        return
    path = (base / str(record['file'])).resolve()
    if not path.is_file() or digest(path) != record.get('sha256'):
        errors.append(label + ': evidence missing or changed')


def verdict(record, base, errors, label, allow_na=True):
    if not isinstance(record, dict):
        errors.append(label + ': actual review missing')
        return
    status = record.get('status')
    if status not in ({'pass', 'not-applicable'} if allow_na else {'pass'}):
        errors.append(label + ': pending/failed review')
    if not isinstance(record.get('finding'), str) or not record['finding'].strip():
        errors.append(label + ': specific finding/reason missing')
    # Both exceptions and passes need traceable current-course evidence.
    checked_file(record.get('evidence'), base, errors, label)


def animation_checks(data, base, phase):
    errors = []
    for scene in data.get('scenes', []):
        sid = str(scene.get('id'))
        design = scene.get('visualDesign') or {}
        for flag in ('fullCanvas', 'readingUnitComplete', 'foregroundCamera'):
            if design.get(flag) is not True:
                errors.append(sid + ': design must protect ' + flag)
        mode = design.get('backgroundMode')
        if mode != 'dot-parallax' and not (mode == 'source-full-frame' and design.get('backgroundReason')):
            errors.append(sid + ': visible dot-parallax plan or actual full-frame-source reason required')
        for field in ('cameraFamily', 'cameraPurpose', 'materialReason', 'presenterReason'):
            if not isinstance(design.get(field), str) or not design[field].strip():
                errors.append(sid + ': missing ' + field)
        if design.get('materialTreatment') not in {'real-source', 'authored-artifact', 'concept-diagram'}:
            errors.append(sid + ': replace placeholder materials with source/artifact or justified concept diagram')
        if design.get('presenterMode') not in {'live-circle', 'full-screen', 'none'}:
            errors.append(sid + ': explicit content-aware presenter treatment required')
        if phase == 'review':
            checks = scene.get('visualChecks') or {}
            for key in VISUAL_CHECKS:
                # These invariants apply to every animation, unlike optional logos/presenter.
                allow_na = key not in {'canvas-clear', 'spatial-camera'}
                if key == 'dot-parallax' and mode == 'dot-parallax':
                    allow_na = False
                instances = [i for i in data.get('sourceInstances', []) if i.get('sceneId') == scene.get('id') and i.get('sourceAvailable') is not False]
                if key == 'human-marks' and any(i.get('useKind') == 'reading' for i in instances):
                    allow_na = False
                if key == 'logo-main-subject' and any(i.get('useKind') == 'identity' for i in instances):
                    allow_na = False
                if key == 'real-materials' and design.get('materialTreatment') in {'real-source','authored-artifact'}:
                    allow_na = False
                if key == 'presenter-clearance' and design.get('presenterMode') != 'none':
                    allow_na = False
                verdict(checks.get(key), base, errors, sid + '/' + key, allow_na)
    for item in data.get('sourceInstances', []):
        label = str(item.get('id'))
        if item.get('sourceAvailable') is False:
            continue  # Existing workflow gate requires the honest limitation.
        kind = item.get('useKind')
        if kind == 'identity':
            if item.get('identityPlacement') != 'main-subject':
                errors.append(label + ': introduce the logo/identity as a main composition subject')
        elif kind == 'reading':
            if item.get('annotationStyle') not in MARK_STYLES:
                errors.append(label + ': human-like source annotation style missing')
            if item.get('coordinateSpace') != 'source-pixels':
                errors.append(label + ': annotations must share source coordinates')
            if item.get('annotationStyle') == 'semantic-frame' and not item.get('annotationReason'):
                errors.append(label + ': a geometric frame requires a semantic reason')
        else:
            errors.append(label + ': useKind must be reading or identity')
        artifact = item.get('authoredArtifact')
        if item.get('materialOrigin') == 'self-authored' and not artifact:
            errors.append(label + ': self-authored example needs actual document and render')
        if artifact:
            if artifact.get('label') != 'self-authored-teaching-example':
                errors.append(label + ': label authored artifacts honestly')
            for key in ('editableSource', 'documentFile', 'renderedImage'):
                checked_file(artifact.get(key), base, errors, label + '/' + key)
    # Every claimed authored-artifact scene must contain the actual corresponding files.
    for scene in data.get('scenes', []):
        if (scene.get('visualDesign') or {}).get('materialTreatment') == 'authored-artifact':
            if not any(i.get('sceneId') == scene.get('id') and i.get('authoredArtifact')
                       for i in data.get('sourceInstances', [])):
                errors.append(str(scene.get('id')) + ': authored-artifact scene has no actual artifact instance')
    if phase == 'review':
        summary = data.get('visualSummary') or {}
        for key in SUMMARY_CHECKS:
            verdict(summary.get(key), base, errors, 'whole-lesson/' + key,
                    allow_na=(key == 'presenter-routing'))
        families = {(s.get('visualDesign') or {}).get('cameraFamily') for s in data.get('scenes', [])}
        if len(data.get('scenes', [])) > 2 and len(families) == 1 and not summary.get('repetitionRationale'):
            errors.append('All camera families repeat: vary the authored design or document the actual teaching reason')
    return errors


def overview_template():
    return {
        'status': 'pending',
        'contentSummary': [], 'learningObjectives': [], 'displayText': '',
        'basis': [],
        'presentation': {'durationSeconds': None, 'fullTextAtSeconds': None,
                         'animatedBackground': True, 'typewriter': True, 'soundEffect': True,
                         'narration': False, 'presenter': False, 'extraFootage': False},
        'timeline': {'introEnd': None, 'overviewStart': None, 'overviewEnd': None,
                     'bodyStart': None, 'bodyEnd': None, 'outroStart': None},
        'contentReview': None, 'readabilityReview': None, 'timingReview': None,
        'mappingEvidence': None, 'userOverride': None,
        'note': 'Write this lesson content and observable learning goals, not an AI-production disclaimer. Actual timing and current output evidence required.'}


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def overview_checks(data, base):
    errors = []
    overview = data.get('lessonOverview') or {}
    override = overview.get('userOverride') or {}
    if override:
        if not isinstance(override.get('instruction'), str) or not override['instruction'].strip():
            errors.append('Lesson overview override needs the actual user instruction')
        checked_file(override.get('evidence'), base, errors, 'overview/user-override')
    if overview.get('status') == 'user-omitted':
        if override.get('omitOverview') is not True:
            errors.append('Only an explicit current user omission can skip the lesson overview')
        if not override:
            errors.append('Lesson overview omission lacks user evidence')
        return errors
    if overview.get('status') != 'included':
        errors.append('Every complete lesson needs the content/learning-objectives overview; pending is incomplete')
    for key in ('contentSummary', 'learningObjectives'):
        values = overview.get(key)
        if not isinstance(values, list) or not values or any(not isinstance(s, str) or not s.strip() for s in values):
            errors.append('Lesson overview needs specific ' + key)
    if not isinstance(overview.get('displayText'), str) or not overview['displayText'].strip():
        errors.append('Actual overview display text missing')
    if not isinstance(overview.get('basis'), list) or not overview['basis']:
        errors.append('Overview must cite the actual lesson content/subtitles')
    else:
        for row in overview['basis']:
            checked_file(row, base, errors, 'overview/content-basis')
    presentation = overview.get('presentation') or {}
    duration, reveal = presentation.get('durationSeconds'), presentation.get('fullTextAtSeconds')
    maximum = override.get('maxSeconds', 10)
    if not finite(maximum) or maximum <= 0:
        errors.append('Overview duration override invalid')
        maximum = 10
    if not finite(duration) or not 0 < duration <= maximum:
        errors.append('Overview exceeds the default ten seconds or declared current user duration')
    if not finite(reveal) or not finite(duration) or not 0 < reveal < duration:
        errors.append('Overview must finish revealing text before its reading hold ends')
    expected = {'animatedBackground': True, 'typewriter': True, 'soundEffect': True,
                'narration': False, 'presenter': False, 'extraFootage': False}
    for key, default in expected.items():
        actual_expected = (override.get('presentation') or {}).get(key, default)
        if presentation.get(key) is not actual_expected:
            errors.append('Overview presentation differs from the default/current instruction: ' + key)
    t = overview.get('timeline') or {}
    required = ('introEnd', 'overviewStart', 'overviewEnd', 'bodyStart', 'bodyEnd', 'outroStart')
    if any(not finite(t.get(key)) or t[key] < 0 for key in required):
        errors.append('Overview/final lesson timeline missing or nonfinite')
    else:
        if not (t['introEnd'] <= t['overviewStart'] < t['overviewEnd'] <= t['bodyStart'] < t['bodyEnd'] <= t['outroStart']):
            errors.append('Expected intro -> lesson overview -> body -> outro order')
        if finite(duration) and abs((t['overviewEnd'] - t['overviewStart']) - duration) > 0.001:
            errors.append('Overview duration and final timeline disagree')
    for key in ('contentReview', 'readabilityReview', 'timingReview'):
        verdict(overview.get(key), base, errors, 'overview/' + key, allow_na=False)
    checked_file(overview.get('mappingEvidence'), base, errors, 'overview/source-to-final-mapping')
    return errors


def music_template():
    return {'status': 'pending', 'style': 'light-electronic-instrumental-without-lyrics',
            'sourceFile': None, 'rightsEvidence': None, 'mixReview': None, 'userOverride': None}


def music_checks(data, base):
    errors = []
    music = data.get('courseMusic') or {}
    override = music.get('userOverride') or {}
    if override:
        if not override.get('instruction'):
            errors.append('Music override needs the actual current user instruction')
        checked_file(override.get('evidence'), base, errors, 'music/user-override')
    if music.get('status') == 'user-omitted':
        if override.get('omitMusic') is not True:
            errors.append('Music omission needs an explicit current user instruction')
        return errors
    if music.get('status') != 'included':
        errors.append('Complete lesson needs the default instrumental music or an explicit user omission')
    if music.get('style') != override.get('style', 'light-electronic-instrumental-without-lyrics'):
        errors.append('Course music must follow the confirmed instrumental style/current instruction')
    checked_file(music.get('sourceFile'), base, errors, 'music/source-file')
    checked_file(music.get('rightsEvidence'), base, errors, 'music/usage-rights')
    verdict(music.get('mixReview'), base, errors, 'music/actual-ducking-and-listening', allow_na=False)
    return errors
