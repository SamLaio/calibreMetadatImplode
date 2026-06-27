# calibreMetadatImplode

這個倉庫並排管理四個 calibre 外掛：

- [`Embed Metadata Safe`](./Embed%20Metadata%20Safe): 在寫入 EPUB metadata 前先清理壞掉的 `calibre:user_metadata`。
- [`Modify ePub`](./Modify%20ePub): 不經轉檔直接修改 EPUB 內容與結構。原始 GitHub: [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub)
- [`Find Duplicates`](./Find%20Duplicates): 依照中繼資料與檔案內容找出重複書籍。原始 GitHub: [JimmXinu/kiwidude68_calibre_plugins](https://github.com/JimmXinu/kiwidude68_calibre_plugins/tree/main/find_duplicates)
- [`EpubSplit`](./EpubSplit): 把 EPUB 切成新的獨立書籍。原始 GitHub: [JimmXinu/EpubSplit](https://github.com/JimmXinu/EpubSplit)

各外掛的完整說明請看對應資料夾內的 README：

- [`Embed Metadata Safe/README.md`](./Embed%20Metadata%20Safe/README.md)
- [`Modify ePub/README.md`](./Modify%20ePub/README.md)
- [`Find Duplicates/README.md`](./Find%20Duplicates/README.md)
- [`EpubSplit/README.md`](./EpubSplit/README.md)

## 打包方式

在倉庫根目錄執行：

```powershell
python build_release.py
```

會先清空 `dist/`，再分別輸出四個 zip：

- `dist/embed-metadata-safe.zip`
- `dist/Modify ePub-zh_TW-release.zip`
- `dist/Find Duplicates-zh_TW-release.zip`
- `dist/EpubSplit-zh_TW-release.zip`
