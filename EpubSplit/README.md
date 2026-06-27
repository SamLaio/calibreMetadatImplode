# EpubSplit

`EpubSplit` 是把一本 EPUB 拆成多本新書的 calibre 外掛。
它特別適合處理合集、雜誌、連載或長篇作品，讓你可以把同一本 EPUB 依章節或 TOC 節點拆成獨立條目。

## 功能

- 依目錄或章節節點拆分 EPUB
- 產生新的獨立書籍與中繼資料
- 支援 EPUB2 與 EPUB3 的結構
- 保留必要資源與內部連結修正

## 使用方式

1. 在 calibre 書庫中選取要拆分的 EPUB。
2. 開啟 `EpubSplit` 外掛。
3. 選擇拆分位置與輸出方式。
4. 讓外掛建立新的書籍條目。

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
