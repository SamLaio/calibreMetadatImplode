import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
from calibre.constants import numeric_version
from calibre.utils.config import config_dir
assert (ROOT / 'dist').resolve() in Path(config_dir).resolve().parents
from calibre.customize.zipplugin import loader
from calibre.gui2 import Application
from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from qt.core import QApplication, QAction, QMainWindow
ARCHIVE = Path(os.environ.get('HC_TEST_ARCHIVE', str(ROOT / 'dist/Hardcover Sync-zh_TW-release.zip')))
EXPECTED = tuple(map(int, os.environ.get('HC_EXPECTED_VERSION', '0.4.0.1').split('.')))
plugin_class = loader.load(str(ARCHIVE))
from calibre_plugins.hardcover_sync import config as cfg, ui
from calibre_plugins.hardcover_sync.hcl_graphql import client
from calibre_plugins.hardcover_sync.cull_isbn import isbn_lookup as lookup, isbn_select_dialog as select
from calibre_plugins.hardcover_sync.cull_isbn.isbn_scan import FoundIsbn


class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or Application([])
        assert numeric_version >= (7, 7, 0), numeric_version

    def setUp(self):
        self.block = patch('socket.socket.connect', side_effect=AssertionError('禁止實際連網'))
        self.block.start()
        self.plugin = plugin_class(str(ARCHIVE))

    def tearDown(self):
        self.block.stop()

    def test_load_config_and_legacy_settings(self):
        self.assertEqual(self.plugin.version, EXPECTED)
        cfg.PLUGIN_PREFS['api_key'] = 'qa-token'
        cfg.PLUGIN_PREFS['requests_per_minute'] = 17
        cfg.PLUGIN_PREFS['auto_push'] = False
        cfg.PLUGIN_PREFS['unknown_future_option'] = 'preserve'
        widget = self.plugin.config_widget()
        self.assertEqual(widget.api_key.text(), 'qa-token')
        self.assertEqual(widget.requests_per_minute.value(), 17)
        self.assertFalse(widget.auto_push.isChecked())
        widget.save_settings()
        self.assertEqual(cfg.PLUGIN_PREFS['unknown_future_option'], 'preserve')
        self.assertEqual(cfg.get_api_key(), 'qa-token')
        widget.close()

    def test_action_genesis_on_local_qt(self):
        gui = QMainWindow()
        gui.keyboard = Mock()
        action = self.plugin.load_actual_plugin(gui)
        action.interface_action_base_plugin = self.plugin
        action.qaction = QAction(gui)
        action.genesis()
        self.assertIsNotNone(action.qaction.menu())
        self.assertIs(action.qaction.menu(), action.menu)
        gui.close()

    def response(self, payload):
        response = Mock()
        response.read.return_value = json.dumps(payload).encode('utf-8')
        context = Mock()
        context.__enter__ = Mock(return_value=response)
        context.__exit__ = Mock(return_value=False)
        return context

    def test_graphql_success_and_auth_errors(self):
        api = client.GraphQLClient('https://api.hardcover.app/v1/graphql')
        api.set_token('qa-token')
        for payload, expected in [({'data': {'editions': []}}, {'editions': []}), ({'data': None}, None)]:
            with patch.object(client.request, 'urlopen', return_value=self.response(payload)), patch.object(client, '_wait_for_rate_slot'), patch.object(client, '_record_request_completed'):
                self.assertEqual(api.execute('query QA { editions { id } }'), expected)
        for payload in ({'error': 'Unable to verify token'}, {'errors': [{'message': 'permission denied'}]}):
            with patch.object(client.request, 'urlopen', return_value=self.response(payload)), patch.object(client, '_wait_for_rate_slot'), patch.object(client, '_record_request_completed'):
                with self.assertRaises(client.GraphQLError):
                    api.execute('query QA { editions { id } }')

    def test_lookup_keeps_identifiers_and_reports_error_with_fallback(self):
        data = {'editions': [{'id': 22, 'title': 'QA', 'isbn_13': '9780306406157', 'book': {'id': 11, 'slug': 'qa-book'}}]}
        with patch.object(lookup.GraphQLClient, 'execute', return_value=data):
            result = lookup._lookup_hardcover('9780306406157', 'qa-token')[0]
        self.assertEqual((result.edition_id, result.book_id, result.book_slug), (22, 11, 'qa-book'))
        with patch.object(lookup, 'get_api_key', return_value='qa-token'), patch.object(lookup, '_lookup_hardcover', side_effect=client.GraphQLError('Unable to verify token')), patch.object(lookup, '_lookup_open_library', return_value=result):
            results, error = lookup.lookup_isbn_with_status('9780306406157')
        self.assertEqual(results, [result])
        self.assertTrue(error)
        with patch.object(lookup.GraphQLClient, 'execute', return_value=None):
            self.assertEqual(lookup._lookup_hardcover('9780306406157', 'qa-token'), [])

    def test_real_selection_dialog_warning_and_cancel(self):
        result = lookup.IsbnLookupResult(title='QA', authors='Test', format_type='E-Book', source='Hardcover', edition_id=22, book_id=11, book_slug='qa-book')
        with patch.object(select, 'Thread'):
            dialog = select.IsbnSelectDialog(None, [FoundIsbn('9780306406157', True)], 'QA')
        dialog._apply_row(0, result)
        dialog.table.setCurrentCell(0, 0)
        self.assertIs(dialog.selected_result(), result)
        self.assertEqual(dialog.selected_isbn(), '9780306406157')
        dialog._show_warning('QA token error')
        self.assertEqual(dialog._warning.text(), 'QA token error')
        dialog.reject()
        dialog._apply_row(0, None)
        self.assertIs(dialog.selected_result(), result)
        dialog.deleteLater()

    def test_save_selected_edition_preserves_other_identifiers(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            db = LibraryDatabase(folder)
            try:
                book_id = db.create_book_entry(Metadata('QA', ['Test']))
                db.new_api.set_field('identifiers', {book_id: {'custom': 'keep'}})
                gui = QMainWindow()
                gui.current_db = db
                gui.status_bar = Mock()
                owner = SimpleNamespace(gui=gui, _isbn_scan_counter=1)
                result = lookup.IsbnLookupResult(title='QA', authors='Test', format_type='E-Book', source='Hardcover', edition_id=22, book_id=11, book_slug='qa-book')
                dialog = Mock()
                dialog.DialogCode.Accepted = 1
                dialog.exec.return_value = 1
                dialog.selected_isbn.return_value = '9780306406157'
                dialog.selected_result.return_value = result
                with patch.object(ui, 'IsbnSelectDialog', return_value=dialog), patch.object(ui, 'info_dialog'):
                    ui.HardcoverSyncAction._on_isbns_found(owner, 1, book_id, ([FoundIsbn('9780306406157', True)], None))
                ids = db.new_api.field_for('identifiers', book_id)
                self.assertEqual(ids['custom'], 'keep')
                self.assertEqual(ids['hardcover-id'], '11')
                self.assertEqual(ids['hardcover-edition'], '22')
                self.assertEqual(ids['hardcover'], 'qa-book')
                self.assertEqual(ids['isbn'], '9780306406157')
                gui.close()
            finally:
                db.close()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompatibilityTests))
    raise SystemExit(not result.wasSuccessful())
