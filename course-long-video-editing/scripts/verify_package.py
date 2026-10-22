"""Verify portable package closure, manifests and common accidental private data. Read-only."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from urllib.parse import unquote, urlsplit

TEXT = {'.md', '.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml', '.html', '.css', '.txt'}


def verify_fonts(root):
    """Check the explicitly supplied original fonts without installing or modifying them."""
    root = root.resolve()
    errors, allowed = [], set()
    font_root = root / 'assets/fonts'
    try:
        font_root.resolve().relative_to(root)
        spec_path = font_root / 'requirements.json'
        spec_path.resolve().relative_to(root)
        if spec_path.is_symlink():
            raise ValueError('font inventory must not be a symlink')
        spec = json.loads(spec_path.read_text(encoding='utf-8'))
        if not isinstance(spec, dict):
            raise ValueError('font inventory must be a JSON object')
        if spec.get('fontBinariesIncluded') is not True or not spec.get('files'):
            raise ValueError('bundled original font inventory is required')
        for record in spec['files'] + [spec['license']]:
            name = record['file']
            if not isinstance(name, str) or Path(name).name != name or '\\' in name:
                raise ValueError('font inventory requires a plain file name')
            path = font_root / name
            path.resolve().relative_to(root)
            if path.is_symlink():
                raise ValueError(f'font/license must not be a symlink: {name}')
            data = path.read_bytes()
            if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
                errors.append(f'original font/license hash mismatch: {name}')
            if record is spec['license']:
                if not data.startswith(b'%PDF'):
                    errors.append('font license is not a PDF')
                continue
            rel = path.relative_to(root).as_posix()
            if rel in allowed or path.suffix != '.ttf':
                raise ValueError('duplicate or unsupported bundled font')
            allowed.add(rel)
            if data[:4] != b'\x00\x01\x00\x00':
                raise ValueError(f'not an original TrueType sfnt: {name}')
            count = struct.unpack_from('>H', data, 4)[0]
            tables = {struct.unpack_from('>4sIII', data, 12 + i * 16)[0]:
                      struct.unpack_from('>4sIII', data, 12 + i * 16)[2]
                      for i in range(count)}
            offset = tables[b'OS/2']
            weight, _, fs_type = struct.unpack_from('>HHH', data, offset + 4)
            if weight != record['weight'] or fs_type != record['fsType']:
                errors.append(f'font weight/embedding metadata mismatch: {name}')
    except (OSError, ValueError, KeyError, TypeError, struct.error) as exc:
        errors.append(f'font inventory/license check failed: {exc}')
    return allowed, errors


def verify(root):
    root = root.resolve()
    errors, warnings = [], []
    allowed_fonts, font_errors = verify_fonts(root)
    errors.extend(font_errors)
    files = sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for path in root.rglob('*'):
        if path.is_symlink():
            errors.append(f'symlink not portable: {path.relative_to(root)}')
        if path.name in {'.DS_Store', '.env', 'auth.json', '.git', 'node_modules'}:
            errors.append(f'private/unneeded entry: {path.relative_to(root)}')
    manifest_path = root / 'assets/manifest.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return {'ok': False, 'errors': [f'manifest: {exc}'], 'warnings': []}
    if not isinstance(manifest, dict) or not isinstance(manifest.get('files'), list):
        return {'ok': False, 'errors': ['manifest files must be an array in an object'], 'warnings': []}
    declared = {}
    for record in manifest.get('files', []):
        if not isinstance(record, dict) or not isinstance(record.get('path'), str):
            errors.append('manifest file record must have a string path')
            continue
        name = record.get('path', '')
        candidate = root / name
        try:
            resolved = candidate.resolve()
            resolved.relative_to(root)
            if not name or Path(name).is_absolute() or '\\' in name:
                raise ValueError('not a portable relative path')
        except ValueError:
            errors.append(f'unsafe manifest path: {name}')
            continue
        if name in declared:
            errors.append(f'duplicate manifest path: {name}')
        declared[name] = record
        if not candidate.is_file():
            errors.append(f'missing: {name}')
            continue
        data = candidate.read_bytes()
        if hashlib.sha256(data).hexdigest() != record.get('sha256') or len(data) != record.get('bytes'):
            errors.append(f'content/hash/size mismatch: {name}')
        if not record.get('role') or not record.get('rights') or not record.get('status'):
            errors.append(f'role/rights/status missing: {name}')
    for path in files:
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            continue
        try:
            path.resolve().relative_to(root)
        except ValueError:
            errors.append(f'file resolves outside package: {rel}')
            continue
        if path != manifest_path and rel not in declared:
            errors.append(f'file not inventoried: {rel}')
        if path.suffix.lower() in {'.ttf', '.otf', '.woff', '.woff2'}:
            if rel not in allowed_fonts:
                errors.append(f'font binary not in original font inventory: {rel}')
        if path.suffix not in TEXT:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            errors.append(f'not UTF-8: {rel}')
            continue
        # Literal original-machine references and project UUIDs do not travel.
        if re.search(r'/Users/[A-Za-z0-9._-]+/|' + r'/private/' + r'tmp/chatcut|[A-Za-z]:\\(?:Users|codex)\\', text):
            errors.append(f'original-machine absolute path: {rel}')
        if re.search(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b', text, re.I):
            errors.append(f'project UUID copied: {rel}')
        if re.search(r'\bsk-[A-Za-z0-9_-]{24,}\b|\bAKIA[A-Z0-9]{16}\b|\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.', text):
            errors.append(f'possible credential: {rel}')
        if path.suffix == '.json':
            try:
                json.loads(text)
            except ValueError as exc:
                errors.append(f'invalid JSON: {rel}: {exc}')
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text):
                if target.startswith(('#', 'http:', 'https:', 'mailto:', 'app:')):
                    continue
                target = unquote(urlsplit(target.strip('<>')).path)
                candidate = (path.parent / target).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    errors.append(f'Markdown link escapes package: {rel}: {target}')
                    continue
                if not candidate.exists():
                    errors.append(f'broken Markdown link: {rel}: {target}')
        if path.suffix in {'.js', '.ts', '.tsx', '.jsx', '.html'}:
            imports = re.findall(r'(?:from\s+|import\s*)[\'"]([^\'"]+)[\'"]', text)
            imports += re.findall(r'(?:src|href)=[\'"](\.[^\'"]+)[\'"]', text)
            for target in imports:
                if target.startswith(('http:', 'https:', 'file:')):
                    errors.append(f'remote/absolute runtime dependency: {rel}: {target}')
                if not target.startswith('.'):
                    continue
                candidate = (path.parent / target).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    errors.append(f'local import escapes package: {rel}: {target}')
                    continue
                options = [candidate] + [Path(str(candidate) + x) for x in ['.ts', '.tsx', '.js', '.jsx', '.json']] + [candidate / ('index' + x) for x in ['.ts', '.tsx', '.js']]
                if not any(p.is_file() for p in options):
                    errors.append(f'missing relative runtime dependency: {rel}: {target}')
    for path in root.rglob('resource.json'):
        try:
            resource = json.loads(path.read_text(encoding='utf-8'))
            entry = (path.parent / resource['entry']).resolve()
            entry.relative_to(root)
            if not entry.is_file():
                errors.append(f'missing resource entry: {path.relative_to(root)}')
            if resource.get('type') == 'research-only':
                warnings.append(f'research-only source is NOT production ready: {path.parent.relative_to(root)}')
            properties_path, defaults_path = path.parent / 'properties.json', path.parent / 'defaults.json'
            if properties_path.exists() and defaults_path.exists():
                schema, defaults = json.loads(properties_path.read_text()), json.loads(defaults_path.read_text())
                if {x['key']: x['defaultValue'] for x in schema} != defaults:
                    errors.append(f'schema/default mismatch: {path.parent.relative_to(root)}')
        except (KeyError, ValueError, OSError) as exc:
            errors.append(f'invalid resource metadata: {path.relative_to(root)}: {exc}')
    try:
        from validate_quote import validate
        quote = json.loads((root / 'assets/templates/quote-highlight-follow/defaults.json').read_text())
        errors.extend('quote defaults: ' + issue for issue in validate(quote))
    except (ImportError, OSError, ValueError) as exc:
        errors.append(f'quote defaults check unavailable: {exc}')
    warnings.extend(['Original MiSans font files and license are bundled; receiver registration and actual native rendering remain unverified.', 'Static checks do not prove native rendering, audibility, aesthetic quality or cross-machine success.'])
    return {'ok': not errors, 'filesChecked': len(files), 'inventoried': len(declared), 'errors': sorted(set(errors)), 'warnings': sorted(set(warnings))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = verify(args.skill_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
