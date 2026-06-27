# AZW6 Image Merge

這個 calibre 外掛會把 Amazon AZW6 sidecar 檔中的高清圖片，合併回同一本書的 AZW3/AZW 內容。

## 功能

- 偵測 `.azw` 匯入流程。
- 在同資料夾中尋找對應的 `.azw.res` sidecar 檔。
- 讀取 sidecar 內的高清圖片，覆寫回主要書檔。
- 合併後輸出新的書檔，交回 calibre 繼續處理。

## 安裝

建議直接安裝倉庫根目錄 `dist/` 內產生的 release zip：

- `AZW6 Image Merge-zh_TW-release.zip`

如果你是從原始碼使用，請確保外掛內容保持在 `src/` 目錄結構下。

## 使用方式

1. 先讓 Kindle for PC 下載出 AZW 主檔與對應的 `.azw.res` sidecar 檔。
2. 如果書檔經過 DeDRM，主檔通常會變成 `.azw3`，這個外掛會在匯入時嘗試處理。
3. 將書籍匯入 calibre。
4. 外掛會自動在背景合併 sidecar 內的高清圖片。

## 注意事項

- 這個外掛只會在找到唯一一個 `.azw.res` 時進行合併。
- 如果資料夾中有多個 `.azw.res`，外掛會跳過處理。
- 主要書檔與 sidecar 的書名必須一致，否則也會跳過。
- 目前邏輯是針對 Amazon AZW6 sidecar 的結構設計，不適合一般 EPUB 或其他格式。

## 打包

請使用倉庫根目錄的 `build_release.py` 產生 release zip。
