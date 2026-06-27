# Embed Metadata Safe

`Embed Metadata Safe` 是 calibre 的書庫外掛，會在把 metadata 寫回 EPUB 之前先檢查並修復壞掉的 `calibre:user_metadata`。
如果書檔裡的內嵌 metadata 已經損壞，這個外掛可以先清理再寫回，降低保存時出錯或把書檔卡住的機會。

## 功能

- 修復 EPUB 內壞掉的 `calibre:user_metadata`
- 在修復後安全地把 metadata 嵌回選取的書籍
- 以書庫外掛方式執行，不需要離開 calibre
- 保留可自訂的設定對話框

## 使用方式

1. 在 calibre 書庫中選取要處理的 EPUB。
2. 執行 `Embed Metadata Safe`。
3. 讓外掛先修復內嵌 metadata，再完成寫回。

## 原始 GitHub

這個專案目前以本倉庫為主，沒有另外獨立的上游來源。

## 結構

- `src/embed_metadata_safe/`：外掛套件
- `src/plugin-import-name-embed_metadata_safe.txt`：calibre 匯入提示檔

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/embed-metadata-safe.zip`。
