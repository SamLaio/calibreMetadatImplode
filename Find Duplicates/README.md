# Find Duplicates

最低 calibre：**2.0.0**；目前外掛版本為 **1.10.11**。

`Find Duplicates` 是用來找出 calibre 書庫中可能重複書籍的外掛。
它會依照你設定的比對規則整理候選項目，讓你再人工確認哪些書應該合併、保留或刪除。

## 目前版本與官方比對

目前為 **1.10.11 正體中文整合版（2026-10-23）**，從本倉庫的 1.10.10 更新。
比對來源為 [官方下載包](https://plugins.calibre-ebook.com/131017.zip) 與 [官方更新](https://github.com/kiwidude68/calibre_plugins/commit/91b0f23da54fa8f020ba387e1f13a1321706c0ff)。

| 項目 | 整合結果 |
| --- | --- |
| 官方語系 | 加入捷克文、法文、日文、韓文、斯洛伐克文、塞爾維亞文（拉丁字母）及瑞典文，並納入官方發行包中的其他已編譯語系。 |
| 本倉庫正體中文 | 保留 `zh_TW`、`zh_Hant`、`zh_Hant_TW` 與翻譯來源，確認涵蓋全部 179 個介面字串。 |
| 既有修改 | 保留中文說明與外掛描述。重複書籍比對演算法與新版相同；同步刪除一行無效註解。 |

## 功能

- 根據 metadata 尋找可能重複的書籍
- 協助檢查作者、標題、格式、系列、出版社、標籤與識別碼等候選項目
- 保留人工判斷空間，避免自動誤刪
- 可自訂比對規則與顯示方式

## 使用方式

1. 在 calibre 書庫中開啟 `Find Duplicates`。
2. 選擇要比對的條件與搜尋方式。
3. 檢視外掛整理出的候選結果。
4. 手動處理重複書目。

## 安裝

從 [本倉庫發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases) 下載 `Find Duplicates-zh_TW-release.zip`，於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。

## 原始 GitHub

- [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/find_duplicates)：目前官方維護來源。
- [JimmXinu/kiwidude68_calibre_plugins](https://github.com/JimmXinu/kiwidude68_calibre_plugins/tree/main/find_duplicates)：先前匯入來源，仍停留在 1.10.10。

## 結構

- `src/`：外掛原始碼
- `src/translations/`：語系檔，包含正體中文

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/Find Duplicates-zh_TW-release.zip`。

## 來源與修改核對（2026-11-01）

- 固定上游基準：[1.10.11](https://github.com/kiwidude68/calibre_plugins/tree/91b0f23da54fa8f020ba387e1f13a1321706c0ff/find_duplicates)。
- 本倉庫版號：**1.10.11**。
- 頂層 Python 比較確認比對核心與固定上游基準一致；差異為描述及共用模組匯入路徑。另保留正體中文資源與說明。早期 JimmXinu 分支的匯入紀錄不等同於目前採用的上游基準。

本次對照固定來源的頂層 Python 檔案，未逐一比較全部圖片、翻譯與巢狀套件資源；此核對不是新一輪完整功能測試。
