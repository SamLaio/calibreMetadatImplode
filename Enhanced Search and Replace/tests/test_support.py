from time import monotonic, sleep
from qt.core import QApplication


def scan(dialog):
    dialog.scan()
    deadline = monotonic() + 30
    while dialog.busy:
        QApplication.processEvents()
        sleep(0.001)
        if monotonic() > deadline:
            dialog.cancel_search()
            raise AssertionError('background search did not finish')
