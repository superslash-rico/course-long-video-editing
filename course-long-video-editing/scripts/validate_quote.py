"""Check actual final quote lines and UTF-16 cue ranges before native import. Read-only."""
import argparse
import json
import math
from pathlib import Path


def utf16_boundaries(text):
    boundaries = {0}
    index = 0
    for char in text:
        index += len(char.encode('utf-16-le')) // 2
        boundaries.add(index)
    return index, boundaries


def validate(values):
    errors = []
    if not isinstance(values, dict):
        return ['values must be an object']
    text = values.get('text')
    duration = values.get('seconds')
    numeric = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
    if not isinstance(text, str) or not text:
        return ['text must be nonempty final text']
    if not numeric(duration) or duration <= 0:
        return ['seconds must be a positive finite number']
    cues = values.get('cues', [])
    try:
        cues = json.loads(cues) if isinstance(cues, str) else cues
    except (ValueError, TypeError):
        return ['cues must be valid JSON']
    if not isinstance(cues, list) or not cues:
        return ['cues must be a nonempty array; fallback does not pass']
    lines = text.split('\n')
    if any(not line.strip() for line in lines):
        errors.append('blank final lines cause fallback; use intentional nonempty lines')
    valid = []
    for i, cue in enumerate(cues):
        if not isinstance(cue, dict):
            errors.append(f'cue {i} must be an object')
            continue
        row, start, end = cue.get('row'), cue.get('start'), cue.get('end')
        left, right = cue.get('from'), cue.get('to')
        integer = lambda x: isinstance(x, int) and not isinstance(x, bool)
        if not integer(row) or not 0 <= row < len(lines):
            errors.append(f'cue {i}: invalid row')
            continue
        length, boundaries = utf16_boundaries(lines[row])
        if not integer(left) or not integer(right) or not 0 <= left < right <= length:
            errors.append(f'cue {i}: invalid UTF-16 half-open range')
            continue
        if left not in boundaries or right not in boundaries:
            errors.append(f'cue {i}: range splits a surrogate pair')
        if not numeric(start) or not numeric(end) or not 0 <= start < end <= duration:
            errors.append(f'cue {i}: invalid finite local-second span')
            continue
        valid.append(cue)
    ordered = []
    for row, text in enumerate(lines):
        row_cues = sorted((c for c in valid if c['row'] == row), key=lambda c: c['from'])
        length, _ = utf16_boundaries(text)
        next_index = 0
        for cue in row_cues:
            if cue['from'] != next_index:
                errors.append(f'row {row}: gap or overlap at UTF-16 index {next_index}')
            next_index = cue['to']
            ordered.append(cue)
        if not row_cues or next_index != length:
            errors.append(f'row {row}: final text is not completely covered')
    for previous, current in zip(ordered, ordered[1:]):
        if current['start'] + 1e-8 < previous['end']:
            errors.append('cue speech order overlaps or reverses across final text')
    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('values', type=Path, help='JSON defaults/instance values containing text,cues,seconds')
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.values.read_text(encoding='utf-8')))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({'ok': not errors, 'errors': errors, 'scope': 'Cue structure/time/UTF-16 coverage only; real speech sync and native visual quality require review.'}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
