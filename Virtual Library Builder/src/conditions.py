from qt.core import QTableWidget, QComboBox, QLineEdit, QPushButton, QHeaderView, pyqtSignal
from calibre_plugins.virtual_library_builder import core


class ConditionsTable(QTableWidget):
    changed = pyqtSignal()

    def __init__(self, metadata):
        super().__init__(0, 5)
        self.metadata = metadata
        self.setHorizontalHeaderLabels(['欄位', '比較方式', '值／天數', '與前面條件', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().moveSection(3, 0)

    def update_joins(self):
        for row in range(self.rowCount()):
            self.cellWidget(row, 3).setEnabled(row > 0)

    def add_row(self):
        row = self.rowCount()
        self.insertRow(row)
        field = QComboBox()
        for key, meta in self.metadata.items():
            field.addItem(str(meta.get('name') or key) + ' (' + key + ')', key)
        field.setCurrentIndex(max(0, field.findData('tags')))
        op = QComboBox()
        value = QLineEdit()
        remove = QPushButton('移除')
        join = QComboBox()
        join.addItem('交集 AND', 'and')
        join.addItem('聯集 OR', 'or')
        join.setEnabled(row > 0)
        join.currentIndexChanged.connect(lambda *args: self.changed.emit())
        for col, widget in enumerate((field, op, value, join, remove)):
            self.setCellWidget(row, col, widget)
        def update_ops():
            datatype = self.metadata[field.currentData()]['datatype']
            pairs = [('等於', 'eq'), ('不等於', 'ne')]
            if datatype in core.TEXT_TYPES:
                pairs += [('包含', 'contains'), ('不包含', 'not_contains'), ('正規表示式', 'regex')]
            elif datatype != 'bool':
                pairs += [('大於／晚於', 'gt'), ('小於／早於', 'lt'), ('大於等於', 'ge'), ('小於等於', 'le')]
            if datatype == 'datetime':
                pairs += [('最近 N 天', 'recent_days'), ('N 天以前', 'older_days'), ('今天', 'today'), ('昨天', 'yesterday'), ('本月', 'thismonth'), ('今年', 'thisyear')]
            if datatype != 'bool':
                pairs += [('空白', 'empty'), ('非空白', 'not_empty')]
            op.blockSignals(True)
            op.clear()
            for text, key in pairs:
                op.addItem(text, key)
            op.blockSignals(False)
            update_value()
        def update_value():
            operator = op.currentData()
            datatype = self.metadata[field.currentData()]['datatype']
            value.setEnabled(operator not in ('today', 'yesterday', 'thismonth', 'thisyear', 'empty', 'not_empty'))
            value.setPlaceholderText('天數，例如 30' if operator in ('recent_days', 'older_days') else 'YYYY-MM-DD' if datatype == 'datetime' else '是／否' if datatype == 'bool' else '0～5 星' if datatype == 'rating' else '輸入值')
            self.changed.emit()
        def remove_row():
            for index in range(self.rowCount()):
                if self.cellWidget(index, 0) is field:
                    self.removeRow(index)
                    self.update_joins()
                    self.changed.emit()
                    break
        field.currentIndexChanged.connect(update_ops)
        op.currentIndexChanged.connect(update_value)
        value.textChanged.connect(lambda *args: self.changed.emit())
        remove.clicked.connect(remove_row)
        update_ops()

    def generated(self):
        terms = []
        for row in range(self.rowCount()):
            field, op, value = [self.cellWidget(row, col) for col in range(3)]
            key = field.currentData()
            terms.append(core.advanced_condition(key, self.metadata[key]['datatype'], op.currentData(), value.text()))
        joins = [self.cellWidget(row, 3).currentData() for row in range(self.rowCount())]
        return core.row_expression(terms, joins)
