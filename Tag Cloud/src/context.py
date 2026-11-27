"""Field-aware actions for a word in the cloud."""
from datetime import datetime, timezone
from html import escape
from copy import deepcopy

from qt.core import (QMenu, QDialog, QVBoxLayout, QLabel, QDialogButtonBox,
                     QLineEdit, QComboBox, QDateEdit, QDate, QPlainTextEdit, QDoubleSpinBox, Qt)
from calibre.gui2 import error_dialog, question_dialog
from calibre_plugins.tag_cloud import editing
from calibre_plugins.tag_cloud.core import field_terms


class ValueDialog(QDialog):
    def __init__(self, panel, api, field, term, ids):
        super().__init__(panel)
        self.setWindowTitle('修改' + (api.field_metadata[field]['name'] or field))
        self.kind = editing.datatype(api, field)
        self.field = field
        values = api.all_field_for(field, ids)
        self.original = deepcopy(values)
        raw = next(iter(values.values()))
        initial = term if api.field_metadata[field].get('is_multiple') else raw
        if field == 'identifiers':
            initial = raw[term.split(':', 1)[0]]
        layout = QVBoxLayout(self)
        label = QLabel(f'目前統計範圍內共 {len(ids)} 本書籍；僅修改「{term}」對應的值。')
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setWordWrap(True)
        layout.addWidget(label)
        if self.kind == 'bool':
            self.editor = QComboBox(self)
            self.editor.addItems(['否', '是'])
            self.editor.setCurrentIndex(1 if raw else 0)
        elif self.kind == 'enumeration':
            self.editor = QComboBox(self)
            self.editor.addItems(api.field_metadata[field]['display']['enum_values'])
            self.editor.setCurrentText(str(initial))
        elif self.kind == 'datetime':
            self.editor = QDateEdit(QDate(raw.year, raw.month, raw.day), self)
            self.editor.setDisplayFormat('yyyy-MM-dd')
            self.editor.setCalendarPopup(True)
        elif self.kind == 'rating':
            self.editor = QDoubleSpinBox(self)
            self.editor.setRange(0, 5)
            self.editor.setSingleStep(0.5)
            self.editor.setDecimals(1)
            self.editor.setSuffix(' 星')
            self.editor.setValue(raw / 2)
        elif self.kind == 'comments':
            layout.addWidget(QLabel('完整評論原文（保留 HTML，可在此修改；不使用詞雲摘要取代原文）：'))
            self.editor = QPlainTextEdit(self)
            self.editor.setPlainText(str(raw))
        else:
            self.editor = QLineEdit(str(initial), self)
            if self.kind in ('int', 'float'):
                self.editor.setPlaceholderText('輸入整數' if self.kind == 'int' else '輸入數字')
        self.editor.setAccessibleName('新欄位值')
        layout.addWidget(self.editor)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.resize(520, 240)

    def value(self):
        if self.kind == 'bool':
            return self.editor.currentIndex() == 1
        if self.kind == 'enumeration':
            return self.editor.currentText()
        if self.kind == 'datetime':
            date = self.editor.date()
            return datetime(date.year(), date.month(), date.day(), tzinfo=timezone.utc)
        if self.kind == 'rating':
            rating = self.editor.value() * 2
            if abs(rating - round(rating)) > 0.00001:
                raise ValueError('評分請使用半星為單位。')
            return int(round(rating))
        if self.kind == 'comments':
            return self.editor.toPlainText()
        text = self.editor.text()
        if self.kind == 'int':
            return int(text)
        if self.kind == 'float':
            return float(text)
        return text


def make_menu(panel, term):
    db = panel.action.gui.current_db
    api = db.new_api
    field = panel.field.currentData()
    ids = set(panel.term_books.get(term, ()))
    name = api.field_metadata[field]['name'] or field
    menu = QMenu(panel.cloud)
    menu.setToolTipsVisible(True)
    menu.addSection((name + '：' + term).replace('&', '&&'))
    edit = menu.addAction('修改' + name + '…')
    edit.setData('edit')
    remove = menu.addAction('移除' + name + '…')
    remove.setData('remove')
    reason = editing.readonly_reason(api, field)
    if not ids:
        reason = '此詞已沒有對應書籍，請重新整理。'
    if reason:
        edit.setEnabled(False)
        remove.setEnabled(False)
        edit.setToolTip(reason)
        remove.setToolTip(reason)
    elif editing.datatype(api, field) == 'comments' and len(set(api.all_field_for(field, ids).values())) > 1:
        edit.setEnabled(False)
        edit.setToolTip('此摘要對應不同完整評論，請逐本編輯。')
    if field == 'title':
        remove.setEnabled(False)
        remove.setToolTip('書名不能留空，請使用修改書名。')
    edit.triggered.connect(lambda: edit_term(panel, term, field, db, ids))
    remove.triggered.connect(lambda: edit_term(panel, term, field, db, ids, remove=True))
    return menu


def show_menu(panel, position):
    anchor = panel.cloud.anchorAt(position)
    if not anchor.startswith('tag:'):
        return
    try:
        term = panel.names[int(anchor[4:])]
    except (ValueError, IndexError):
        return
    make_menu(panel, term).exec(panel.cloud.viewport().mapToGlobal(position))


def edit_term(panel, term, field, db, ids, remove=False):
    committed = False
    try:
        if panel.action.gui.current_db is not db or panel.field.currentData() != field:
            raise ValueError('書庫或欄位已切換，請重新開啟右鍵選單。')
        api = db.new_api
        reason = editing.readonly_reason(api, field)
        if reason:
            raise ValueError(reason)
        value = None
        if not remove:
            dialog = ValueDialog(panel, api, field, term, ids)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            value = dialog.value()
        change = editing.prepare(api, field, term, ids, value, remove)
        if not remove and change.before != dialog.original:
            raise ValueError('編輯期間欄位內容已變更，未寫入；請重新整理後重試。')
        label = api.field_metadata[field]['name'] or field
        verb = '移除' if remove else '修改'
        preview = '清空此值' if remove else '、'.join(field_terms(change.value, editing.datatype(api, field)))
        if len(preview) > 240:
            preview = preview[:240] + '…（完整原文已於編輯視窗顯示）'
        message = (f'即將{verb}目前統計範圍內 {len(change.before)} 本書籍的「{label}」。\n'
                   f'原詞：{term}\n新值：{preview}\n'
                   '其他欄位及多值欄位中的其他值會保留。')
        if field == 'authors' and remove:
            message += '\n若移除後沒有作者，會改為「未知」。'
        if editing.datatype(api, field) == 'series':
            message += '\n修改時保留各書系列編號；移除時將編號重設為 1。'
        if not question_dialog(panel, verb + label, '<p>' + escape(message).replace('\n', '<br>') + '</p>', default_yes=False):
            return
        if panel.action.gui.current_db is not db or panel.field.currentData() != field:
            raise ValueError('確認期間書庫或欄位已切換，未寫入。')
        changed = editing.apply(api, change)
        committed = True
        if term in panel.selected:
            panel.selected.remove(term)
            if not remove:
                new_terms = ([term.split(':', 1)[0] + ':' + str(change.value)] if field == 'identifiers'
                             else field_terms(change.value, editing.datatype(api, field)))
                actual = {word for raw in api.all_field_for(field, ids).values()
                          for word in field_terms(raw, editing.datatype(api, field))}
                for candidate in new_terms:
                    word = next((word for word in actual if word.casefold() == candidate.casefold()), None)
                    if word is not None and word not in panel.selected:
                        panel.selected.append(word)
        model = panel.action.gui.library_view.model()
        model.refresh_ids(list(changed))
        model.research()
        panel.action.gui.tags_view.recount()
        panel.reload()
        panel.apply_search()
    except Exception as error:
        message = '資料已寫入，但介面更新失敗。請手動重新整理。' if committed else '無法完成操作。'
        error_dialog(panel, '詞雲書目修改', message, det_msg=str(error), show=True)
