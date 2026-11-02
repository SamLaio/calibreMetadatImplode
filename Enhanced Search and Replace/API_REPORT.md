# Calibre 9.x Edit Book API 查核報告

日期：2026-11-02；插件 1.1.0。本機 `calibre-debug --version` 為 **calibre 9.17**。本報告以官方教學及 GitHub **v9.0.0、v9.17.0** 固定標籤來源查核；不將 master 或目前線上手冊視為所有 9.x 的證明。下載來源的 SHA256 列於 tests/source_manifest.json（widget.py 是 editor/widget.py 的本機縮短名稱）。

## 1.1.0 發行核對

正式版整合本次新增功能與版面修正，版號、README／操作截圖、CHANGELOG、根目錄摘要及整合發行 v1.3.14 說明一致。發行 ZIP 重新執行七組驗證，包括獨立程序的原生儲存重開流程。

## 1.1.0 背景搜尋與整合驗收

- SearchWorker 於 QThread 執行純資料的搜尋／投影與檔案讀取；Qt 編輯器緩衝區在主執行緒分檔擷取，工作中不存取 Qt 控件。搜尋只讀，切換書籍後丟棄舊工作結果；取消採合作式中斷，Regex 最長等到單檔 2 秒逾時。
- QAbstractTableModel／QSortFilterProxyModel 按需顯示結果，定位與勾選透過來源索引映射；數值位置排序、狀態篩選與可見列批次均有回歸。
- Windows 真實 Main、Boss、WebEngine、SaveManager 及外掛動作已驗收，沒有主視窗替身：修改、Undo/Redo、原始碼取代、跨檔批次、原生儲存、正常退出、新程序重開及預覽文字一致均通過。實測 QPA windows、縮放 1.75；測試由 Qt 程式操作實際控件，不等於所有手動鍵鼠流程。
- 下面早期各節的「完整 GUI／保存未測」屬當時的證據界線；本節更新上述已完成路徑，其餘版本、平台與未覆蓋流程仍不宣稱通過。

## 0.4.0 文字檔類型補記

使用 Calibre syntax_from_mime 辨識可編輯文字，補上 text/* 及 JSON 類型；類型選單依書中副檔名建立並預設全選。非 HTML 檔案對原始碼執行相同 Regex／群組擴展，XML 與 JSON 的整份輸出在提交前驗證；CSS／JS 不做完整語法驗證。未開啟檔案的讀取明確停用隱含 NFC 正規化，仍由寫入驗證拒絕非 NFC 輸出。OPF 單檔同步沿用真實 Boss.commit_editor_to_container；跨檔則於更新 OPF 後刷新 MIME 清單。完整視窗與保存事件鏈尚未驗收。

## 0.3.0 取代模式補記

搜尋仍只作用於全書文字投影，模式僅決定寫回形式。跨標籤純文字以字元差異形成來源修補並保留原標記，檢查群組的原位對應；無法確定新文字格式歸屬時拒絕。HTML 片段先檢查新內容與原來源跨度的配對，再由 replace 驗證完整文件；不宣稱完成 EPUB schema 驗證。保留列的來源位移依實際寫入的原碼長度調整。

## 0.2.0 全書搜尋補記

以下原始單檔決策記錄為 0.1.0 的驗證背景；0.2.0 已改為遍歷 Container 的 OEB_DOCS，已開啟檔案讀取編輯器緩衝區，未開啟檔案讀取 raw_data。結果包含檔名與各檔快照，定位時呼叫 Boss.edit_file。跨檔勾選先驗證所有輸出，以真實 Boss.add_savepoint／rewind_savepoint、GlobalUndoHistory 與 Container 完成寫入、整批回復及 Undo/Redo 測試；GUI 更新接收端仍是最小替身，僅 update_editors_from_container 使用真實方法。跨檔復原使用原生書籍「復原至」，不是單一編輯器 Ctrl+Z。完整視窗、存檔事件鏈及其他版本仍未實測。

## 1.0.0 發行核對

原始碼版號為 1.0.0，外掛來源、作者及安裝要求已同步根目錄與外掛 README，更新摘要見 CHANGELOG.md。以下早期章節保留各階段驗證背景，不代表所有功能已完成可見 GUI 驗收。

## 官方文件與版本來源

- [官方插件教學：Edit book plugins](https://manual.calibre-ebook.com/creating_plugins.html#edit-book-plugins)：EditBookToolPlugin、import-name marker、main.py Tool 與 create_action。
- [官方 API 文件](https://manual.calibre-ebook.com/plugins.html)：插件基類；實際 Editor/Boss 操作以下列固定版本原始碼為準。
- [v9.0.0 官方教學來源](https://github.com/kovidgoyal/calibre/blob/v9.0.0/manual/creating_plugins.rst)、[v9.17.0 官方教學來源](https://github.com/kovidgoyal/calibre/blob/v9.17.0/manual/creating_plugins.rst)。

## 實際 API 所在（兩版本均找到對應定義）

| API／定義 | 固定版本來源 |
| --- | --- |
| `EditBookToolPlugin` | [v9.0.0:L795](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/customize/__init__.py#L795) / [v9.17.0:L835](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/customize/__init__.py#L835) |
| `Tool` | [v9.0.0:L19](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/plugin.py#L19) / [v9.17.0:L17](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/plugin.py#L17) |
| `load_plugin_tools` | [v9.0.0:L112](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/plugin.py#L112) / [v9.17.0:L116](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/plugin.py#L116) |
| `current_editor` | [v9.0.0:L185](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/ui.py#L185) / [v9.17.0:L181](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/ui.py#L181) |
| `edit_file(` | [v9.0.0:L1801](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/boss.py#L1801) / [v9.17.0:L2054](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/boss.py#L2054) |
| `show_editor(` | [v9.0.0:L1827](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/boss.py#L1827) / [v9.17.0:L2084](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/boss.py#L2084) |
| `commit_all_editors_to_container(` | [v9.0.0:L1303](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/boss.py#L1303) / [v9.17.0:L1469](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/boss.py#L1469) |
| `commit_editor_to_container(` | [v9.0.0:L1289](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/boss.py#L1289) / [v9.17.0:L1455](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/boss.py#L1455) |
| `replace_data(` | [v9.0.0:L235](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/editor/widget.py#L235) / [v9.17.0:L375](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/editor/widget.py#L375) |
| `replace_text(` | [v9.0.0:L320](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/editor/text.py#L320) / [v9.17.0:L325](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/editor/text.py#L325) |
| `add_savepoint(` | [v9.0.0:L887](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/boss.py#L887) / [v9.17.0:L993](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/boss.py#L993) |
| `apply_container_update_to_gui(` | [v9.0.0:L466](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/gui2/tweak_book/boss.py#L466) / [v9.17.0:L518](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/gui2/tweak_book/boss.py#L518) |
| `compile_regular_expression(` | [v9.0.0:L12](https://github.com/kovidgoyal/calibre/blob/v9.0.0/src/calibre/ebooks/conversion/search_replace.py#L12) / [v9.17.0:L11](https://github.com/kovidgoyal/calibre/blob/v9.17.0/src/calibre/ebooks/conversion/search_replace.py#L11) |

## 實作決策及可行性

1. **載入與視窗**：ZIP 根層 __init__.py 宣告 EditBookToolPlugin，marker 指定 text_regex_p0 匯入名；loader 從 main.py 尋找 Tool 子類。QAction 開 QDialog.show()，非模態。隔離安裝及工具 discovery 已測；完整主視窗選單未實測。
2. **取得編輯中內容**：gui.central.current_editor 是 Editor wrapper，底層 ed.editor 是 TextEdit。直接 toPlainText() 取精確緩衝區快照，避開 Editor.get_raw_data() 的 NFC／尾端零字元正規化對位置的影響。Container.raw_data 不能代表尚未同步的手改文字；寫入後使用 Boss.commit_all_editors_to_container。關閉分頁、換書及內容變更以物件身分和全文快照檢查。
3. **純文字與群組**：嚴格 XML 檢查後，用 HTMLParser 事件建立文字到原始碼字元跨度映射；inline 標籤不產生分隔，block 產生換行。這不是 CSS 渲染文字。使用 Calibre compile_regular_expression 與 REGEX_FLAGS（VERSION1、WORD、FULLCASE、MULTILINE、UNICODE），同其 Edit Book 搜尋使用的 regex 引擎；不走 HTML 原始碼搜尋。`match.expand` 使用原生 `\g<1>`／命名群組；`$1` 是明確的 UI 轉接層，不是上游原生語法。搜尋逾時 2 秒。
4. **定位**：boss.show_editor(name) 切到來源分頁；QTextCursor 使用 UTF-16 code unit，必須轉換 emoji 等非 BMP 字元的位置。跨 inline 標籤來源範圍含標籤。真實 TextEdit 選取已離屏測試；完整 GUI 切頁與焦點尚未測試。
5. **寫入與 Undo/Redo**：Editor.replace_data → TextEdit.replace_text，內部 beginEditBlock/endEditBlock 插入全文，不用 setPlainText 清掉 undo stack。每次單筆／單檔勾選批次是一個文字編輯步驟。以真實 Editor 驗證 undo/redo 還原精確全文；寫入的 XML 先完整驗證，非 NFC 輸出拒絕，避免 replace_data 的正規化改動其他文字。safe 匹配只改動連續來源文字跨度，保留其他標記與屬性；跨標籤只預覽，不宣稱已實作保格式寫回。
6. **同步**：Editor 的 textChanged → _data_changed 設 is_synced_to_container=False 並發 data_changed；Boss.commit_editor_to_container 以 ed.data 寫入 Container 並標同步。真實 Boss 方法＋真實臨時 EPUB Container 已執行；接收 Boss 的 host 為最小替身，未執行完整 init_editor／預覽／保存事件鏈。Undo 後編輯器再變 dirty，須正常同步後 Container 才更新。
7. **另一條交易路線**：Boss.add_savepoint、apply_container_update_to_gui 提供 Container 級修改／書籍歷史路徑。本 P0 不混用它與編輯器 Undo；沒有全書原子交易的實測證據，故限制單檔。這些方法僅原始碼查核，未在本 P0 執行。

API 風險：Tool 是正式插件入口；Boss、central、Editor.editor 等屬內部實作介面，即使兩個標籤存在也不等於穩定相容合約。插件宣告 minimum 9.0 只代表安裝門檻；實際執行證據僅本機 9.17，不宣稱全部 9.x 通過。

## 證據強度

| 項目 | 結果／限制 |
| --- | --- |
| API 存在與呼叫路徑 | 9.0.0、9.17.0 原始碼查核，連結如上；未逐版檢查中間版本 |
| 安裝 ZIP | 9.17 calibre-customize 隔離設定成功，未修改使用者原設定 |
| 未儲存緩衝區、純文字投影、群組、實體、排除屬性/head/script/style | 自動斷言通過 |
| 真實 Editor 寫入／精確 Undo/Redo／UTF-16 選取 | 9.17 離屏通過 |
| QDialog／QTableWidget 搜尋、逐筆、勾選批次、過期拒絕、格式拒絕 | 真實 Qt 控件離屏通過，主視窗接收端是最小替身 |
| Container 同步 | 真實 Boss 兩個 commit 方法與 Container 通過；主視窗事件鏈未測 |
| 完整 GUI、預覽、存檔重開、其他版本與平台 | 未實測；見 TEST_PLAN.md |
| 跨標籤保格式取代 | 未實作，刻意拒絕；不能列為通過 |

## 結論

已建立可安裝並可重跑測試的 P0。已得到單檔緩衝區讀取、跨標籤純文字搜尋與群組預覽、來源位置轉換及編輯器 Undo/Redo 的執行證據；完整 Edit Book 整合仍須按人工測試表驗收。下一階段應先完成 GUI／保存事件鏈測試，再決定跨標籤格式歸屬規則及全書交易，不直接擴大批次寫入範圍。

## 接續驗證補記（2026-11-02）

修正搜尋條件變更後仍可套用舊結果的問題：文字欄位變動及開始搜尋會清空結果，無結果時禁止定位／批次寫入。新增 Qt 回歸斷言並重跑核心與 Editor 測試通過。真正 9.17 主視窗已觀察到插件結果與 WebEngine 文字，但擷取及輸入工具不穩定，未完成 GUI 寫入／保存事件鏈；詳見 TEST_PLAN.md。

## XHTML 相容性修正（2026-11-02）

搜尋與寫入共用 validate_xhtml：使用標準庫 Expat 驗證，允許 DOCTYPE，禁止讀取外部 DTD 及參數實體，內部 DTD 子集拒絕。僅在驗證副本將 XHTML 標準具名實體轉成數字實體，略過註解、CDATA 與處理指令；來源投影與修補仍使用原文，所以位置及宣告不因驗證改變。未知實體及不合法 XML 拒絕。錯誤訊息不再包含測試階段稱呼。
