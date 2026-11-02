import re
import unicodedata
import json
from difflib import SequenceMatcher
from regex import error as RegexError
from calibre.ebooks.conversion.search_replace import compile_regular_expression, REGEX_FLAGS
from html import unescape, escape
from html.entities import name2codepoint
from html.parser import HTMLParser
from xml.parsers import expat

INLINE = {'span', 'b', 'i', 'em', 'strong', 'a', 'small', 'sup', 'sub', 'u', 's'}

def validate_xhtml(raw):
    def entity_for_validation(match):
        name = match.group(1)
        if name in name2codepoint:
            return f'&#{name2codepoint[name]};'
        return match[0]

    def check_doctype(name, system_id, public_id, internal_subset):
        if internal_subset:
            raise ValueError('不支援含內部 DTD／自訂實體宣告的 XHTML；請先將自訂實體轉為文字或數字實體')

    # Only the validation copy expands standard XHTML entities; source offsets stay intact.
    checked = re.sub(r'<!--[\s\S]*?-->|<!\[CDATA\[[\s\S]*?\]\]>|<\?[\s\S]*?\?>|&([A-Za-z][A-Za-z0-9]*);',
                     entity_for_validation, raw)
    parser = expat.ParserCreate(namespace_separator='}')
    parser.StartDoctypeDeclHandler = check_doctype
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    parser.ExternalEntityRefHandler = lambda *args: 1  # Never open a DTD or external entity.
    try:
        parser.Parse(checked, True)
    except expat.ExpatError as err:
        raise ValueError(f'XHTML 格式錯誤（第 {err.lineno} 行）：{expat.ErrorString(err.code)}') from err

class Projection(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        validate_xhtml(raw)
        self.raw, self.text, self.mapping = raw, '', []
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer('\n', raw))
        self.stack = []
        self.feed(raw)

    def source_offset(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def boundary(self):
        self.text += '\n'
        self.mapping.append(None)

    def handle_starttag(self, tag, attrs):
        tag = tag.split(':')[-1]
        self.stack.append(tag)
        if tag not in INLINE:
            self.boundary()

    def handle_startendtag(self, tag, attrs):
        self.boundary()

    def handle_endtag(self, tag):
        if self.stack:
            self.stack.pop()
        if tag.split(':')[-1] not in INLINE:
            self.boundary()

    def visible(self):
        return 'body' in self.stack and not set(self.stack) & {'script', 'style'}

    def handle_data(self, data):
        if self.visible():
            start = self.source_offset()
            self.text += data
            self.mapping.extend((start+i, start+i+1) for i in range(len(data)))

    def entity(self, literal):
        if self.visible():
            value = unescape(literal)
            start = self.source_offset()
            self.text += value
            self.mapping.extend([(start, start+len(literal))] * len(value))

    def handle_entityref(self, name):
        self.entity('&'+name+';')

    def handle_charref(self, name):
        self.entity('&#'+name+';')


def expand(match, template):
    # Calibre regex uses \g<1>; $1 is an explicit UI compatibility adapter.
    template = re.sub(r'\$(\d+)', lambda m: r'\g<' + m[1] + '>', template)
    try:
        return match.expand(template)
    except (IndexError, RegexError) as err:
        raise ValueError('取代式無效：請確認 $1 或 \\g<名稱> 引用的群組已在尋找式中用括號定義，並檢查跳脫語法。') from err


def template_parts(match, template, html=False):
    expand(match, template)  # Validate native escapes and group references first.
    template = re.sub(r'\$(\d+)', lambda m: r'\g<' + m[1] + '>', template)
    parts, references = [], []
    position = 0
    length = 0
    for token in re.finditer(r'\\\\|\\[0-7]{3}|\\g<([^>]+)>|\\([1-9][0-9]?)', template):
        literal = expand(match, template[position:token.start()])
        parts.append(literal)
        length += len(literal)
        group = token[1] or token[2]
        if group is not None:
            group = int(group) if group.isdigit() else group
            value = match.group(group) or ''
            start, end = match.span(group)
            if value:
                references.append((start - match.start(), end - match.start(), length))
            value = escape(value, quote=False) if html else value
        else:
            value = expand(match, token[0])
        parts.append(value)
        length += len(value)
        position = token.end()
    parts.append(expand(match, template[position:]))
    return ''.join(parts), references


def text_replacement(row, after, references):
    fragment = row['fragment']
    if row['source_safe']:
        return escape(after, quote=False)
    matcher = SequenceMatcher(None, row['before'], after, autojunk=False)
    equal = {i + n: j + n for i, j, size in matcher.get_matching_blocks() for n in range(size)}
    for start, end, output in references:
        if start < 0 or end > len(row['before']) or any(equal.get(i) != output + i - start for i in range(start, end)):
            raise ValueError('跨格式群組無法原位保留；請保留群組順序，或使用完整 HTML 片段')
    patches = []
    mapping = row['mapping']
    for tag, i, j, a, b in matcher.get_opcodes():
        if tag == 'equal':
            continue
        value = escape(after[a:b], quote=False)
        if i == j:
            if 0 < i < len(mapping) and mapping[i - 1][1] != mapping[i][0]:
                raise ValueError('新增文字位於格式邊界，無法判定應繼承的格式；請使用 HTML 片段')
            offset = mapping[i][0] if i < len(mapping) else mapping[-1][1]
            patches.append((offset, offset, value))
        else:
            spans = mapping[i:j]
            contiguous = all(left[1] == right[0] for left, right in zip(spans, spans[1:]))
            if value and not contiguous:
                raise ValueError('新文字跨越不同格式，無法安全分配；請保留擷取群組或使用 HTML 片段')
            if contiguous:
                patches.append((spans[0][0], spans[-1][1], value))
            else:
                patches.extend((start, end, '') for start, end in spans)
    for start, end, value in sorted(patches, reverse=True):
        fragment = fragment[:start] + value + fragment[end:]
    return fragment


def update_preview(row, template, mode='text'):
    error = ''
    after, replacement = '', ''
    try:
        if row.get('raw_source'):
            after = expand(row['match'], template)
            replacement = after
            if not row['mapped']:
                raise ValueError('零寬結果無法安全取代')
            row.update(after=after, replacement=replacement, error='', safe=True, reason='')
            return
        after, references = template_parts(row['match'], template, html=mode == 'html')
        if not row['mapped']:
            raise ValueError('跨區塊或零寬結果無法安全取代')
        if mode == 'html':
            wrapper = '<div xmlns="http://www.w3.org/1999/xhtml">{}</div>'
            validate_xhtml(wrapper.format(after))
            validate_xhtml(wrapper.format(row['fragment']))
            replacement = after
        elif mode == 'text':
            replacement = text_replacement(row, after, references)
        else:
            raise ValueError('未知的取代模式')
    except ValueError as err:
        error = str(err)
    row.update(after=after, replacement=replacement, error=error, safe=not error, reason=error)


def search(raw, pattern, template, mode='text', syntax='html'):
    projection = Projection(raw) if syntax == 'html' else None
    rows = []
    # Each match stays within one XHTML document.
    for m in compile_regular_expression(pattern, flags=REGEX_FLAGS).finditer(projection.text if projection else raw, timeout=2):
        if projection is None:
            row = dict(before=m[0], start=m.start(), end=m.end(), match=m, source_safe=True,
                       mapped=m.start() != m.end(), raw_source=True, syntax=syntax)
            update_preview(row, template, mode)
            rows.append(row)
            continue
        spans = projection.mapping[m.start():m.end()]
        valid = bool(spans) and all(s is not None for s in spans)
        start, end = (spans[0][0], spans[-1][1]) if valid else (0, 0)
        safe = valid and all(a[1] == b[0] for a,b in zip(spans,spans[1:]))
        row = dict(before=m[0], start=start, end=end, match=m, source_safe=safe,
                   mapped=valid, fragment=raw[start:end],
                   mapping=[(a - start, b - start) for a, b in spans] if valid else [])
        update_preview(row, template, mode)
        rows.append(row)
    return rows


def replace(raw, rows):
    if any(not row['safe'] for row in rows):
        raise ValueError('選取結果包含無法安全取代的項目')
    for row in sorted(rows, key=lambda x:x['start'], reverse=True):
        raw = raw[:row['start']] + row.get('replacement', escape(row['after'], quote=False)) + raw[row['end']:]
    syntax = rows[0].get('syntax', 'html') if rows else 'html'
    if syntax in {'html', 'xml'}:
        validate_xhtml(raw)
    elif syntax == 'json':
        try:
            json.loads(raw)
        except ValueError as err:
            raise ValueError(f'JSON 格式錯誤：{err}') from err
    if unicodedata.normalize("NFC", raw) != raw:
        raise ValueError("拒絕會觸發編輯器 NFC 正規化的內容")
    return raw


def utf16(text, offset):
    return len(text[:offset].encode('utf-16-le')) // 2
