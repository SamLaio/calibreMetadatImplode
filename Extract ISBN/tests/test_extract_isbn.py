import gettext
import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Extract ISBN' / 'src'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    'calibre_plugins.extract_isbn', SOURCE / '__init__.py',
    submodule_search_locations=[str(SOURCE)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.extract_isbn import config, jobs, nonpdf, pdf
from calibre_plugins.extract_isbn.scan import BookScanner


class ExtractISBNTests(unittest.TestCase):
    def scanner(self, text, forward=True):
        with patch.object(config, 'plugin_prefs', {
                config.STORE_NAME: config.DEFAULT_STORE_VALUES}):
            scanner = BookScanner(Mock())
        scanner.look_for_identifiers_in_text([text], forward=forward)
        return scanner.get_isbn_result()

    def test_lowercase_check_digit_in_both_directions(self):
        for forward in (True, False):
            self.assertEqual(self.scanner('ISBN 0-8044-2957-x', forward), '080442957X')

    def test_prefixes_validation_and_isbn13_preference(self):
        self.assertEqual(self.scanner('ISBN-10 1-4020-4136-5'), '1402041365')
        self.assertEqual(self.scanner('ISBN-13 978-0-306-40615-7'), '9780306406157')
        self.assertIsNone(self.scanner('ISBN 9780306406158'))
        self.assertIsNone(self.scanner('ISBN 1111111111'))
        self.assertEqual(self.scanner('080442957X; 9780306406157'), '9780306406157')

    def test_reverse_scan_selects_last_isbn(self):
        self.assertEqual(self.scanner('9780306406157; 9780140328721', False), '9780140328721')

    def test_pdf_scans_exactly_last_five_pages_in_reverse(self):
        scanner = Mock()
        scanner.has_identifier.return_value = False
        with patch.object(pdf, 'get_page_count', return_value=100), \
                patch.object(pdf, 'call_pdftohtml', side_effect=['front', 'back']) as convert, \
                patch.object(pdf, 'BookScanner', return_value=scanner):
            pdf.get_isbn('folder', 'book.pdf', Mock())
        self.assertEqual(convert.call_args_list[0].args[3:], (1, 10))
        self.assertEqual(convert.call_args_list[1].args[3:], (96, 100))
        scanner.look_for_identifiers_in_text.assert_any_call(['back'], forward=False)

    def test_short_pdf_scans_all_pages(self):
        with patch.object(pdf, 'get_page_count', return_value=15), \
                patch.object(pdf, 'call_pdftohtml', return_value='text') as convert:
            self.assertIsNone(pdf.get_isbn('folder', 'book.pdf', Mock()))
        self.assertEqual(len(convert.call_args.args), 3)

    def test_failure_summary_distinguishes_missing_formats(self):
        job = SimpleNamespace(result=([], [], [(1, 'Empty'), (2, 'Text')], [(1, 'Empty')]), details='')
        with patch.object(jobs, '_', side_effect=lambda text: text, create=True):
            details = jobs.get_job_details(job)[3]
        self.assertIn('Empty (No formats)', details)
        self.assertIn('Text (ISBN not found)', details)

    def test_real_epub_extraction(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            book = Path(folder) / 'book.epub'
            with zipfile.ZipFile(book, 'w') as archive:
                archive.writestr('mimetype', 'application/epub+zip')
                archive.writestr('META-INF/container.xml',
                    '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">'
                    '<rootfiles><rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>'
                    '</rootfiles></container>')
                archive.writestr('content.opf',
                    '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="id">'
                    '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
                    '<dc:title>測試書籍</dc:title><dc:identifier id="id">test</dc:identifier>'
                    '<dc:language>zh-TW</dc:language></metadata>'
                    '<manifest><item id="text" href="text.xhtml" media-type="application/xhtml+xml"/></manifest>'
                    '<spine><itemref idref="text"/></spine></package>')
                archive.writestr('text.xhtml',
                    '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>版權頁</title></head>'
                    '<body><p>ISBN 0-8044-2957-x</p></body></html>')
            self.assertEqual(nonpdf.get_isbn_from_non_pdf(Mock(), str(book)), '080442957X')

    def test_real_pdf_text_extraction(self):
        stream = b'BT /F1 12 Tf 72 720 Td (ISBN 0-8044-2957-x) Tj ET'
        objects = [
            b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
            b'/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
            b'<< /Length %d >>\nstream\n' % len(stream) + stream + b'\nendstream',
        ]
        data = b'%PDF-1.4\n'
        offsets = [0]
        for number, obj in enumerate(objects, 1):
            offsets.append(len(data))
            data += b'%d 0 obj\n' % number + obj + b'\nendobj\n'
        xref = len(data)
        data += b'xref\n0 6\n0000000000 65535 f \n'
        data += b''.join(b'%010d 00000 n \n' % offset for offset in offsets[1:])
        data += b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % xref
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            (Path(folder) / 'book.pdf').write_bytes(data)
            self.assertEqual(pdf.get_isbn(folder, 'book.pdf', Mock()), '080442957X')

    def test_release_contains_traditional_chinese(self):
        with zipfile.ZipFile(ROOT / 'dist' / 'Extract ISBN-zh_TW-release.zip') as archive:
            translation = gettext.GNUTranslations(io.BytesIO(archive.read('translations/zh_TW.mo')))
            self.assertEqual(translation.gettext('Extract ISBN'), '擷取 ISBN')
            self.assertEqual(translation.gettext('No formats'), '沒有書籍格式')
            self.assertTrue(all(not name.endswith(('.po', '.pyc')) for name in archive.namelist()))
            self.assertIn('common_dialogs.py', archive.namelist())
            self.assertIn('plugin-import-name-extract_isbn.txt', archive.namelist())


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ExtractISBNTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
