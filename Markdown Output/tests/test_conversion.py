import base64
import os
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]
config = Path(os.environ.get('CALIBRE_CONFIG_DIRECTORY', '')).resolve()
assert (ROOT / 'dist').resolve() in config.parents, '請使用 dist 下的獨立設定目錄'
folder = ROOT / 'dist/markdown-conversion-qa'
folder.mkdir(parents=True, exist_ok=True)
source = folder / 'sample.epub'
files = {
    'META-INF/container.xml': '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0"><rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',
    'content.opf': '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">qa</dc:identifier><dc:title>Markdown 測試</dc:title><dc:language>zh-TW</dc:language></metadata><manifest><item id="text" href="chapter.xhtml" media-type="application/xhtml+xml"/><item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/><item id="image" href="image.png" media-type="image/png"/></manifest><spine toc="toc"><itemref idref="text"/></spine></package>',
    'chapter.xhtml': '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>測試</title></head><body><h1>中文標題</h1><p>保留中文內文與<a href="https://example.com/">測試連結</a>。</p><p><img src="image.png" alt="測試圖片"/></p></body></html>',
    'toc.ncx': '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="qa"/></head><docTitle><text>測試</text></docTitle><navMap><navPoint id="p1" playOrder="1"><navLabel><text>章節</text></navLabel><content src="chapter.xhtml"/></navPoint></navMap></ncx>',
}
with ZipFile(source, 'w') as z:
    z.writestr('mimetype', 'application/epub+zip')
    for name, text in files.items():
        z.writestr(name, text.encode('utf-8'), compress_type=ZIP_DEFLATED)
    z.writestr('image.png', base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6PQkAAAAASUVORK5CYII='))
subprocess.run(['calibre-customize', '-a', str(ROOT / 'dist/Markdown Output-zh_TW-release.zip')], check=True, capture_output=True)
output = folder / 'output.md'
result = subprocess.run(['ebook-convert', str(source), str(output)], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
(folder / 'conversion.log').write_text(result.stdout + result.stderr, encoding='utf-8')
assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
text = output.read_text(encoding='utf-8')
assert '中文標題' in text
assert '保留中文內文' in text
assert 'https://example.com/' in text
assert '![' in text and '.png' in text
print('Real EPUB to Markdown conversion, Chinese text, links and image references: OK')
