# Embed Metadata Safe

`Embed Metadata Safe` calibre 外掛的原始碼目錄。

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
