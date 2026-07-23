# Feature Factory 樣版(Plan A:逐 repo 安裝、版本控制)

**語言 Language:** [English](../README.md) · 繁體中文

一套可重複使用、語言無關的 Claude Code 開發管線。同一份樣版複製進每個 repo,
行為由各 repo 自己的 manifest(`.claude/factory/project.json`)驅動。全端、
純前端、純後端專案皆適用。

## 深入了解
- **[教育訓練教材](factory-training_zh-TW.html)** — 一頁式導覽:設計理念、產線圖、
  底層機制與 Fable 5 升級內容(適合新人上手)。
- **[速查表](factory-cheatsheet_zh-TW.md)** — 單一畫面速查:安裝、指令流、卡住狀態
  對照表、鐵則(適合日常查閱)。

## 環境需求
- Claude Code(CLI)。Agents / commands / hooks 只在其中生效。
- PATH 上要有 `bash` 與 `jq`(hooks 依賴它們)。Windows 請從 Git Bash 或 WSL
  執行 Claude Code 讓 hooks 能運作,並安裝 `jq`。缺少 `jq` 時,hooks 會 fail-safe
  放行並印出提示——也就是強制機制被跳過,但不會弄壞任何東西。

## 安裝進一個 repo
```
# macOS / Linux
./install.sh /path/to/your/repo
# Windows PowerShell
./install.ps1 C:\path\to\your\repo
```
安裝器會把 `.claude/` 複製進 repo 並把 hooks 設為可執行。若 repo 已有
`CLAUDE.md`,安裝器**不會**修改它——只把 `CLAUDE.factory-snippet.md` 放在旁邊
供你自行合併;若沒有 `CLAUDE.md`,snippet 會直接複製為起始版。
安裝後的預期數量:8 個 agents、15 個 commands、3 個 hooks。

## repo 內首次設定(3 步)
1. 把 `CLAUDE.factory-snippet.md` 合併進你的 `CLAUDE.md`(頂部附近加入兩行
   `@import` —— `CONVENTIONS.md` 與 `terminology-zh-tw.md`;區塊貼進
   「Project-Specific Rules」)。若讓 snippet 直接當起始版則跳過。
2. 在 repo 內開啟 Claude Code,執行 `/feat-init`(偵測技術棧或直接問你;
   寫出含 `docsDir` 的 `project.json`,**不會** scaffold 程式碼)。
3. 確認 manifest 內容。

## 跑一個 feature
```
/feat-new <slug> "你要的東西"
/feat-research <slug>
/feat-grill <slug>      # 互動拷問 -> decisions.md(story 步驟強制檢查)
/feat-story <slug>      # 看過 story.md 之後:
/feat-spec <slug>       # 看過 brief.md 之後:
/feat-backend <slug>    # backend track 有啟用才跑
/feat-frontend <slug>   # frontend track 有啟用才跑
/feat-ship <slug>       # FABLE 5(選用):用一個 /goal 收斂 verify→validate→fix
/feat-verify <slug>
/feat-validate <slug>
/feat-fix <slug>        # 有 findings 才跑;受 loopMaxRetries 限制
/feat-docs <slug>       # validate 乾淨後:README + 指南/範例(英文,再繁中)
/feat-distill <slug>    # FABLE 5:收尾步驟——把驗證過的教訓存入 MEMORY.md
/feat-status <slug>     # 隨時可查
```
FABLE 5 新增功能(model 路由、classifier-refusal 處理、記憶層、收斂迴圈)
記載於 `.claude/factory/CONVENTIONS.md` 的「Fable 5 addendum」。在其他模型的
session 下,這些新增功能惰性無害。
完整設計見 `.claude/factory/CONVENTIONS.md`。

## 註解、文件與台灣用詞
`.claude/factory/terminology-zh-tw.md`(由 `CLAUDE.md` @import)是以下三件事的
單一事實來源:
- **雙語註解** — 每則註解為一行英文、緊接一行繁體中文(台灣)。
- **文件語言政策** — `.claude/factory/<slug>/` 底下的開發過程產物一律英文;
  使用者文件(`README.md` 與 `docsDir` 底下所有檔案)先寫英文,再產出 `_zh-TW`
  翻譯版,兩版頂部都要有語言切換連結。
- **台灣用詞字典** — 一律使用台灣主流用詞(不用中國大陸用詞)。

`/feat-docs`(**doc-writer** agent)產出上述使用者文件,並以 **Mermaid** 繪製
圖表(流程圖 / 循序圖 / 甘特圖 / 心智圖 / 類別圖 / 狀態圖)。它**不會**搬移或
封存各 slug 的 artifacts——那些檔案留在原地,作為管線的紀錄。


本樣版刻意不自動 commit、不自動開 PR。
