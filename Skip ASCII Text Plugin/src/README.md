# Skip ASCII Text Plugin（保留原文字元）

版本：**1.0.1**；作者：**SamLiao & Codex**；授權：GPL v3；最低 calibre：5.0.0。

## 功用與理念

保留檔名中的中文等原文字元，避免轉成拼音。透過執行期間替換 calibre 的檔名轉寫函式達成，不直接修改 calibre 安裝檔；非法檔名字元仍由 calibre 清理。

## 安裝與使用

1. 從 [v1.3.9 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.9) 下載此外掛 ZIP。
2. 在 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝，重新啟動 calibre。
3. 從「偏好設定 → 工具列與選單」加入「保留原文字元」。
4. 點選按鈕，在設定視窗切換「啟用原文字元保留」，查看效果示意後按「儲存」。

全新安裝預設啟用，舊安裝沿用原設定。按「取消」不套用變更。

## 本倉庫修改

- 重新實作核心與設定介面，保留舊版識別名稱與設定。
- 修正位元組輸入、重複切換及停用還原，不重新載入整個模組。
- 加入正體中文介面、「文」字勾號圖示、檔名示意及大字體排版。

## 限制

- 只影響使用此共用函式的流程，不保證所有裝置及匯出方式都生效，也不會自動重新命名既有檔案。
- 與其他修改同一函式的外掛可能互相影響；停用或移除整個外掛後，請重新啟動 calibre。
- 本機 calibre 9.17.0 通過 10 組測試；尚未驗證所有舊版與實際裝置傳輸。

## 來源與授權

功能參考 [shiratori3/calibre-plugins v1.0.0](https://gitee.com/shiratori3/calibre-plugins/releases/tag/v1.0.0) 及 [Bilibili 原文](https://www.bilibili.com/opus/781451729027727384)。原版作者欄為 Billy Zhou，採 BSD 3-Clause 授權，著作權標示為白鳥。

本倉庫重寫版作者為 SamLiao & Codex，採 GPL v3。原版授權全文見 `UPSTREAM_LICENSE.txt`，重寫版授權見 `LICENSE`。

## 自行打包

在專案根目錄執行 `python -B build_release.py`，安裝包會輸出至 `dist/Skip ASCII Text Plugin-zh_TW-release.zip`。
