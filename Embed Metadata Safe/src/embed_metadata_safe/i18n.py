from __future__ import annotations

from dataclasses import dataclass

from qt.core import QApplication, QLocale


def current_locale() -> QLocale:
    app = QApplication.instance()
    if app is not None:
        try:
            return app.locale()
        except Exception:
            pass
    return QLocale.system()


def is_traditional_chinese_locale(locale: QLocale | None = None) -> bool:
    locale = locale or current_locale()
    candidates = []

    try:
        candidates.append(locale.name())
    except Exception:
        pass

    try:
        for value in locale.uiLanguages():
            candidates.append(value)
    except Exception:
        pass

    normalized = [value.replace('-', '_').lower() for value in candidates if value]
    return any(
        value.startswith(('zh_tw', 'zh_hk', 'zh_mo')) or 'zh_hant' in value
        for value in normalized
    )


@dataclass(frozen=True)
class Texts:
    action_label: str
    action_tooltip: str
    window_title: str
    cancel_button_label: str
    settings_title: str
    settings_help: str
    mode_section_title: str
    mode_epub_only_label: str
    mode_selectable_formats_label: str
    mode_epub_only_description: str
    mode_selectable_formats_description: str
    no_books_selected_title: str
    no_books_selected_body: str
    preparing_progress: str
    checking_progress_prefix: str
    checking_progress_template: str
    embedding_progress_template: str
    operation_cancelled: str
    summary_selected: str
    summary_repaired: str
    summary_processed: str
    summary_errors: str
    more_errors_template: str
    error_title: str
    info_title: str
    format_dialog_title: str
    format_dialog_body: str
    format_dialog_empty: str
    format_dialog_none_selected: str
    format_enum_error_template: str
    repair_error_template: str
    embed_error_template: str
    unknown_title: str
    working: str


def build_texts(locale: QLocale | None = None) -> Texts:
    if is_traditional_chinese_locale(locale):
        return Texts(
            action_label='安全嵌入詮釋資料',
            action_tooltip='先修正 EPUB 內壞掉的 calibre:user_metadata，再嵌入詮釋資料',
            window_title='安全嵌入詮釋資料',
            cancel_button_label='取消',
            settings_title='安全嵌入詮釋資料',
            settings_help='選擇這個工具的處理模式。',
            mode_section_title='處理模式',
            mode_epub_only_label='只處理 EPUB',
            mode_selectable_formats_label='可選格式',
            mode_epub_only_description='只對 EPUB 格式進行修正與嵌入。',
            mode_selectable_formats_description='執行時會讓你勾選要處理的格式。',
            no_books_selected_title='安全嵌入詮釋資料',
            no_books_selected_body='請先選取一本或多本書。',
            preparing_progress='準備詮釋資料中...',
            checking_progress_prefix='檢查詮釋資料中...',
            checking_progress_template='檢查詮釋資料：{index}/{total}',
            embedding_progress_template='嵌入詮釋資料：{done}/{total} - {title}',
            operation_cancelled='作業已取消。',
            summary_selected='已選取書籍：{count}',
            summary_repaired='已修正 EPUB 格式：{count}',
            summary_processed='已處理書籍：{count}',
            summary_errors='錯誤數：{count}',
            more_errors_template='... 還有 {count} 筆。',
            error_title='發生錯誤',
            info_title='完成',
            format_dialog_title='選擇格式',
            format_dialog_body='請勾選要處理的格式：',
            format_dialog_empty='目前選取的書籍沒有可用格式。',
            format_dialog_none_selected='請至少勾選一種格式。',
            format_enum_error_template='書號 {book_id}：無法列出格式：{error}',
            repair_error_template='書號 {book_id} [{fmt}]：修正 EPUB 時發生錯誤：{error}',
            embed_error_template='{title} [{fmt}]\n{traceback}',
            unknown_title='未知書名',
            working='處理中',
        )

    return Texts(
        action_label='Embed Metadata Safe',
        action_tooltip='Repair malformed EPUB calibre:user_metadata before embedding metadata',
        window_title='Embed Metadata Safe',
        cancel_button_label='Cancel',
        settings_title='Embed Metadata Safe',
        settings_help='Choose how this action processes formats.',
        mode_section_title='Processing mode',
        mode_epub_only_label='EPUB only',
        mode_selectable_formats_label='Selectable formats',
        mode_epub_only_description='Repair and embed metadata only for EPUB files.',
        mode_selectable_formats_description='You will choose which formats to process when running the action.',
        no_books_selected_title='Embed Metadata Safe',
        no_books_selected_body='Please select one or more books first.',
        preparing_progress='Preparing metadata...',
        checking_progress_prefix='Checking metadata...',
        checking_progress_template='Checking metadata: {index}/{total}',
        embedding_progress_template='Embedding metadata: {done}/{total} - {title}',
        operation_cancelled='Operation cancelled.',
        summary_selected='Selected books: {count}',
        summary_repaired='EPUB formats repaired: {count}',
        summary_processed='Books processed: {count}',
        summary_errors='Errors: {count}',
        more_errors_template='... and {count} more.',
        error_title='Error',
        info_title='Done',
        format_dialog_title='Choose formats',
        format_dialog_body='Select the formats to process:',
        format_dialog_empty='No usable formats were found in the selected books.',
        format_dialog_none_selected='Please select at least one format.',
        format_enum_error_template='Book {book_id}: could not enumerate formats: {error}',
        repair_error_template='Book {book_id} [{fmt}]: error while repairing EPUB: {error}',
        embed_error_template='{title} [{fmt}]\n{traceback}',
        unknown_title='Unknown title',
        working='Working',
    )
