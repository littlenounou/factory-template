# Feature Factory 模板（方案 A：逐 repo、納入版本控制）

**Language 語言:** [English](../README.md) · 繁體中文

可重複使用、與程式語言無關的 Claude Code 流水線。一份模板複製進每個 repo，行為由該 repo 的
清單檔（`.claude/factory/project.json`）驅動。全端、純前端、純後端專案皆適用。

## 延伸閱讀
- **[訓練指南](factory-training_zh-TW.html)** — 單頁導覽：設計哲學、裝配線、各項機制，以及
  Fable 5 升級內容（供新人上手）。
- **[速查表](factory-cheatsheet_zh-TW.md)** — 單一畫面快速參考：安裝、命令流程、卡住狀態對照表、
  不可妥協事項（供日常使用）。

## 環境需求
- Claude Code（CLI）。agents／commands／hooks 只在其中生效。
- PATH 上要有 `bash` 與 `jq`（hooks 會用到）。在 Windows 上請從 Git Bash 或 WSL 啟動
  Claude Code 以便 hooks 能執行，並安裝 `jq`。缺少 `jq` 時 hooks 會安全降級（放行）並印出
  提示——亦即略過強制檢查，不會壞掉任何東西。

## 安裝進 repo
```
# macOS / Linux
./install.sh /path/to/your/repo
# Windows PowerShell
./install.ps1 C:\path\to\your\repo
```
安裝程式會把 `.claude/` 複製進 repo，並讓 hooks 具備執行權限。若 repo 已有 `CLAUDE.md`，
它**不會**被修改——安裝程式會把 `CLAUDE.factory-snippet.md` 放在旁邊供你自行合併。若沒有
`CLAUDE.md`，則直接以該 snippet 作為起始檔。安裝後的預期數量：8 個 agents、17 個 commands、
3 個 hooks。

## 在 repo 內的首次設定（3 步驟）
1. 把 `CLAUDE.factory-snippet.md` 合併進你的 `CLAUDE.md`（在檔案上方加入兩行 `@import` ——
   `CONVENTIONS.md` 與 `terminology-zh-tw.md`；並把該區塊貼進「Project-Specific Rules」）。
   若你讓 snippet 直接當起始檔則可略過。`.claude/factory/` 底下的三份伴隨文件是以 pointer
   觸達、不匯入的，請勿把它們列入 `@import`。
2. 在 repo 內開啟 Claude Code 並執行 `/feat-init`（偵測技術堆疊或詢問你；寫出
   `project.json`，含 `docsDir`；**不會**產生任何程式碼骨架）。
3. 確認產出的清單檔。

## 跑一個功能
```
/feat-new <slug> "你想要什麼"
/feat-research <slug>
/feat-grill <slug>      # 逐輪次訪談 -> decisions.md（story 以此為前置條件）
/feat-story <slug>      # 審閱 story.md，然後：
/feat-spec <slug>       # 審閱 brief.md，然後：
/feat-backend <slug>    # 若後端軌道啟用
/feat-frontend <slug>   # 若前端軌道啟用
/feat-ship <slug>       # FABLE 5（選用）：在單一 /goal 下收斂 verify→validate→fix
/feat-verify <slug>
/feat-validate <slug>
/feat-fix <slug>        # 僅在有發現時；受 loopMaxRetries 限制
/feat-unblock <slug>    # `blocked` 之後：人工授權復工——重置 retry 額度
/feat-docs <slug>       # validate 乾淨後：README + 指南／範例（先英文，再 zh-TW）
/feat-distill <slug>    # FABLE 5：收尾步驟——把已驗證的教訓存入 MEMORY.md
/feat-status <slug>     # 任何時候

# 維護指令（產線之外——無 slug、不產 artifacts）
/feat-recomment [path]  # 把舊的交錯式雙語註解轉成區塊形式
```
FABLE 5 的增補（模型路由、classifier 拒絕處理、記憶層、收斂迴圈）記載於
`.claude/factory/CONVENTIONS.md` 的「Fable 5 addendum」。在其他模型上執行時，這些增補
無作用但也無害。完整設計請見 `.claude/factory/CONVENTIONS.md`。

## 代理恆常載入什麼，又在何時去取用什麼

`CLAUDE.md` 承載行為契約並 `@import` 兩份文件，因此這三份每一輪都在 context 內。另有三份
文件放在它們旁邊，只在對應分支觸發時才被取用——藉此把它們排除在恆常載入的預算之外：

| 檔案 | 何時被取用 |
|---|---|
| `.claude/factory/EXPLORE-MODE.md` | 開始探索性工作時（`explore mode`／`spike`／POC） |
| `.claude/factory/PHASE-BOUNDARIES.md` | 你正站在階段邊界、決定這份 context 該怎麼處理時 |
| `.claude/factory/CLAUDE-rationale.md` | 由人判斷某條規則是否仍值得保留時——代理永遠不讀這一份 |

每條規則的**設計理由**都在 `CLAUDE-rationale.md`。修改規則前先讀它；修改時在同一個 PR 內
一併更新它。

## 註解、文件與台灣術語
`.claude/factory/terminology-zh-tw.md`（由 `CLAUDE.md` 匯入）是以下三件事的單一真實來源：
- **雙語註解** — 先寫完整的英文區塊，中間以一行空註解作為分隔，再寫完整的繁體中文（台灣）
  區塊。切勿逐行交錯。
- **文件語言政策** — `.claude/factory/<slug>/` 底下的流水線產出物一律英文；面向使用者的文件
  （`README.md` 與 `docsDir` 底下的全部內容）先英文，再加上 `_zh-TW` 譯本，兩個版本頂端各放
  一條語言切換連結。
- **台灣術語辭典** — 只用台灣主流用語（不使用中國大陸的變體）。

在區塊規則之前寫下的程式碼，可用 `/feat-recomment [path]` 就地遷移，該命令驅動
`.claude/factory/comment-migrate.py` —— 一支確定性腳本，只**重新排序**既有的註解行
（絕不翻譯或改寫），任何有疑義的部分都留給人處理，並列在
`comment-migration-report.md` 內。預設為 dry-run；`--check` 在仍有交錯註解時以非零狀態
結束，可作為 CI 守門。

`/feat-docs`（**doc-writer** agent）會用 **Mermaid** 圖表產出上述面向使用者的文件
（flowchart／sequence／Gantt／mindmap／class／state）。它**不會**移動或封存各 slug 的產出物
——那些留在原處，作為流水線的紀錄。


本模板刻意不自動 commit，也不自動開 PR。
