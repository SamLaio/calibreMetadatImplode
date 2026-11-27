from collections import Counter
from math import log1p
import re


def count_tags(values):
    counts = Counter()
    for tags in values.values():
        if isinstance(tags, str):
            tags = (tags,)
        counts.update(set(tags or ()))
    return sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold()))


def tag_query(tags, match_all=True, field='tags'):
    terms = []
    for tag in tags:
        # Leading periods otherwise invoke calibre's hierarchical equality search.
        value = '~^' + re.escape(tag) + '$' if tag.startswith('.') else '=' + tag
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        terms.append(field + ':"' + escaped + '"')
    return (' and ' if match_all else ' or ').join(terms)


def font_size(count, maximum):
    if maximum <= 1:
        return 12
    return 12 + round(12 * log1p(count - 1) / log1p(maximum - 1))
