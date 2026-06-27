# Find Duplicates

`Find Duplicates` 是用來找出 calibre 書庫中可能重複書籍的外掛。
它會依照你設定的比對規則整理候選項目，讓你再人工確認哪些書應該合併、保留或刪除。

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

## 原始 GitHub

- [JimmXinu/kiwidude68_calibre_plugins](https://github.com/JimmXinu/kiwidude68_calibre_plugins/tree/main/find_duplicates)

## 結構

- `src/`：外掛原始碼
- `src/translations/`：語系檔，包含正體中文

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/Find Duplicates-zh_TW-release.zip`。
