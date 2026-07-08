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

## 跑一個 feature

```
/feat-new <slug> "描述"        → idea.md
/feat-research <slug>          → research.md(先讀 MEMORY.md 帶入 Prior knowledge)
/feat-story <slug>             → story.md      ⏸ 人工核准才繼續
/feat-spec <slug>              → brief.md      ⏸ 人工核准才繼續
/feat-backend <slug>           → 程式碼 + backend-summary.md(該 track 啟用才跑)
/feat-frontend <slug>          → UI(消費契約,缺什麼回報缺口、不發明 endpoint)

# A 手動收斂                    # B 自動收斂(FABLE5)
/feat-verify <slug>            /feat-ship <slug>
/feat-validate <slug>          → 貼上它印出的 /goal,評估者逐回合判定
  有 findings → /feat-fix(上限 loopMaxRetries=3)→ 回 verify

/feat-docs <slug>              → 使用者文件:README + docsDir 指南(英文→繁中,Mermaid)
/feat-distill <slug>           → 收尾:教訓入 MEMORY.md(失敗也要蒸餾)
/feat-status <slug>            → 隨時查進度
```

產線不代你 commit、不開 PR——最後自己 review、自己 commit。

## 卡住時看這裡

| 狀態 | 意思 / 處置 |
|---|---|
| validate 乾淨 | 跑 `/feat-docs` 產出使用者文件,收尾 `/feat-distill`,然後自己 review + commit |
| `blocked` | fix 迴圈觸頂(3 次),交人工。先 distill 把開放問題入 Watchlist |
| `blocked-classifier` | 安全分類器拒絕,**不是程式碼壞了**。該 agent 改 `model: opus` 重跑或人工處理 |
| 寫入被 hook 擋下 | 設計如此,不要繞過。真有需要:`rm .claude/factory/.active` 離開產線模式 |
| `jq not found` | 強制其實沒開。裝 jq 再繼續 |
| gate 顯示 `(none configured, skipped)` | manifest 該指令留空;補上 script 後回填 project.json |

## 鐵則

1. **產線 = Default Mode**:prototype/spike 走 EXPLORE,不進 `/feat-*`。
2. **⏸ 閘門要真的看**:story 與 spec 是僅有的兩個人工判斷點。
3. **MEMORY.md 是程式碼**:diff 要 review,壞記憶的複利跟好記憶一樣快。
4. **Fail-Loud**:每步以 ✅/⚠️/❓ 收尾;「tests pass」不准掩蓋跳過的測試;絕不在 `disableAllHooks` 下跑產線。

<sub>FABLE5 升級(model 路由 / classifier 分流 / 記憶層 / /goal 收斂)在其他模型下惰性無害——全團隊只維護這一套,模型用 `/model` 選。</sub>
