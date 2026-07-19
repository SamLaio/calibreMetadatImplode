# calibreMetadatImplode

這個倉庫並排管理七個 calibre 外掛：

- [`AZW6 Image Merge`](./AZW6%20Image%20Merge): 把 Amazon AZW6 sidecar 的高清圖片合併回 AZW3/AZW 內容。
- [`Embed Metadata Safe`](./Embed%20Metadata%20Safe): 先修復 EPUB 內壞掉的 `calibre:user_metadata`，再安全地把 metadata 寫回選取的書籍。
- [`Modify ePub`](./Modify%20ePub): 直接對 EPUB 做清理與小幅修改，不必先跑轉檔流程。原始 GitHub: [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub)
- [`Find Duplicates`](./Find%20Duplicates): 依照 metadata 比對規則找出可能重複的書籍，方便人工複核。原始 GitHub: [JimmXinu/kiwidude68_calibre_plugins](https://github.com/JimmXinu/kiwidude68_calibre_plugins/tree/main/find_duplicates)
- [`EpubSplit`](./EpubSplit): 依 TOC 或章節把一本 EPUB 拆成多本新書。原始 GitHub: [JimmXinu/EpubSplit](https://github.com/JimmXinu/EpubSplit)
- [`Count Pages`](./Count%20Pages): 計算頁數、字數與可讀性統計，並寫入自訂欄位。原始 GitHub: [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/count_pages)
- [`Send to Kindle`](./Send%20to%20Kindle): 把選取的電子書透過 Calibre email 設定寄到 Kindle，並可在送出前改書名。原始 GitHub: [bookfere/Send-to-Kindle-Calibre-Plugin](https://github.com/bookfere/Send-to-Kindle-Calibre-Plugin)

各外掛的完整說明請看對應資料夾內的 README：

- [`Embed Metadata Safe/README.md`](./Embed%20Metadata%20Safe/README.md)
- [`AZW6 Image Merge/README.md`](./AZW6%20Image%20Merge/README.md)
- [`Modify ePub/README.md`](./Modify%20ePub/README.md)
- [`Find Duplicates/README.md`](./Find%20Duplicates/README.md)
- [`EpubSplit/README.md`](./EpubSplit/README.md)
- [`Count Pages/README.md`](./Count%20Pages/README.md)
- [`Send to Kindle/README.md`](./Send%20to%20Kindle/README.md)

## 打包方式

在倉庫根目錄執行：

```powershell
python build_release.py
```

會先清空 `dist/`，再分別輸出七個 zip：

- `dist/AZW6 Image Merge-zh_TW-release.zip`
- `dist/embed-metadata-safe.zip`
- `dist/Modify ePub-zh_TW-release.zip`
- `dist/Find Duplicates-zh_TW-release.zip`
- `dist/EpubSplit-zh_TW-release.zip`
- `dist/Count Pages-zh_TW-release.zip`
- `dist/Send to Kindle-zh_TW-release.zip`
