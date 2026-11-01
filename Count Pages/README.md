# Count Pages

最低 calibre：**3.48.0**；目前外掛版本為 **1.15.3**。

`Count Pages` 是用來計算頁數、字數與可讀性統計的 calibre 外掛。
它可以把結果寫入自訂欄位，也能依設定從外部來源抓取統計資料，適合做閱讀進度、頁數估算或 Kindle APNX 相關流程。

## 目前版本與官方比對

目前為 **1.15.3 正體中文整合版（2026-10-23）**，從本倉庫的 1.15.2 更新。
比對來源為 [官方下載包](https://plugins.calibre-ebook.com/134000.zip) 與 [官方更新](https://github.com/kiwidude68/calibre_plugins/commit/d46d9197ac2f78e98f2a774a6afbf8d54d9ce68a)。

| 項目 | 整合結果 |
| --- | --- |
| Goodreads 頁數下載 | 採用官方 `.xml` 網址修正，保留原有頁數解析與來源備援流程。 |
| 官方語系 | 更新捷克文、法文及俄文，新增日文、韓文、斯洛伐克文、塞爾維亞文（拉丁字母）及瑞典文。 |
| 本倉庫修改 | 保留中文說明、外掛描述、批次處理與三個正體中文語系別名；補齊 12 個提示翻譯，涵蓋全部 119 個介面字串。 |
| 英文斷句模型 | 還原與官方一致的 `nltk_lite/english.pickle`，並加入二進位屬性，避免 Windows 換行轉換破壞模型。 |

Goodreads 仍屬外部網站服務，實際連線結果可能受網站防護或頁面變動影響。

## 功能

- 計算頁數、字數與可讀性統計
- 把結果寫入 calibre 自訂欄位
- 支援依書籍內容估算，或從外部來源下載統計資料
- 可搭配 Kindle APNX 或其他頁數工作流程
- 內建正體中文介面語系

## 使用方式

1. 先在 calibre 建好要存放結果的自訂欄位。
2. 對選取書籍執行 `Count Pages`。
3. 依需求選擇估算或下載來源。
4. 將頁數、字數與可讀性統計寫回書庫。

## 安裝

從 [本倉庫發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases) 下載 `Count Pages-zh_TW-release.zip`，於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。

## 原始 GitHub

- [kiwidude68/calibre_plugins/tree/main/count_pages](https://github.com/kiwidude68/calibre_plugins/tree/main/count_pages)

## 說明

- 這個外掛可以估算或下載書籍的頁數、字數與可讀性統計。
- 目前這個倉庫收錄的是外掛發行內容，可直接納入 calibre 外掛打包流程。

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/Count Pages-zh_TW-release.zip`。

## 測試

```powershell
calibre-debug -e "Count Pages/tests/test_update.py"
```

測試使用離線頁面驗證 Goodreads 網址、頁數解析及來源備援，並載入實際英文斷句模型，檢查三個正體中文語系的完整覆蓋率。

## 來源與修改核對（2026-11-01）

- 固定上游基準：[1.15.3](https://github.com/kiwidude68/calibre_plugins/tree/d46d9197ac2f78e98f2a774a6afbf8d54d9ce68a/count_pages)。
- 本倉庫版號：**1.15.3**。
- 頂層 Python 差異為描述及共用模組匯入路徑，Goodreads `.xml` 網址修正來自上游。另有正體中文翻譯、本地測試，以及 `src/nltk_lite/english.pickle` 的二進位屬性設定（`.gitattributes`），避免模型被換行轉換。

本次對照固定來源的頂層 Python 檔案，未逐一比較全部圖片、翻譯與巢狀套件資源；此核對不是新一輪完整功能測試。
