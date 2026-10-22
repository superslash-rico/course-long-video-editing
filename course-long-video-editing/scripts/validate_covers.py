"""Read-only PNG container/dimension checks for the three course cover exports."""
import argparse
import binascii
import json
import struct
from pathlib import Path

EXPECTED = {'cover-4x3.png': (4, 3), 'cover-3x4.png': (3, 4), 'cover-16x9.png': (16, 9)}
SIGNATURE = b'\x89PNG\r\n\x1a\n'


def dimensions(path):
    if path.is_symlink():
        raise ValueError('cover must be an ordinary file, not a symlink')
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('cover exceeds this checker\'s 64 MiB limit; inspect with a decoder')
    data = path.read_bytes()
    if not data.startswith(SIGNATURE):
        raise ValueError('not a PNG file')
    cursor, size, saw_idat, saw_end = 8, None, False, False
    while cursor < len(data):
        if len(data) - cursor < 12:
            raise ValueError('truncated PNG chunk')
        length = struct.unpack_from('>I', data, cursor)[0]
        tag = data[cursor + 4:cursor + 8]
        end = cursor + 12 + length
        if end > len(data):
            raise ValueError('truncated PNG payload')
        payload = data[cursor + 8:cursor + 8 + length]
        stored_crc = struct.unpack_from('>I', data, cursor + 8 + length)[0]
        if binascii.crc32(tag + payload) & 0xffffffff != stored_crc:
            raise ValueError('PNG chunk CRC mismatch')
        if cursor == 8 and tag != b'IHDR':
            raise ValueError('IHDR must be the first chunk')
        if tag == b'IHDR':
            if size is not None or length != 13:
                raise ValueError('invalid or duplicate IHDR')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
            if not width or not height or depth not in valid_depths.get(color, set()) or compression or filtering or interlace not in {0, 1}:
                raise ValueError('invalid PNG dimensions or IHDR format')
            size = (width, height)
        elif tag == b'IDAT':
            saw_idat = True
        elif tag == b'IEND':
            if length != 0 or end != len(data):
                raise ValueError('invalid IEND or trailing data')
            saw_end = True
        cursor = end
    if size is None or not saw_idat or not saw_end:
        raise ValueError('PNG requires IHDR, IDAT and IEND')
    return size


def validate(directory):
    errors, files = [], []
    for name, (a, b) in EXPECTED.items():
        path = directory / name
        try:
            width, height = dimensions(path)
            if width * b != height * a:
                raise ValueError(f'expected {a}:{b}, got {width}x{height}')
            files.append({'file': name, 'width': width, 'height': height, 'ratio': f'{a}:{b}'})
        except (OSError, ValueError, struct.error) as exc:
            errors.append(f'{name}: {exc}')
    return {'ok': not errors, 'files': files, 'errors': errors, 'scope': 'PNG signature/IHDR/chunk CRC/IDAT/IEND and aspect ratios only; not complete pixel decoding, text, visual style or aesthetic acceptance.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    result = validate(parser.parse_args().directory.expanduser())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
