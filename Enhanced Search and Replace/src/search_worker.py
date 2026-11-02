from qt.core import QThread, pyqtSignal
from calibre.ebooks.conversion.search_replace import compile_regular_expression, REGEX_FLAGS
from calibre_plugins.text_regex_p0.core import search, SearchCancelled


class SearchWorker(QThread):
    progress = pyqtSignal(int, str)
    completed = pyqtSignal(object)

    def __init__(self, container, tasks, pattern, template, mode, parent=None):
        super().__init__(parent)
        self.container, self.tasks = container, tasks
        self.pattern, self.template, self.mode = pattern, template, mode

    def run(self):
        rows, snapshots, errors = [], {}, []
        fatal = ''
        try:
            compile_regular_expression(self.pattern, flags=REGEX_FLAGS)
            total = len(self.tasks)
            for i, (name, syntax, raw) in enumerate(self.tasks):
                if self.isInterruptionRequested():
                    break
                def report(fraction, phase):
                    self.progress.emit(int(1000 * (i + fraction) / total), f'{i + 1}/{total}　{name}：{phase}')
                try:
                    report(0, '讀取')
                    if raw is None:
                        raw = self.container.raw_data(name, normalize_to_nfc=False)
                        if isinstance(raw, bytes):
                            raw = raw.decode('utf-8')
                    found = search(raw, self.pattern, self.template, self.mode, syntax,
                                   cancelled=self.isInterruptionRequested, progress=report)
                    snapshots[name] = raw
                    rows.extend(dict(row, name=name) for row in found)
                except SearchCancelled:
                    break
                except Exception as err:
                    message = f'{name}：{err}'
                    errors.append(message)
                    rows.append(dict(name=name, before='', after='', start=0, end=0,
                                     safe=False, error=message, reason=message))
                report(1, f'累計 {len(rows)} 筆')
        except Exception as err:
            fatal = str(err)
        self.completed.emit((rows, snapshots, errors, self.isInterruptionRequested(), fatal))
