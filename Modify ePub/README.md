# Modify ePub

`Modify ePub` 是 calibre 的書庫外掛，讓你可以直接對 EPUB 做清理與小幅修改，而不用先做 ePub->ePub 轉檔。
它適合處理你想保留原始結構、但又需要局部修補內容、資源或中繼資料的情境。

## 功能

- 直接對 EPUB 內容與結構做修改
- 避免轉檔流程帶來的額外重寫與副作用
- 適合做內容清理、格式修補、資源調整
- 內建設定與語系檔，包含正體中文

## 使用方式

1. 在 calibre 書庫中選取要處理的 EPUB。
2. 開啟 `Modify ePub` 外掛。
3. 依照對話框中的選項套用修改。
4. 外掛會直接更新原書的 EPUB 內容，不需另行轉檔。

## 原始 GitHub

- [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub)

## 結構

- `src/`：解開後的外掛原始碼
- `src/translations/`：語系檔，包含正體中文

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/Modify ePub-zh_TW-release.zip`。
