---
status: authoritative
version: v0.1
updated: 2026-09-06
supersedes: none
authoritative_outline: 00_course-plan/18_week_authoritative_outline_v1.md
---

# 交接帳本 HANDOFF

**這是 Codex 與 Claude Code 共編的單一入口。** 每次工作前讀第 1、2、3 節，結束前更新第 1、3、4 節；詳細過程寫在 `10_review-skills/`。

## 1. 現在的狀態

- 2026-09-06 由 Codex 建立 115-1 課程生產骨架。學期、系級與每週時數仍待老師確認，因此課程 profile 與 18 週大綱維持 `draft`。
- 原始來源位於 `/Users/slchu/Library/CloudStorage/Dropbox/Lecture/色彩學/`，共 1,454 個檔案、約 3.2 GB；原檔不得覆寫或移動。
- 已讀來源：舊版「色彩應用」課綱文字、iPAS 2026 色彩學教學與學習指引部分內容、iPAS 2026 色彩計畫實務評量重點部分內容，以及舊版 iPAS 色彩計畫實務參考指引目錄。
- 已建立初步來源地圖、課程 profile、18 週大綱、外部審查追蹤與 Claude R1 prompt。
- 已建立中央課程子 skill：`/Users/slchu/.codex/skills/course-color-communication/`，`quick_validate.py` 驗證通過。
- 2026-09-06 老師更正：Claude 的既有課程資料與審查工作位於 GitHub repo `hitaiwan0705/color-planning-skill` 的 `claude/skill-comparison-color-course-npvyrl` 分支；先前以本機 CLI 登入作為唯一協作入口的判斷已撤回。
- Codex `lecture/` 已推送至該分支 commit `0fb5da5`；其前一個 commit `14c7053` 為 Claude 已完成的 W01-W05 講義，兩條工作均已保留。
- 在大綱升為 authoritative 前，不產週講義、作業 rubric 或 PPTX。

## 2. 下一步（明確指派）

下一步給 Claude Code：在 GitHub comparison 分支比較 repo 既有 skill／contract 與匯入的 `lecture/` 草案。

1. repo：`https://github.com/hitaiwan0705/color-planning-skill.git`。
2. 分支：`claude/skill-comparison-color-course-npvyrl`。
3. 比較 repo 的 `CONTEXT.md`、`skill/color-planning/` 與匯入的 `lecture/`；原始教材維持唯讀。
4. 將建議分為「可直接採用／需老師裁示／需查證」，不得自行把大綱升為 authoritative。
5. 下一步交回 Codex：依 repo 已定案事實修正 Dropbox 草案、更新 source map，並準備老師裁示版。

老師待確認：學期是否為 115-1、開課年級、每週時數、班級人數與場地設備、研究用途，以及是否採用本 draft 的 4 份平時報告與期末專題方向。

## 3. 待辦看板

| ID | 項目 | 負責 | 狀態 | 備註 |
|---|---|---|---|---|
| SETUP-01 | 課程資料夾與必要子資料夾 | Codex | 已完成 | 115-1 為待老師確認的工作假設 |
| SRC-01 | 第一批來源盤點與路徑登錄 | Codex | 已完成 | 深讀與授權查核待續 |
| SKILL-01 | 建立 `course-color-communication` 子 skill | Codex | 已完成 | 中央單一真實來源；validator 通過 |
| PLAN-01 | 課程 profile v0.1 | Codex | 已完成 | draft |
| PLAN-02 | 18 週大綱 v0.1 | Codex | 已完成 | draft；待 Claude 與老師覆核 |
| SYNC-01 | clone GitHub repo、切換 comparison 分支並匯入 `lecture/` | Codex | 已完成 | commit `0fb5da5` 已 push；未 force push |
| REVIEW-01 | Claude R1 課程定位與週次審查 | Claude Code | 待處理 | 改由 GitHub comparison 分支進行 |
| PLAN-03 | 老師確認必備輸入並升級 authoritative | 老師／Codex | 待處理 | 學期、年級、時數、設備、研究角色 |
| HANDOUT-01 | W01 整合講義 | Codex 起稿／Claude 審查 | 待處理 | PLAN-03 完成後才可開始 |

## 4. 交接紀錄（時間倒序）

### 2026-09-06｜Codex｜GitHub comparison 分支同步完成｜下一步：Claude 比較兩條內容線

第一次 push 因 Claude 同時新增 W01-W05（remote `14c7053`）而被 non-fast-forward 拒絕。Codex 先 fetch、檢查路徑無衝突，再 rebase 本次 `lecture/` commit，未使用 force push；最終 `0fb5da5` 已成功推送。staged 學生資料／機密檢查通過、`git diff --check` 無錯、CIEDE2000 測試 15/15 通過（參照涵蓋率仍為 7/34）。全 repo 的非 staged 外洩掃描會命中既有負向測試字串 `tools/materials/tests/test_check_materials.py:163`，本輪未修改該既有驗證契約。

### 2026-09-06｜Codex｜更正 Claude 協作入口並準備 GitHub 同步｜下一步：完成 commit／push

老師指出 Claude 的資料在 GitHub。已 clone `hitaiwan0705/color-planning-skill` 至 `/Users/slchu/Projects/color-planning-skill`，切換 `claude/skill-comparison-color-course-npvyrl`，並依老師指定建立 repo `lecture/`，匯入本課 Codex 草案。repo `CONTEXT.md` 顯示大三上必修、已修色彩學與色彩度量學、設備及 iPAS 時程等已定案事實；這些將在 Claude 比較後回整，不先掩蓋差異。

### 2026-09-06｜Codex｜建立共同編寫骨架｜下一步：Claude Code R1 審查

已依 `AGENTS.md` 與 `research-integrated-course-system` 的產出鏈建立課程資料夾、來源地圖、draft profile、draft 18 週大綱、review audit 與 Claude prompt。舊課綱的 40/20/30/10 評量未沿用；本課一律遵守校內固定的期中 30%、期末 30%、平時 30%、參與 10%。

依 course registry 與 skill-creator 建立 `course-color-communication` v0.1.0，並同步建立 `CHANGELOG.md`。驗證原始輸出：

```text
Skill is valid!
COURSES_YML_OK 2026-09-06 3
COLOR_COURSE_OK 色彩規劃與傳播應用 /Users/slchu/Library/CloudStorage/Dropbox/Lecture/115-1/色彩規劃與傳播應用 TBD
```

Claude CLI 實際輸出：

```text
Not logged in · Please run /login
```

因此本輪沒有 Claude 內容，不能宣稱已共同完成課程設計。下一步給 Claude Code；完成後交回 Codex 整合。
