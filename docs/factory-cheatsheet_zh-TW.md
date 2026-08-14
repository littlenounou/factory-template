# Feature Factory 速查表(Fable 5 版)

**語言 Language:** 繁體中文 · [English](factory-cheatsheet_en.md)

> 完整教材:`docs/factory-training_zh-TW.html` · 設計細節:`.claude/factory/CONVENTIONS.md`
> 核心信念:可靠性來自系統,不是模型——順序靠指令、範圍靠 hooks、迴圈有停損、驗收靠獨立驗證者。

## 安裝(每 repo 一次)

```bash
./install.sh /path/to/repo   # 複製 .claude/;Windows 用 install.ps1(Claude Code 走 Git Bash/WSL)
jq --version                 # hooks 依賴 jq;缺少 = 強制機制沒開(fail-safe 放行)
/feat-init                   # 在 Claude Code 內執行:偵測技術棧、寫 project.json,不 scaffold
```

已有 CLAUDE.md → 合併兩個 `<<< FEATURE FACTORY >>>` 區塊;全新 repo → snippet 自動成為起始 CLAUDE.md。

**契約檔案。** `CLAUDE.md` `@import` 了 `CONVENTIONS.md` 與 `terminology-zh-tw.md`,這三份每一輪都載入。`.claude/factory/` 底下另有三份以 pointer 觸達、不匯入:`EXPLORE-MODE.md`、`PHASE-BOUNDARIES.md`,以及 `CLAUDE-rationale.md`(每條規則的理由——只給人讀;改規則時在同一個 PR 內一併更新)。安裝程式會逐份列出 ok/MISSING。

## 跑一個 feature

```
/feat-new <slug> "描述"        → idea.md
/feat-research <slug>          → research.md(先讀 MEMORY.md 帶入 Prior knowledge)
/feat-grill <slug>             → decisions.md  ⏸ 逐輪次訪談(/feat-story 的前置關卡)
/feat-story <slug>             → story.md      ⏸ 人工核准才繼續
/feat-spec <slug>              → brief.md      ⏸ 人工核准才繼續
/feat-backend <slug>           → 程式碼 + backend-summary.md(該 track 啟用才跑)
/feat-frontend <slug>          → UI(消費契約,缺什麼回報缺口、不發明 endpoint)

# A 手動收斂                    # B 自動收斂(FABLE5)
/feat-verify <slug>            /feat-ship <slug>
/feat-validate <slug>          → 貼上它印出的 /goal,評估者逐回合判定
  有 findings → /feat-fix(上限 loopMaxRetries=3)→ 回 verify
  觸頂 → blocked → distill → 人工處理 → /feat-unblock(重置 retries)

/feat-unblock <slug>           → `blocked` 之後:人工授權復工(重置 retries)
/feat-docs <slug>              → 使用者文件:README + docsDir 指南(英文→繁中,Mermaid)
/feat-distill <slug>           → 收尾:教訓入 MEMORY.md(失敗也要蒸餾)
/feat-status <slug>            → 隨時查進度
```

產線不代你 commit、不開 PR——最後自己 review、自己 commit。

## 維護指令(產線之外)

```
/feat-recomment [path]         → 把舊的交錯式雙語註解轉成區塊形式
```

沒有 slug、不產 artifacts。先確認 git working tree 乾淨、先跑 dry run,再驅動
`.claude/factory/comment-migrate.py`——該腳本只「重排」註解行,絕不翻譯或改寫措辭。
它不敢動的區塊(混著被註解掉的程式碼、單行中英夾雜)會列進
`comment-migration-report.md` 交給人處理。加 `--check` 時只要還有交錯就回傳非零 exit code。

## 卡住時看這裡

| 狀態 | 意思 / 處置 |
|---|---|
| validate 乾淨 | 跑 `/feat-docs` 產出使用者文件,收尾 `/feat-distill`,然後自己 review + commit |
| `blocked` | fix 迴圈觸頂(3 次),交人工。流程:`/feat-distill`(開放問題入 Watchlist)→ 人工修/回 ⏸ 閘門改規格/接受風險 → `/feat-unblock`(重置 retries,回到 verify)。`state.json` 由該指令改,不手改 |
| `blocked-classifier` | 安全分類器拒絕,**不是程式碼壞了**。該 agent 改 `model: opus` 重跑或人工處理,之後用 `/feat-unblock` 回產線 |
| 同一 feature 第 2 次 blocked | 問題在上游——回 ⏸ 閘門改 story/spec 或拆 slug(`/feat-unblock` 會警告) |
| 寫入被 hook 擋下 | 設計如此,不要繞過。真有需要:`rm .claude/factory/.active` 離開產線模式 |
| context 感覺臃腫 / 自己在重複發問 | 你在階段中途——先做完。到下一個邊界時照 `PHASE-BOUNDARIES.md` 的階梯走:continue → `/clear` → 交接 → 子代理 → `/compact` 墊底。預設是 `/clear`:磁碟上的 artifacts 會把 context 重建起來 |
| `jq not found` | 強制其實沒開。裝 jq 再繼續 |
| gate 顯示 `(none configured, skipped)` | manifest 該指令留空;補上 script 後回填 project.json |

## 鐵則

1. **產線 = Default Mode**:prototype/spike 走 EXPLORE,不進 `/feat-*`。
2. **⏸ 閘門要真的看**:story 與 spec 是僅有的兩個人工判斷點。
3. **MEMORY.md 是程式碼**:diff 要 review,壞記憶的複利跟好記憶一樣快。
4. **註解一律區塊制**:先寫完整段英文 → 一行空註解 → 再寫完整段繁中。不可一行英一行中交錯;舊程式碼用 `/feat-recomment` 轉,不要手動逐檔改。
5. **在邊界決定 context**:`/feat-*` 步驟之間的接縫才是你做選擇的地方——`/compact` 在那裡是最後一個選項,不是第一個。階段中途:要嘛繼續,要嘛拆給子代理。
6. **Fail-Loud**:每步以 ✅/⚠️/❓ 收尾;「tests pass」不准掩蓋跳過的測試;絕不在 `disableAllHooks` 下跑產線。

<sub>FABLE5 升級(model 路由 / classifier 分流 / 記憶層 / /goal 收斂)在其他模型下惰性無害——全團隊只維護這一套,模型用 `/model` 選。</sub>
