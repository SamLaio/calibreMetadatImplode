from __future__ import annotations

import traceback

from calibre.gui2 import I, error_dialog, info_dialog
from calibre.gui2.actions import InterfaceAction
from qt.core import (
    QApplication,
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QProgressDialog,
    Qt,
)

from calibre_plugins.embed_metadata_safe.format_dialog import FormatSelectionDialog
from calibre_plugins.embed_metadata_safe.i18n import build_texts
from calibre_plugins.embed_metadata_safe.main import EmbedMetadataSafeEngine
from calibre_plugins.embed_metadata_safe.settings import (
    MODE_SELECTABLE_FORMATS,
    load_settings,
)


class EmbedMetadataSafeAction(InterfaceAction):
    name = 'Embed Metadata Safe'
    action_type = 'current'
    priority = 1
    action_spec = (
        'Embed Metadata Safe',
        I('modified.png'),
        'Safely embed metadata after repairing malformed EPUB calibre:user_metadata',
        None,
    )

    def _build_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor('#1f6f8b'))
        painter.drawRoundedRect(8, 8, 48, 48, 14, 14)

        painter.setBrush(QColor('#f8fbff'))
        painter.setPen(QPen(QColor('#d6dde6'), 2))
        painter.drawRoundedRect(19, 15, 26, 34, 4, 4)

        fold = QPainterPath()
        fold.moveTo(35, 15)
        fold.lineTo(45, 25)
        fold.lineTo(35, 25)
        fold.closeSubpath()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor('#c8d3dd'))
        painter.drawPath(fold)

        check = QPainterPath()
        check.moveTo(24, 35)
        check.lineTo(30, 41)
        check.lineTo(39, 30)
        painter.setPen(QPen(QColor('#2ca58d'), 4.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(check)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor('#134b5f'))
        painter.drawEllipse(42, 40, 14, 14)

        painter.setBrush(QColor('#ffffff'))
        painter.drawEllipse(46, 44, 3, 3)
        painter.end()
        return QIcon(pixmap)

    def genesis(self):
        self.texts = build_texts()
        self.settings = self._current_settings()
        self.qaction.setText(self.texts.action_label)
        self.qaction.setToolTip(self.texts.action_tooltip)
        self.qaction.setStatusTip(self.texts.action_tooltip)
        self.qaction.setIcon(self._build_icon())
        self.qaction.setIconVisibleInMenu(True)
        self.qaction.triggered.connect(self.run_safe_embed)

    def apply_settings(self):
        self.texts = build_texts()
        self.settings = self._current_settings()

    def _current_settings(self):
        base_plugin = getattr(self, 'interface_action_base_plugin', None)
        site_customization = None
        if base_plugin is not None:
            site_customization = getattr(base_plugin, 'site_customization', None)
        if not site_customization:
            site_customization = getattr(self, 'site_customization', None)
        return load_settings(site_customization)

    def _collect_available_formats(self, book_ids):
        formats = set()
        db = self.gui.current_db.new_api
        for book_id in book_ids:
            try:
                formats.update(fmt.upper() for fmt in db.formats(book_id))
            except Exception:
                continue
        return sorted(formats)

    def _choose_formats(self, book_ids):
        formats = self._collect_available_formats(book_ids)
        if not formats:
            error_dialog(
                self.gui,
                self.texts.error_title,
                self.texts.format_dialog_empty,
                show=True,
            )
            return None

        dialog = FormatSelectionDialog(formats, self.gui)
        if not dialog.exec():
            return None

        selected = dialog.selected_formats()
        if not selected:
            error_dialog(
                self.gui,
                self.texts.error_title,
                self.texts.format_dialog_none_selected,
                show=True,
            )
            return None
        return selected

    def location_selected(self, loc):
        self.qaction.setEnabled(loc == 'library')

    def initialization_complete(self):
        self.qaction.setEnabled(True)

    def library_changed(self, db):
        self.qaction.setEnabled(True)

    def shutting_down(self):
        pass

    def run_safe_embed(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows:
            return error_dialog(
                self.gui,
                self.texts.no_books_selected_title,
                self.texts.no_books_selected_body,
                show=True,
            )

        model = self.gui.library_view.model()
        book_ids = [model.id(row) for row in rows]
        settings = self._current_settings()
        only_fmts = ['EPUB']
        if settings['mode'] == MODE_SELECTABLE_FORMATS:
            only_fmts = self._choose_formats(book_ids)
            if not only_fmts:
                return None

        engine = EmbedMetadataSafeEngine(self.gui.current_db.new_api)
        progress = QProgressDialog(
            self.texts.preparing_progress,
            self.texts.cancel_button_label,
            0,
            len(book_ids),
            self.gui,
        )
        progress.setWindowTitle(self.texts.window_title)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()

        app = QApplication.instance()
        try:
            result = engine.run(
                book_ids,
                self.texts,
                only_fmts=only_fmts,
                progress=progress,
                app=app,
            )
        except Exception:
            return error_dialog(
                self.gui,
                self.texts.error_title,
                traceback.format_exc(),
                show=True,
            )
        finally:
            progress.close()

        if result.cancelled:
            return info_dialog(
                self.gui,
                self.texts.info_title,
                self.texts.operation_cancelled,
                show=True,
            )

        summary = [
            self.texts.summary_selected.format(count=result.selected_books),
            self.texts.summary_repaired.format(count=result.repaired_formats),
            self.texts.summary_processed.format(count=result.processed_books),
        ]
        if result.errors:
            summary.append(self.texts.summary_errors.format(count=len(result.errors)))
            details = '\n\n'.join(result.errors[:3])
            if len(result.errors) > 3:
                details += f'\n\n{self.texts.more_errors_template.format(count=len(result.errors) - 3)}'
            return error_dialog(
                self.gui,
                self.texts.error_title,
                '\n'.join(summary + ['', details]),
                show=True,
            )

        return info_dialog(
            self.gui,
            self.texts.info_title,
            '\n'.join(summary),
            show=True,
        )
