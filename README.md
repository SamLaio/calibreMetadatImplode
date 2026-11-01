# calibreMetadatImplode

本專案將九個 calibre 外掛並排維護，整合上游程式、正體中文資源與本地修正。各外掛可獨立使用；操作、設定、限制、安裝與打包方式請點各外掛名稱閱讀其 README。

## 本專案來源、版號與修改點

| 項目 | 說明 |
| --- | --- |
| 專案來源 | [SamLaio/calibreMetadatImplode](https://github.com/SamLaio/calibreMetadatImplode)，本倉庫為整合與修訂來源；各外掛的原作者及授權保留於各自目錄。 |
| 整合發行版號 | **[v1.3.8（2026-11-01）](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.8)**。這是整套發行附件的版號，與各外掛在 calibre 顯示的版號分開管理。 |
| 專案層修改 | 將外掛整理為各自的 `src/`，使用 `build_release.py` 統一輸出九個獨立安裝包到 `dist/`；排除隱藏檔、快取及 `.po` 翻譯來源。Extract ISBN 的翻譯在打包時編譯。 |
| 本次文件整理 | 核對九個外掛的來源、版號與修改點，修正 Extract ISBN 上游基準版號，補列 Send to Kindle 的偏好格式設定鍵修正；詳細說明歸回各外掛 README。 |

## 各外掛簡介、來源與版號

核對日期：**2026-11-01**。下表的「上游基準」是本倉庫採用或本次比對的固定版本／提交，並非宣稱所有上游目前的最新版。版號以原始碼宣告為準；同版號也可能含有本地修改。

| 外掛及完整說明 | 簡介 | 上游來源與比對基準 | 本倉庫版號 |
| --- | --- | --- | --- |
| [Extract ISBN](./Extract%20ISBN/README.md) | 從電子書內文擷取 ISBN，確認後更新書庫識別碼。 | Grant Drake；[kiwidude68/calibre_plugins/extract_isbn，提交 `2a2dbb2`](https://github.com/kiwidude68/calibre_plugins/tree/2a2dbb2469ec6e68179cd71ba943db240045d097/extract_isbn)，程式宣告 **1.6.7**。 | **1.6.7.1**，基於上游 1.6.7 的本倉庫修訂版。 |
| [Goodreads](./Goodreads/README.md) | 從 Goodreads 下載書籍中繼資料與封面。 | Grant Drake；最初由使用者提供的 1.10.0 安裝包匯入，已對照 [kiwidude68/calibre_plugins/goodreads，提交 `2a2dbb2`](https://github.com/kiwidude68/calibre_plugins/tree/2a2dbb2469ec6e68179cd71ba943db240045d097/goodreads)，基準 **1.10.0**。 | **1.10.1**，本倉庫修正版。 |
| [AZW6 Image Merge](./AZW6%20Image%20Merge/README.md) | 將 Amazon AZW6 sidecar 高畫質圖片合併至主書檔。 | Andrew Timson；[HamsterExAstris/calibre-azw6-image-merge，提交 `63f76d4`](https://github.com/HamsterExAstris/calibre-azw6-image-merge/tree/63f76d46e19de901536b9bc7c1a02998f26c439b)，基準 **1.0.0**。 | **1.0.0**，含本地相容性修改。 |
| [Embed Metadata Safe](./Embed%20Metadata%20Safe/README.md) | 清理 EPUB 的特定損壞自訂欄位資料，再嵌入書庫中繼資料。 | [本倉庫自有外掛](./Embed%20Metadata%20Safe/src/embed_metadata_safe/__init__.py)，作者為 SamLiao 及 codex；沒有獨立上游。 | **1.0.0**。 |
| [Modify ePub](./Modify%20ePub/README.md) | 直接清理與修改 EPUB，免經轉檔流程。 | Grant Drake 等；[kiwidude68/calibre_plugins/modify_epub，提交 `51f4bde`](https://github.com/kiwidude68/calibre_plugins/tree/51f4bde27bfb095826bda6e3254ea98e72c4f937/modify_epub)，基準 **1.8.11**。 | **1.8.11**，正體中文整合版。 |
| [Find Duplicates](./Find%20Duplicates/README.md) | 依設定的書目比對規則找出可能重複的書籍。 | Grant Drake；[kiwidude68/calibre_plugins/find_duplicates，提交 `91b0f23`](https://github.com/kiwidude68/calibre_plugins/tree/91b0f23da54fa8f020ba387e1f13a1321706c0ff/find_duplicates)，基準 **1.10.11**；早期來源為 JimmXinu 分支。 | **1.10.11**，正體中文整合版。 |
| [EpubSplit](./EpubSplit/README.md) | 按目錄或章節將 EPUB 拆成多本新書。 | Jim Miller；[JimmXinu/EpubSplit，標籤 `v3.12.0`](https://github.com/JimmXinu/EpubSplit/tree/a0b31ea9c0c9b439329574c4752b24eaaab67f72)，基準 **3.12.0**。 | **3.12.0**，含本地 EPUB3 修改。 |
| [Count Pages](./Count%20Pages/README.md) | 計算或下載頁數、字數與可讀性統計，寫入自訂欄位。 | Grant Drake；[kiwidude68/calibre_plugins/count_pages，提交 `d46d919`](https://github.com/kiwidude68/calibre_plugins/tree/d46d9197ac2f78e98f2a774a6afbf8d54d9ce68a/count_pages)，基準 **1.15.3**。 | **1.15.3**，正體中文整合版。 |
| [Send to Kindle](./Send%20to%20Kindle/README.md) | 透過 calibre 電子郵件設定寄書到 Kindle，可指定寄送書名與檔名。 | BookFere／bookfere.com；[bookfere/Send-to-Kindle-Calibre-Plugin，標籤 `v1.1.1`](https://github.com/bookfere/Send-to-Kindle-Calibre-Plugin/tree/e57861e85fcddded1344d784e3c1d4cc4306520c)，基準 **1.1.1**。 | **v1.1.1_r.1**；calibre 數字版號顯示 **1.1.1**。 |

## 各外掛修改摘要

以下區分本倉庫修改與採用的上游修正；完整差異、驗證紀錄及限制請見各外掛 README。

| 外掛 | 本倉庫修改點 |
| --- | --- |
| Extract ISBN | 修正 ISBN-10 小寫 `x` 校驗、PDF 書尾掃描範圍與方向、缺少格式的錯誤摘要；新增 65 個正體中文介面翻譯、中文說明及 9 組測試，納入共用模組與統一打包。 |
| Goodreads | 補強書名／作者詞比對、ISBN／ASIN 詳細頁核對與搜尋備援；按引用關係取得系列與作品；修正封面缺少長度標頭、ISBN-13 空值、缺漏日期／評分及重試／逾時處理，加入 8 組離線測試。 |
| AZW6 Image Merge | 以 calibre 內建 Pillow 取代已移除的 `imghdr`，保留 JPEG 位元特徵備援及 TIFF／WDP 對應；補上中文說明與統一打包。合併主流程沿用上游。 |
| Embed Metadata Safe | 本倉庫自行實作：先移除可解析 JSON 物件中缺少 `datatype` 的 `calibre:user_metadata` 項目，再呼叫 calibre 嵌入流程；加入正體中文介面、進度與取消、錯誤摘要及處理格式設定。 |
| Modify ePub | 採用上游 1.8.11 的非數值 CSS 邊距修正及語系更新；保留正體中文語系別名、中文說明與外掛描述調整，加入邊距回歸測試。核心邊距修正來自上游。 |
| Find Duplicates | 更新上游至 1.10.11 並整合語系；保留 179 個正體中文介面翻譯、語系別名、中文說明與描述調整。重複書籍比對核心未自行改寫。 |
| EpubSplit | 解除 EPUB3 阻擋，加入 EPUB3 導覽解析及 EPUB3 輸出，依來源保留 EPUB2／EPUB3；加入 HTML 解析器備援、正體中文翻譯與說明。 |
| Count Pages | 採用上游 1.15.3 的 Goodreads `.xml` 網址與語系更新；保留正體中文語系別名，補齊 12 個提示至 119 個介面翻譯；還原英文斷句模型並設為二進位，避免 Windows 換行破壞，加入離線回歸測試。 |
| Send to Kindle | 寄送檔名改用 calibre `mtp_devices.send_template` 與書庫欄位，套用寄送視窗書名並保留 Unicode；修正偏好格式設定鍵為 `preferred_format`，移除介面未使用的格式查詢，保留正體中文與中文說明。 |

本次以本地版本宣告、Git 提交紀錄及固定上游來源交叉核對，逐檔比較八個有外部上游外掛的 79 個 `src/` 頂層 Python 檔案。此核對不等同於重跑全部功能測試，也未逐一比對全部圖片、翻譯及巢狀套件資源；各外掛既有驗證紀錄保留於其 README。
