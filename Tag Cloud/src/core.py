from collections import Counter
from math import log1p
import re
from datetime import date
from html import unescape


def count_tags(values):
    counts = Counter()
    for tags in values.values():
        if isinstance(tags, str):
            tags = (tags,)
        counts.update(set(tags or ()))
    return sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold()))


def field_terms(value, datatype='text'):
    if value is None or value == '':
        return []
    if isinstance(value, dict):
        return [str(key) + ':' + str(item) for key, item in value.items()]
    if isinstance(value, (list, tuple, set, frozenset)):
        return list(dict.fromkeys(str(item) for item in value if item is not None and str(item)))
    if isinstance(value, bool):
        return ['是' if value else '否']
    if isinstance(value, date):
        return [value.strftime('%Y-%m-%d')] if value.year > 101 else []
    if datatype == 'rating':
        return [f'{value / 2:g} ★'] if value else []
    text = str(value)
    if datatype == 'comments':
        text = ' '.join(unescape(re.sub('<[^>]*>', ' ', text)).split())
        text = text[:120] + ('…' if len(text) > 120 else '')
    return [text] if text else []


def indexed_terms(values, datatype='text'):
    books = {}
    for book_id, value in values.items():
        for term in field_terms(value, datatype):
            books.setdefault(term, set()).add(book_id)
    return sorted(((term, len(ids)) for term, ids in books.items()),
                  key=lambda item: (-item[1], item[0].casefold())), books


def book_query(book_ids):
    ids = sorted(book_ids)
    if not ids:
        return 'id:false'
    ranges = []
    start = end = ids[0]
    for book_id in ids[1:] + [None]:
        if book_id == end + 1:
            end = book_id
            continue
        ranges.append(f'id:{start}' if start == end else f'(id:>={start} and id:<={end})')
        start = end = book_id
    return ' or '.join(ranges)


def tag_query(tags, match_all=True, field='tags'):
    terms = []
    for tag in tags:
        # Leading periods otherwise invoke calibre's hierarchical equality search.
        value = '~^' + re.escape(tag) + '$' if tag.startswith('.') else '=' + tag
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        terms.append(field + ':"' + escaped + '"')
    return (' and ' if match_all else ' or ').join(terms)


def font_size(count, maximum, minimum=1):
    if maximum <= minimum:
        return 20
    fraction = (log1p(count) - log1p(minimum)) / (log1p(maximum) - log1p(minimum))
    return 12 + round(24 * max(0, min(1, fraction)))
