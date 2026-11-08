# 整合更新紀錄

記錄各外掛何時加入本倉庫、升級版號及主要修改。整合發行版號與外掛版號分開管理；日期採臺灣時間（UTC+8），以 Git 與 GitHub 發行紀錄回補。各外掛的操作、來源及限制見各自 README。

## 各外掛首次加入

| 外掛 | 首次整合發行 | 日期 | 首次外掛版號 |
| --- | --- | --- | --- |
| Embed Metadata Safe | v1.0.0 | 2026-06-27 | 1.0.0 |
| Find Duplicates | v1.1.0 | 2026-06-27 | 1.10.10 |
| Modify ePub | v1.1.0 | 2026-06-27 | 1.8.9 |
| EpubSplit | v1.2.0 | 2026-06-28 | 3.12.0 |
| Count Pages | v1.3.0 | 2026-06-28 | 1.15.2 |
| AZW6 Image Merge | v1.3.2 | 2026-06-28 | 1.0.0 |
| Send to Kindle | v1.3.3 | 2026-07-19 | 1.1.1 |
| Goodreads | v1.3.6 | 2026-11-01 | 1.10.1 |
| Extract ISBN | v1.3.7 | 2026-11-01 | 1.6.6.1；v1.3.8 校正為 1.6.7.1 |
| Skip ASCII Text Plugin | v1.3.9 | 2026-11-01 | 1.0.1 |
| Generate Cover | v1.3.10 | 2026-11-02 | 2.4.2.1 |
| Toolbar Manager | v1.3.11 | 2026-11-02 | 1.0.0 |
| Enhanced Search and Replace | v1.3.13 | 2026-11-02 | 1.0.0 |
| Goodreads Sync | v1.3.17 | 2026-11-09 | 1.17.6.1 |
| Hardcover Sync | v1.3.17 | 2026-11-09 | 0.3.1.1 |
| Markdown Output | v1.3.17 | 2026-11-09 | 1.0.3.1 |
| Traditional Chinese Supplement | v1.3.17 | 2026-11-09 | 1.1.1 |

## [v1.3.18] — 2026-11-09

- Traditional Chinese Supplement **1.1.2**：完整掃描本機 calibre 9.18.0 三份官方正體中文目錄，為含明確簡體字的 310 筆文字建立精確顯示對照。
- 修正「在網路上分享」設定中的簡體文字及連接埠、處理程序、回應等用語；16 項隔離測試通過，保護輸入、下拉與數值設定。
- Hardcover Sync 維持 **0.3.1.1**；0.4.0.1 候選版尚未完成驗收，不納入此次發行。

- 新增根目錄整合更新紀錄，回補外掛首次加入與歷次升級。
- 精簡 Traditional Chinese Supplement 說明，僅保留自身用途、支援範圍、安裝及限制。

## [v1.3.17] — 2026-11-09

- 新增 Goodreads Sync **1.17.6.1**，基於 1.17.6 直接正體中文化，保留同步核心與設定鍵。
- 新增真正的 Hardcover Sync **0.3.1.1**，基於 Juan York 的 0.3.1，直接正體中文化並驗證與 Goodreads Sync 共存。
- 新增 Markdown Output **1.0.3.1**，基於 1.0.3，重建中文設定頁，修正新版 calibre 的版面元件相容問題。
- 新增 Traditional Chinese Supplement **1.1.1**，於主介面及 Edit Book 自動補翻指定顯示文字，不顯示工具列或選單按鈕；1.0.0 與 1.1.0 為首次發行前的本地迭代。
- Generate Cover **2.5.0.1 → 2.5.2.1**：同步上游字重、設定與圖片內距遷移，保留中文及本地修正。
- Modify ePub **1.8.11 → 1.8.12.1**：加入 calibre 9.18 封面標題／語言相容修正，補齊移除封面的呼叫參數。
- 更正驗證歸因：Goodreads Sync 的屬性錯誤來自不完整測試替身；原誤標 HardCover 的包其實是 Goodreads Sync 1.16.11，不是真正的 Hardcover 外掛。
- 整合安裝包由十三個增為十七個，核對設定儲存、翻譯格式及實際 EPUB → Markdown 轉檔。

## [v1.3.16] — 2026-11-07

- Enhanced Search and Replace **1.1.0 → 1.2.0**：HTML／XHTML 原始碼模式支援逐字取代及暫時不完整的標籤；縮短錯誤摘要。

## [v1.3.15] — 2026-11-05

- Generate Cover **2.4.2.1 → 2.5.0.1**：採用上游 Qt 字型清單修正與六種語系更新，保留本地修正。

## [v1.3.14] — 2026-11-02

- Enhanced Search and Replace **1.0.0 → 1.1.0**：新增原始碼搜尋、背景進度／取消、篩選排序，補上操作截圖與儲存重開驗證。

## [v1.3.13] — 2026-11-02

- 新增 Enhanced Search and Replace **1.0.0**，提供 Edit Book 全書搜尋、預覽、定位與選擇性取代。

## [v1.3.12] — 2026-11-02

- Embed Metadata Safe **1.0.0 → 1.0.1**：修正 ZIP 安裝層級，按鈕名稱縮為「嵌入資料」。

## [v1.3.11] — 2026-11-02

- 新增 Toolbar Manager **1.0.0**，提供工具列右鍵管理、設定與移除入口。

## [v1.3.10] — 2026-11-02

- 新增 Generate Cover **2.4.2.1**，基於上游 2.4.2，提供正體中文、自動縮字、背景模式、批次取消、匯入保護及小螢幕修正。

## [v1.3.9] — 2026-11-01

- 新增 Skip ASCII Text Plugin **1.0.1** 重寫版，保留檔名原文字元，提供中文設定與切換還原。

## [v1.3.8] — 2026-11-01

- 核對各外掛來源、作者及修改摘要；Extract ISBN 的來源基準與版號由 **1.6.6.1 校正為 1.6.7.1**。

## [v1.3.7] — 2026-11-01

- 首次加入 Extract ISBN，當時宣告 **1.6.6.1**；加入中文介面、ISBN／PDF 掃描修正與測試。版號於下一版校正。

## [v1.3.6] — 2026-11-01

- 新增 Goodreads **1.10.1**，補強書名／作者、識別碼、系列、封面與缺漏資料處理。

## [v1.3.5] — 2026-10-23

- Modify ePub **1.8.9 → 1.8.11**：同步非數值 CSS 邊距修正與語系更新。
- Find Duplicates **1.10.10 → 1.10.11**：同步上游與語系，保留正體中文。
- Count Pages **1.15.2 → 1.15.3**：同步 Goodreads 網址修正、補齊翻譯，還原英文斷句模型並加入回歸測試。
- 統一核對七個外掛的版號、來源、說明與封裝。

## [v1.3.4] — 2026-07-19

- Send to Kindle **1.1.1 → v1.1.1_r.1**（calibre 數字版號仍為 1.1.1）：修正附件檔名模板及未定義格式查詢，保留 Unicode。

## [v1.3.3] — 2026-07-19

- 新增 Send to Kindle **1.1.1**，接入 calibre 寄送流程與檔名模板。

## [v1.3.2] — 2026-06-28

- 新增 AZW6 Image Merge **1.0.0**，合併 AZW6 sidecar 高畫質圖片並納入統一打包。

## [v1.3.1] — 2026-06-28

- 補齊各外掛用途、操作與來源說明，重建安裝包；未記錄外掛版號變更。

## [v1.3.0] — 2026-06-28

- 新增 Count Pages **1.15.2**，納入統一發行；移除失敗的 MultiDict OpenCC 移植。

## [v1.2.0] — 2026-06-28

- 新增 EpubSplit **3.12.0**，加入正體中文、EPUB3 導覽解析及依來源保留 EPUB2／EPUB3 輸出。

## [v1.1.2] — 2026-06-28

- 精簡根目錄 README，將三個外掛的詳細說明分移各自目錄；維持三個獨立安裝包。

## [v1.1.1] — 2026-06-27

- 修正 Find Duplicates 遺漏的共用模組。
- 每次打包前清空 `dist/`，固定產生三個獨立安裝包。

## [v1.1.0] — 2026-06-27

- 首次加入 Modify ePub **1.8.9** 與 Find Duplicates **1.10.10**，將外掛分置各自的 `src/`。
- 此發行因共用模組遺漏，已由 v1.1.1 取代。

## [v1.0.0] — 2026-06-27

- 首次發布 Embed Metadata Safe **1.0.0**，提供中繼資料清理、安全嵌入及格式選擇。

[v1.0.0]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.0.0
[v1.1.0]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.1.0
[v1.1.1]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.1.1
[v1.1.2]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.1.2
[v1.2.0]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.2.0
[v1.3.0]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.0
[v1.3.1]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.1
[v1.3.2]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.2
[v1.3.3]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.3
[v1.3.4]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.4
[v1.3.5]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.5
[v1.3.6]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.6
[v1.3.7]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.7
[v1.3.8]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.8
[v1.3.9]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.9
[v1.3.10]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.10
[v1.3.11]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.11
[v1.3.12]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.12
[v1.3.13]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.13
[v1.3.14]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.14
[v1.3.15]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.15
[v1.3.16]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.16
[v1.3.17]: https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.17
