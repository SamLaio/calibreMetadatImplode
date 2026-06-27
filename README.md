# calibreMetadatImplode

`Embed Metadata Safe` for calibre.

這個 plugin 的目標是保留 calibre 內建 `Embed Metadata` 的核心流程，但先替 EPUB 做一層保護：

- 選取書籍
- 先掃掉 EPUB 內壞掉的 `calibre:user_metadata`
- 再呼叫 calibre 自己的 `db.new_api.embed_metadata()`
- 界面會自動偵測正體中文環境，切換成正體中文；其他情況使用英文
- 按鈕已附上圖示
- 有一個設定頁可以切換成「只處理 EPUB」或「可選格式」
- 當選擇「可選格式」時，執行時會跳出格式選擇對話框

相關實作放在：

- [`embed_metadata_safe/__init__.py`](./embed_metadata_safe/__init__.py)
- [`embed_metadata_safe/ui.py`](./embed_metadata_safe/ui.py)
- [`embed_metadata_safe/main.py`](./embed_metadata_safe/main.py)
- [`embed_metadata_safe/safe_epub.py`](./embed_metadata_safe/safe_epub.py)

如果要在 calibre 內安裝，這個資料夾就是 plugin source。

安裝方式：

1. 打開 calibre 的 plugin 安裝流程，選這個 `embed_metadata_safe` 資料夾
2. 或在這個 repo 根目錄執行 `calibre-customize -b .`
3. 重啟 calibre 後，就會看到 `Embed Metadata Safe`

這個版本的策略是保守的：

- 只在選取的書籍上執行
- 只有真的缺 `datatype` 的 `calibre:user_metadata` 才會被清理
- `EPUB` 才會先做 `calibre:user_metadata` 清理
- 實際寫回 metadata 仍然交給 calibre 原生 API
