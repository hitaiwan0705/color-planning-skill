# color-planning-skill

「色彩規劃與傳播應用」課程的 LLM 技能與決定性工具。
中國文化大學 資訊傳播學系｜朱尚禮

---

## 這個 repo 怎麼運作

三方協作，**GitHub Pull Request 就是審查協定**，不另建 YAML 流程。

| 角色 | 做什麼 | 在哪裡 |
|---|---|---|
| 您 | 課程目標、設備條件、產業判斷、最終裁決 | 合併 PR |
| ChatGPT / Codex | 課程內容、前後課銜接、批判性審查 | 分支 + `@codex review` |
| Claude Code | 檔案結構、程式、測試、schema、patch | 本機 + `@claude` |

規則檔：Claude 讀 `CLAUDE.md`，Codex 讀 `AGENTS.md`，兩者內容同步。
已定案事實統一放 `CONTEXT.md`，兩邊都先讀它——這取代每輪重述背景。
可直接複製的驅動指令放在 `PROMPTS.md`（P0→P5 依序執行）。

---

## 一次性設定

### 1. 建立 repo

```bash
# GitHub 網頁上建立 private repo，名稱 color-planning-skill，不要勾選任何初始化選項
git clone https://github.com/<你的帳號>/color-planning-skill.git
cd color-planning-skill
# 把本壓縮檔內容解壓到此
git add -A && git commit -m "初始骨架：CI、資料防線、色差工具與驗證套件"
git push -u origin main
```

### 2. 本機安裝 Claude Code

```bash
npm install -g @anthropic-ai/claude-code   # 需 Node.js
cd color-planning-skill
claude                                      # 首次會引導登入
```

進入後直接對話即可，它會自動讀取 `CLAUDE.md` 與 `CONTEXT.md`。

### 3. 接上 GitHub（讓 `@claude` 可用）

在 Claude Code 內執行：

```
/install-github-app
```

依指示選擇 repo，它會自動開一個 PR 加入 `.github/workflows/claude.yml`。
合併後，在任何 PR 或 issue 留言 `@claude ...` 即可觸發。

需在 repo 的 Settings → Secrets and variables → Actions 加入 `ANTHROPIC_API_KEY`。

### 4. 接上 Codex

在 Codex 設定中對本 repo 開啟 Code review，之後於 PR 留言 `@codex review`。
Codex 會依 `AGENTS.md` 的規則審查 diff 並貼出 inline comment。

### 5. 開啟分支保護（重要）

Settings → Branches → Add rule，套用到 `main`：

- [x] Require a pull request before merging
- [x] Require status checks to pass → 勾選 `validate`
- [x] Do not allow bypassing the above settings

這一步是整套流程的關鍵：**測試沒過、資料防線沒過，任何人（包含 AI）都無法合併。**
這也自動回答了「工具是否已驗證」的問題——CI 綠燈即是答案，不需要口頭宣稱。

---

## 日常循環

```bash
git switch -c topic/加入色彩量測模組       # 開分支
# ...本機用 Claude Code 修改...
python3 tools/color/tests/test_ciede2000.py          # 本機先跑測試
python3 tools/validation/check_no_student_data.py    # 本機先跑防線
git push -u origin topic/加入色彩量測模組
# GitHub 上開 PR → 留言 @codex review 或 @claude
# 兩方意見衝突時，由您在 PR 留言裁決 → 合併
```

---

## CI 會擋什麼

| 檢查 | 內容 |
|---|---|
| 學生資料外洩檢查 | 身分證、手機、email、API key、雜湊鹽值、真實 `student_hash`、資料檔副檔名 |
| CIEDE2000 驗證套件 | 7 組參照資料 + 8 項性質測試，每項皆經負向驗證 |

**外洩檢查是縱深防禦，不是保證。** 它會漏掉沒有明顯格式特徵的個資
（例如單獨出現的學號、姓名）。真實資料一律放在 repo 之外的加密位置，
路徑記在 `CONTEXT.md`，值永遠不進版本控制。

若不慎已 commit 並 push，刪除檔案不夠——git history 仍保留，需重寫歷史。

---

## 工具

```bash
# 色票稽核：五情境（常態 / 三型色覺 / 灰階）兩兩 ΔE00
python3 tools/color/scripts/color_audit.py --palette "#0072B2,#D55E00,#009E73,#CC79A7"

# 前景背景對比：WCAG 2.2 + 色覺模擬後對比度
python3 tools/color/scripts/color_audit.py --pair "#767676" "#FFFFFF"

# JSON 輸出（供證據契約使用）
python3 tools/color/scripts/color_audit.py --palette "..." --json
```

### 驗證狀態

```yaml
tool_validation_status:
  implementation: provisionally_credible
  reference_tests: 7/34        # 不足以宣稱完整驗證
  property_tests: 8/8          # 皆經負向驗證
  known_blind_spot: dhp_wraparound_self_cancelling
  research_grade_use: not_approved
  classroom_demo_use: conditionally_approved
```

補齊完整 34 組參照資料的方式：從 Sharma 等人的公開頁面下載後
覆蓋 `tools/color/tests/sharma_reference_data.csv`，重跑測試套件即可。

---

## 現階段範圍限制

只做「色彩規劃與傳播應用」一門課。**不建立**其他課程目錄、全系能力地圖、
共用 schema 集或母規格。待第二門課（資訊視覺化設計）完成後，
才從兩門課抽取真正重複的部分。

新增目錄層級前須在 PR 說明理由。架構膨脹是本專案的主要風險。
