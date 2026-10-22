"""Preview or rebuild the Skill inventory, preserving existing resource rights/status."""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath

REQUIRED_METADATA = ('role', 'rights', 'status')
PRIVATE_NAMES = {'.git', '.env', 'auth.json', 'node_modules', '.DS_Store'}


def relative_name(value):
    if not isinstance(value, str) or not value or '\\' in value or PureWindowsPath(value).drive:
        raise ValueError('metadata path must be a portable relative name')
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != value:
        raise ValueError('metadata path must stay inside the Skill')
    return value


def build(root, additions, allow_remove=False):
    root = root.resolve()
    manifest_path = root / 'assets/manifest.json'
    for path in (manifest_path, root / 'PACKAGE.json'):
        path.resolve().relative_to(root)
        if path.is_symlink():
            raise ValueError('manifest and package metadata must be ordinary files')
    previous = json.loads(manifest_path.read_text(encoding='utf-8'))
    package = json.loads((root / 'PACKAGE.json').read_text(encoding='utf-8'))
    if not isinstance(previous, dict) or not isinstance(previous.get('files'), list) or not isinstance(additions, list):
        raise ValueError('manifest must have files array; added metadata must be an array')
    known = {}
    for row in previous['files']:
        if not isinstance(row, dict):
            raise ValueError('invalid existing metadata record')
        name = relative_name(row.get('path'))
        if name in known:
            raise ValueError('duplicate existing resource path')
        known[name] = row
    extra = {}
    for row in additions:
        if not isinstance(row, dict):
            raise ValueError('invalid added metadata record')
        name = relative_name(row.get('path'))
        if name in extra or any(not isinstance(row.get(k), str) or not row[k].strip() for k in REQUIRED_METADATA):
            raise ValueError('duplicate or incomplete added resource metadata')
        extra[name] = row
    actual = {}
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if '__pycache__' in rel.parts:
            continue
        if path.is_symlink() or any(part in PRIVATE_NAMES or part.startswith('.env.') for part in rel.parts):
            raise ValueError(f'private/nonportable entry: {rel.as_posix()}')
        if path.is_file() and path != manifest_path:
            actual[rel.as_posix()] = path
    if set(extra) - set(actual):
        raise ValueError('added metadata references files absent from this Skill')
    removed = sorted(set(known) - set(actual))
    if removed and not allow_remove:
        raise ValueError('files missing from previous inventory; restore them or explicitly pass --allow-remove')
    records = []
    for name, path in sorted(actual.items()):
        row = {**known.get(name, {}), **extra.get(name, {})}
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in REQUIRED_METADATA):
            raise ValueError(f'explicit role/rights/status required for new file: {name}')
        data = path.read_bytes()
        row.update(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        records.append(row)
    result = {**previous, 'version': package['version'], 'files': records}
    return result, {'version': package['version'], 'files': len(records), 'added': sorted(set(actual) - set(known)), 'removed': removed, 'metadataUpdated': sorted(extra)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--metadata', type=Path)
    parser.add_argument('--allow-remove', action='store_true')
    parser.add_argument('--write', action='store_true', help='Write manifest; default is a read-only preview')
    args = parser.parse_args()
    try:
        additions = json.loads(args.metadata.read_text(encoding='utf-8')) if args.metadata else []
        manifest, summary = build(args.skill_root, additions, args.allow_remove)
        if args.write:
            (args.skill_root / 'assets/manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'ok': True, 'mode': 'written' if args.write else 'read-only-preview', **summary, 'scope': 'Inventory/hash update only; content, privacy, rights and native quality require review.'}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
