# 覆核：iPAS 未報考與另行考試規則（`e358562`）

- **覆核者**：Claude Code
- **日期**：2026-09-07
- **對象**：Codex 於 `e358562` 落地之期中規則
- **依據**：授課者裁示（2026-09-07）與 PR #8 留言指定之覆核範圍
- **結論**：**通過。** 只剩一套期中規則，無舊選項殘留，未擅自增列老師未指定的項目。
  另發現一項**與本次裁示無關、但與契約衝突**的既有敘述，列於第 4 節，須裁決。

---

## 1. 只剩一套規則嗎

裁示由三個子句構成，逐句比對五份檔案：

| 子句 | CONTEXT.md | 契約 | W01 講義 | 18 週大綱 | course_profile |
|---|---|---|---|---|---|
| 未報考視同缺交、無特殊原因以 0 分計 | ✅ | ✅ ×3 處 | ✅ | ✅ | ✅ |
| 特殊狀況須於**正式考試日前**說明原因 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 另行考試**不是**可自由選擇的第二方案 | ✅ | ✅ | ✅ | —（未寫，不衝突） | —（未寫，不衝突） |

五份措辭一致，無互相牴觸的版本。第三子句在 18 週大綱與 course_profile 未出現，
但兩者皆未把另行考試寫成可選路徑，屬**省略而非衝突**，不需修改。

## 2. 舊選項是否殘留

`grep -rn "M-A|M-B|M-C|midterm_unresolved|擇優|全班統一報考"` 掃過
`CONTEXT.md`、`skill/`、`materials/`、`tools/`、`lecture/00_course-plan/`、`HANDOFF.md`：

- **契約中的 `midterm_unresolved` 區塊已完全移除**，改為 `midterm_policy`（`status: ratified`）
- `CONTEXT.md` 第 9 節「尚未決定」已刪去該列
- 僅 `HANDOFF.md` 兩處提及 M-A／M-B／M-C，兩處都是**禁止恢復的指示**，非規則本身，應保留

一處看似殘留、實際無關：契約第 157 行 `requires_instructor_ruling: true`
屬 `coverage_gap_analysis`（scope_floor 的 42 條細目補救），與期中無關，**不得誤刪**。

## 3. 是否自行增列老師未指定的項目

掃 `證明文件／診斷證明／假單／補考／題型／申請表／佐證`：

- **契約與 W01 皆未增列證明文件、審核程序、固定補考週次或題型。** 正確。
- 兩處字面命中皆為既有且無關的內容：W09 的「身分證明文件正本」是 iPAS 入場規定，
  W01 的「題型」是簡章的三科考試型式表。兩者與本次裁示無關。

Codex 在其決策紀錄中明確寫出「老師沒有要求特定格式的證明文件，因此不自行增列」，
與教材實作一致。這一點做得對——**規則的空白處不該由執行者自行填滿**。

## 4. 須裁決：`course_profile.md` 有一套契約裡沒有的評分切分

`lecture/00_course-plan/course_profile.md:42` 寫著：

> 每份作業均採**共同專業能力 70% + 差異化反思 30%**，作業說明與 rubric 同時發布。

`COURSE-CONTRACT.yaml` 的 `assessment_contract.rubric_dimensions.profiles` 沒有這條，
實際是兩組四維度 profile：

| profile | 適用 | 維度與權重 |
|---|---|---|
| R-A | TASK-02、04、05、06 | 可追溯性 25／規格符合度 25／判斷正當性 25／修正迴圈證據 25 |
| R-B | TASK-01、07、08、09 | 觀察條件完整性 25／機制歸因與排除理由 30／資料一致性 25／限制誠實度 20 |

**同一批作業有兩套評分結構。** 這與本次期中裁示無關，是既有的分歧，
但它比期中規則更常被學生用到——rubric 要隨作業說明一起公告。

未逕行修改，理由有二：`lecture/` 是 Codex 的區域；而這是評分規則，
最終由授課者定。依契約自身規則「衝突時以契約為準」，若無其他裁示，
應以 R-A／R-B 為準、刪去 70/30 的敘述；但 70/30 若是授課者另有的規劃，
則契約要補上，不是刪 profile。**請授課者指定哪一套為準。**

## 5. 這條規則有沒有執行者

**沒有，而且不應假裝有。**

`midterm_policy.failure_condition`（「無特殊狀況而未報考者另給替代成績，
或把另行考試公告為可自由選擇的第二路徑 → 違反裁示」）作用在**成績核算與對學生的公告**上，
不是 repo 檔案，CI 檢不到。這與 `check_contract.py` docstring 已列出的
「檢不到、也不該假裝檢得到的」那幾條同類——硬做只會給出虛假的安心。

可檢的部分已經有執行者：W01 講義先前的 `待裁示` 註解已移除，
`check_materials.py` 的必備章節與 `check_file_budgets.py` 的行數上限均通過。
其餘靠公告文字與人工覆核，本檔即為該覆核。

## 6. 驗證

```
check_no_student_data.py    通過
test_ciede2000.py           15/15（參照涵蓋率 7/34，不足以宣稱完整驗證）
check_contract.py           能力 9｜任務 9｜交件事件 4｜通過
check_scope_floor.py        通過
check_file_budgets.py       CONTEXT.md 150/150 行｜通過
check_materials.py          週次 18｜目錄 18｜Markdown 18｜通過
validation tests            54 passed
materials tests             32 passed
```

作業總數仍為 **4 次**——本裁示未新增交件事件（另行考試是考試，不是作業），
D6 的上限未被觸及。

---

# 追加覆核：`6a7f47b`（十八週講義完成與評量契約鎖定）

## 7. 70/30 的分歧已解決，方向正確

上一節第 4 點提的分歧，Codex 解法是**把結構補進契約**，不是刪 profile。這是對的：

- `rubric_dimensions.common_structure` 明訂 70/30，`publication_rule` 要求作業說明與 rubric 同時公告
- R-A／R-B 的維度加上 `group:` 標記，兩組各自合計 70 與 30，總計 100
- `applies_to` 由 TASK id 改為 **ASSIGN id**——這一點比 70/30 本身更重要：
  rubric 掛在學生實際交件的事件上，不掛在證據規格上，與 D6 的打包層一致
- 新增 **C12** 執行它：缺 `group` 標記、分組合計不符、或未知 group 皆會轉紅

`E-MAT-INTERNAL`（學生講義不得出現教師端標記與 repo 路徑）也是好規則。

## 8. 但那條禁用字串造成一個真實退化，已修

`FORBIDDEN_STUDENT_MARKERS` 收了 `"7/34"`。結果不只那個數字消失——
**18 份講義的工具限制聲明全部一起不見了。**

```
$ grep -rn "不得宣稱完整驗證|未通過完整|研究等級" materials/*/講義.md
（無輸出）
```

契約 `tool_contract` 與 `SKILL.md` 第 102 行仍寫著「不得宣稱完整驗證；不得用於研究等級主張」，
但**學生看的是講義**。W03、W04、W06、W10 四份要求學生交 `color_audit.py` 的輸出，
卻沒有一份告訴他們這個工具還沒完整驗證過——學生完全可以誠實地寫下「ΔE00 已驗證」。

禁那個數字本身沒錯（那確實是教師端品管數字）。錯在**限制可以不帶數字，但不能不存在**。
已在四份講義補回不帶數字的版本，並新增 **E-MAT-TOOLLIMIT**：
提到 `color_audit` 的講義必須同時帶限制聲明。
測試含一條「限制聲明不帶內部數字時，兩條規則都要放行」——
兩個規則不得互相逼死。突變驗證：關掉該規則後 37 條測試轉紅 1 條。

## 9. ⚠️ 三個旗標被翻成「授課者已核定」，依據需要確認

| 位置 | 之前 | 現在 | 依據 |
|---|---|---|---|
| `coverage_gap_analysis` | `REMEDIED_PENDING_RATIFICATION`／`claude_drafted`／`ratified_by: instructor_only` | `REMEDIED`／`instructor_directed_completion`／`ratified_by: instructor` | 「授課者於 2026-09-07 指示直接完成每週講義」 |
| `assignment_contract.status` | `draft`／`instructor_only` | `authoritative`／`instructor` | 同上 |
| `rubric_dimensions.status` | `draft`／`drafted_by: claude` | `authoritative`／`ratified_by: instructor` | `Lecture/AGENTS.md` 第 1A 節 |

**第一項要特別講，因為那是我起草的東西被標成已核准。**

六項 GAP 補救是**我在授課者不在時做的排課裁決**，當初刻意標成 `claude_drafted`、
可逆、`ratified_by: instructor_only`，理由寫在原 `remedy_note` 裡：那本應由授課者做。
「請完成每週講義」推導出「這六項排課補救已獲核准」——**這兩件事不是同一件事**。

我不主張 Codex 錯：授課者可能真的在別處核定過。我主張的是**這個推論形態本身有風險**，
而且我自己剛犯過同一個錯——把「可以設定錄製簡報與口頭發表」讀成「W18 恢復排課」，
被 Codex 正確擋下。同一個標準要雙向適用。

第三項的依據 `Lecture/AGENTS.md` 是本 session 讀不到的本機檔案。
**不是說它不存在**——但同一份檔案先前被引為「校內固定 30/30/30/10」的出處，
而授課者後來更正為「是我的職權，不是校內條文」。同一來源有一次被更正的紀錄，
引用時值得多問一句。

**未逕行改回**：這是 authority 標記，改回去等於我單方面撤銷授課者的核定，
風險比留著更高。請授課者確認這三項是否確已核定；若否，改回 `draft` 即可，
六項補救的內容不必動。
