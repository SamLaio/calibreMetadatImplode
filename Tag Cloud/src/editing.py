"""Scoped metadata edits: preserve unrelated values and reject stale previews."""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
import re

from calibre.utils.localization import _, canonicalize_lang
from calibre_plugins.tag_cloud.core import field_terms


WRITABLE = {'title', 'authors', 'tags', 'publisher', 'series', 'rating', 'pubdate',
            'timestamp', 'comments', 'languages', 'identifiers', 'author_sort', 'sort', 'series_index'}


def datatype(api, field):
    return 'comments' if field == 'comments' else api.field_metadata[field]['datatype']


def readonly_reason(api, field):
    if not field or field not in api.fields or field not in api.field_metadata:
        return '這是唯讀或計算欄位，不能由詞雲修改。'
    kind = datatype(api, field)
    if kind not in {'text', 'series', 'rating', 'datetime', 'int', 'float', 'bool', 'enumeration', 'comments'}:
        return '這個欄位類型不支援直接修改。'
    if not field.startswith('#') and field not in WRITABLE:
        return '這是系統或唯讀欄位，不能由詞雲修改。'
    return ''


@dataclass
class Change:
    field: str
    term: str
    before: dict
    after: dict
    indices: dict
    value: object


def prepare(api, field, term, book_ids, value=None, remove=False):
    reason = readonly_reason(api, field)
    if reason:
        raise ValueError(reason)
    if remove and field == 'title':
        raise ValueError('書名不可清空，請使用修改書名。')
    ids = set(book_ids)
    if not ids or not ids <= api.all_book_ids():
        raise ValueError('對應書籍已變更，請重新整理詞雲。')
    kind = datatype(api, field)
    before = deepcopy(api.all_field_for(field, ids))
    if any(term not in field_terms(old, kind) for old in before.values()):
        raise ValueError('欄位內容已變更，請重新整理詞雲後再操作。')
    if kind == 'comments' and not remove and len(set(before.values())) > 1:
        raise ValueError('這個摘要對應不同的完整評論，請逐本編輯，避免覆蓋不同原文。')
    if not remove:
        if kind in {'text', 'series', 'enumeration', 'comments'}:
            value = str(value).strip()
            if not value:
                raise ValueError('新值不可空白；清空請使用移除。')
        if getattr(api.fields[field], 'is_many', False) and str(value).casefold() == term.casefold() and value != term:
            raise ValueError('僅變更大小寫可能影響範圍外的共用值；請使用 calibre 原生分類管理。')
        if kind == 'series' and re.search(r'\[\s*-?\d+(?:\.\d+)?\s*\]\s*$', value):
            raise ValueError('請只輸入系列名稱，勿在尾端加上 [編號]；現有系列編號會保留。')
        if kind == 'enumeration' and value not in api.field_metadata[field].get('display', {}).get('enum_values', []):
            raise ValueError('請選擇此欄位既有的允許值。')
        if field == 'languages':
            value = canonicalize_lang(value)
            if not value:
                raise ValueError('請輸入有效的語言代碼，例如 eng、zho、jpn。')
        if kind == 'bool' and type(value) is not bool:
            raise ValueError('請選擇是或否。')
        if kind == 'datetime' and not isinstance(value, datetime):
            raise ValueError('請選擇有效日期。')
        if kind in {'int', 'rating'} and type(value) is not int:
            raise ValueError('請輸入整數。')
        if kind in {'int', 'float', 'rating'} and (isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)):
            raise ValueError('請輸入有效數字。')
        if kind == 'rating' and not 0 <= value <= 10:
            raise ValueError('評分必須介於 0 至 5 星。')
    after = {}
    multiple = api.field_metadata[field].get('is_multiple')
    for book_id, old in before.items():
        if field == 'identifiers':
            key = term.split(':', 1)[0]
            new = dict(old)
            if remove:
                new.pop(key, None)
            else:
                new[key] = value
        elif multiple:
            new = [item for item in old if str(item) != term] if remove else [value if str(item) == term else item for item in old]
            new = list(dict.fromkeys(new))
            if field == 'authors' and not new:
                new = [_('Unknown')]
        else:
            new = None if remove else value
        after[book_id] = new
    indices = api.all_field_for(field + '_index', ids) if kind == 'series' else {}
    return Change(field, term, before, after, indices, value)


def apply(api, change):
    if not set(change.before) <= api.all_book_ids() or api.all_field_for(change.field, change.before) != change.before:
        raise ValueError('確認期間書籍或欄位已變更，未寫入；請重新整理後重試。')
    if change.indices and api.all_field_for(change.field + '_index', change.indices) != change.indices:
        raise ValueError('確認期間系列編號已變更，未寫入。')
    try:
        changed = api.set_field(change.field, change.after, allow_case_change=False)
        if change.indices:
            indices = {book_id: 1.0 if change.after[book_id] is None else index
                       for book_id, index in change.indices.items()}
            changed |= api.set_field(change.field + '_index', indices)
        return changed
    except Exception as error:
        try:
            api.set_field(change.field, change.before, allow_case_change=False)
            if change.indices:
                api.set_field(change.field + '_index', change.indices)
        except Exception as rollback_error:
            raise RuntimeError(f'寫入失敗且還原失敗，請檢查受影響書籍。寫入：{error}；還原：{rollback_error}') from error
        raise RuntimeError(f'寫入失敗，已還原原值：{error}') from error
