from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field

from calibre_plugins.embed_metadata_safe.i18n import Texts
from calibre_plugins.embed_metadata_safe.safe_epub import sanitize_epub_user_metadata


class CancelledError(RuntimeError):
    pass


@dataclass
class EmbedMetadataSafeResult:
    selected_books: int = 0
    repaired_formats: int = 0
    processed_books: int = 0
    errors: list[str] = field(default_factory=list)
    cancelled: bool = False


class EmbedMetadataSafeEngine:
    def __init__(self, db):
        self.db = db

    def run(self, book_ids, texts: Texts, only_fmts=None, progress=None, app=None):
        book_ids = list(book_ids)
        result = EmbedMetadataSafeResult(selected_books=len(book_ids))
        selected_formats = self._normalize_only_fmts(only_fmts)

        if not book_ids:
            return result

        self._preclean_epubs(
            book_ids,
            result,
            texts=texts,
            only_fmts=selected_formats,
            progress=progress,
            app=app,
        )
        if result.cancelled:
            return result

        def report_error(mi, fmt, tb):
            title = getattr(mi, 'title', texts.unknown_title)
            result.errors.append(texts.embed_error_template.format(title=title, fmt=fmt, traceback=tb))

        def report_progress(done, total, mi):
            if progress is None:
                return
            title = getattr(mi, 'title', texts.working)
            progress.setMaximum(total)
            progress.setValue(done)
            progress.setLabelText(texts.embedding_progress_template.format(done=done, total=total, title=title))
            if app is not None:
                app.processEvents()
            if progress.wasCanceled():
                raise CancelledError()

        try:
            kwargs = {
                'report_error': report_error,
                'report_progress': report_progress,
            }
            if selected_formats is not None:
                kwargs['only_fmts'] = selected_formats
            self.db.embed_metadata(book_ids, **kwargs)
        except CancelledError:
            result.cancelled = True
            return result

        result.processed_books = len(book_ids)
        return result

    def _normalize_only_fmts(self, only_fmts):
        if only_fmts is None:
            return None
        normalized = sorted({fmt.strip().upper() for fmt in only_fmts if fmt and fmt.strip()})
        return normalized or None

    def _preclean_epubs(self, book_ids, result, texts: Texts, only_fmts=None, progress=None, app=None):
        if progress is not None:
            progress.setMaximum(len(book_ids))
            progress.setValue(0)
            progress.setLabelText(texts.checking_progress_prefix)

        selected_formats = {fmt.lower() for fmt in only_fmts} if only_fmts is not None else None
        should_clean_epub = selected_formats is None or 'epub' in selected_formats

        for index, book_id in enumerate(book_ids, start=1):
            if progress is not None:
                progress.setValue(index - 1)
                progress.setLabelText(texts.checking_progress_template.format(index=index, total=len(book_ids)))
                if app is not None:
                    app.processEvents()
                if progress.wasCanceled():
                    result.cancelled = True
                    return

            try:
                formats = tuple(self.db.formats(book_id))
            except Exception as e:
                result.errors.append(texts.format_enum_error_template.format(book_id=book_id, error=e))
                continue

            for fmt in formats:
                normalized_fmt = fmt.lower()
                if should_clean_epub is False or normalized_fmt != 'epub':
                    continue
                try:
                    changed = self._repair_epub_format(book_id, fmt)
                except Exception as e:
                    result.errors.append(
                        texts.repair_error_template.format(book_id=book_id, fmt=fmt, error=e)
                    )
                    continue
                if changed:
                    result.repaired_formats += 1

        if progress is not None:
            progress.setValue(len(book_ids))

    def _repair_epub_format(self, book_id, fmt):
        temp_path = None
        try:
            fd, temp_path = tempfile.mkstemp(suffix='.epub')
            os.close(fd)
            self.db.copy_format_to(book_id, fmt, temp_path)
            changed = sanitize_epub_user_metadata(temp_path)
            if not changed:
                return False
            self.db.add_format(book_id, fmt, temp_path, replace=True, run_hooks=False)
            return True
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
