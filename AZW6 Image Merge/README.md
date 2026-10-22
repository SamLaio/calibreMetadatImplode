# AZW6 Image Merge

版本：**1.0.0**；最低 calibre：**5.0.0**。本倉庫保留以 Pillow 取代 `imghdr` 的 Python 3.13 以上相容性修改。

這個 calibre 外掛會把 Amazon AZW6 sidecar 檔中的高清圖片，合併回同一本書的 AZW3/AZW 內容。

## 功能

- 偵測原始 `.azw` 經 DeDRM 轉為 `.azw3` 的匯入流程。
- 在同資料夾中尋找對應的 `.azw.res` sidecar 檔。
- 讀取 sidecar 內的高清圖片，覆寫回主要書檔。
- 合併後輸出新的書檔，交回 calibre 繼續處理。

## 安裝

建議直接安裝倉庫根目錄 `dist/` 內產生的 release zip：

- `AZW6 Image Merge-zh_TW-release.zip`

也可由 [本倉庫發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases) 下載同名 ZIP，於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。

如果你是從原始碼使用，請確保外掛內容保持在 `src/` 目錄結構下。

## 使用方式

1. 先讓 Kindle for PC 下載出 AZW 主檔與對應的 `.azw.res` sidecar 檔。
2. 如果書檔經過 DeDRM，主檔通常會變成 `.azw3`，這個外掛會在匯入時嘗試處理。
3. 將書籍匯入 calibre。
4. 外掛會自動在背景合併 sidecar 內的高清圖片。

## 注意事項

- 這個外掛只會在找到唯一一個 `.azw.res` 時進行合併。
- 如果資料夾中有多個 `.azw.res`，外掛會跳過處理。
- 主要書檔與 sidecar 內部記錄的書名必須一致；不符合時會記錄合併失敗。
- 直接匯入 `.azw3`，或 `.azw` 沒有在匯入流程轉為 `.azw3`，不會觸發合併。
- 目前邏輯是針對 Amazon AZW6 sidecar 的結構設計，不適合一般 EPUB 或其他格式。

## 打包

請使用倉庫根目錄的 `build_release.py` 產生 release zip。

## 上游來源

[HamsterExAstris/calibre-azw6-image-merge](https://github.com/HamsterExAstris/calibre-azw6-image-merge)。截至 2026-10-23，上游仍為 1.0.0，最後提交為 2021-12-17。
