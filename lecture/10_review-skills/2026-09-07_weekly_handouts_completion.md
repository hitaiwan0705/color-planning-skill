---
status: authoritative
version: v1.0
updated: 2026-09-07
supersedes: none
authoritative_outline: ../00_course-plan/18_week_authoritative_outline_v1.md
---

# W01–W18 每週講義完成與收斂紀錄

## 本輪指令與範圍

授課者指示「直接完成每週講義內容生成」。本輪完成 `materials/` W01–W18 全部 18 份學生端
講義，並將課程 profile、18 週大綱、來源地圖與評分契約收斂成可供後續簡報與作業文件引用的
權威版本。原始來源未覆寫或移動。

## Claude 意見的處理

- 保留 Claude 對期中規則的覆核結論：未報考視同缺交、無特殊原因以 0 分計；特殊狀況須於
  正式考試日前說明，並另行考試；另行考試不是自由選擇的第二路徑。
- Claude 指出的 rubric 衝突已依授課者上位決策修正：每份作業均採共同專業能力 70%＋
  差異化反思 30%。契約新增可機器檢查的 C12 規則與負向測試，避免再漂移。
- Claude 原始意見保留於 `2026-09-07_claude_midterm_policy_review.md`，未刪除或覆寫。

## 內容完成狀態

- W01–W16：各 120 分鐘授課；W02、W05 即使客座講者未到，仍有完整替代教學流程。
- W17–W18：不排課；學生以 W16 前取得的證據完成書面報告、簡報檔與錄製口頭發表。
- 四個交件事件：ASSIGN-01、02、03 各占平時 10%；ASSIGN-04 占期末 30%。
- W03、W06、W10、W13／W18 已在作業公布時同步公告相應 rubric。
- 研究問卷維持自願、不計分；研究同意與作品／影片再使用同意分開。
- 每週皆由傳播問題起始，並把螢幕、紙張、描述檔、量測、輸出設備與交接流程具體化。

## Persona 與 gate 覆核

| 視角 | 判定 | 實際檢查 |
|---|---|---|
| 傳播教師 | 通過 | 每週均連到訊息、閱聽人、接觸點、詮釋或信任後果 |
| 色彩科學 | 通過 | CIEDE2000、色貌、ICC 與觀看條件均附正式來源或明確限制 |
| 媒體物質性 | 通過 | 紙張、螢幕、profile、UV 輸出、資料與版本鏈均進入活動與證據 |
| 無障礙與倫理 | 通過 | 顏色不作唯一訊息通道；問卷不計分；作品／錄影授權分離 |
| 學生可執行性 | 通過 | 授課週有 120 分鐘流程、交件清單、失敗條件與下週銜接 |
| 專案管理 | 通過 | 18 週、四次交件、九站證據鏈與 authoritative outline 一致 |

## 驗證原始摘要

```text
check_contract.py: 契約內部一致性通過；能力 9、任務 9、交件事件 4
check_scope_floor.py: REMEDIED；42 條評鑑細目；涵蓋範圍下限通過
check_materials.py: 18 週／18 目錄／18 Markdown，全部通過
materials unit tests: Ran 34 tests — OK
validation unit tests: Ran 58 tests — OK
check_no_student_data.py: 學生資料／機密外洩檢查通過
check_file_budgets.py: 檔案長度上限通過
test_ciede2000.py: 15/15 通過；參照資料涵蓋率 7/34，不宣稱完整基準驗證
course-color-communication quick_validate.py: Skill is valid!
git diff --check: 通過
```

## 下一步給誰

下一步給 Claude Code：以本次 authoritative 課綱與契約做第二次內容審查，優先檢查學生能否
依每週講義直接執行、外部來源是否支持主張、四次 rubric 是否保持 70/30。若無阻斷問題，
再交 Codex 依 weekly schema 產生 W01–W16 簡報；W17–W18 不做上課簡報。
