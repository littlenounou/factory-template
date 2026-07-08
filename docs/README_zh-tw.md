# Feature Factory 模板(Plan A:逐 repo 安裝、版本控制)

**語言 Language:** [English](../README.md) · 繁體中文

一套可重複使用、語言無關的 Claude Code 開發管線。同一份模板複製進每個 repo,
行為由各 repo 自己的 manifest(`.claude/factory/project.json`)驅動。全端、
純前端、純後端專案皆適用。

## 深入了解
- **[教育訓練教材](factory-training_zh-tw.html)** — 一頁式導覽:設計理念、產線圖、
  底層機制與 Fable 5 升級內容(適合新人上手)。
- **[速查表](factory-cheatsheet_zh-tw.md)** — 一屏速查:安裝、指令流、卡住狀態
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

## repo 內首次設定(3 步)
1. 把 `CLAUDE.factory-snippet.md` 合併進你的 `CLAUDE.md`(`@import` 那行放頂部
   附近;區塊貼進「Project-Specific Rules」)。若讓 snippet 直接當起始版則跳過。
2. 在 repo 內開啟 Claude Code,執行 `/feat-init`(偵測技術棧或直接問你;
   只寫 `project.json`,**不會** scaffold 程式碼)。
3. 確認 manifest 內容。

## 跑一個 feature
```
/feat-new <slug> "你要的東西"
/feat-research <slug>
/feat-story <slug>      # 看過 story.md 之後:
/feat-spec <slug>       # 看過 brief.md 之後:
/feat-backend <slug>    # backend track 有啟用才跑
/feat-frontend <slug>   # frontend track 有啟用才跑
/feat-verify <slug>
/feat-validate <slug>
/feat-fix <slug>        # 有 findings 才跑;受 loopMaxRetries 限制
/feat-distill <slug>    # FABLE 5:把這個 feature 驗證過的教訓存入 MEMORY.md
/feat-ship <slug>       # FABLE 5(選用):用一個 /goal 收斂 verify→validate→fix
/feat-status <slug>     # 隨時可查
```
FABLE 5 新增功能(model 路由、classifier-refusal 處理、記憶層、收斂迴圈)
記載於 `.claude/factory/CONVENTIONS.md` 的「Fable 5 addendum」。在其他模型的
session 下,這些新增功能惰性無害。
完整設計見 `.claude/factory/CONVENTIONS.md`。


本模板刻意不自動 commit、不自動開 PR。
