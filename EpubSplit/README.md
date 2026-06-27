# EpubSplit

`EpubSplit` calibre 外掛的原始碼目錄，已支援 EPUB2 與 EPUB3 的 TOC 解析與拆分輸出。

## 原始 GitHub

- [JimmXinu/EpubSplit](https://github.com/JimmXinu/EpubSplit)

## 結構

- `src/`：外掛原始碼
- `src/translations/`：語系檔，包含正體中文

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/EpubSplit-zh_TW-release.zip`。
