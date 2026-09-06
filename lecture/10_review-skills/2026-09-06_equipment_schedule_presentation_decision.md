---
status: authoritative
version: v1.0
updated: 2026-09-06
supersedes: none
authoritative_outline: ../00_course-plan/18_week_authoritative_outline_v1.md
---

# 老師裁示：設備、18 週結構、錄製發表與學習問卷

## 原始裁示摘要

1. 設備待確認項不影響教學內容；因需求找工具，不讓課程被工具限制綁定，實際操作前再處理。
2. 18 週固定為 16 週上課＋2 週自主學習做報告，需寫入需求。
3. 期末採錄製簡報與口頭發表，搭配學習問卷。

## 編譯後規則

- 未確認設備不再是概念或方法教學的 blocker；只有依賴特定設備功能的操作步驟在實作前核對，並準備功能等價替代工具。
- W17–W18 均不排實體課。為同時符合「兩週自主學習」與「口頭發表」，口頭發表採非同步錄製，隨書面報告與簡報檔線上提交。
- W18 學習問卷自願、不計分、不影響 ASSIGN-04 完整性。
- 問卷研究使用同意與錄製簡報／作品公開授權分開；現階段 research overlay 維持 false。

## 修改範圍

- `CONTEXT.md`
- `skill/color-planning/COURSE-CONTRACT.yaml`
- `materials/W17_自主學習/講義.md`
- `materials/W18_成果繳交/講義.md`
- `lecture/00_course-plan/`
- `lecture/08_research-publication/W18_learning_questionnaire_v1.md`
- `lecture/HANDOFF.md`
- 中央 `course-color-communication` skill v0.2.0 與 changelog

## 驗證原始摘要

```text
Skill is valid!
契約內部一致性：通過。
涵蓋範圍下限：通過。
教材目錄: materials
週次: 18 ｜ 週次目錄: 18 ｜ Markdown 檔: 18
全部通過。
Ran 45 tests ... OK
Ran 28 tests ... OK
學生資料／機密外洩檢查：通過
```

## 下一步給 Claude Code

核對本次老師裁示是否已在 `CONTEXT.md`、契約、W17、W18 與問卷五處一致；若發現文字衝突，保留老師裁示並直接修正下游檔案，不得再把設備未確認或 W18 發表列為待裁示。
