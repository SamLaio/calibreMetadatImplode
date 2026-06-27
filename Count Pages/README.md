# Count Pages

`Count Pages` 是用來計算頁數、字數與可讀性統計的 calibre 外掛。
它可以把結果寫入自訂欄位，也能依設定從外部來源抓取統計資料，適合做閱讀進度、頁數估算或 Kindle APNX 相關流程。

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
