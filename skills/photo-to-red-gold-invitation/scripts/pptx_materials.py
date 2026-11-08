#!/usr/bin/env python3
"""Inspect or fill selected native PPT objects, without changing original media."""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import posixpath
import re
import struct
import sys
import zlib
from urllib.parse import unquote
from zipfile import ZipFile

from lxml import etree as E

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
IMAGE_REL = NS['r'] + '/image'
FILL_TAGS = {f'{{{NS["a"]}}}{x}' for x in ('noFill', 'solidFill', 'gradFill', 'blipFill', 'pattFill', 'grpFill')}
SKILL_DIR = Path(__file__).resolve().parents[1]


def parse(data):
    return E.fromstring(data, E.XMLParser(resolve_entities=False, no_network=True))


def encoded(root):
    return E.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def private_output(value):
    path = Path(value).resolve()
    if path.is_relative_to(SKILL_DIR):
        raise ValueError('Runtime output must be outside the skill installation.')
    if path.exists():
        raise ValueError('Output already exists; choose a new filename or directory.')
    for parent in path.parents:
        if parent.exists():
            if not parent.is_dir():
                raise ValueError('An output parent is a file, not a directory.')
            break
    return path


def package(path):
    data = Path(path).read_bytes()
    with ZipFile(io.BytesIO(data)) as z:
        infos = z.infolist()
        if len({x.filename for x in infos}) != len(infos):
            raise ValueError('Duplicate package entries are unsupported.')
        items = {x.filename: z.read(x.filename) for x in infos}
    if 'ppt/presentation.xml' not in items:
        raise ValueError('Input is not a PowerPoint OOXML presentation.')
    return data, infos, items


def slides(items):
    pres = parse(items['ppt/presentation.xml'])
    rels = parse(items['ppt/_rels/presentation.xml.rels'])
    targets = {x.get('Id'): x for x in rels}
    result = []
    for node in pres.findall('p:sldIdLst/p:sldId', NS):
        rel = targets[node.get(f'{{{NS["r"]}}}id')]
        if rel.get('TargetMode') == 'External':
            raise ValueError('External slides are unsupported.')
        target = unquote(rel.get('Target'))
        part = target.lstrip('/') if target.startswith('/') else posixpath.normpath('ppt/' + target)
        if part not in items:
            raise ValueError('A slide relationship does not resolve.')
        result.append(part)
    return result


def shape_by_id(root, value):
    result = []
    for node in root.xpath('//p:sp|//p:pic', namespaces=NS):
        ids = node.xpath('./p:nvSpPr/p:cNvPr/@id|./p:nvPicPr/p:cNvPr/@id', namespaces=NS)
        if ids == [str(value)]:
            result.append(node)
    if len(result) != 1:
        raise ValueError('A target shape ID is missing or not unique on its slide.')
    return result[0]


def inspect(path):
    _, _, items = package(path)
    result = []
    for number, part in enumerate(slides(items), 1):
        root = parse(items[part])
        objects = []
        for node in root.xpath('//p:sp|//p:pic', namespaces=NS):
            ids = node.xpath('./p:nvSpPr/p:cNvPr/@id|./p:nvPicPr/p:cNvPr/@id', namespaces=NS)
            xfrm = node.find('p:spPr/a:xfrm', NS)
            box = None
            if xfrm is not None:
                off, ext = xfrm.find('a:off', NS), xfrm.find('a:ext', NS)
                if off is not None and ext is not None:
                    box = {**dict(off.attrib), **dict(ext.attrib)}
            objects.append({'shape_id': ids[0], 'kind': E.QName(node).localname,
                            'box_emu': box, 'paragraphs': len(node.findall('p:txBody/a:p', NS)),
                            'vector_outline': node.find('p:spPr/a:custGeom', NS) is not None})
        result.append({'slide': number, 'objects': objects})
    return {'slides': result}


def png_material(config, base, items):
    path = Path(config['path'])
    data = (path if path.is_absolute() else base / path).read_bytes()
    if not data.startswith(b'\x89PNG\r\n\x1a\n') or len(data) < 33 or data[12:16] != b'IHDR':
        raise ValueError('Material must be a PNG image.')
    offset, chunks, image_data, finished = 8, 0, False, False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('Material PNG is truncated.')
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            raise ValueError('Material PNG is truncated.')
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        crc = struct.unpack('>I', data[offset + 8 + length:end])[0]
        if not re.fullmatch(b'[A-Za-z]{4}', kind) or zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError('Material PNG has an invalid chunk or CRC.')
        if chunks == 0 and (kind != b'IHDR' or length != 13):
            raise ValueError('Material PNG has an invalid header.')
        if kind == b'IHDR' and chunks != 0:
            raise ValueError('Material PNG has repeated headers.')
        if kind == b'IDAT':
            image_data = True
        if kind == b'IEND':
            if length != 0 or not image_data or end != len(data):
                raise ValueError('Material PNG has an invalid end marker.')
            finished = True
            break
        chunks += 1
        offset = end
    if not finished:
        raise ValueError('Material PNG is missing image data or an end marker.')
    width, height = struct.unpack('>II', data[16:24])
    depth, color, compression, filtering, interlace = data[24:29]
    depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
    if not width or not height or depth not in depths.get(color, set()) or compression != 0 or filtering != 0 or interlace not in (0, 1):
        raise ValueError('Material has invalid dimensions.')
    part = 'ppt/media/invitation-material-' + sha(data)[:20] + '.png'
    if part in items and items[part] != data:
        raise ValueError('Material part collision.')
    items[part] = data
    return part, width / height


def relationship(part, image_part, items, rel_roots):
    rel_part = posixpath.dirname(part) + '/_rels/' + posixpath.basename(part) + '.rels'
    if rel_part not in rel_roots:
        rel_roots[rel_part] = parse(items[rel_part]) if rel_part in items else E.Element(f'{{{REL}}}Relationships', nsmap={None: REL})
    root = rel_roots[rel_part]
    target = posixpath.relpath(image_part, posixpath.dirname(part))
    for node in root:
        if node.get('Type') == IMAGE_REL and node.get('Target') == target:
            return node.get('Id')
    used = {x.get('Id') for x in root}
    count = 1
    while f'rIdMaterial{count}' in used:
        count += 1
    rid = f'rIdMaterial{count}'
    E.SubElement(root, f'{{{REL}}}Relationship', Id=rid, Type=IMAGE_REL, Target=target)
    return rid


def without_fills(root, targets):
    clean = copy.deepcopy(root)
    for kind, target in targets:
        node = shape_by_id(clean, target['shape_id'])
        if kind == 'paper':
            node.find('p:blipFill/a:blip', NS).set(f'{{{NS["r"]}}}embed', 'material')
        elif kind == 'gold':
            props = node.find('p:spPr', NS)
            for child in list(props):
                if child.tag in FILL_TAGS:
                    props.remove(child)
        else:
            for props in node.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr', namespaces=NS):
                for child in list(props):
                    if child.tag in FILL_TAGS:
                        props.remove(child)
                if len(props) == 0 and not props.attrib and props.getparent() is not None:
                    props.getparent().remove(props)
    return E.tostring(clean, method='c14n')


def apply(source, config_path, output, report):
    output = private_output(output)
    report = private_output(report) if report else None
    if report == output:
        raise ValueError('Report and PPT must have separate paths.')
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text(encoding='utf-8-sig'))
    if set(config) - {'paper', 'gold', 'text', 'disable_picture_compression'}:
        raise ValueError('Unknown configuration keys.')
    data, infos, original = package(source)
    items = dict(original)
    order = slides(items)
    roots, before, per_slide, rel_roots = {}, {}, {}, {}
    changed_targets = []
    for kind in ('paper', 'gold', 'text'):
        if kind not in config:
            continue
        options = config[kind]
        targets = options.get('targets', [])
        if not targets:
            raise ValueError('Every selected operation needs explicit targets.')
        image_part, ratio = png_material(options, config_path.parent, items) if kind != 'text' else (None, None)
        color = options.get('color', '')
        if kind == 'text' and not re.fullmatch(r'[0-9A-Fa-f]{6}', color):
            raise ValueError('Text color must be a six-digit RGB hex string.')
        seen = set()
        for target in targets:
            number, sid = target['slide'], str(target['shape_id'])
            if type(number) is not int or not 1 <= number <= len(order):
                raise ValueError('Target slide is out of range.')
            if (number, sid) in seen:
                raise ValueError('Repeated target in the same operation.')
            seen.add((number, sid))
            part = order[number - 1]
            if part not in roots:
                roots[part] = parse(items[part])
                before[part] = copy.deepcopy(roots[part])
            node = shape_by_id(roots[part], sid)
            if kind == 'paper':
                blip = node.find('p:blipFill/a:blip', NS)
                if E.QName(node).localname != 'pic' or blip is None:
                    raise ValueError('Paper target must be a native picture.')
                blip.set(f'{{{NS["r"]}}}embed', relationship(part, image_part, items, rel_roots))
            elif kind == 'gold':
                props = node.find('p:spPr', NS)
                ext = props.find('a:xfrm/a:ext', NS) if props is not None else None
                geometry = props.find('a:custGeom', NS) if props is not None else None
                if geometry is None and props is not None:
                    geometry = props.find('a:prstGeom', NS)
                if E.QName(node).localname != 'sp' or geometry is None or ext is None or node.xpath('.//a:t', namespaces=NS):
                    raise ValueError('Gold target must be an outline shape, not a text box or picture.')
                width, height = int(ext.get('cx')), int(ext.get('cy'))
                if min(width, height) <= 0:
                    raise ValueError('Gold target has an empty frame.')
                indexes = [i for i, x in enumerate(props) if x.tag in FILL_TAGS]
                index = indexes[0] if indexes else list(props).index(geometry) + 1
                for child in list(props):
                    if child.tag in FILL_TAGS:
                        props.remove(child)
                fill = E.Element(f'{{{NS["a"]}}}blipFill', rotWithShape='1')
                E.SubElement(fill, f'{{{NS["a"]}}}blip', {f'{{{NS["r"]}}}embed': relationship(part, image_part, items, rel_roots)})
                crop = E.SubElement(fill, f'{{{NS["a"]}}}srcRect')
                target_ratio = width / height
                if ratio > target_ratio:
                    edge = str(round((1 - target_ratio / ratio) * 50000))
                    crop.set('l', edge); crop.set('r', edge)
                else:
                    edge = str(round((1 - ratio / target_ratio) * 50000))
                    crop.set('t', edge); crop.set('b', edge)
                E.SubElement(E.SubElement(fill, f'{{{NS["a"]}}}stretch'), f'{{{NS["a"]}}}fillRect')
                props.insert(index, fill)
            else:
                body = node.find('p:txBody', NS)
                if body is None or not body.xpath('.//a:t', namespaces=NS):
                    raise ValueError('Text target must contain native editable text.')
                for run in body.xpath('.//a:r|.//a:fld', namespaces=NS):
                    if run.find('a:rPr', NS) is None:
                        run.insert(0, E.Element(f'{{{NS["a"]}}}rPr'))
                for props in body.xpath('.//a:rPr|.//a:defRPr|.//a:endParaRPr', namespaces=NS):
                    indexes = [i for i, x in enumerate(props) if x.tag in FILL_TAGS]
                    index = indexes[0] if indexes else next((i for i, x in enumerate(props) if E.QName(x).localname != 'ln'), len(props))
                    for child in list(props):
                        if child.tag in FILL_TAGS:
                            props.remove(child)
                    fill = E.Element(f'{{{NS["a"]}}}solidFill')
                    E.SubElement(fill, f'{{{NS["a"]}}}srgbClr', val=color.upper())
                    props.insert(index, fill)
            per_slide.setdefault(part, []).append((kind, target))
            changed_targets.append({'slide': number, 'shape_id': sid, 'operation': kind})
    if not changed_targets:
        raise ValueError('No material or text targets were selected.')
    for part, root in roots.items():
        if without_fills(before[part], per_slide[part]) != without_fills(root, per_slide[part]):
            raise ValueError('A non-fill property changed; no file has been written.')
        items[part] = encoded(root)
    for part, root in rel_roots.items():
        items[part] = encoded(root)
    if any(k in config for k in ('paper', 'gold')):
        types = parse(items['[Content_Types].xml'])
        if not any(x.tag == f'{{{CT}}}Default' and x.get('Extension').lower() == 'png' for x in types):
            E.SubElement(types, f'{{{CT}}}Default', Extension='png', ContentType='image/png')
            items['[Content_Types].xml'] = encoded(types)
    if config.get('disable_picture_compression', True):
        pres = parse(items['ppt/presentation.xml'])
        pres.set('autoCompressPictures', '0')
        items['ppt/presentation.xml'] = encoded(pres)
    if not all(items[k] == v for k, v in original.items() if k.startswith('ppt/media/')):
        raise ValueError('An original image changed; no file has been written.')
    buffer = io.BytesIO()
    with ZipFile(buffer, 'w') as z:
        for info in infos:
            z.writestr(info, items[info.filename])
        for part in sorted(set(items) - set(original)):
            z.writestr(part, items[part])
    result = buffer.getvalue()
    if Path(source).read_bytes() != data:
        raise ValueError('Source changed during processing; no file has been written.')
    summary = {'input_sha256': sha(data), 'output_sha256': sha(result), 'slide_count': len(order),
               'targets': changed_targets, 'original_media_unchanged': True,
               'geometry_and_text_preserved': True,
               'changed_parts': sorted(k for k in original if items[k] != original[k]),
               'added_parts': sorted(set(items) - set(original))}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(result)
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        with report.open('x', encoding='utf-8') as stream:
            json.dump(summary, stream, ensure_ascii=False, indent=2)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    read = commands.add_parser('inspect')
    read.add_argument('source')
    edit = commands.add_parser('apply')
    edit.add_argument('source')
    edit.add_argument('--config', required=True)
    edit.add_argument('--output', required=True)
    edit.add_argument('--report')
    args = parser.parse_args()
    result = inspect(args.source) if args.command == 'inspect' else apply(args.source, args.config, args.output, args.report)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, E.XMLSyntaxError) as error:
        print(f'Error: {error}', file=sys.stderr)
        raise SystemExit(1)
