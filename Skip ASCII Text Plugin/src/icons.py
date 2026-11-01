try:
    from qt.core import QColor, QFont, QIcon, QPainter, QPen, QPixmap
except ImportError:
    from PyQt5.Qt import QColor, QFont, QIcon, QPainter, QPen, QPixmap


def create_icon():
    image = QPixmap(128, 128)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor('#127b96'), 2))
    painter.setBrush(QColor('#127b96'))
    painter.drawRoundedRect(12, 6, 88, 110, 12, 12)
    font = QFont('Microsoft JhengHei')
    font.setPixelSize(66)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor('#ffffff'))
    painter.drawText(22, 80, '文')
    painter.setBrush(QColor('#218a56'))
    painter.setPen(QPen(QColor('#ffffff'), 4))
    painter.drawEllipse(75, 77, 48, 48)
    painter.setPen(QPen(QColor('#ffffff'), 7))
    painter.drawLine(86, 101, 96, 111)
    painter.drawLine(96, 111, 113, 92)
    painter.end()
    return QIcon(image)
