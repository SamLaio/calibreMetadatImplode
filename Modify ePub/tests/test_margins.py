import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from margins import MarginsUpdater, RE_BOOK_MGNS


class MarginsTests(unittest.TestCase):
    def setUp(self):
        self.updater = MarginsUpdater(lambda *args: None, None)
        self.updater.user_margins = dict.fromkeys(
            ['margin_top', 'margin_right', 'margin_bottom', 'margin_left'], 5.0)
        self.css = self.updater._prefs_to_css_properties(self.updater.user_margins)

    def match(self, styles, allow_less=False):
        return self.updater._match_margins(
            RE_BOOK_MGNS.findall('@page { ' + styles + ' }'), allow_less)

    def test_non_numeric_and_negative_margins_need_replacement(self):
        for value in ['auto', 'inherit', 'initial', 'unset', 'calc(100% - 1em)',
                      'var(--margin)', '-5pt', '5pt !important']:
            with self.subTest(value=value):
                self.assertTrue(self.match('margin-top: ' + value))
        self.assertTrue(self.match('margin: auto'))

    def test_unrelated_and_malformed_declarations_are_ignored(self):
        for extra in ['color: red;', 'background: url(https://example.org/bg.png);',
                      'invalid;', '', ';']:
            with self.subTest(extra=extra):
                self.assertFalse(self.match(extra + self.css))

    def test_matching_and_smaller_margins(self):
        self.assertFalse(self.match(self.css))
        self.assertFalse(self.match(self.css.replace('5.0pt', '+5pt')))
        smaller = self.css.replace('5.0pt', '.5pt')
        self.assertTrue(self.match(smaller))
        self.assertFalse(self.match(smaller, allow_less=True))
        self.assertTrue(self.match(self.css.replace('margin-top: 5.0pt;', '')))
        self.updater.user_margins['margin_top'] = -1
        self.assertTrue(self.match(self.css))

    def test_rewrite_css_and_inline_styles_preserves_other_content(self):
        for name, mime, text in [
            ('style.css', 'text/css',
             '@page { color: red; margin-top: auto; } p { color: blue; }'),
            ('chapter.xhtml', 'application/xhtml+xml',
             '<html><head><style>@page { margin-top: auto; color: red; }'
             '</style></head><body><p>Keep this text.</p></body></html>'),
        ]:
            with self.subTest(name=name):
                files = {name: text}
                self.updater.container = SimpleNamespace(
                    name_path_map=files, mime_map={name: mime},
                    get_raw=files.__getitem__, set=files.__setitem__)
                with patch.object(self.updater, '_get_user_margins',
                                  return_value=self.updater.user_margins):
                    self.assertTrue(self.updater.rewrite_css_margins())
                    self.assertIn(self.css, files[name])
                    self.assertIn('color: red', files[name])
                    self.assertNotIn('auto', files[name])
                    self.assertIn('Keep this text.' if name.endswith('.xhtml')
                                  else 'p { color: blue; }', files[name])
                    self.assertFalse(self.updater.rewrite_css_margins())


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(
        unittest.defaultTestLoader.loadTestsFromTestCase(MarginsTests))
    raise SystemExit(not result.wasSuccessful())
