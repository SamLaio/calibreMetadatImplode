from __future__ import annotations

import json

MODE_EPUB_ONLY = 'epub'
MODE_SELECTABLE_FORMATS = 'selectable'
DEFAULT_MODE = MODE_EPUB_ONLY


def normalize_mode(mode: str | None) -> str:
    if mode == MODE_SELECTABLE_FORMATS:
        return MODE_SELECTABLE_FORMATS
    return MODE_EPUB_ONLY


def load_settings(site_customization: str | None) -> dict[str, str]:
    if not site_customization:
        return {'mode': DEFAULT_MODE}

    try:
        raw = json.loads(site_customization)
    except Exception:
        return {'mode': DEFAULT_MODE}

    if not isinstance(raw, dict):
        return {'mode': DEFAULT_MODE}

    return {'mode': normalize_mode(raw.get('mode'))}


def dump_settings(mode: str) -> str:
    return json.dumps({'mode': normalize_mode(mode)}, separators=(',', ':'))
