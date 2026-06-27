# Modify ePub

`Modify ePub` calibre 外掛的原始碼目錄。

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
