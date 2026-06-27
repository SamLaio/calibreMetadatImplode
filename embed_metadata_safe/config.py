from __future__ import annotations

from qt.core import QLabel, QButtonGroup, QRadioButton, QVBoxLayout, QWidget

from calibre_plugins.embed_metadata_safe.i18n import build_texts
from calibre_plugins.embed_metadata_safe.settings import (
    MODE_EPUB_ONLY,
    MODE_SELECTABLE_FORMATS,
    dump_settings,
    load_settings,
)


class EmbedMetadataSafeConfigWidget(QWidget):
    def __init__(self, site_customization: str | None = None, parent=None):
        super().__init__(parent)
        self.texts = build_texts()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel(self.texts.settings_help)
        title.setWordWrap(True)
        layout.addWidget(title)

        group_title = QLabel(self.texts.mode_section_title)
        group_title.setStyleSheet('font-weight: 600;')
        layout.addWidget(group_title)

        self.mode_group = QButtonGroup(self)
        self.epub_only = QRadioButton(self.texts.mode_epub_only_label)
        self.selectable = QRadioButton(self.texts.mode_selectable_formats_label)
        self.mode_group.addButton(self.epub_only)
        self.mode_group.addButton(self.selectable)

        layout.addWidget(self.epub_only)
        epub_desc = QLabel(self.texts.mode_epub_only_description)
        epub_desc.setWordWrap(True)
        epub_desc.setIndent(18)
        layout.addWidget(epub_desc)

        layout.addWidget(self.selectable)
        selectable_desc = QLabel(self.texts.mode_selectable_formats_description)
        selectable_desc.setWordWrap(True)
        selectable_desc.setIndent(18)
        layout.addWidget(selectable_desc)

        layout.addStretch(1)

        self.load_site_customization(site_customization)

    def load_site_customization(self, site_customization: str | None):
        settings = load_settings(site_customization)
        if settings['mode'] == MODE_SELECTABLE_FORMATS:
            self.selectable.setChecked(True)
        else:
            self.epub_only.setChecked(True)

    def get_site_customization(self) -> str:
        mode = MODE_SELECTABLE_FORMATS if self.selectable.isChecked() else MODE_EPUB_ONLY
        return dump_settings(mode)
