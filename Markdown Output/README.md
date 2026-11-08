# Markdown Output

版本：**1.0.3.1**；原作者：**The_book**。基於上游 **1.0.3**，本倉庫負責正體中文與下列修訂；隨整合版 v1.3.17 發布。最低 calibre 5.0（Python 3），實測為 9.18.0。

## 用途

將電子書輸出為 Markdown，沿用 calibre TXTOutput 轉換核心，保留連結與圖片參照。

安裝包見 [v1.3.17 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.17)。

## 安裝與使用

1. 在根目錄執行 `python -B build_release.py`，取得 `dist/Markdown Output-zh_TW-release.zip`。
2. 在 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。
3. 在轉換書本時選擇 MD／Markdown 輸出格式，再調整 Markdown 輸出選項。

此外掛直接提供中文，不依賴「正體中文補強」外掛。

## 本倉庫修改

- 以本機原版 1.0.3 匯入，保留 The_book 作者與原轉換核心。
- 改為獨立設定頁，移除對 calibre TXT 輸出頁 `gridLayout`、`label_4` 等舊元件的依賴，修正在 calibre 9.18.0 無法開啟設定頁的問題。
- 直接將七個設定選項及說明改為正體中文；換行格式與字元編碼保留原有技術值。
- 保留 `Markdown_output` 設定識別及七個內部選項鍵；驗證選項儲存與實際 EPUB → Markdown 轉檔的中文、連結和圖片參照。

## 來源

[原始專案／討論串](https://www.mobileread.com/forums/showthread.php?t=328999)。匯入日期：2026-11-09。

本機原安裝包 SHA-256：`ac62626195d285a743bb3e7af8f9a4250960f056eb04d48080e4a70f631ffdf8`。

## 測試與限制

Windows、calibre 9.18.0 已通過設定頁、版本與相關功能測試；翻譯目錄另核對格式佔位符及三種語系別名。

換行及編碼的技術值保留英文以維持參數相容。已測試一份含中文、連結與圖片的 EPUB；未逐一驗收所有來源格式與排版。原安裝包沒有附獨立授權檔，保留原作者及來源資訊。

```powershell
$env:CALIBRE_CONFIG_DIRECTORY = Join-Path $PWD 'dist/standalone-qa/config'
$env:QT_QPA_PLATFORM = 'offscreen'
calibre-debug -e "Markdown Output/tests/test_markdown_output.py"
python -B "Markdown Output/tests/test_conversion.py"
```
