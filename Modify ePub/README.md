# Modify ePub

版本：**1.8.12.1 正體中文修訂版**；最低 calibre：**3.48.0**；授權：GPL v3。
作者：Grant Drake，另有 Robert L. Hood、Leigh Parry 與 Charles Haley 的貢獻。

## 用途與操作

直接清理、修補 EPUB 的內容、樣式、封面與中繼資料，避免為小幅修改而重新轉檔。

1. 在 calibre 書庫選取要處理的 EPUB，開啟 Modify ePub。
2. 勾選需要的處理選項並執行。
3. 檢查記錄後確認回寫；若停用儲存確認，外掛會直接回寫。操作前請先備份。

## 安裝與打包

從 [v1.3.17 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.17) 下載 `Modify ePub-zh_TW-release.zip`，或在根目錄執行 `python -B build_release.py`。於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝後重新啟動。

## 更新與本地修改

- 採用上游 1.8.12 的 calibre 9.18 封面標題、語言替換修正，並同步日文翻譯。
- 補齊上游漏改的「移除封面」建構參數，避免執行時失敗。
- 保留上游 1.8.11 的非數值 CSS 邊距修正，以及本倉庫中文描述、說明、邊距回歸測試。
- 保留 `zh_TW`、`zh_Hant`、`zh_Hant_TW`，涵蓋 127 個介面字串。

## 來源

[kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/0c15171817995eaf819fce75bf2966cd5aefda3d/modify_epub)，固定提交 `0c15171817995eaf819fce75bf2966cd5aefda3d`，2026-11-08 核對。
完整更新紀錄見 [CHANGELOG](src/CHANGELOG.md)。

## 驗證與限制

```powershell
calibre-debug -e "Modify ePub/tests/test_margins.py"
calibre-debug -e "Modify ePub/tests/test_covers.py"
```

Windows、calibre 9.17.0 通過四組邊距與兩組封面測試。封面測試涵蓋移除封面呼叫、SVG／非 SVG 模板及新舊中繼資料 API；calibre 9.18 API 以模擬方式驗證，尚未在實際 9.18 或使用者書庫回寫驗收。
