from calibre.customize.conversion import OutputFormatPlugin, OptionRecommendation
from calibre.ebooks.conversion.plugins.txt_output import TXTOutput, NEWLINE_TYPES



class MarkdownOutput(TXTOutput):
    name = "Markdown Output"
    author = "The_book"
    description = "將書籍轉換為 Markdown，保留連結、圖片參照與可選目錄。"
    version = (1, 0, 3, 1)
    minimum_calibre_version = (5, 0, 0)
    file_type = "md"
    commit_name = "md_output"
    ui_data = {
        "newline_types": NEWLINE_TYPES,
    }

    options = {
        OptionRecommendation(
            name="newline",
            recommended_value="system",
            level=OptionRecommendation.LOW,
            short_switch="n",
            choices=NEWLINE_TYPES,
            help=_(
                '換行格式，可選 %s。預設為 system（使用目前作業系統的換行格式）。old_mac 適用於 Mac OS 9 及更舊版本；macOS 請用 unix。'
            )
            % sorted(NEWLINE_TYPES),
        ),
        OptionRecommendation(
            name="txt_output_encoding",
            recommended_value="utf-8",
            level=OptionRecommendation.LOW,
            help=_(
                '指定輸出文件的字元編碼，預設為 utf-8。'
            ),
        ),
        OptionRecommendation(
            name="inline_toc",
            recommended_value=False,
            level=OptionRecommendation.LOW,
            help=_('在書籍開頭加入目錄。'),
        ),
        OptionRecommendation(
            name="max_line_length",
            recommended_value=0,
            level=OptionRecommendation.LOW,
            help=_(
                '每行最多字元數。優先在上限前的空白處換行；找不到時使用其後的空白，可能超過上限。最少為 25 字元，0 表示不自動換行。'
            ),
        ),
        OptionRecommendation(
            name="force_max_line_length",
            recommended_value=False,
            level=OptionRecommendation.LOW,
            help=_(
                '沒有空白時也依每行字元上限強制換行，並允許上限低於一般最小值。'
            ),
        ),
        OptionRecommendation(
            name="keep_links",
            recommended_value=True,
            level=OptionRecommendation.LOW,
            help=_('保留文件中的連結。'),
        ),
        OptionRecommendation(
            name="keep_image_references",
            recommended_value=True,
            level=OptionRecommendation.LOW,
            help=_('保留文件中的圖片參照。'),
        ),
    }

    def convert(self, oeb_book, output_path, input_plugin, opts, log):
        setattr(opts, "txt_output_formatting", "markdown")
        TXTOutput.convert(self, oeb_book, output_path, input_plugin, opts, log)
    def gui_configuration_widget(
        self, parent, get_option_by_name, get_option_help, db, book_id=None
    ):
        from calibre_plugins.markdown_output.ui import PluginWidget
        return PluginWidget(parent, get_option_by_name, get_option_help, db, book_id)