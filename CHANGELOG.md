# 整合更新紀錄

記錄各外掛何時加入本倉庫、升級版號及主要修改。整合發行版號與外掛版號分開管理；日期採臺灣時間（UTC+8），以 Git 與 GitHub 發行紀錄回補。各外掛的操作、來源及限制見各自 README。

### 各外掛首次加入

| 外掛 | 首次收錄／整合發行 | 日期 | 首次外掛版號 |
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
| Export Folder | v1.3.20 | 2026-11-17 | 1.2.2 |
| Manage Series | v1.3.24 | 2026-11-21 | 1.5.5.1 |
| GitHub Plugin Updater | v1.3.27 | 2026-11-22 | 0.1 |
| CBZ Output | v1.3.26 | 2026-11-22 | 0.1 |
| CrossPoint Reader | v1.3.26 | 2026-11-22 | 0.2.8.1 |
| Shortcuts Helper | v1.3.26 | 2026-11-22 | 1.1.0.1 |
| Columns Helper | v1.3.25 | 2026-11-22 | 2.1.1.1 |
| Diaps Editing Toolbag | v1.3.25 | 2026-11-22 | 0.5.0.1 |
| Plugin Backup | v1.3.25 | 2026-11-22 | 0.1 |
| Tag Cloud | v1.3.33 | 2026-11-27 | 0.1 |
| Virtual Library Builder | v1.3.39 | 2026-11-28 | 0.1.6 |

## [v1.3.40](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.40) — 2026-11-28

### 書庫建立器 0.1.11

- 書庫建立器升級為 0.1.11；大圖示保留開啟建立器，工具列箭頭下拉新增「條件篩選器」，共用既有條件元件。
- 篩選器直接套用 calibre 原生搜尋列，支援 AND／OR 組合或取代，保留目前虛擬書庫範圍。
- 採非模態浮動視窗，套用後保持開啟，仍可操作主書單；反覆套用不疊加舊條件。
- 同次執行關閉再開可還原條件，重啟 calibre 後清空；新增「清空條件」，保留原搜尋及手動改寫內容。
- 左下「建立書庫」透過名稱對話框保存目前組合條件與範圍；取消不建立，同名不覆蓋。
- 通過 43 項隔離測試與原生主視窗、重啟及名稱對話框驗證；其餘 27 支外掛不變，提供 28 個安裝包及 plugins.json。

## [v1.3.39](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.39) — 2026-11-28

### 書庫建立器 0.1.6

- 新增原生虛擬書庫建立、修改、刪除與更名；同名保護，刪除只移除設定、不刪書。
- 支援整庫預覽、欄位值批次建立、上移／下移並保存原生分頁順序。
- 主畫面與產生器共用完整條件表格，逐列 AND／OR 由上往下組合，支援相對日期與原始搜尋式。
- 單一書庫直接儲存，批次及刪除保留確認；固定模式切換版面，加高預設視窗。
- 介面採「書庫建立器」名稱與兩層、左虛線右彩色書架圖示。
- 通過 30 項隔離測試與實際安裝包主視窗驗證；其餘 27 支外掛不變，提供 28 個安裝包及 plugins.json。

## [v1.3.38](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.38) — 2026-11-28

### Tag Cloud 0.1.7

- 新增側欄／浮動視窗模式，切換保留選取與搜尋；保存浮窗位置與大小。
- 新增 calibre 原生快捷鍵設定入口，預設不占用按鍵；僅切換顯示／隱藏，沿用目前模式。關閉或 Esc 僅隱藏浮窗。
- 補上側欄與浮窗實際畫面，更新內外層 README；通過 5 項核心、21 項 Qt／資料庫、11 項書目寫回測試，以及主視窗快捷鍵與重開保存驗證。
- 其餘 26 支外掛版號與內容不變；發行提供 27 個獨立安裝包及 plugins.json，說明不重複標題。

## [v1.3.37](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.37) — 2026-11-28

### Tag Cloud 0.1.6

- 右鍵改為依欄位提供修改／移除；新增型別輸入、原值／新值與影響本數確認，取消不寫入。
- 保留多值欄位的其他值與修改時的系列編號；最後作者改為未知，識別資料只動對應種類。
- 系統／計算欄位停用，書名不可清空；評論以完整原文編輯，不同原文共用摘要時停用批次修改。
- 檢查書庫與資料變更，寫入失敗嘗試還原原值；通過 5 項核心、18 項 Qt／資料庫與 11 項書目寫回測試，另驗證原生確認視窗、實際寫回及重開書庫。
- 核對 27 支外掛的程式版號、內外層 README 與發行清單；其餘 26 支內容不變，發行說明不重複標題。

## [v1.3.36](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.36) — 2026-11-27

### Tag Cloud 0.1.5

- 欄位下拉右側新增齒輪，提供全部欄位勾選清單；預設僅作者、標籤、出版社，各書庫分別保存。
- 支援各類欄位原值產雲及點選篩書；已選詞固定置前，保留未選詞排序，搜尋與顯示數量不隱藏已選詞。
- 同步程式宣告、內外層 README 與發行清單；通過 5 項核心、15 項 Qt／資料庫及實際安裝包主視窗驗證。
- 發行說明正文不重複 GitHub Release 標題；其餘 26 支外掛版號與內容不變。

## [v1.3.35](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.35) — 2026-11-27

### Tag Cloud 0.1.4

- 新增「排序」：跟隨標籤瀏覽器／隨機排列；保留 calibre 的名稱、本數或評分排序設定，預設保持隨機排列。
- 設定按確定後套用並保存；通過名稱／本數／評分排序、隨機位置穩定性與原有篩書測試。
- 同步內外層 README、發行清單與說明；其餘 26 支外掛版號與內容不變。

## [v1.3.34](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.34) — 2026-11-27

### EpubSplit 3.12.0.2

- 修正啟動版號格式寫死三段、遇到本倉庫四段版號時初始化中斷，恢復工具列圖示與按鈕連線；上游基準保持 3.12.0。
- 維護腳本支援任意段數的完整上游基準及本地修訂段，預設只遞增最後修訂次數；暫存檔改放同目錄並原子取代，避免 Windows 跨磁碟搬移失敗。

### Tag Cloud 0.1.3

- 底部雲朵圖示獨立切換詞雲；原標籤瀏覽器開啟時上下分割，關閉時詞雲使用整欄，兩者皆關時收起左欄；保留欄寬與分割比例。
- 原標籤瀏覽器搜尋／設定列歸回分類樹區塊；移除詞雲上方工具列入口、面板標題與關閉按鈕。
- 欄位、統計範圍、數量、配色與清除選取集中至設定；支援標籤、系列、作者及相容自訂欄位，數量提供 50／100／200／500／全部。
- 字級依顯示詞彙本數縮放為 12～36 pt，取熱門詞後亂序排列，行距縮至 115%；同次開啟維持詞彙位置與配色。
- 點選動作提供交集與獨選；底部操作列使用原生搜尋歷史下拉框、清除、放大鏡搜尋、重新整理及齒輪設定。

### 全庫版號與文件核對

- 檢查 27 支外掛的版號格式、宣告、內外層 README 與發行清單；除 EpubSplit 外未發現同類的執行期三段格式問題，其餘 25 支外掛程式及版號保持不變。
- 驗證 27 包共存啟動及 19 個主視窗介面外掛載入；Tag Cloud 通過 4 項核心與 10 項 Qt／資料庫測試，EpubSplit 通過完整版號初始化與維護腳本回歸測試。
- 先前撤下的 v1.3.34／v1.3.35 測試發行調整併入本次正式 v1.3.34，Tag Cloud 的各階段修改保留於外掛更新紀錄。

## [v1.3.33](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.33) — 2026-11-27

### Tag Cloud 0.1

- 新增自有外掛，作者 SamLiao & Codex；在左側分類樹下方顯示可調高度的詞雲。
- 支援標籤、系列、作者與相容自訂欄位、搜尋、多選交集／聯集篩書，以及整庫／虛擬書庫範圍。
- 設定可指定五個候選色、隨機配色或單色，並保存欄位與版面設定。
- 統一建置新增 TagCloud.zip，更新 27 支外掛發行清單；需要 calibre 9.19 或以上。

## [v1.3.32](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.32) — 2026-11-23

### CrossPoint Reader 0.2.8.2

- 2026-11-23 核對 17 支上游修訂外掛；CrossPoint Reader 同步上游 0.2.8 後續提交 `54f73d7`，其餘來源未發現待合併更新。
- 新增 EPUB 拆分前後閱讀位置對照，保留 OPF 屬性、內文空白與寫入失敗回復；保留本地連線修正及正體中文翻譯。
- 8 項位置對照、7 項連線及 4 項語言／設定／協定測試通過；Gutenberg 選用案例因來源網站維護而未驗證，未驗收實體閱讀器。

### GitHub Plugin Updater 0.3.3

- 未安裝項目的狀態統一顯示「未安裝」，移除括號補充文字。

## [v1.3.31](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.31) — 2026-11-22

### GitHub Plugin Updater 0.3.2

- 在設定備份資料夾右側加入「自動備份」，預設勾選並記住設定；更新確認顯示當次選擇。
- 取消勾選後不保留備份包與登錄檔，安裝暫存仍可供一般失敗回復，作業結束即清除。
- Windows、calibre 9.19 通過 71 項測試及原生主視窗入口驗證；同步內外層 README、來源指南、更新紀錄與身分 SHA，重新產出 26 個安裝包及 plugins.json。

## [v1.3.30](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.30) — 2026-11-22

### GitHub Plugin Updater 0.3.1

- 管理來源新增選填 GitHub Token（遮罩輸入、保存及清除），僅授權 API 請求；本機明文設定的限制同步說明。
- API JSON 快取 5 分鐘並依 Token 隔離，記錄限流恢復時間，失敗來源不再顯示成沒有更新。
- Windows、calibre 9.19 通過 68 項測試及原生主視窗入口驗證；未使用真實 Token 進行線上驗證。

### 說明、打包與清單

- 同步內外層 README、來源庫指南與更新紀錄，說明 Token 保存位置、公開庫限制、快取延遲及限流等待行為。
- 重新產出 26 個獨立安裝包與 plugins.json，核對身分內容 SHA、完整 ZIP SHA 與實際程式宣告。

## [v1.3.29](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.29) — 2026-11-22

### GitHub 外掛更新器 0.3

- 新增 kiwidude68/calibre_plugins 的多外掛前綴發行規則，分頁查找 25 支外掛的最新正式版，依標籤與唯一 ZIP 配對。
- 新增 HamsterExAstris/calibre-azw6-image-merge 的單庫單外掛規則，固定配對 AZW6ImageMerge.zip，從最新正式標籤取得版號。
- 使用 GitHub 附件 digest 比對，沒有摘要時明確退回版號判斷；附件 ID 只提示重傳，不代替 SHA。上游原包不要求本倉庫身分檔，仍核對名稱、版號及實際相容性。
- 同名分來源列出且不自動改綁；同批不能勾選兩個同名來源。全新安裝仍只預設本倉庫，更新／重裝保留使用者來源，包含空清單。
- 來源欄可雙擊開啟 GitHub 庫，排序後仍對應正確來源。

### 指南、清單與驗證

- 更新內外層 README、來源庫指南，新增前綴與單庫單外掛規則說明，同步 26 個包的身分與發行 plugins.json。
- Windows、calibre 9.19 通過 58 項測試及原生主視窗入口驗證；實際查詢 kiwidude 247 筆發行取得 25 支外掛，AZW6 單一來源僅需一份 JSON。
- 上游 AZW6 v1.0.0 原包在 calibre 9.19 的隔離載入因 imghdr 缺失失敗；未安裝到正式設定，不自動套用本倉庫修正。macOS／Linux、真實上游安裝及斷電回復尚未驗收。

## [v1.3.28](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.28) — 2026-11-22

### GitHub 外掛更新器 0.1.1

- 入口移至偏好設定進階區第二列左側，使用專用更新圖示，不再提供工具列按鈕；管理來源移至視窗左下方。
- 支援貼上完整 GitHub 庫、Release、分支及檔案網址；勾選欄可切換全選／取消全選，各資料欄可排序，版號按數字段比較，排序不影響勾選外掛身分。
- 已勾選項目經確認後可強制同版重裝、降版或切換來源；保留下載 SHA、身分、名稱、版號與相容性核對。未安裝與載入失敗分別顯示。
- 更新後保留清單，只刷新成功項目的目前版號與狀態；備份資料夾可設定並記憶，舊包以「外掛名稱-原版號.zip」保存。

### 說明、清單與驗證

- 新增來源庫建立與版本檢查指南，連結於內外層 README，說明建庫、清單與身分檔、發布及 SHA／版號判斷流程。

- 補齊內外層 SHA 更新流程、來源綁定與強制安裝說明，核對 26 支外掛的身分／內容 SHA、完整 ZIP SHA 與程式宣告，同步根目錄及發行附件 plugins.json。
- Windows、calibre 9.19 通過 32 項測試，另以原生主視窗確認進階區第二列入口與開關流程；未驗收 macOS／Linux、中途斷電及真實第三方來源。

## [v1.3.27](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.27) — 2026-11-22

### GitHub 外掛更新器 0.1

- 新增多個公開 GitHub 庫來源，預設追蹤本倉庫；固定 ID 與來源綁定，不以同名外掛自動接管其他分支。
- 檢查只取得 Release 資訊與 JSON，先比較本機身分檔的內容 SHA，不同才比較清單版號；勾選並確認後才下載，不自動降版或覆蓋同版不同內容。
- 更新前備份舊包、登錄及啟用狀態，失敗回復；支援更新自身，至少一支成功更新後才啟用「重新啟動 calibre」按鈕。

- 線上驗證後補齊 GitHub 附件空白轉句點的名稱配對，保留本機安裝包檔名；以附件 ID 區分重傳檔案，避免下載快取混用舊清單。

### 身分與發行清單

- 26 個獨立安裝包加入身分檔，包含固定 ID、來源及內容 SHA。內容雜湊排除身分檔、目錄與 ZIP 時間／壓縮資訊；完整 ZIP SHA 另供下載校驗。
- 打包固定時間戳、屬性與順序，產生並同步根目錄及發行附件 `plugins.json`，包含各外掛名稱、版號、相容性、內容 SHA、ZIP SHA 與大小。
- 核對內外層說明、更新紀錄與清單規格；24 項測試通過，涵蓋來源失敗隔離、SHA 優先、原生安裝／回復、自我更新、重啟按鈕及可重現打包。實體第三方來源及 macOS／Linux 尚未驗收。

## [v1.3.26](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.26) — 2026-11-22

- 發行 25 個獨立安裝包；新增 CBZ Output、CrossPoint Reader 與 Shortcuts Helper，更新 Hardcover Sync 與正體中文補強。
- 核對內外層說明、來源、版號與限制；自研及上游修訂列表分開呈現，Skip ASCII 歸入獨立重寫，版號慣例移至上游列表。
- 同步 EpubSplit、Count Pages 包內中文說明；各項功能與測試詳見下列紀錄。

### Hardcover Sync、CrossPoint Reader 與快捷鍵助手

- Hardcover Sync **0.4.0.1 → 0.4.0.2**：重現首次建立欄位確認中關閉 calibre 後的 NoneType.field_metadata 例外，確認返回後重新核對書庫身分，並在沒有書庫時略過快取還原。13 項測試及舊／新版本原生主視窗關閉、正常確認驗證通過。
- 新增 CrossPoint Reader **0.2.8.1**，來源為官方 **0.2.8**、MIT。重現使用者舊 0.1.0 接受任意 UDP 封包即宣告連接；加入探索回覆／連接埠與 HTTP 檔案服務驗證、連線檢查、失敗清理、冷卻及退出／停止控制，保留原生 BookList 與上游功能。
- CrossPoint Reader 補上 **134 條原生正體中文**，涵蓋設定、進度、摘要、錯誤與文字最佳化提示。7 項連線及 4 項語言／設定／協定測試通過，未驗收實體裝置傳輸。
- 新增 Shortcuts Helper **1.1.0.1**，Comfy.n 官方 1.1 附件的程式數字基準為 **1.1.0**，依慣例追加 `.1`。新增 25 條原生正體中文，修正 Qt 6 色彩、排序資料配對、自訂標記與表頭重複連接；4 項測試及原生主視窗驗證通過。
- 兩支新外掛納入統一打包，專案增為二十五支；內外層說明、作者、來源、版號及更新紀錄同步。

### 正體中文補強 1.2.1

- 補齊原生主視窗的開啟書本資料夾／資料檔案資料夾與書本詳細資料動態選單翻譯，啟動及選單顯示時套用，保留快捷鍵、動作資料與觸發回呼。
- Windows、calibre 9.19 通過 3 項選單測試、11 項顯示回歸測試與實際安裝包的原生主視窗驗證，內外層說明及更新紀錄同步。

### 新增 CBZ Output

- 新增自有 **CBZ Output 0.1**，以圖片擷取與 CBZ 封裝需求獨立重寫；功能靈感與新設計記錄於該外掛 NOTES.md，不複製原專案程式。
- 依閱讀順序輸出並識別明確封面；使用唯一流水號避免同名圖片碰撞，保留傳入圖片內容，成功完成暫存檔後才取代目的檔。
- Windows、calibre 9.19 通過 8 項核心與 3 項實際安裝包轉檔測試；同步內外層說明與更新紀錄，納入統一打包，專案增為二十三支外掛。

## [v1.3.25](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.25) — 2026-11-22

- 訂定有上游外掛的版號慣例：完整保留上游基準版號，另加一段本倉庫修訂次數 `.x`；不限制上游版號段數。同一基準依序遞增，更新上游基準後從 `.1` 起算。
- **Send to Kindle 1.1.1 → 1.1.1.1**：統一本倉庫修訂版號，保留上游基準與既有功能。
- **Goodreads 1.10.1 → 1.10.0.1**：統一本倉庫修訂版號，保留上游基準與既有功能。
- **Find Duplicates 1.10.11 → 1.10.11.1**：統一本倉庫修訂版號，保留上游基準與既有功能。
- **EpubSplit 3.12.0 → 3.12.0.1**：統一本倉庫修訂版號，保留上游基準與既有功能。
- **Count Pages 1.15.3 → 1.15.3.1**：統一本倉庫修訂版號，保留上游基準與既有功能。
- **AZW6 Image Merge 1.0.0 → 1.0.0.1**：統一本倉庫修訂版號，保留上游基準與既有功能。

- 新增 **Plugin Backup 0.1**，在外掛偏好設定底部提供勾選或一次全部匯出／批次匯入入口，可選是否包含設定，提供全選切換與兩列按鈕；勾選模式只備份所選外掛可辨識專用設定，全部模式保留工具列位置與快捷鍵等完整設定，保留目前書庫位置。通過 10 項格式／設定測試、4 項安裝 API 測試及原生 GUI 往返驗證，專案增為二十二支外掛。
- 修正 Columns Helper 與 Diaps Editing Toolbag 測試腳本，避免 calibre 最佳化模式略過隔離目錄保護及 GUI 結果檢查；以重新打包的安裝包重跑驗證。
- 核對全部外掛的 README、現有更新紀錄與根目錄總表；同步 Generate Cover 安裝包內的舊版說明並補上 2.5.4.2 紀錄，修正閱讀日期／頁數下載等功能描述、測試範圍與授權標示。

- 新增 **Diaps Editing Toolbag 0.5.0.1**，基於 DiapDealer 的上游 0.5.0（`4589e1a`），包含標籤編輯、智慧標點與 CSS cm 轉 em；新增 71 條原生正體中文及兩份中文內建說明。
- 修正 Qt 6 對話框／列舉、批次進度錯誤傳遞、目前檔案結果清單、Python 3 例外詞重複使用及快捷鍵衝突。七項隔離測試及兩階段原生編輯器儲存重開驗證通過。

- 新增 **Columns Helper 2.1.1.1**，來源為 Comfy.n 的官方 2.1.1 安裝包，提供欄位管理、套組預覽與範本工具。
- 補齊並修正 323 條原生正體中文訊息，新增套組欄位標題／說明與工具列的翻譯入口；保留查詢名稱、公式及內部設定值。納入統一打包。
- Windows、calibre 9.19 的六項原生 Qt 離屏測試通過：語言包、預覽／篩選與範本測試器、排序、取消、四類欄位寫回及資料庫重開。上述操作不需額外的上游核心相容性修正。

## [v1.3.24](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.24) — 2026-11-21

- 新增 **Manage Series 1.5.5.1**，基於 Grant Drake 的上游 1.5.5（`c01cf614`），新增 67 條原生正體中文語言包，修正 calibre 9.19／Qt 6 相容性、自訂系列欄位選取與小數累加誤差。
- 七項隔離測試及安裝包原生 GUI 寫回、關閉重開驗證通過，涵蓋系列編號、取消、自訂欄位、空白書本與資料保護。納入共用打包入口，發行外掛總數增為十九個。

## [v1.3.23](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.23) — 2026-11-21

- 正體中文補強 **1.1.4 → 1.2.0**，擴充偏好設定、動態子視窗、工具列、快捷鍵、範本與編輯器文法／改寫介面的翻譯。
- 核對 43 個調校項目、184 個核心快捷鍵與 196 段書本檢查訊息，補上 Stylelint 全部 32 條啟用規則的訊息，保留內部值、位置及修復行為。
- 在 Windows、calibre 9.19 通過 12 支隔離測試程式；精簡內層使用說明並同步外層版本、來源與修改摘要。附件沿用十八個獨立安裝包的發行方式。

## [v1.3.22](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.22) — 2026-11-21

- 正體中文補強 **1.1.3 → 1.1.4**，補翻「將書本儲存至磁碟」的選項與範本說明。
- 六支自製外掛在 Windows、calibre 9.19 通過隔離驗證，更新內外層說明，記錄實際嵌入、匯出與編輯器儲存重開的範圍。

## [v1.3.21](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.21) — 2026-11-21

- 2026-11-21 核對各外掛上游，Generate Cover **2.5.4.1 → 2.5.4.2** 同步上游同版號的塞爾維亞拉丁語翻譯修訂（`cd41919`），保留正體中文與本倉庫功能修正。其他既有上游沒有新版。

## [v1.3.20](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.20) — 2026-11-17

- 新增 **Export Folder 1.2.2**。從書庫右鍵選單選取固定目的地，沿用 calibre 原生匯出。每個目的地可設定命名範本及格式優先順序，預設為 `{title} - {authors}` 與 `EPUB > PDF`。
- 範本編輯視窗採正體中文，提供三行高的輸入區、即時預覽及可雙擊插入的變數清單。

## [v1.3.19](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.19) — 2026-11-12

- Generate Cover **2.5.2.1 → 2.5.4.1**，採用上游文字量測修正，保留正體中文及本地修正。
- Modify ePub **1.8.12.1 → 1.8.14.1**，採用上游封面替換與移除修正，保留封面頁樣式、正體中文及邊距修正。
- Traditional Chinese Supplement **1.1.2 → 1.1.3**，新增 268 條 calibre 編輯器正體中文對照。

## [v1.3.18](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.18) — 2026-11-09

- Traditional Chinese Supplement **1.1.2**：完整掃描本機 calibre 9.18.0 三份官方正體中文目錄，為含明確簡體字的 310 筆文字建立精確顯示對照。
- 修正「在網路上分享」設定中的簡體文字及連接埠、處理程序、回應等用語；16 項隔離測試通過，保護輸入、下拉與數值設定。
- Hardcover Sync **0.3.1.1 → 0.4.0.1**：採用上游 0.4.0，補翻 ISBN 版本連結與 API 錯誤提示；9 項隔離測試及真實帳號唯讀驗證通過，未驗收遠端寫入。

- 新增根目錄整合更新紀錄，回補外掛首次加入與歷次升級。
- 精簡 Traditional Chinese Supplement 說明，僅保留自身用途、支援範圍、安裝及限制。

## [v1.3.17](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.17) — 2026-11-09

- 新增 Goodreads Sync **1.17.6.1**，基於 1.17.6 直接正體中文化，保留同步核心與設定鍵。
- 新增真正的 Hardcover Sync **0.3.1.1**，基於 Juan York 的 0.3.1，直接正體中文化並驗證與 Goodreads Sync 共存。
- 新增 Markdown Output **1.0.3.1**，基於 1.0.3，重建中文設定頁，修正新版 calibre 的版面元件相容問題。
- 新增 Traditional Chinese Supplement **1.1.1**，於主介面及 Edit Book 自動補翻指定顯示文字，不顯示工具列或選單按鈕；1.0.0 與 1.1.0 為首次發行前的本地迭代。
- Generate Cover **2.5.0.1 → 2.5.2.1**：同步上游字重、設定與圖片內距遷移，保留中文及本地修正。
- Modify ePub **1.8.11 → 1.8.12.1**：加入 calibre 9.18 封面標題／語言相容修正，補齊移除封面的呼叫參數。
- 更正驗證歸因：Goodreads Sync 的屬性錯誤來自不完整測試替身；原誤標 HardCover 的包其實是 Goodreads Sync 1.16.11，不是真正的 Hardcover 外掛。
- 整合安裝包由十三個增為十七個，核對設定儲存、翻譯格式及實際 EPUB → Markdown 轉檔。

## [v1.3.16](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.16) — 2026-11-07

- Enhanced Search and Replace **1.1.0 → 1.2.0**：HTML／XHTML 原始碼模式支援逐字取代及暫時不完整的標籤；縮短錯誤摘要。

## [v1.3.15](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.15) — 2026-11-05

- Generate Cover **2.4.2.1 → 2.5.0.1**：採用上游 Qt 字型清單修正與六種語系更新，保留本地修正。

## [v1.3.14](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.14) — 2026-11-02

- Enhanced Search and Replace **1.0.0 → 1.1.0**：新增原始碼搜尋、背景進度／取消、篩選排序，補上操作截圖與儲存重開驗證。

## [v1.3.13](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.13) — 2026-11-02

- 新增 Enhanced Search and Replace **1.0.0**，提供 Edit Book 全書搜尋、預覽、定位與選擇性取代。

## [v1.3.12](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.12) — 2026-11-02

- Embed Metadata Safe **1.0.0 → 1.0.1**：修正 ZIP 安裝層級，按鈕名稱縮為「嵌入資料」。

## [v1.3.11](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.11) — 2026-11-02

- 新增 Toolbar Manager **1.0.0**，提供工具列右鍵管理、設定與移除入口。

## [v1.3.10](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.10) — 2026-11-02

- 新增 Generate Cover **2.4.2.1**，基於上游 2.4.2，提供正體中文、自動縮字、背景模式、批次取消、匯入保護及小螢幕修正。

## [v1.3.9](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.9) — 2026-11-01

- 新增 Skip ASCII Text Plugin **1.0.1** 重寫版，保留檔名原文字元，提供中文設定與切換還原。

## [v1.3.8](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.8) — 2026-11-01

- 核對各外掛來源、作者及修改摘要；Extract ISBN 的來源基準與版號由 **1.6.6.1 校正為 1.6.7.1**。

## [v1.3.7](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.7) — 2026-11-01

- 首次加入 Extract ISBN，當時宣告 **1.6.6.1**；加入中文介面、ISBN／PDF 掃描修正與測試。版號於下一版校正。

## [v1.3.6](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.6) — 2026-11-01

- 新增 Goodreads **1.10.1**，補強書名／作者、識別碼、系列、封面與缺漏資料處理。

## [v1.3.5](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.5) — 2026-10-23

- Modify ePub **1.8.9 → 1.8.11**：同步非數值 CSS 邊距修正與語系更新。
- Find Duplicates **1.10.10 → 1.10.11**：同步上游與語系，保留正體中文。
- Count Pages **1.15.2 → 1.15.3**：同步 Goodreads 網址修正、補齊翻譯，還原英文斷句模型並加入回歸測試。
- 統一核對七個外掛的版號、來源、說明與封裝。

## [v1.3.4](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.4) — 2026-07-19

- Send to Kindle **1.1.1 → v1.1.1_r.1**（calibre 數字版號仍為 1.1.1）：修正附件檔名模板及未定義格式查詢，保留 Unicode。

## [v1.3.3](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.3) — 2026-07-19

- 新增 Send to Kindle **1.1.1**，接入 calibre 寄送流程與檔名模板。

## [v1.3.2](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.2) — 2026-06-28

- 新增 AZW6 Image Merge **1.0.0**，合併 AZW6 sidecar 高畫質圖片並納入統一打包。

## [v1.3.1](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.1) — 2026-06-28

- 補齊各外掛用途、操作與來源說明，重建安裝包；未記錄外掛版號變更。

## [v1.3.0](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.0) — 2026-06-28

- 新增 Count Pages **1.15.2**，納入統一發行；移除失敗的 MultiDict OpenCC 移植。

## [v1.2.0](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.2.0) — 2026-06-28

- 新增 EpubSplit **3.12.0**，加入正體中文、EPUB3 導覽解析及依來源保留 EPUB2／EPUB3 輸出。

## [v1.1.2](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.1.2) — 2026-06-28

- 精簡根目錄 README，將三個外掛的詳細說明分移各自目錄；維持三個獨立安裝包。

## [v1.1.1](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.1.1) — 2026-06-27

- 修正 Find Duplicates 遺漏的共用模組。
- 每次打包前清空 `dist/`，固定產生三個獨立安裝包。

## [v1.1.0](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.1.0) — 2026-06-27

- 首次加入 Modify ePub **1.8.9** 與 Find Duplicates **1.10.10**，將外掛分置各自的 `src/`。
- 此發行因共用模組遺漏，已由 v1.1.1 取代。

## [v1.0.0](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.0.0) — 2026-06-27

- 首次發布 Embed Metadata Safe **1.0.0**，提供中繼資料清理、安全嵌入及格式選擇。
