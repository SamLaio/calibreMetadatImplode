# calibreMetadatImplode

目前整合發行版：**v1.3.7（2026-11-01）**，新增 **Extract ISBN 1.6.6.1 本倉庫修訂版**，修正 ISBN 辨識、PDF 書尾掃描與錯誤摘要，補齊正體中文。整合發行版號與各外掛程式版號分開管理。

這個倉庫並排管理九個 calibre 外掛：

- [`Extract ISBN`](./Extract%20ISBN)：從電子書內文擷取 ISBN，經確認後更新書庫識別碼；本倉庫修訂版 1.6.6.1。原始 GitHub：[kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/extract_isbn)
- [`Goodreads`](./Goodreads): 下載 Goodreads 書籍中繼資料與封面；本倉庫修正版 1.10.1 補強書籍比對、資料引用與缺值處理。原始 GitHub: [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/goodreads)
- [`AZW6 Image Merge`](./AZW6%20Image%20Merge): 在 `.azw` 匯入並經 DeDRM 轉為 AZW3 時，將同資料夾唯一一份 `.azw.res` 的高清圖片合併回主書檔。
- [`Embed Metadata Safe`](./Embed%20Metadata%20Safe): 先移除 EPUB 中缺少 `datatype` 的 `calibre:user_metadata` JSON 物件，再嵌入書庫中繼資料；預設只處理 EPUB，也可設定為選擇格式。
- [`Modify ePub`](./Modify%20ePub): 直接對 EPUB 做清理與小幅修改，不必先跑轉檔流程。原始 GitHub: [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub)
- [`Find Duplicates`](./Find%20Duplicates): 依照 metadata 比對規則找出可能重複的書籍，方便人工複核。原始 GitHub: [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/find_duplicates)
- [`EpubSplit`](./EpubSplit): 依目錄或章節把一本 EPUB 拆成多本新書；本倉庫另含 EPUB3 導覽解析與 EPUB3 輸出支援。原始 GitHub: [JimmXinu/EpubSplit](https://github.com/JimmXinu/EpubSplit)
- [`Count Pages`](./Count%20Pages): 計算頁數、字數與可讀性統計，並寫入自訂欄位。原始 GitHub: [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/count_pages)
- [`Send to Kindle`](./Send%20to%20Kindle): 透過 calibre 電子郵件設定寄書到 Kindle，可在送出前改書名，並依寄送檔名模板代入書庫欄位，保留正體中文而不轉拼音。原始 GitHub: [bookfere/Send-to-Kindle-Calibre-Plugin](https://github.com/bookfere/Send-to-Kindle-Calibre-Plugin)

各外掛的完整說明請看對應資料夾內的 README：

- [`Extract ISBN/README.md`](./Extract%20ISBN/README.md)
- [`Goodreads/README.md`](./Goodreads/README.md)
- [`Embed Metadata Safe/README.md`](./Embed%20Metadata%20Safe/README.md)
- [`AZW6 Image Merge/README.md`](./AZW6%20Image%20Merge/README.md)
- [`Modify ePub/README.md`](./Modify%20ePub/README.md)
- [`Find Duplicates/README.md`](./Find%20Duplicates/README.md)
- [`EpubSplit/README.md`](./EpubSplit/README.md)
- [`Count Pages/README.md`](./Count%20Pages/README.md)
- [`Send to Kindle/README.md`](./Send%20to%20Kindle/README.md)

## 目前原始碼版本與安裝

從 [v1.3.7 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.7) 下載需要的 ZIP，於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」選取 ZIP，安裝後重新啟動 calibre。每個 ZIP 是獨立外掛，不需全部安裝。

下表列出本版九個外掛的原始碼版本與安裝包；也可依下方「打包方式」自行產生 ZIP。

| 外掛 | 目前程式版號 | 最低 calibre | 安裝包 |
| --- | --- | --- | --- |
| Extract ISBN | 1.6.6.1（本倉庫修訂版） | 2.0.0 | [Extract ISBN-zh_TW-release.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/Extract.ISBN-zh_TW-release.zip) |
| Goodreads | 1.10.1（本倉庫修正版） | 2.0.0 | [Goodreads.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/Goodreads.zip) |
| AZW6 Image Merge | 1.0.0 | 5.0.0 | [AZW6 Image Merge-zh_TW-release.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/AZW6.Image.Merge-zh_TW-release.zip) |
| Embed Metadata Safe | 1.0.0 | 9.8.0 | [embed-metadata-safe.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/embed-metadata-safe.zip) |
| Modify ePub | 1.8.11 | 3.48.0 | [Modify ePub-zh_TW-release.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/Modify.ePub-zh_TW-release.zip) |
| Find Duplicates | 1.10.11 | 2.0.0 | [Find Duplicates-zh_TW-release.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/Find.Duplicates-zh_TW-release.zip) |
| EpubSplit | 3.12.0 | 3.48.0 | [EpubSplit-zh_TW-release.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/EpubSplit-zh_TW-release.zip) |
| Count Pages | 1.15.3 | 3.48.0 | [Count Pages-zh_TW-release.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/Count.Pages-zh_TW-release.zip) |
| Send to Kindle | v1.1.1_r.1（calibre 顯示 1.1.1） | 2.0.0 | [Send to Kindle-zh_TW-release.zip](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/Send.to.Kindle-zh_TW-release.zip) |

最低版本取自各外掛宣告，不代表已在所有舊版 calibre 實測。會修改書庫或書檔的操作，建議先備份。

## Extract ISBN 1.6.6.1：用途、操作與限制

### 適合什麼情況？

書庫缺少 ISBN，但 EPUB、PDF 等電子書的版權頁或其他內文印有 ISBN 時，可用此外掛找出號碼，經確認後填入 calibre 書庫，再使用 calibre 的中繼資料下載功能取得書名、作者、封面等資料。

它會驗證 ISBN-10 或 ISBN-13 的檢查碼，支援單本與批次處理。它本身不會上網搜尋 ISBN 或下載書目資料，也不修改原始電子書；套用時只新增或替換書庫的 ISBN，保留其他識別碼。既有 ISBN 若與擷取結果不同，確認套用後會被替換；掃描失敗不會清空原有值。

### 安裝與使用

1. 下載 [Extract ISBN 1.6.6.1 安裝包](https://github.com/SamLaio/calibreMetadatImplode/releases/download/v1.3.7/Extract.ISBN-zh_TW-release.zip)。
2. 在 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝 ZIP，重新啟動 calibre。
3. 在「偏好設定 → 工具列與選單」加入「擷取 ISBN」。使用正體中文介面時會載入正體中文翻譯。
4. 選取一本或多本書，執行「擷取 ISBN」。
5. 查看掃描結果與詳細紀錄，核對號碼後確認更新書庫。取得 ISBN 後，需要書目資料時再另外執行中繼資料下載。

### 掃描規則與設定

| 項目 | 目前行為 |
| --- | --- |
| 多種書籍格式 | 依 calibre 輸入格式偏好順序掃描；某個格式找到 ISBN 後停止嘗試其他格式。可用格式取決於 calibre 的輸入支援。 |
| EPUB 等非 PDF 格式 | 先掃書前內容檔，再反向掃書尾，最後掃其餘內文；此處的檔案數不是頁數。 |
| PDF | 不超過 15 頁時全掃；較長文件先掃前 10 頁，找不到再反向掃最後 5 頁，不掃中間頁面。 |
| 多個 ISBN | 已收集的候選中優先選 ISBN-13，再選 ISBN-10；不是全書比對，也不辨識書籍版本。 |
| 工作方式 | 預設單本使用執行緒，多本使用背景工作程序，每批 100 本；背景工作門檻與每批數量可調整。 |
| 完成後 | 預設詢問是否套用；可設定是否顯示找不到或相同 ISBN 的提示，以及是否只顯示已更新書籍。 |

建議保留「套用 ISBN 變更前先詢問」，特別是書庫已有 ISBN，或版權頁同時列出精裝、平裝、電子版號碼時。

### 為什麼會找不到 ISBN？

目前只掃描閱讀順序中的內文，不讀取 EPUB 的 OPF 中繼資料，也沒有 OCR。ISBN 只存在 `content.opf`、圖片或長 PDF 的中間頁面時，可能找不到；號碼被換行或標籤拆開，或未通過校驗，也可能漏判。

實際案例：《書店怪問》的 `content.opf` 含有通過校驗的 `isbn:9789863610212`，但內文沒有找到 ISBN，因此外掛回報失敗。這不代表整個 EPUB 沒有 ISBN；本版未加入讀取 OPF 的備援功能。OPF 的值可能是先前由 calibre 嵌入，仍須人工核對。

ISBN 校驗只確認號碼有效，無法確認它是否屬於目前書籍的正確版本。遇到找不到或多版本號碼，可查看版權頁及書庫現有識別碼，再決定是否手動填入。

### 本倉庫修正與來源（2026-11-01）

- 基於上游程式宣告版本 1.6.6，本倉庫修訂版號為 **1.6.6.1**，不是上游正式發行版本。
- 修正 ISBN-10 小寫 `x` 檢查碼漏判。
- 修正 PDF 書尾多掃一頁及未反向搜尋的問題。
- 修正沒有書籍格式時，錯誤摘要誤顯示為找不到 ISBN。
- 補齊 65 個正體中文介面字串，保留上游其他語系、作者與 GPL v3 授權。
- 加入統一打包流程與 9 組回歸測試；共用模組隨外掛放在 `Extract ISBN/src/`。

來源為 [kiwidude68/calibre_plugins 的 Extract ISBN](https://github.com/kiwidude68/calibre_plugins/tree/2a2dbb2469ec6e68179cd71ba943db240045d097/extract_isbn)，匯入提交為 `2a2dbb2469ec6e68179cd71ba943db240045d097`。該提交程式宣告為 1.6.6，另含 1.6.7 語系更新紀錄；本地修訂版沿用使用者指定的 1.6.6.1。

完整說明、打包方式與授權見 [`Extract ISBN/README.md`](./Extract%20ISBN/README.md)。

## Goodreads 匯入與修正（2026-11-01）

從使用者提供的 `Goodreads.zip` 1.10.0 匯入，保留上游作者、授權宣告與翻譯資源。2026-11-01 已確認來源為 [kiwidude68/calibre_plugins 的 Goodreads 外掛](https://github.com/kiwidude68/calibre_plugins/tree/main/goodreads)：上游當時版本為 1.10.0，作者為 Grant Drake，原始 README 與 `config.py` 與匯入來源一致。

本倉庫的 1.10.1 是基於上游 1.10.0 的本地修正版，並非上游正式發行版本。上游 1.10.0 的更新包含改用 JSON 自動完成搜尋，與匯入外掛的實作一致；本次未逐一核對所有翻譯資源。

- 書名與作者比對改為符合全部有效詞，ISBN／ASIN 搜尋結果再以詳細頁核對；失敗時可改用書名與作者搜尋。
- 書籍、系列與作品依引用關係配對，避免混用其他書籍的資料。
- 修正封面缺少長度標頭、ISBN-13 空值、出版日期缺漏與無效評分識別碼處理。
- 缺少書籍 JSON 時最多請求三次、每次間隔一秒，並傳遞連線逾時設定。

完整說明見 [`Goodreads/README.md`](./Goodreads/README.md)。

## 官方版本檢查（2026-10-23，歷史紀錄）

| 外掛 | 檢查前本機版本 | 官方最新版 | 本次處理 |
| --- | --- | --- | --- |
| AZW6 Image Merge | 1.0.0 | [1.0.0](https://github.com/HamsterExAstris/calibre-azw6-image-merge/tree/63f76d46e19de901536b9bc7c1a02998f26c439b) | 沒有新版；保留本機以 Pillow 取代 `imghdr` 的 Python 3.13 以上相容性修改及中文說明。上游最後提交為 2021-12-17，未建立正式 release。 |
| Embed Metadata Safe | 1.0.0 | 無獨立上游 | 本倉庫自有外掛，維持現版。 |
| Modify ePub | 1.8.9 | [1.8.11](https://github.com/kiwidude68/calibre_plugins/commit/51f4bde27bfb095826bda6e3254ea98e72c4f937) | 整合 CSS 非數值邊距修正與官方語系更新，保留正體中文整合內容。 |
| Find Duplicates | 1.10.10 | [1.10.11](https://github.com/kiwidude68/calibre_plugins/commit/91b0f23da54fa8f020ba387e1f13a1321706c0ff) | 已整合官方語系更新，保留原有 179 個正體中文介面字串、中文說明及外掛描述。 |
| EpubSplit | 3.12.0 | [3.12.0](https://github.com/JimmXinu/EpubSplit/releases/tag/v3.12.0) | 沒有新版；比對官方包後保留本機 EPUB3 導覽解析、EPUB3 輸出、HTML 解析器備援與正體中文。 |
| Count Pages | 1.15.2 | [1.15.3](https://github.com/kiwidude68/calibre_plugins/commit/d46d9197ac2f78e98f2a774a6afbf8d54d9ce68a) | 已整合 Goodreads `.xml` 網址與官方語系更新，補齊 12 個正體中文提示，修復英文斷句模型的 Windows 換行問題。 |
| Send to Kindle | v1.1.1_r.1 | [1.1.1](https://github.com/bookfere/Send-to-Kindle-Calibre-Plugin/releases/tag/v1.1.1) | 沒有新版；保留 calibre 寄送檔名模板、書庫欄位代入及不轉拼音的本機修改。 |

上表保留 2026-10-23 的檢查結果；後續加入的 Goodreads 與 Extract ISBN 來源及版本另見前述段落。

有新版的外掛已逐檔比對官方發行包，再套回本倉庫的語系與說明差異；詳細比對見各外掛 README。
`Find Duplicates` 原先標示的 JimmXinu 分支仍停留在 1.10.10，因此改以 kiwidude68 的官方維護來源為準。
表中的上游連結記錄本次比對來源；官方原始下載包不列入本倉庫發行附件。

## 打包方式

在倉庫根目錄執行：

```powershell
python build_release.py
```

會先清空 `dist/`，再分別輸出九個 zip：

- `dist/Extract ISBN-zh_TW-release.zip`
- `dist/Goodreads.zip`
- `dist/AZW6 Image Merge-zh_TW-release.zip`
- `dist/embed-metadata-safe.zip`
- `dist/Modify ePub-zh_TW-release.zip`
- `dist/Find Duplicates-zh_TW-release.zip`
- `dist/EpubSplit-zh_TW-release.zip`
- `dist/Count Pages-zh_TW-release.zip`
- `dist/Send to Kindle-zh_TW-release.zip`

請先備份 `dist/` 中需要保留的檔案。安裝包會排除隱藏檔、`__pycache__` 與 `.po` 翻譯來源；編譯後的 `.mo` 語系檔會保留。Extract ISBN 的翻譯會在打包時編譯，需要 `calibre-debug` 可由執行檔搜尋路徑找到。

## 驗證

```powershell
calibre-debug -e "Modify ePub/tests/test_margins.py"
calibre-debug -e "Count Pages/tests/test_update.py"
calibre-debug -e "Goodreads/tests/test_goodreads.py"
calibre-debug -e "Extract ISBN/tests/test_extract_isbn.py"
```

v1.3.5 發行時已通過 Modify ePub 與 Count Pages 共 8 組回歸測試、Python 語法與安裝包內容檢查；Count Pages 的 Goodreads 頁數解析使用離線頁面驗證。

新增 Goodreads 外掛另已通過 8 組離線回歸測試、原有搜尋輔助函式測試，以及 Python 語法與安裝包內容檢查；並以《61 Hours》（Goodreads ID：6977769）實際驗證書名、作者、ISBN、系列集數與封面解析。未涵蓋 SMTP 寄信、calibre 圖形介面安裝或所有舊版相容性；網站改版或存取限制仍可能影響下載。

Extract ISBN 1.6.6.1 已在 calibre 9.17.0 通過 9 組測試，包含實際 EPUB、PDF 擷取，並核對 65 個正體中文介面字串及安裝包內容。未測試圖形介面安裝與所有舊版相容性。
