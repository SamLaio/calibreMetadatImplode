from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from core import search, replace, update_preview


def document(text):
    return '<html xmlns="http://www.w3.org/1999/xhtml"><body><p class="title">' + text + '</p></body></html>'


source = document('第<span class="tcy">10</span>話「荷葉邊騎士」')
for pattern, template in [(r'第(\d+)話', '第$1章'), (r'第(?P<n>\d+)話', r'第\g<n>章')]:
    rows = search(source, pattern, template)
    assert rows[0]['safe'], rows[0]['reason']
    assert replace(source, rows) == source.replace('話', '章', 1)
source = document('第<b>1<span>0</span></b><i>話</i>')
rows = search(source, r'第(\d+)話', '第$1章')
assert replace(source, rows) == source.replace('話', '章')
source = document('第<span>1&#48;</span>話 第<b>20</b>話')
rows = search(source, r'第(\d+)話', '第$1章')
assert replace(source, rows) == source.replace('話', '章')
# Literal markup stays text in text mode, including cross-tag matches.
rows = search(document('第<span>10</span>話'), r'第(\d+)話', '第$1<&')
assert rows[0]['safe'] and replace(document('第<span>10</span>話'), rows) == document('第<span>10</span>&lt;&amp;')
for pattern, template in [(r'第(\d+)話', '其他內容'), (r'第(1)(0)話', '第$2$1章'), (r'第(\d+)話', '第$1$1章')]:
    rows = search(document('第<span>10</span>話'), pattern, template)
    assert not rows[0]['safe'] and rows[0]['reason']
# Complete HTML fragments replace the whole balanced source span.
source = document('第<span class="tcy">10</span>話')
rows = search(source, r'第(\d+)話', '<strong>第$1章</strong>', 'html')
assert rows[0]['safe']
assert replace(source, rows) == document('<strong>第10章</strong>')
source = document('甲&amp;乙')
rows = search(source, '(甲&乙)', '<em>$1</em>', 'html')
assert rows[0]['after'] == '<em>甲&amp;乙</em>'
assert replace(source, rows) == document('<em>甲&amp;乙</em>')
for template in ['<b>第$1章', '<b>第$1章</i>', '</p><p>越界</p>', '<!DOCTYPE html><b>文字</b>', '<b>&unknown;</b>']:
    rows = search(document('第<span>10</span>話'), r'第(\d+)話', template, 'html')
    assert not rows[0]['safe'], template
    try:
        replace(document('第<span>10</span>話'), rows)
    except ValueError:
        pass
    else:
        raise AssertionError('broken fragment accepted')
# A valid replacement must not cut away half of the original tag pair.
source = document('第<b>10</b><i>話</i>')
rows = search(source, r'第(\d+)話', '<b>第$1章</b>', 'html')
assert not rows[0]['safe']
update_preview(rows[0], '第$1章', 'text')
assert rows[0]['safe'] and replace(source, rows) == source.replace('話', '章')
assert not search('<html><body><p>第10</p><p>話</p></body></html>', r'第(\d+)\s*話', '第$1章')[0]['safe']
source = document('x' * 65500 + '第<span>1&#48;</span>話')
rows = search(source, r'第(\d+)話', '第$1章')
assert replace(source, rows) == source.replace('話', '章')
print('PASS modes: inline/group formatting, entities, ambiguous format refusal, complete HTML, escaped groups, mode recovery')

# Raw HTML uses literal replacement, including incomplete tags.
source = document('one<br/>two<br/>three')
rows = search(source, '<br/>', '<p class="a">', syntax='html-source')
assert len(rows) == 2 and all(row['safe'] for row in rows)
assert replace(source, rows) == source.replace('<br/>', '<p class="a">')
assert replace(source, rows[:1]) == source.replace('<br/>', '<p class="a">', 1)
assert replace(source, search(source, '<br/>', '<br/>', syntax='html-source')) == source
try:
    replace(source, search(source, '<br/>', '<p class="a">', syntax='xml'))
except ValueError:
    pass
else:
    raise AssertionError('XML validation was bypassed')
print('Raw HTML literal replacement passed')
