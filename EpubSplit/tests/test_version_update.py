import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class VersionUpdateTests(unittest.TestCase):
    def test_preserves_arbitrary_upstream_segments(self):
        root = Path(__file__).parents[2]
        for version in ((3, 12, 0, 2), (1, 5, 0, 1, 0, 2)):
            with self.subTest(version=version), tempfile.TemporaryDirectory(dir=root / 'dist') as directory:
                target = Path(directory)
                shutil.copyfile(root / 'EpubSplit/src/version_update.py', target / 'version_update.py')
                (target / '__init__.py').write_text('version = ' + repr(version) + '\n', encoding='utf-8')
                (target / 'epubsplit.py').write_text('# no version here\n', encoding='utf-8')
                subprocess.run([sys.executable, '-B', 'version_update.py', 'release'], cwd=target, check=True,
                               capture_output=True, text=True)
                expected = version[:-1] + (version[-1] + 1,)
                self.assertEqual((target / '__init__.py').read_text(encoding='utf-8'),
                                 'version = ' + repr(expected) + '\n')


if __name__ == '__main__':
    unittest.main()
