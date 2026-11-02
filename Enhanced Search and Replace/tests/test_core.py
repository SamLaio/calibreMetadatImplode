from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from core import search,replace,utf16
raw=(Path(__file__).resolve().parents[1]/'fixtures/chapter.xhtml').read_text(encoding='utf-8')
rows=search(raw,r'第(\d+)章','第$1回')
assert [r['before'] for r in rows]==['第12章','第3章','第34章','第56章','第78章']
assert [r['safe'] for r in rows]==[True,True,True,True,True]
assert rows[0]['after']=='第12回'
assert search(raw,r'第(\d+)章',r'第\g<1>回')[0]['after']=='第12回'
changed=replace(raw,[r for r in rows if r['safe']])
assert '第12回' in changed and '<span class="n">34</span>回' in changed
assert 'title="第777章"' in changed and '第999章' in changed
assert utf16('😀第',1)==2
assert replace(raw,[dict(start=raw.index('第12章'),end=raw.index('第12章')+4,after='<&',safe=True)]).count('&lt;&amp;')==1
for action in [lambda:search('<bad>', 'x','y'),lambda:search(raw,'(',''),lambda:replace(raw,search(raw,r'第(\d+)章','新內容')[2:3])]:
    try: action()
    except Exception: pass
    else: raise AssertionError('expected rejection')
print('PASS core: projection, groups, safety, escaping, UTF16, invalid inputs')

assert search(raw,r'第(?P<n>\d+)章',r'第\g<n>回')[0]['after']=='第12回'
for pattern, template in [(r'第(\d+)章','$2'), ('第12章','第$1回'), (r'第(\d+)章',r'\g<missing>'), ('第12章',r'\q')]:
    failed=search(raw,pattern,template)
    assert failed and all(r['error'] and not r['safe'] for r in failed)
    try: replace(raw,failed)
    except ValueError: pass
    else: raise AssertionError('invalid preview was applied')

for declaration in [
    '<!DOCTYPE html>',
    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">',
    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">',
    '<!DOCTYPE html SYSTEM "file:///must-not-be-opened.dtd">',
]:
    source=re.sub(r'<!DOCTYPE[^>]*>',lambda match: declaration,raw,count=1)
    found=search(source,r'第(\d+)章','第$1回')
    assert [r['before'] for r in found]==[r['before'] for r in rows]
    assert source[found[0]['start']:found[0]['end']]=='第12章'
    assert replace(source,[found[0]])==source.replace('第12章','第12回',1)
assert len(search(re.sub(r'<!DOCTYPE[^>]*>','',raw),r'第(\d+)章','$1'))==5

source='<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml"><body><p title="&nbsp;">第&nbsp;12章 &copy; &mdash; &amp;</p></body></html>'
found=search(source,r'第\s*(\d+)章','第$1回')
assert found[0]['safe'] and found[0]['before']=='第\u00a012章'
assert replace(source,found)==source.replace('第&nbsp;12章','第12回')
# Declarations and entity-looking text inside comments/CDATA are not interpreted.
assert search('<html><body><!-- <!DOCTYPE html [&bad;]> --><![CDATA[&unknown;]]><p>第12章</p></body></html>',r'第(\d+)章','$1')[0]['after']=='12'
for source in [
    '<!DOCTYPE html [<!ENTITY x "第12章">]><html><body>&x;</body></html>',
    '<!DOCTYPE html [<!ENTITY x SYSTEM "file:///secret">]><html><body>&x;</body></html>',
    '<!DOCTYPE html><html><body>&unknown;</body></html>',
    '<!DOCTYPE html><html><body title="&unknown;"/></html>',
    '<!DOCTYPE html><html><body><p></body></html>',
]:
    try: search(source,'x','y')
    except ValueError as err:
        assert 'P0' not in str(err) and 'fixture' not in str(err)
    else: raise AssertionError('invalid XML or custom entity accepted')
print('PASS XHTML: DOCTYPE preserved, standard named entities, offsets, unsafe declarations rejected')
