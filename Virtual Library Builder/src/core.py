"""Build native calibre searches without evaluating user input as code."""
from datetime import date
import math
import re


TEXT_TYPES = {'text', 'series', 'enumeration', 'comments'}


def fields(db):
    result = {}
    for key, meta in db.field_metadata.items():
        datatype = meta.get('datatype')
        if meta.get('search_terms') and datatype in TEXT_TYPES | {'datetime', 'int', 'float', 'rating', 'bool'}:
            if key not in {'id', 'uuid', 'path', 'sort', 'author_sort'}:
                result[key] = meta
    return result


def quote(value):
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def condition(field, datatype, operator, value):
    if datatype == 'bool' and operator in ('empty', 'not_empty'):
        raise ValueError('是非欄位請使用等於「是」或「否」，空值判定依 calibre 是非欄位設定。')
    if operator == 'empty':
        return field + ':false'
    if operator == 'not_empty':
        return field + ':true'
    value = value.strip()
    if not value:
        raise ValueError('請填寫條件值。')
    if datatype == 'bool':
        if value not in ('是', '否', 'true', 'false'):
            raise ValueError('是非欄位請輸入「是」或「否」。')
        if operator != 'eq':
            raise ValueError('是非欄位只支援等於。')
        return field + ':' + ('true' if value in ('是', 'true') else 'false')
    if datatype in ('int', 'float', 'rating', 'datetime'):
        if operator not in ('eq', 'gt', 'lt'):
            raise ValueError('此欄位請使用等於、大於／晚於或小於／早於。')
        if datatype == 'datetime':
            date.fromisoformat(value)
        else:
            number = float(value)
            if not math.isfinite(number) or (datatype == 'int' and not number.is_integer()):
                raise ValueError('請輸入有效數字。')
            if datatype == 'rating' and not 0 <= number <= 5:
                raise ValueError('評分請輸入 0 到 5。')
        return field + ':' + {'eq': '=', 'gt': '>', 'lt': '<'}[operator] + value
    if operator not in ('eq', 'contains'):
        raise ValueError('文字欄位請使用等於或包含。')
    return field + ':' + quote(('=' + value) if operator == 'eq' else ('~' + re.escape(value)))



def expression(conditions, any_match=False):
    if not conditions:
        raise ValueError('請至少新增一項條件。')
    return (' or ' if any_match else ' and ').join('(' + term + ')' for term in conditions)


def batch_values(db, field):
    counts = {}
    meta = fields(db)[field]
    if meta['datatype'] not in {'text', 'series', 'enumeration'}:
        raise ValueError('批次建立支援文字、系列與列舉欄位。')
    for value in db.new_api.all_field_for(field, db.new_api.all_book_ids()).values():
        values = value if isinstance(value, (list, tuple, set)) else (value,)
        for term in set(str(x) for x in values if x is not None and str(x)):
            counts[term] = counts.get(term, 0) + 1
    return sorted(counts.items(), key=lambda pair: pair[0].casefold())


def plan(db, entries, conflict='skip'):
    existing = dict(db.new_api.pref('virtual_libraries', {}))
    names = set(existing)
    seen = set()
    result = []
    for name, search in entries:
        name = name.strip()
        if not name or name.startswith('*') or len(name) > 40:
            raise ValueError('名稱須為 1～40 字，且不能以 * 開頭。')
        if conflict != 'rename' and name in seen:
            raise ValueError('待建立清單有重複名稱：' + name)
        seen.add(name)
        original = name
        if conflict == 'rename':
            index = 2
            while name in names:
                suffix = ' (' + str(index) + ')'
                name = original[:40-len(suffix)] + suffix
                index += 1
        elif name in names and name not in existing:
            raise ValueError('待建立清單有重複名稱：' + name)
        status = '跳過' if name in existing and conflict == 'skip' else '更新' if name in existing else '建立'
        ids = db.new_api.search(search)
        result.append((name, search, len(ids), status))
        names.add(name)
    if not result:
        raise ValueError('請至少勾選一個值。')
    return result


def save(db, rows, expected, rename_from=None):
    if dict(db.new_api.pref('virtual_libraries', {})) != expected:
        raise ValueError('虛擬書庫已變更，請重新預覽。')
    updated = dict(expected)
    if rename_from is not None:
        if len(rows) != 1 or rename_from not in expected or rows[0][0] in expected:
            raise ValueError('無法更名：原書庫不存在，或新名稱已被使用。')
        updated.pop(rename_from)
    for name, search, count, status in rows:
        if status != '跳過':
            db.new_api.search(search)
            updated[name] = search
    order = ordered_names(db) if rename_from is not None else None
    db.new_api.set_pref('virtual_libraries', updated)
    if rename_from is not None:
        new_name = rows[0][0]
        db.new_api.set_pref('virt_libs_order', [new_name if name == rename_from else name
                                             for name in native_order(db, order)])
        hidden = db.new_api.pref('virt_libs_hidden', [])
        db.new_api.set_pref('virt_libs_hidden', [new_name if name == rename_from else name for name in hidden])
        if db.new_api.pref('virtual_lib_on_startup', '') == rename_from:
            db.new_api.set_pref('virtual_lib_on_startup', new_name)
    db.new_api.clear_search_caches()


def editable_conditions(search, metadata):
    """Only unpack expressions whose meaning we can preserve exactly."""
    atom = r'\(?([#\w]+):("(?:\\.|[^"\\])*"|[^\s()]+)\)?'
    if not re.fullmatch(atom + r'(?:\s+(?:and|or)\s+' + atom + r')*', search.strip()):
        return None
    matches = list(re.finditer(atom, search.strip()))
    joins = [search.strip()[a.end():b.start()].strip() for a, b in zip(matches, matches[1:])]
    if len(set(joins)) > 1:
        return None
    rows = []
    for match in matches:
        key, value = match.groups()
        if key not in metadata:
            return None
        datatype = metadata[key]['datatype']
        if value.startswith('"'):
            value = re.sub(r'\\([\\"])', r'\1', value[1:-1])
        if value in ('true', 'false'):
            if datatype == 'bool':
                op, value = 'eq', '是' if value == 'true' else '否'
            else:
                op, value = ('not_empty' if value == 'true' else 'empty'), ''
        elif datatype in TEXT_TYPES:
            if value.startswith('='):
                op, value = 'eq', value[1:]
            elif value.startswith('~'):
                literal = re.sub(r'\\(.)', r'\1', value[1:])
                if re.escape(literal) != value[1:]:
                    return None
                op, value = 'contains', literal
            elif value.startswith('^'):
                return None
            else:
                return None
        elif datatype in ('int', 'float', 'rating', 'datetime'):
            op = {'=': 'eq', '>': 'gt', '<': 'lt'}.get(value[:1])
            if op is None:
                return None
            value = value[1:]
        else:
            return None
        if value != value.strip():
            return None
        try:
            condition(key, datatype, op, value)
        except ValueError:
            return None
        rows.append((key, op, value))
    return rows, bool(joins and joins[0] == 'or')


def ordered_names(db):
    names = set(db.new_api.pref('virtual_libraries', {}))
    saved = db.new_api.pref('virt_libs_order', [])
    result = list(dict.fromkeys(name for name in saved if name in names))
    return result + sorted(names - set(result), key=str.casefold)


def native_order(db, names):
    saved = db.new_api.pref('virt_libs_order', [])
    all_books = saved.index('') if '' in saved else 0
    result = list(names)
    result.insert(min(all_books, len(result)), '')
    return result


def save_order(db, names, expected):
    if ordered_names(db) != expected or len(names) != len(set(names)) or set(names) != set(expected):
        raise ValueError('虛擬書庫或排列已變更，請重新開啟後再移動。')
    db.new_api.set_pref('virt_libs_order', native_order(db, names))


def advanced_condition(field, datatype, operator, value):
    if operator in ('recent_days', 'older_days', 'today', 'yesterday', 'thismonth', 'thisyear'):
        if datatype != 'datetime':
            raise ValueError('相對日期僅供日期欄位使用。')
        field = 'date' if field == 'timestamp' else field
        if operator in ('recent_days', 'older_days'):
            days = int(value)
            if not 1 <= days <= 365000:
                raise ValueError('天數請輸入 1～365000 的整數。')
            return field + ':' + ('>' if operator == 'recent_days' else '<=') + str(days) + '_daysago'
        return field + ':_' + operator
    if operator == 'regex':
        re.compile(value)
        if not value:
            raise ValueError('請輸入正規表示式。')
        return field + ':' + quote('~' + value)
    if operator in ('ge', 'le', 'ne') and datatype in ('datetime', 'int', 'float', 'rating'):
        term = condition(field, datatype, 'eq', value)
        return field + ':' + {'ge': '>=', 'le': '<=', 'ne': '!='}[operator] + term[len(field) + 2:]
    if operator in ('not_contains', 'ne'):
        return 'not (' + condition(field, datatype, 'contains' if operator == 'not_contains' else 'eq', value) + ')'
    return condition(field, datatype, operator, value)


def combine_search(existing, generated, mode='and'):
    if mode not in ('and', 'or', 'replace'):
        raise ValueError('不支援的組合方式。')
    if not generated.strip():
        raise ValueError('產生的條件不可空白。')
    if not existing.strip() or mode == 'replace':
        return generated
    return '(' + existing.strip() + ') ' + mode + ' (' + generated + ')'


def row_expression(terms, joins):
    if not terms:
        raise ValueError('請至少新增一項條件。')
    result = '(' + terms[0] + ')'
    for term, join in zip(terms[1:], joins[1:]):
        if join not in ('and', 'or'):
            raise ValueError('請選擇交集或聯集。')
        result = '(' + result + ' ' + join + ' (' + term + '))'
    return result


def editable_rows(search, metadata):
    # Recognize only flat expressions or the explicit left-to-right groups we emit.
    relative = re.fullmatch(r'\(?([#\w]+):([><=]*)(\d+_daysago|_today|_yesterday|_thismonth|_thisyear)\)?', search.strip())
    if relative:
        key, comparator, value = relative.groups()
        key = 'timestamp' if key == 'date' and 'timestamp' in metadata else key
        if key in metadata and metadata[key]['datatype'] == 'datetime':
            if value.endswith('_daysago') and comparator in ('>', '<='):
                return [(key, 'recent_days' if comparator == '>' else 'older_days', value[:-8], 'and')]
            if not comparator and value.startswith('_'):
                return [(key, value[1:], '', 'and')]
    parsed = editable_conditions(search, metadata)
    if parsed is not None:
        rows, any_match = parsed
        return [(key, op, value, 'or' if any_match else 'and') for key, op, value in rows]
    negated = re.fullmatch(r'\(?not \((.*)\)\)?', search.strip())
    if negated:
        inner = editable_rows(negated[1], metadata)
        if inner is not None and len(inner) == 1 and inner[0][1] in ('eq', 'contains'):
            key, op, value, join = inner[0]
            return [(key, 'ne' if op == 'eq' else 'not_contains', value, join)]
    comparison = re.fullmatch(r'\(?([#\w]+):(>=|<=|!=)([^\s()]+)\)?', search.strip())
    if comparison:
        key, comparator, value = comparison.groups()
        if key in metadata and metadata[key]['datatype'] in ('int', 'float', 'rating', 'datetime'):
            op = {'>=': 'ge', '<=': 'le', '!=': 'ne'}[comparator]
            try:
                advanced_condition(key, metadata[key]['datatype'], op, value)
                return [(key, op, value, 'and')]
            except ValueError:
                pass
    regex = re.fullmatch(r'\(?([#\w]+):("(?:\\.|[^"\\])*")\)?', search.strip())
    if regex and regex[1] in metadata and metadata[regex[1]]['datatype'] in TEXT_TYPES:
        value = re.sub(r'\\([\\"])', r'\1', regex[2][1:-1])
        if value.startswith('~'):
            try:
                re.compile(value[1:])
                return [(regex[1], 'regex', value[1:], 'and')]
            except re.error:
                pass
    text = search.strip()
    if not (text.startswith('(') and text.endswith(')')):
        return None
    depth = 0
    quoted = escaped = False
    split = None
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == '\\':
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
        if quoted:
            continue
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0 and index != len(text) - 1:
                return None
        elif depth == 1:
            for join in (' and ', ' or '):
                if text.startswith(join, index):
                    if split is not None:
                        return None
                    split = (index, join)
    if quoted or depth != 0 or split is None:
        return None
    index, join = split
    left = editable_rows(text[1:index], metadata)
    right = editable_rows(text[index + len(join):-1], metadata)
    if left is None or right is None or len(right) != 1:
        return None
    key, op, value, unused = right[0]
    return left + [(key, op, value, join.strip())]
