# Documentation, Comments & TW Terminology (project-wide contract)

This file is imported by the repo's root `CLAUDE.md`, so every agent and builder reads it.
It governs three things: (1) how code comments are written, (2) which language each kind of
document uses, and (3) the canonical Traditional Chinese (Taiwan) term for common jargon.

## 1. Comment rule (language-agnostic)

Code comments MUST be **thorough** and **bilingual**, written **block after block**, using
the target language's native comment syntax (`//`, `#`, `///`, `"""`, …):

1. **English block** — the complete English text, all of it, finished first.
2. **Separator** — one empty comment line (a bare `//` / `#`, or a blank line inside a
   docstring) so the two blocks read as two distinct passages.
3. **Traditional Chinese (Taiwan) block** — the same content, in the same order, translated.

**Do NOT interleave line by line.** Alternating one English line with one Chinese line makes
both languages unreadable — the reader has to skip every other line to follow either one.
Finish the English thought completely, then restate it completely in Chinese.

Rules:
- The Chinese block mirrors the English block **idea for idea, in the same order**, so the
  two passages can be lined up without re-reading.
- Both blocks stay inside ONE comment block, immediately above (or inside) the thing they
  describe. Never park the Chinese elsewhere — end of function, end of file, separate doc.
- Prefer explaining *why* (intent, edge cases, invariants), not just *what* the code does.
- A one-line comment is the degenerate case: one English line, then one Chinese line, no
  separator needed.

Multi-line example (TypeScript):
```ts
// Reject the request when the tenant does not own the record.
// This is the last line of defence: the repository layer already scopes queries by tenant,
// but a hand-written query can bypass that, so we re-check before any mutation runs.
//
// 當租戶並未擁有該紀錄時拒絕請求。
// 這是最後一道防線：repository 層雖已依租戶限縮查詢，但手寫查詢可能繞過，
// 因此在任何寫入動作執行前於此再檢查一次。
if (record.tenantId !== ctx.tenantId) throw new ForbiddenError();
```

Docstring example (Python) — same shape, blank line as the separator:
```python
def rotate_token(user_id: str) -> Token:
    """
    Issue a new token and revoke the previous one in a single transaction.
    Revocation is ordered first so that a crash mid-way fails closed: the user must log in
    again, rather than being left with two simultaneously valid tokens.

    在單一交易中簽發新 token 並撤銷舊的。
    撤銷動作刻意排在前面，如此中途失敗時會 fail closed：使用者需重新登入，
    而不會留下兩個同時有效的 token。
    """
```

One-line example (Go):
```go
// The cache is intentionally unbounded; the key space is already capped by the config schema.
// 此快取刻意不設上限；鍵的數量已由設定 schema 限制。
```

Anti-pattern — never do this:
```ts
// ❌ Reject the request when the tenant does not own the record.
// ❌ 當租戶並未擁有該紀錄時拒絕請求。
// ❌ This is the last line of defence: the repository layer already scopes by tenant,
// ❌ 這是最後一道防線：repository 層雖已依租戶限縮查詢，
// ❌ but a hand-written query can bypass that.
// ❌ 但手寫查詢可能繞過。
```

## 2. Document language policy (resolves the artifacts-vs-user-docs split)

There are TWO classes of documents; they follow DIFFERENT language rules. Do not mix them up.

- **Development-process artifacts** — anything under `<artifactsDir>/<slug>/`
  (`research.md`, `story.md`, `brief.md`, `backend-summary.md`, `verification.md`,
  `validation.md`, `state.json`): **English only.** These are internal pipeline hand-offs;
  keep them in one language for diff-ability and agent consumption. Do NOT translate them.

- **User-facing documentation** — the repo-root `README.md` and everything under `<docsDir>/`
  (usage guides, operation manuals, examples) produced by `/feat-docs`:
  **English first, then a Traditional Chinese (Taiwan) translation.**
  - The Chinese version uses the `_zh-TW` filename suffix
    (`README.md` → `README_zh-TW.md`; `docs/usage.md` → `docs/usage_zh-TW.md`).
  - BOTH versions carry a language-switch line at the very top, e.g.
    English: `> 🌐 **English** | [繁體中文](./README_zh-TW.md)`
    zh-TW:  `> 🌐 [English](./README.md) | **繁體中文**`
  - Diagrams use **Mermaid** (flowchart / sequence / Gantt / mindmap / class / state …)
    wherever a diagram is clearer than prose.

## 3. TW terminology dictionary

For all Traditional Chinese text, strictly use the Taiwan mainstream term.
NEVER use Mainland China variants (e.g. 函数, 字符串, 默认, 数据库, 字段).

Function:函式, String:字串, Pointer:指標, Thread:執行緒, Callback:回呼, Buffer:緩衝區, Memory leak:記憶體洩漏, Enumeration:列舉, Instance:實例, Compile:編譯, Parameter:參數, Return value:回傳值, Call:呼叫, Interface:介面, Implement:實作, Register:註冊, Priority:優先權, Timeout:逾時, Overflow:溢位, Alignment:對齊, Exception:例外, Variable:變數, Array:陣列, Object:物件, Class:類別, Inheritance:繼承, Constructor:建構式, Destructor:解構式, Module:模組, Package:套件, Dependency:相依性, Concurrency:並行, Asynchronous:非同步, Socket:通訊端/socket, Protocol:協定, Checksum:校驗碼, Handshake:交握, Baud rate:鮑率, Default:預設, Project:專案, Performance:效能, Optimization:最佳化, Support:支援, Information:資訊, Deployment:佈署, Database:資料庫, Data:資料, Log:紀錄/日誌, Field:欄位, Query:查詢, Property:屬性, Access:存取, Cache:快取, Garbage Collection:記憶體回收, Network:網路, Server:伺服器, Client:用戶端, Login:登入, Logout:登出, User:使用者, Template:樣版, One-Screen:單一畫面
