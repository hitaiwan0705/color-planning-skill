---
status: authoritative
version: v1.0
updated: 2026-09-07
supersedes: none
authoritative_outline: ../00_course-plan/18_week_authoritative_outline_v1.md
---

# 老師裁示：iPAS 未報考與特殊狀況另行考試

## 原始裁示

> 未報考等同缺交，若無特殊原因則以 0 分計。若因特殊狀況不能報考者，則需考試前先說明原因，並另外考試。

## 編譯後規則

1. 期中 30% 原則上以 iPAS 考試成績計算。
2. 未報考視同期中缺交；無特殊原因者以 0 分計。
3. 因特殊狀況不能報考者，須於 iPAS 正式考試日前向授課者說明原因，由授課者另行安排考試。
4. 另行考試是特殊狀況的處理方式，不是學生可自由選擇的第二種期中方案。
5. 本裁示取代先前 `midterm_unresolved` 的 M-A／M-B／M-C 三選一草案。

## 修改範圍

- `skill/color-planning/COURSE-CONTRACT.yaml`
- `materials/W01_課程契約與iPAS報考/講義.md`
- `CONTEXT.md`
- `lecture/00_course-plan/course_profile.md`
- `lecture/00_course-plan/18_week_authoritative_outline_v1.md`
- `lecture/HANDOFF.md`

## 取捨說明

- 老師沒有要求學生提出特定格式的證明文件，因此教材不自行增列證明文件或審核程序。
- 老師沒有指定另行考試的週次、題型或計分換算，因此只寫「由授課者另行安排考試」，
  不把過去草案的 W09 或 iPAS 三科等值條件冒充已定案內容。
- 這項裁示高於 Claude 與 Codex 先前列出的三個候選方案；原始審查意見保留在舊紀錄中，
  但不得再作為學生端規則。

## 驗證原始輸出

```text
契約內部一致性：通過。
涵蓋範圍下限：通過。
教材目錄: materials
週次: 18 ｜ 週次目錄: 18 ｜ Markdown 檔: 18
全部通過。
Ran 54 tests ... OK
Ran 32 tests ... OK
學生資料／機密外洩檢查：通過
CONTEXT.md: 150 / 150 行
檔案長度上限：通過。
git diff --check：通過（無輸出）
```

## 下一步給 Claude Code

覆核契約、W01、`CONTEXT.md` 與 course plan 是否一致。若修正文字，必須保留上述五條規則；
不得加入老師尚未指定的證明文件、固定補考週次或把另行考試變成自由選項。
