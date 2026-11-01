# Goodreads

從 Goodreads 下載書籍中繼資料與封面，於 calibre「下載中繼資料」中使用。

## 來源與版本

- 匯入來源：使用者提供的已安裝 `Goodreads.zip`，原始版本 1.10.0。
- 作者：Grant Drake；保留原始 GPL v3 宣告與翻譯資源。
- 本倉庫修正版：1.10.1，最低 calibre 宣告沿用 2.0.0；未在舊版實測。
- 上游來源：[kiwidude68/calibre_plugins 的 Goodreads 外掛](https://github.com/kiwidude68/calibre_plugins/tree/main/goodreads)。
- 原始說明與歷史保留於 `src/README.md`、`src/CHANGELOG.md`。

2026-11-01 已比對上游原始檔，確認為同一隻外掛：名稱、作者、原始 README 與設定程式 `config.py` 均與匯入來源一致。上游當時版本為 1.10.0，其更新紀錄包含改用 JSON 自動完成搜尋，與匯入外掛相符。

本倉庫的 **1.10.1 是基於上游 1.10.0 的本地修正版，並非上游正式發行版本**。本次來源比對未逐一核對所有翻譯資源。

## 本地修正（2026-11-01）

- 書名與作者須符合全部有效詞，避免只命中一個詞或詞的一部分就接受錯書。
- ISBN／ASIN 搜尋結果須與詳細頁識別碼吻合；不吻合或查詢失敗時，可改用書名與作者搜尋。
- 依指定書籍及其引用取得系列、作品資料，避免混用頁面中其他書籍的節點。
- 封面回應未提供 `Content-Length` 時仍可使用；保留過小圖片的排除規則。
- ISBN-13 為空時使用 ISBN-10；缺少作品日期時使用版本出版日期。
- 沒有評分或票數時不產生無效識別碼；修正錯誤頁訊息的節點處理。
- 缺少書籍 JSON 時最多請求三次，重試間隔一秒；傳遞呼叫端指定的連線逾時。

## 安裝與驗證

可從本倉庫 [v1.3.6 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.6) 下載 `Goodreads.zip`；此安裝包為本倉庫修正版。

在專案根目錄執行 `python build_release.py`，再於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」選擇 `dist/Goodreads.zip`，重新啟動 calibre。

離線回歸檢查：

```powershell
calibre-debug -e "Goodreads/tests/test_goodreads.py"
```

已通過 8 組離線回歸測試，並以《61 Hours》（Goodreads ID：6977769）實際驗證詳細頁、系列與封面解析。網站結構或存取限制變動仍可能影響下載；未測試 calibre 圖形介面安裝與所有舊版相容性。

## 來源與修改核對（2026-11-01）

- 固定上游基準：[1.10.0](https://github.com/kiwidude68/calibre_plugins/tree/2a2dbb2469ec6e68179cd71ba943db240045d097/goodreads)。
- 本倉庫版號：**1.10.1**。
- 原始來源為使用者提供的 1.10.0 安裝包，本次以固定上游提交交叉核對。主要功能差異在 `src/__init__.py` 與 `src/worker.py`，包括前述比對、引用關係、缺值及連線處理；`config.py` 與固定基準一致，共用模組只調整外掛匯入路徑。

本次對照固定來源的頂層 Python 檔案，未逐一比較全部圖片、翻譯與巢狀套件資源；此核對不是新一輪完整功能測試。
