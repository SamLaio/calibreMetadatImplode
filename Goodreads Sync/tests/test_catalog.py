import io
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
from string import Formatter
from zipfile import ZipFile
import gettext

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'dist' / 'Goodreads Sync-zh_TW-release.zip'


def fields(text):
    return Counter((field, spec, conversion) for _, field, spec, conversion in Formatter().parse(text) if field is not None)


class CatalogTests(unittest.TestCase):
    def test_all_locale_aliases_and_format_fields(self):
        with ZipFile(ARCHIVE) as z:
            catalogs = [gettext.GNUTranslations(io.BytesIO(z.read('translations/' + locale + '.mo')))
                        for locale in ('zh_TW', 'zh_Hant', 'zh_Hant_TW')]
        self.assertEqual(catalogs[0]._catalog, catalogs[1]._catalog)
        self.assertEqual(catalogs[0]._catalog, catalogs[2]._catalog)
        count = 0
        for source, target in catalogs[0]._catalog.items():
            if not isinstance(source, str) or not source:
                continue
            count += 1
            with self.subTest(source=source):
                self.assertEqual(fields(source), fields(target))
                pattern = r'%(?:\([^)]+\))?[-+0-9.#]*[sdfiv]'
                self.assertEqual(Counter(re.findall(pattern, source)), Counter(re.findall(pattern, target)))
        self.assertGreater(count, 300)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CatalogTests))
    raise SystemExit(not result.wasSuccessful())
