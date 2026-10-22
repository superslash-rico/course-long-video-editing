"""Install this complete package into a chosen Codex skill root; never overwrite another version."""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from verify_package import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-root', type=Path, help='Skill directory, not the individual skill folder')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    result = verify(source)
    if not result['ok']:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    target_root = (args.target_root or Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills').expanduser().resolve()
    target = target_root / 'course-long-video-editing'
    if target == source or source in target.parents:
        print(json.dumps({'ok': False, 'error': 'Target must be outside the source package.'}))
        return 2
    if target.exists():
        existing = verify(target)
        identical = existing['ok'] and (target / 'assets/manifest.json').read_bytes() == (source / 'assets/manifest.json').read_bytes()
        print(json.dumps({'ok': identical, 'state': 'already-installed-identical' if identical else 'existing-version-kept-no-overwrite', 'target': str(target)}, ensure_ascii=False, indent=2))
        return 0 if identical else 2
    if args.dry_run:
        print(json.dumps({'ok': True, 'state': 'dry-run-no-write', 'target': str(target)}, ensure_ascii=False, indent=2))
        return 0
    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store', '.git', '*.pyc'))
    installed = verify(target)
    print(json.dumps({'ok': installed['ok'], 'state': 'installed-files-verified', 'target': str(target), 'skillDiscoveryInNewSession': 'requires-current-session-confirmation', 'errors': installed['errors']}, ensure_ascii=False, indent=2))
    return 0 if installed['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
