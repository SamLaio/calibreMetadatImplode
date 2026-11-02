from pathlib import Path
import zipfile
p=Path(__file__).resolve().parents[1]
x=(p/'fixtures/chapter.xhtml').read_text(encoding='utf-8')
files={'META-INF/container.xml':'<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>',
'OEBPS/content.opf':'''<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">urn:uuid:text-regex-p0</dc:identifier><dc:title>Regex P0 Fixture</dc:title><dc:language>zh-TW</dc:language></metadata><manifest><item id="c" href="chapter.xhtml" media-type="application/xhtml+xml"/><item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/></manifest><spine toc="ncx"><itemref idref="c"/></spine></package>''',
'OEBPS/toc.ncx':'''<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="urn:uuid:text-regex-p0"/></head><docTitle><text>Regex P0 Fixture</text></docTitle><navMap><navPoint id="c" playOrder="1"><navLabel><text>Test</text></navLabel><content src="chapter.xhtml"/></navPoint></navMap></ncx>''','OEBPS/chapter.xhtml':x}

output=p.parent/'dist/text-regex-p0-fixture.epub'
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output,'w') as z:
 z.writestr('mimetype','application/epub+zip',compress_type=zipfile.ZIP_STORED)
 for name,data in files.items():z.writestr(name,data.encode('utf-8'),compress_type=zipfile.ZIP_DEFLATED)
print(output)
