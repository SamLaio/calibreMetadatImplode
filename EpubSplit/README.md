# EpubSplit

版本：**3.12.0（本倉庫修訂版）**；最低 calibre：**3.48.0**。截至 2026-10-23，官方正式版仍為 3.12.0。

`EpubSplit` 是把一本 EPUB 拆成多本新書的 calibre 外掛。
它特別適合處理合集、雜誌、連載或長篇作品，讓你可以把同一本 EPUB 依章節或 TOC 節點拆成獨立條目。

## 功能

- 依目錄或章節節點拆分 EPUB
- 產生新的獨立書籍與中繼資料
- 支援 EPUB2 的 NCX 目錄；本倉庫另加入 EPUB3 導覽目錄解析，並依來源版本輸出 EPUB2 或 EPUB3
- 保留必要資源與內部連結修正
- HTML 解析器依序嘗試 `html5lib`、`lxml` 與 `html.parser`

## 使用方式

1. 在 calibre 書庫中選取一本要拆分、且未受 DRM 保護的 EPUB。
2. 開啟 `EpubSplit` 外掛。
3. 選擇拆分位置與輸出方式。
4. 讓外掛建立新的書籍條目。

## 安裝

從 [本倉庫發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases) 下載 `EpubSplit-zh_TW-release.zip`，於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。上游官方 ZIP 不含本倉庫的 EPUB3 修改。

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
