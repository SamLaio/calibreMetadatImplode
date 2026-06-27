from __future__ import annotations

import json
import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET

CONTAINER_NS = 'urn:oasis:names:tc:opendocument:xmlns:container'
OPF_NS = 'http://www.idpf.org/2007/opf'


def _local_name(tag: str) -> str:
    if '}' in tag:
        return tag.rsplit('}', 1)[1]
    return tag


def _copy_zipinfo(info: zipfile.ZipInfo) -> zipfile.ZipInfo:
    cloned = zipfile.ZipInfo(info.filename, date_time=info.date_time)
    cloned.comment = info.comment
    cloned.extra = info.extra
    cloned.create_system = info.create_system
    cloned.create_version = info.create_version
    cloned.extract_version = info.extract_version
    cloned.flag_bits = info.flag_bits
    cloned.internal_attr = info.internal_attr
    cloned.external_attr = info.external_attr
    cloned.compress_type = info.compress_type
    return cloned


def _find_opf_name(zf: zipfile.ZipFile) -> str | None:
    try:
        container = ET.fromstring(zf.read('META-INF/container.xml'))
    except Exception:
        return None

    rootfiles = container.find(f'{{{CONTAINER_NS}}}rootfiles')
    if rootfiles is None:
        return None

    for rootfile in rootfiles.findall(f'{{{CONTAINER_NS}}}rootfile'):
        opf_name = rootfile.get('full-path')
        if opf_name:
            return opf_name
    return None


def _is_bad_calibre_user_metadata(meta: ET.Element) -> bool:
    token = meta.get('name') or meta.get('property') or meta.get('id') or ''
    if not token.startswith('calibre:user_metadata'):
        return False

    content = meta.get('content')
    if not content:
        return False

    try:
        payload = json.loads(content)
    except Exception:
        return False

    return isinstance(payload, dict) and 'datatype' not in payload


def _sanitize_opf(opf_bytes: bytes) -> tuple[bytes, bool]:
    try:
        root = ET.fromstring(opf_bytes)
    except Exception:
        return opf_bytes, False

    metadata = root.find(f'{{{OPF_NS}}}metadata')
    if metadata is None:
        return opf_bytes, False

    removed = False
    for child in list(metadata):
        if _local_name(child.tag) == 'meta' and _is_bad_calibre_user_metadata(child):
            metadata.remove(child)
            removed = True

    if not removed:
        return opf_bytes, False

    return ET.tostring(root, encoding='utf-8', xml_declaration=True), True


def sanitize_epub_user_metadata(epub_path: str) -> bool:
    replacement_data = None
    with zipfile.ZipFile(epub_path, 'r') as zin:
        opf_name = _find_opf_name(zin)
        if not opf_name:
            return False

        opf_bytes = zin.read(opf_name)
        sanitized_opf, changed = _sanitize_opf(opf_bytes)
        if not changed:
            return False

        directory = os.path.dirname(epub_path) or None
        fd, tmp_path = tempfile.mkstemp(suffix='.epub', dir=directory)
        os.close(fd)
        try:
            with zipfile.ZipFile(tmp_path, 'w') as zout:
                for info in zin.infolist():
                    data = sanitized_opf if info.filename == opf_name else zin.read(info.filename)
                    zout.writestr(_copy_zipinfo(info), data)
            replacement_data = tmp_path
        except Exception:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise

    if replacement_data is None:
        return False

    try:
        os.replace(replacement_data, epub_path)
    finally:
        if os.path.exists(replacement_data):
            try:
                os.remove(replacement_data)
            except OSError:
                pass
    return True
