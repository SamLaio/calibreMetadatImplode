# calibreMetadatImplode

這個倉庫現在並排管理三個 calibre 外掛：

- [`Embed Metadata Safe`](./Embed%20Metadata%20Safe)
- [`Modify ePub`](./Modify%20ePub)
- [`Find Duplicates`](./Find%20Duplicates)

每個外掛都有自己的 `src/` 原始碼樹，發布時會分別打包到 `dist/`。

## 目錄結構

- [`Embed Metadata Safe/src/embed_metadata_safe`](./Embed%20Metadata%20Safe/src/embed_metadata_safe)
- [`Modify ePub/src`](./Modify%20ePub/src)
- [`Find Duplicates/src`](./Find%20Duplicates/src)
- [`build_release.py`](./build_release.py)
- [`dist/`](./dist)

## 發布打包

執行：

```powershell
python build_release.py
```

會產生：

- `dist/embed-metadata-safe.zip`
- `dist/Modify ePub-zh_TW-release.zip`
- `dist/Find Duplicates-zh_TW-release.zip`

## 備註

- `Embed Metadata Safe` 會保留 Python 套件名稱 `embed_metadata_safe`，方便 calibre 匯入。
- `Modify ePub` 以解開後的外掛原始碼形式保存，包含正體中文翻譯檔。
- `Find Duplicates` 以解開後的外掛原始碼形式保存，並附上正體中文翻譯檔。
