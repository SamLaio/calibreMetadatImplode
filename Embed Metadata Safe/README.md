# Embed Metadata Safe

版本：**1.0.0**；最低 calibre：**9.8.0**。

`Embed Metadata Safe` 是 calibre 的書庫外掛，會在把 metadata 寫回 EPUB 之前先檢查並修復壞掉的 `calibre:user_metadata`。
如果書檔裡的內嵌 metadata 已經損壞，這個外掛可以先清理再寫回，降低保存時出錯或把書檔卡住的機會。

## 功能

- 移除 EPUB OPF 中可解析為 JSON 物件、但缺少 `datatype` 的 `calibre:user_metadata` 項目；不會重建缺少的欄位資料
- 在修復後安全地把 metadata 嵌回選取的書籍
- 以書庫外掛方式執行，不需要離開 calibre
- 保留可自訂的設定對話框
- 預設只嵌入 EPUB；可在外掛設定切換為執行時選擇格式，其他格式仍交由 calibre 內建嵌入流程處理

## 使用方式

1. 在 calibre 書庫中選取要處理的 EPUB。
2. 執行 `Embed Metadata Safe`。
3. 預設只處理 EPUB；若設定為選擇格式，先勾選本次要處理的格式。
4. 外掛先清理符合上述條件的 EPUB metadata，再將書庫 metadata 嵌入所選格式。

此外掛會回寫書庫中的書檔，請先備份。無法解析的 JSON 或 XML 不在目前的清理範圍內，處理結果與錯誤會顯示於完成摘要。

## 安裝

從 [本倉庫發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases) 下載 `embed-metadata-safe.zip`，於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。

## 原始 GitHub

這個專案目前以本倉庫為主，沒有另外獨立的上游來源。

## 結構

- `src/embed_metadata_safe/`：外掛套件
- `src/plugin-import-name-embed_metadata_safe.txt`：calibre 匯入提示檔

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/embed-metadata-safe.zip`。

## 來源與版號核對（2026-11-01）

本倉庫自有外掛，沒有外部上游；`src/embed_metadata_safe/__init__.py` 宣告作者為 Codex、版本 1.0.0、最低 calibre 9.8.0。Git 以 `fbc927d` 記錄加入此外掛。

主要實作位於 `safe_epub.py` 與 `main.py`：只移除能解析為 JSON 物件、但缺少 `datatype` 的 `calibre:user_metadata`，不猜補欄位型別；先修復 EPUB 再呼叫 calibre 的嵌入流程。另提供正體中文介面、進度與取消、錯誤摘要及格式選擇。這些屬於本倉庫實作，不應列為上游修正。
