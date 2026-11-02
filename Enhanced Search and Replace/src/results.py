from qt.core import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt

HEADERS = ['勾選', '原文', '取代預覽', '來源位置', '狀態／原因', '檔案']


class ResultsModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(HEADERS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return HEADERS[section] if orientation == Qt.Orientation.Horizontal else str(section + 1)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, column = self.rows[index.row()], index.column()
        if column == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                return Qt.CheckState.Checked if row.get('checked') else Qt.CheckState.Unchecked
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole, Qt.ItemDataRole.UserRole):
            values = [row['before'], row['after'], row['start'], row['reason'], row['name']]
            value = values[column - 1]
            if role == Qt.ItemDataRole.UserRole:
                return value
            text = str(value)
            limit = 5000 if role == Qt.ItemDataRole.ToolTipRole else 400
            return text if len(text) <= limit else text[:limit] + '…'

    def flags(self, index):
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.isValid() and index.column() == 0:
            if self.rows[index.row()].get('done'):
                return Qt.ItemFlag.NoItemFlags
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
            row = self.rows[index.row()]
            if not row.get('done'):
                row['checked'] = value == Qt.CheckState.Checked or value == Qt.CheckState.Checked.value
                self.dataChanged.emit(index, index, [role])
                return True
        return False

    def reset_rows(self, rows):
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def changed(self):
        if self.rows:
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.rows) - 1, 5), [])


class ResultsFilter(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = 'all'
        self.setDynamicSortFilter(False)
        self.setSortRole(Qt.ItemDataRole.UserRole)

    def filterAcceptsRow(self, row_number, parent):
        row = self.sourceModel().rows[row_number]
        failed = bool(row.get('failed') or row.get('error'))
        return (self.status == 'all' or
                self.status == 'done' and bool(row.get('done')) or
                self.status == 'failed' and failed and not row.get('done') or
                self.status == 'pending' and not row.get('done') and not failed)
