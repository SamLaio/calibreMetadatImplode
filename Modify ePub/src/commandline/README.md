## 從命令列執行 Modify ePub

`me.py` 可直接修改磁碟上的 EPUB，無需先加入書庫。請先安裝 calibre 與本倉庫的 Modify ePub **1.8.11**；最低 calibre 為 **3.48.0**。腳本會載入已安裝的外掛。

### 查看選項

在本倉庫根目錄執行：

```powershell
calibre-debug -e "Modify ePub/src/commandline/me.py" -- --help
```

若使用發行 ZIP，可將 `commandline/me.py` 解開，再把命令中的腳本路徑改為實際位置。

### 修改書檔

```powershell
calibre-debug -e "Modify ePub/src/commandline/me.py" -- "input.epub" "output.epub" --smarten_punctuation --remove_javascript
```

第一個路徑是來源 EPUB，第二個是輸出 EPUB。省略輸出路徑時會覆寫來源；執行前請備份，並避免指定已有重要檔案的輸出路徑。

### 限制

- 命令列不支援 `--add_replace_jacket` 與 `--update_metadata`，因為缺少圖形介面提供的書庫中繼資料。
- 其他可用選項以腳本的 `--help` 為準。
- 可參考同資料夾的 [example.cmd](example.cmd) 建立批次命令。

