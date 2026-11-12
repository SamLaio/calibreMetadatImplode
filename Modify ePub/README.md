# Modify ePub

版本：**1.8.14.1 正體中文修訂版**；最低 calibre：**3.48.0**；授權：GPL v3。
作者：Grant Drake，另有 Robert L. Hood、Leigh Parry 與 Charles Haley 的貢獻。

## 用途與操作

直接清理、修補 EPUB 的內容、樣式、封面與中繼資料，避免為小幅修改而重新轉檔。

1. 在 calibre 書庫選取要處理的 EPUB，開啟 Modify ePub。
2. 勾選需要的處理選項並執行。
3. 檢查記錄後確認回寫；若停用儲存確認，外掛會直接回寫。操作前請先備份。

## 安裝與打包

從 [v1.3.19 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.19) 下載 `Modify ePub-zh_TW-release.zip`，或在根目錄執行 `python -B build_release.py`。於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝後重新啟動。

## 更新與本地修改

- 採用上游 1.8.14 的封面移除、替換及 calibre 9.18 標題與語言修正。檢查封面文字時保留原有樣式及標題。
- 補齊上游漏改的「移除封面」建構參數，避免執行時失敗。
- 保留上游 1.8.11 的非數值 CSS 邊距修正，以及本倉庫中文描述、說明、邊距回歸測試。
- 保留 `zh_TW`、`zh_Hant`、`zh_Hant_TW`，涵蓋 127 個介面字串。

## 來源

[kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/683c9968aa0302212ee88d769eb598788c88a8b1/modify_epub)，固定提交 `683c9968aa0302212ee88d769eb598788c88a8b1`，2026-11-12 核對。
完整更新紀錄見 [CHANGELOG](src/CHANGELOG.md)。

## 驗證與限制

```powershell
calibre-debug -e "Modify ePub/tests/test_margins.py"
calibre-debug -e "Modify ePub/tests/test_covers.py"
```

Windows、calibre 9.18.0 通過四組邊距與三組封面測試。封面測試涵蓋移除封面呼叫、SVG／非 SVG 模板、新舊中繼資料 API 與封面文字檢查。模板測試使用模擬資料。
