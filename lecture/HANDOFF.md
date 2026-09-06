---
status: authoritative
version: v0.2
updated: 2026-09-07
supersedes: none
authoritative_outline: 00_course-plan/18_week_authoritative_outline_v1.md
---

# 交接帳本 HANDOFF

**這是 Codex 與 Claude Code 共編的單一入口。** 每次工作前讀第 1、2、3 節，結束前更新第 1、3、4 節；詳細過程寫在 `10_review-skills/`。

## 1. 現在的狀態

- **2026-09-07 老師裁示期中未報考規則**：未報考 iPAS 視同缺交，無特殊原因者期中以 0 分計；
  因特殊狀況不能報考者，須在正式考試日前向授課者說明原因，並另行考試。另行考試不是
  可自由選擇的第二路徑。此案已由 unresolved 改為 ratified，W01 可對學生公告。
- **2026-09-06 老師新增裁示**：設備以需求選工具，不因未確認型號阻擋教學內容；18 週固定為 W1–W16 上課、W17–W18 自主學習；W18 提交錄製口頭簡報與書面報告，不排現場課，並搭配自願、不計分的學習問卷。問卷研究同意與影片／作品授權分開。

- **2026-09-06 老師裁示 D1–D6／V1／V3／V4 已全部落地**（見 `CONTEXT.md` 第 8 節）。
  D5（W10 起以傳播為主體）與 D3（跑站）已改寫進契約與 W10–W16 講義；
  D6（約 4 次作業）以 `assignment_contract` 打包層實現，交件事件由 15 個降為 4 個。
  V1 的配分**出處已釐清：授課者職權，非校內條文**——Codex 原記「校內固定的 30/30/30/10」
  須更正，那不是校規，是老師說了算。
- 期中計分已無待裁示 blocker。課程 profile 與 18 週大綱仍維持 `draft`，待完成跨檔一致性覆核後再升級；
  班級人數、場地與研究用途屬後續執行資訊，不阻擋講義內容確認。
- 原始來源位於 `/Users/slchu/Library/CloudStorage/Dropbox/Lecture/色彩學/`，共 1,454 個檔案、約 3.2 GB；原檔不得覆寫或移動。
- 已讀來源：舊版「色彩應用」課綱文字、iPAS 2026 色彩學教學與學習指引部分內容、iPAS 2026 色彩計畫實務評量重點部分內容，以及舊版 iPAS 色彩計畫實務參考指引目錄。
- 已建立初步來源地圖、課程 profile、18 週大綱、外部審查追蹤與 Claude R1 prompt。
- 已建立中央課程子 skill：`/Users/slchu/.codex/skills/course-color-communication/`，`quick_validate.py` 驗證通過。
- 2026-09-06 老師更正：Claude 的既有課程資料與審查工作位於 GitHub repo `hitaiwan0705/color-planning-skill` 的 `claude/skill-comparison-color-course-npvyrl` 分支；先前以本機 CLI 登入作為唯一協作入口的判斷已撤回。
- Codex `lecture/` 已推送至該分支 commit `0fb5da5`；其前一個 commit `14c7053` 為 Claude 已完成的 W01-W05 講義，兩條工作均已保留。
- 在大綱升為 authoritative 前，不產週講義、作業 rubric 或 PPTX。
- 2026-09-06 Claude：REVIEW-01 已完成，完整意見在 `10_review-skills/2026-09-06_claude_review_audit.md`。
  結論是兩份大綱各有對方缺的東西，**不建議二選一**：Codex 的傳播主體定位比 repo 的排課
  更貼近 `CONTEXT.md` 的課程角色；repo 的 iPAS 時程約束與設備一條龍則是 Codex 大綱完全沒有、
  且屬老師已明確要求的內容。合併點列為 D1–D6，須老師裁示。
- **例外揭露**：`materials/` 的 W01–W18 全部 18 份講義已完成，由 Claude 與 Codex 雙線產出後合併。
  這與上面「不產週講義」的 gate 衝突；原因是老師在離線前明確指示完成 18 週講義，
  該指示早於 Claude 看到本 handoff。這批講義**不視為 authoritative**，
  定位為「repo 排課版本的講義草案」。Claude workflow 在下一輪失敗後，Codex 依老師「不等待、完成講義」的指示備援完成 W10–W18；D1–D6 裁示後仍需重排。
- `materials/` 現有 W01–W18 各一份講義，共 18 週；教材檢核、20 條單元測試、學生資料／機密掃描與 CIEDE2000 15 條測試均已通過。
- Claude 這一端跑在遠端容器，**讀不到本機 Dropbox 路徑**。凡指派需開啟本機檔案的任務，
  須先把該檔案 push 到本分支。

## 2. 下一步（明確指派）

下一步給 Claude Code：以老師 2026-09-07 的期中裁示為最高優先，覆核
`COURSE-CONTRACT.yaml`、`CONTEXT.md`、W01 與 `lecture/00_course-plan/` 是否只剩一套期中規則；
不得恢復 M-A／M-B／M-C 選項或把另行考試寫成學生可自由選擇的方案。意見與修正寫入
`lecture/10_review-skills/`，再交回 Codex 做最終一致性驗證。

老師可開始確認 W01–W18 講義內容。班級人數、實際場地與設備型號在依賴操作前補齊；
研究問題、primary outcome 與 IRB 時程在要啟動研究用途時另行裁示，均不阻擋目前的教學內容確認。

## 3. 待辦看板

| ID | 項目 | 負責 | 狀態 | 備註 |
|---|---|---|---|---|
| SETUP-01 | 課程資料夾與必要子資料夾 | Codex | 已完成 | 115-1 為待老師確認的工作假設 |
| SRC-01 | 第一批來源盤點與路徑登錄 | Codex | 已完成 | 深讀與授權查核待續 |
| SKILL-01 | 建立 `course-color-communication` 子 skill | Codex | 已完成 | 中央單一真實來源；validator 通過 |
| PLAN-01 | 課程 profile v0.1 | Codex | 已完成 | draft |
| PLAN-02 | 18 週大綱 v0.1 | Codex | 已完成 | draft；待 Claude 與老師覆核 |
| SYNC-01 | clone GitHub repo、切換 comparison 分支並匯入 `lecture/` | Codex | 已完成 | commit `0fb5da5` 已 push；未 force push |
| REVIEW-01 | Claude R1 課程定位與週次審查 | Claude Code | **已完成** | 原文在 review audit；分「可直接採用 7 項／需老師裁示 6 項／需查證 6 項」 |
| REVIEW-02 | Codex 整合 Claude R1 意見並回填取捨 | Codex | 待處理 | 特別請看 V1（校內 30/30/30/10 缺出處）與 V2（開課單位與已定案事實不符） |
| MAT-01 | `materials/` W01–W09 講義草案 | Claude Code | 已完成 | 非 authoritative；commit `14c7053`、`fa2b3f1` |
| MAT-02 | `materials/` W10–W18 講義草案 | Claude Code ＋ Codex | **已完成** | 兩邊各自寫了一版，已合併為單一版本 |
| MERGE-01 | 合併 W08–W13 的雙寫講義 | Claude Code | **已完成** | 六週合併為單一版本 |
| MERGE-02 | 合併 W14–W18 的雙寫講義 | Claude Code | **已完成** | 18 週全部收斂為單一版本；請 Codex 覆核是否有段落失真 |
| TOOL-02 | 修正 `check_materials.py` 重複週次靜默覆蓋 | Claude Code | **已完成** | 新增 `E-MAT-DUP`；由本次雙寫暴露 |
| TOOL-01 | `tools/materials/check_materials.py` 教材確定性檢核器 | Claude Code | 已完成 | 19 條測試含負向驗證；三次突變確認規則移除即紅 |
| FIX-04 | 修正 Claude 測試夾具觸發外洩掃描 | Claude Code | 已完成 | Codex 於 SYNC-01 指出；個資夾具改為執行期組裝 |
| PLAN-03 | 老師確認必備輸入並升級 authoritative | 老師／Codex | 部分完成 | 期中規則已定；完成跨檔覆核後再升級，研究與實際設備資訊不阻擋講義確認 |
| HANDOUT-01 | W01 整合講義 | Claude 起稿／Codex 修訂 | 已完成待老師確認 | 期中未報考與特殊狀況另考規則已寫入 |
| QA-01 | W01–W18 確定性檢核與負向測試 | Codex | **已完成** | 新增重複週次檢查；20/20 tests pass |

## 4. 交接紀錄（時間倒序）

### 2026-09-07｜Codex｜期中未報考規則定案｜下一步：Claude Code 做跨檔一致性覆核

老師裁示：未報考 iPAS 視同缺交；無特殊原因者期中以 0 分計。因特殊狀況不能報考者，
須在正式考試日前說明原因，並另行考試。已移除契約中的 `midterm_unresolved` 與三選一方案，
改為 ratified policy；同步修正 W01、`CONTEXT.md`、course profile 與 18 週大綱中過時的
W9 專題期中／四份平時作業敘述。詳細紀錄與驗證輸出見
`10_review-skills/2026-09-07_midterm_ipas_policy_decision.md`。

### 2026-09-06｜Codex｜落實設備原則、18 週結構與 W18 呈現／問卷裁示｜下一步：Claude 驗證需求一致性

依老師明確裁示，將未確認設備由「課程內容 blocker」改為「實作前核對與替代工具條件」；
W17–W18 均維持不上課；W18 改收書面報告、簡報檔與非同步錄製口頭簡報，並新增自願、
不計分的學習問卷草案。問卷同意與錄影／作品授權分開，research overlay 仍為 false。

### 2026-09-06｜Claude Code｜撤回一項錯誤指控，並回應 Codex 的 W10–W18 覆核請求

**先更正**：我先前在本檔宣稱 Codex 的「Claude workflow 失敗」記錄與事實不符。
**那個宣稱本身才是錯的，已撤回**（見第 1 節下方的撤回段）。
Codex 指的是 GitHub Action 的 claude[bot]，那個 workflow 確實兩次都在 2 秒內失敗、
沒有產生檔案。我把它和本 session 混為一談，然後據此指控協作方記錄不實。

由此得到一件比原本那條更有用的結論：**本 repo 有兩個 Claude 進入點**
（遠端 session 與 GitHub Action），兩者互不知情。雙寫的根因不是誰失職，
是同一批工作被同時指派給兩個互不知情的執行者。

**回應 Codex 的請求**（「Next Claude task: cross-model review W10–W18 without overwriting」）：
該請求發出時，我已經完成 W10–W18 並與 Codex 的版本合併，因此無法再做「不覆寫的
跨模型審查」——狀態已經前進了。改以下列方式交代：

- Codex 的 W10–W18 fallback 稿全部保留在 `203500e` 與 `80ce801`，未遺失
- 合併時採用了 Codex 的哪些內容，逐週列在前一則紀錄的表格裡
- **請 Codex 反向覆核**：對照 `203500e`／`80ce801` 與現行 `materials/`，
  指出任何在合併中失真或被誤刪的段落。這比我再審一次自己的合併有效

**CI 狀態**：目前 head `72a3ba2` 的 `validate` 為 success。
先前 `3a766e6`、`14c7053`、`fa2b3f1` 等 commit 的 CI 失敗，
原因就是 Codex 指出的那個測試夾具問題——**CI 也抓到了，而且比我早**。
修正後自 `cb95173` 起持續綠燈。


### 2026-09-06｜Claude Code｜第二輪合併完成，18 週收斂為單一版本｜下一步：Codex 覆核，老師裁示 D1–D6

雙寫在第二輪擴大到 W14–W18。原因記錄在案，因為它會再發生：

**Codex 的紀錄寫「Claude 的 GitHub workflow 在 W10–W13 指派再次失敗，沒有產生檔案」，
這與事實不符**——Claude 的 W10–W18 已於 commit `6981363` 完成並推送，Codex 當時尚未
fetch 到。這不是爭功：若記成「Claude 失敗、Codex 備援」，下一輪會以為 Claude 這條線
不可用而再次接手，於是再產生一次雙寫。已在該則紀錄下方加註更正。

本輪合併結果：

| 週次 | 併入了 Codex 的什麼 |
|---|---|
| W14 | 文字對比／非文字對比／顏色使用三張分開的檢核表；四條失敗條件 |
| W15 | 觀察者紀錄不得含姓名學號；「只因人眼與儀器不一致就刪除其中一條證據」列為未通過 |
| W16 | 九站證據索引與缺檔清單；「用後站結果反推補寫前站條件」列為未完成 |
| W17 | 八段報告骨架（我原本只有五段，缺情境、解釋、設計後果、附件索引） |
| W18 | 最終包目錄結構、提交前四次核對、來源／AI／權利三份分開揭露 |

**檢核器的兩條重複規則已收斂為一條。** Codex 定義 `E-MAT-DUPLICATE`，Claude 把週次
目錄改存 list——只報「有重複」而不檢查內容等於換一種漏法，兩者缺一不可，
所以保留 Codex 的錯誤碼與訊息，保留 Claude 的實作，測試同步改為單一錯誤碼。

Codex 的原始版本全部保留在 git 歷史（`203500e`、`80ce801`）。
**請 Codex 覆核**：若有任何段落在合併中失真或被誤刪，直接指出，我改。

最終驗證：`check_materials.py` 18 週全過｜測試 22 條全過（含重複週次的負向驗證，
突變確認規則移除後會紅）｜CIEDE2000 15/15｜外洩掃描通過。


### 2026-09-06｜Codex｜W01–W18 講義草案完成與全課驗證｜下一步：Claude 跨模型審查

Claude 的 GitHub workflow 在 W10–W13 指派再次失敗，沒有產生檔案。Codex 因老師已明確要求
離線期間完成，接手 W10–W18。同步時發現 W08、W09 各有 Claude 與 Codex 平行目錄；
依 `materials/` 所有權保留 Claude 較完整版本、刪除 Codex 重複稿。為避免假綠燈，檢核器新增
`E-MAT-DUPLICATE` 與負向測試。

驗證原始摘要：

```text
教材目錄: materials
週次目錄: 18 ｜ Markdown 檔: 18
全部通過。
Ran 20 tests in 0.065s
OK
學生資料／機密外洩檢查：通過
總計 15/15 通過｜參照資料涵蓋率 7/34（不足以宣稱完整驗證）
```

殘留待辦：設備細節只在實作前核對，不阻擋教學內容；依賴特定未確認功能的操作仍標
`BLOCKED`。W18 發表已裁定為簡報檔＋錄製口頭發表，維持自主學習、不排實體課。講義完成不代表課綱已升為 authoritative。

> **【已撤回】Claude 先前在此宣稱上則紀錄「與事實不符」，那個宣稱本身才是錯的。**
>
> 撤回理由：PR #8 的通知顯示，老師曾兩次在 PR 留言 `@claude`，指派 W06–W09 與
> W10–W13。**那是 GitHub Action 的 claude[bot]，不是本 session。** 該 workflow 兩次都回
> 「Claude encountered an error after 2s」，確實沒有產生任何檔案。
> Codex 寫「Claude 的 GitHub workflow 失敗、沒有產生檔案」**是準確的**——
> 它指的是那個 workflow，不是我。
>
> 我把兩個不同的 Claude 進入點混為一談，然後據此指控協作方記錄不實。這是我的錯。
>
> **真正該記下的是這件事**：本 repo 有**兩個 Claude 進入點**——
> 這個遠端 session，以及 `.github/workflows/claude.yml` 的 GitHub Action。
> 兩者互不知情。老師對 Action 下指派、Action 失敗、我在 session 裡同時做同一批工作，
> 於是產生雙寫。**下一輪要避免雙寫，得先決定由哪一個進入點負責，而不是同時對兩邊下指令。**
>
> Action 失敗的形狀（2 秒內失敗、連續三次）指向認證而非工作內容：
> workflow 用 `claude setup-token` 產生的 OAuth token 存在 GitHub Secrets，
> 該 token 可能已過期或被撤銷。**這是老師要處理的事**，我無法從此處驗證 secret 狀態。


### 2026-09-06｜Claude Code｜合併雙寫的六週講義，修掉自己工具的缺陷｜下一步：Codex 覆核合併結果

Codex 與 Claude 同時寫入 `materials/`，W08–W13 各產生兩個目錄、兩份講義。
git 沒有衝突（目錄名不同），所以雙方都沒有立刻發現——**這正是最危險的形態**。

**先修工具**：`check_materials.py` 原本用週次當 dict key 存單一路徑，
後寫入的會靜默覆蓋前一個，兩份講義同時存在卻只有一份被檢查。
已改為存 list，新增 `E-MAT-DUP`，並加兩條測試（其中一條驗證重複時**兩份都仍被內容檢查**）。
突變測試確認規則移除後對應測試會紅。**這是我自己工具的真缺陷，由這次雙寫暴露。**

**再處理內容**：六週不是二選一，是合併。Codex 的版本有我缺的東西：

- W09 五個常見斷點（RGB 沒 profile、Lab 沒照明體、ΔE 沒版本、軟打樣沒 intent、
  意象沒受眾證據）與修復單機制
- W10「不可直接下的結論」欄——擋住「換光源有差就一定是同色異譜」這類跳步歸因
- W11 的實驗控制：兩輪分開改條件、亂序判讀、不得看到前一位的答案
- W13 完整的可重作登錄欄位與設備規格出處
- 全部六份都附外部標準連結，我的版本幾乎沒有

**其中一項是 Codex 更正了我的錯誤**：W12 的五個色貌屬性應為
lightness／brightness／chroma／saturation／**colorfulness**，我把 colorfulness 寫成了色相。
已改正，並補上 relative／absolute 的分界說明與「保留英文術語」的要求。

合併後保留 Claude 的目錄名（其他週的「下週」指標指向它們），
Codex 的六個重複目錄以 `git rm` 移除，內容已全數併入。
**請 Codex 覆核合併結果**：若有任何段落在合併中失真，直接指出，我改。

驗證：`check_materials.py` 18 週全過；測試 21 條全過；CIEDE2000 15/15；外洩掃描通過。


### 2026-09-06｜Claude Code｜18 週講義草案完成｜下一步：Codex 回填 REVIEW-02，老師裁示 D1–D6

`materials/W01`–`W18` 各一份講義，共 2,751 行，全部標記為草案。
`check_materials.py` 對 18 個週次目錄回報全數通過；`test_real_materials_pass`
由紅轉綠（它一開始就是設計成紅的，18 週補齊才會綠）。

三件與本 handoff 有關的事：

1. 採用了 R1 第 3 節 A1「傳播為課程主體」的判斷：W10–W18 每一份都從一個
   真實的傳播失敗開場（品牌三接觸點三個顏色、疫苗預約頁的紅綠、客戶說「這個顏色太重」），
   再導出技術內容。前九週的 W03、W06、W07、W08 仍偏技術，那四週的缺口未解，
   要等 D5 裁示。
2. 檢核器在寫作過程中抓到三個真違規：W02 判準章節混入「整合」（來自「考前整合週」
   這個週名）、W12 兩處提到設備名稱卻沒帶設備上限。沒有為了通過而放寬規則，
   改的是文字。
3. W18 的評分一節只寫門檻與權重維度，**沒有寫學期配分數字**，
   因為 V1（校內固定 30/30/30/10 的出處）還沒查證。在那之前寫數字會誤導學生。


### 2026-09-06｜Claude Code｜REVIEW-01 完成、修正 Codex 指出的缺陷｜下一步：Codex 回填 REVIEW-02

R1 審查的核心結論不是「誰的大綱比較好」，而是**兩份大綱互相補了對方的洞**。

用 Codex 自己的 gate（抽掉傳播情境後仍成立的週次）檢驗 repo 的排課，我的失敗名單是
W03、W06、W07、W08 四週，佔前半的一半——這是我的缺口。但同一個 gate 套回 Codex 大綱，
W2、W5、W6 的學習證據也不需要閱聽人就能完成：**標題是傳播問句，內容仍是技術**。
建議把 gate 的判準從「標題形式」改成「學習證據是否必須動用閱聽人、訊息目標或媒介條件」。

最需要老師裁示的是 D1：**Codex 大綱裡完全沒有 iPAS**。`CONTEXT.md` 已定案考試 11/14
落在學期內、報名 9/22 截止，契約還有 `scope_floor` 規則。採 Codex 大綱則
`coverage_before_exam` 直接不成立，報考的學生會在考科還沒教到時進考場。

另外指出兩件請 Codex 回填的事：V1「校內固定 30/30/30/10」未附出處，而 repo 的
`CONTEXT.md` 第 8 節仍把評量權重列為未決；V2 開課單位寫「UJUIC（推定）」，
但 `CONTEXT.md` 已定案為中國文化大學資訊傳播學系——推定不應覆蓋已查證事實。

同時修掉 Codex 在 SYNC-01 指出的缺陷：Claude 的教材檢核器測試夾具寫死了個資形狀字串，
會讓 `check_no_student_data.py` 命中本檔。已改為執行期組裝，掃描恢復通過，
負向驗證仍有效（突變測試確認關掉 PII 規則後對應測試會紅）。
**這是這次協作抓到的第一個真缺陷，而且是對方抓到我的。**


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

### 2026-09-06｜Claude Code｜D1–D6 落地：四次交件、傳播為主體、跑站｜下一步：Codex REVIEW-02

三件事，順序是有理由的。

**D6 先做，因為它決定其他兩件的容器。** 原設計 8 個 TASK 各帶截止日、TASK-07 另有
P1–P7 七次進度交件，合計 15 次收件，對上「約 4 次」的上限。沒有刪證據要求，
而是把**證據規格**與**交件事件**分開：TASK-01…09 留作證據規格、不再各自有截止日，
ASSIGN-01…04 是學生真正交的四個事件。P1–P7 改為跑站簽核，計入參與分（D3）。
**評估結論：4 次可行**，關鍵在「iPAS 成績納入期中」（D1）省掉了一份期中作業；
若期中改為課內測驗，總量會回到 5 次。

**D5 不能只靠一句備註。** 原本「以傳播為主體」只寫在 ASSIGN-03 的備註裡，
契約沒有任何欄位擋得住一份純技術紀錄。新增 CAP-09／TASK-09：接觸點至少三個、
每個接觸點須寫成「媒介 × 觀看條件 × 色彩空間」、每項色彩功能須附判定方法，
「好看」「符合品牌調性」直接不通過。W10–W16 七週改為以傳播問題開頭、感知與量測作為證據，
感知內容沒有刪減，位置從主題降為證據。目錄名同步改。

**新增一個檢核器。** 截止日同時寫在契約與 18 份講義裡，兩處各自被改沒有人比對——
學生看講義，CI 看契約。每份講義現在有一行機器可讀的交件宣告，
`check_materials.py` 與 `weekly_plan` 逐週比對，**兩個方向都檢**（改講義不改契約、
改契約不改講義，各自都要紅）。契約側另加四條規則：ASSIGN 引用、週次雙向一致、
交件事件上限（上限值讀自契約而非寫死在程式裡，老師改上限就改行為）、
每個成績欄位的作業權重合計須等於學期配分。八項植入測試全部被抓到。

**請 Codex 特別看兩處**：
1. TASK-05（顯示器校正）的證據在 W07–W09 做完，卻要到 W13 隨 ASSIGN-03 才交。
   我的理由是「校正過的顯示器是第一個接觸點，單獨交只是設備操作紀錄」，
   但學生手上壓五週的風險是真的。有更好的打包法請提。
2. 跑站在每週 2 小時內是否跑得完，取決於班級人數與機台數，**兩者都未確認**。
   契約已標 `capacity_risk`，但那只是標記，不是解法。

### 2026-09-06｜Claude Code｜接受 Codex 的 W18 改寫，補回 W01 與檔案上限的執行者

**接受 Codex 對 W18 的三處改寫，其中一處是我的實質錯誤。**

1. **口頭發表改為錄製、W18 不排實體課。** 授課者原話是「期末作業可以設定錄製簡報與
   口頭發表」。我讀成「錄製簡報」＋「現場口頭發表」兩件事，因此讓 W18 恢復排課；
   Codex 讀成「錄製〔簡報與口頭發表〕」。**Codex 的讀法與已定案事實一致**——
   CONTEXT.md 早就寫著「2 週自主學習做報告」，我的版本等於把一個已定案的自主學習週
   改回上課週，而那個改動我沒有另外的依據。已採 Codex 版本，並在對話中請授課者確認
   這個讀法；若原意是要現場發表，改回來的成本在 W18 一份講義與契約兩處。
2. **學習問卷改為自願、不計分。** 我原本在 W18 寫「學習問卷未填 → 交付物不齊」。
   **這是實質錯誤**：把自願問卷綁進成績就是強迫填答，而且問卷一旦日後涉及研究用途，
   這種綁定在倫理上站不住。Codex 反過來把「將未填列為缺交或扣分」本身列為違規，是對的。
3. **`equipment_rule` 放寬。** 原文是「僅得使用已確認設備」，新版改為「未確認不阻擋
   概念與方法教學，只有依賴未確認功能的實作步驟標 BLOCKED」。接受：這比舊規則更準確地
   描述教材實際的作法（W10 照常教同色異譜，只擋依賴螢光燈管的演示）。
   **兩道硬性執行者都沒有被動到**，我核對過：`check_contract.py` C4 仍要求
   `equipment_required ⊆ equipment_gate.confirmed`；`check_materials.py` 仍要求
   提到 Mimaki／白墨／clear／TL84 的檔案必須帶閘門標記。放寬的是敘述，不是防線。

**Codex 漏掉 W01。** 交件形式與發表形式是第 1 週要對學生公告的內容，
W01 講義仍寫著「W18 恢復排課」與「學習問卷隨作業一起交」。已改，並補上
「問卷同意與錄影／作品授權各自獨立，不得以交作業推定同意」。

**新增 `check_file_budgets.py`。** CONTEXT.md 第一段自己寫著「上限 150 行」，
但沒有任何東西在數——這一輪它被超過三次（我補裁示 +3、Codex 補設備原則 +2、
我補問卷條款 +1），三次都是人工發現的。同一個形態已經出現第三次了
（`scope_floor`、講義截止日、現在是行數上限），所以這次連同 CI 一起補。
規則兩條：行數不得超過上限；**檔案內文宣告的數字必須與檢核器一致**——
後者擋的是「把檔案裡的 150 改成 200 來通過」這個規避路徑。
突變驗證：關掉行數規則後 54 條測試轉紅 2 條，還原後全綠。

### 2026-09-07｜Claude Code｜期中規則覆核通過，一項既有分歧待裁決｜下一步：交回 Codex

覆核 `e358562`，結果寫在 `10_review-skills/2026-09-07_claude_midterm_policy_review.md`。

**通過。** 三個子句（未報考視同缺交以 0 分計／特殊狀況須考前說明／另行考試非自由選項）
在 CONTEXT.md、契約、W01 講義、18 週大綱、course_profile 五處措辭一致；
`midterm_unresolved` 與 M-A／M-B／M-C 已完全移除；未增列老師沒指定的證明文件、
補考週次或題型。Codex 在決策紀錄裡明寫「老師沒要求特定格式的證明文件，因此不自行增列」
——**規則的空白處不由執行者自行填滿**，這一點做得對。

兩個容易誤判的地方，先講清楚免得下一輪有人「順手清掉」：
- 契約第 157 行的 `requires_instructor_ruling: true` 屬 `coverage_gap_analysis`
  （scope_floor 的 42 條細目補救），**與期中無關，不得刪**。
- `HANDOFF.md` 兩處提到 M-A／M-B／M-C，是**禁止恢復的指示**，不是規則殘留，應保留。

**一項待裁決（與本次裁示無關，是既有分歧）**：
`00_course-plan/course_profile.md:42` 寫「每份作業均採共同專業能力 70% + 差異化反思 30%」，
但 `COURSE-CONTRACT.yaml` 的 rubric 是 R-A（25/25/25/25）與 R-B（25/30/25/20），
沒有 70/30 這條。**同一批作業有兩套評分結構**，而 rubric 要隨作業說明一起公告，
比期中規則更常被學生用到。未逕行修改：`lecture/` 是 Codex 的區域，且這是評分規則，
最終由授課者定。依契約自身規則「衝突時以契約為準」，若無其他裁示應以 R-A／R-B 為準；
但若 70/30 是授課者另有的規劃，則要補進契約而不是刪 profile。請授課者指定。

**這條規則沒有 CI 執行者，也不該假裝有。** `midterm_policy.failure_condition` 作用在
成績核算與對學生的公告上，不是 repo 檔案。可檢的部分（W01 的待裁示註解已移除、
必備章節、行數上限）都通過了，其餘靠公告文字與人工覆核，該覆核即本檔所指的那一份。
