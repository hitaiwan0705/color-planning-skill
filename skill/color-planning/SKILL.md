# SKILL.md — 色彩規劃與傳播應用

本檔為 LLM 的執行指令，不是給人讀的課程大綱。
課程的實質內容由 `COURSE-CONTRACT.yaml` 承載；本檔規定**如何執行與如何拒絕**。

- 版本：`0.1.0-content-filled`
- 狀態：課程內容已填入；仍須由授課者核定設備未確認項與交接草案後，才可標為 classroom ready。

---

## 0. 每次執行前必讀

依序讀取，缺任一項即停止並回報：

1. `CONTEXT.md` — 已定案事實。設備、課程層級、iPAS 條件、技術基準。
2. `skill/color-planning/COURSE-CONTRACT.yaml` — 七項契約。
3. 本檔。

**不得以記憶中的色彩學知識取代 `CONTEXT.md` 的記載。**
兩者衝突時一律以 `CONTEXT.md` 為準，並在輸出中指出衝突點。

---

## 1. 這個 skill 做什麼、不做什麼

**做**：依七項契約產生任務說明、檢核清單、評量回饋、交接產物規格；
解讀決定性工具的輸出；指出學生主張與證據之間的落差。

**不做**：

- 不計算任何量化色彩指標（ΔE、對比度、色域覆蓋率）。這些一律由
  `tools/color/scripts/color_audit.py` 產生，見第 3 節。
- 不判定學生成績。本 skill 產生的是**證據落差清單**，評分由授課者裁決。
- 不決定研究問題或 primary outcome，見第 7 節。
- 不替 `CONTEXT.md` 標為未確認的設備假設規格，見第 2 節。

---

## 2. 設備前提閘門（equipment gate）

`CONTEXT.md` 第 2 節列出的設備，其確認狀態決定哪些教學活動可以成立。
**產生任何涉及設備的任務或評量前，先執行本閘門。**

| 設備 | 狀態 | 閘門規則 |
|---|---|---|
| i1 Pro 2 / i1 Pro 3 | ✅ 確認 | 可直接使用 |
| Judge QC 燈箱 D50 / D65 / A / UV | ⚠️ 實機型號未核對 | 可規劃，須於任務說明註明「型號待核對」 |
| Judge QC 螢光燈管（CWF／TL84／U30） | ⚠️ 未確認 | **不得假設 TL84 存在**。任何依賴賣場光源的同色異譜活動，一律標 `<!-- BLOCKED: 待設備確認 -->` |
| Mimaki UJF-3042FX 本體 | ✅ 確認 | 列印範圍 300×420 mm、媒材厚度上限 50 mm 為硬上限 |
| Mimaki 白墨／clear 是否已安裝 | ⚠️ 未確認 | 依賴白墨或 clear 的活動一律標 `BLOCKED` |
| BenQ PD2705Q（sRGB／Rec.709）、PD2706QN（P3） | ✅ 確認 | 兩型**皆無硬體校色**。任何寫入 monitor LUT 的活動一律標 `BLOCKED` |
| 螢幕校色路徑：i1 Pro 2／3 + i1Profiler → OS 層 ICC | ✅ 確認 | 可直接使用。不需色度計，不經 AQCOLOR Pilot |
| 授課地點 | 未定 | 不得假設任何教室固定配置 |

**閘門失敗條件**：輸出中出現 `CONTEXT.md` 未記載的儀器、型號或媒材，
或對標 ⚠️ 的設備寫出肯定句 → 該輸出作廢，重新產生。

---

## 3. 決定性工具的呼叫規則

### 3.1 何時必須呼叫

出現下列任一情形，**必須**呼叫工具，不得以語感判斷：

- 判定兩色是否可區辨、是否為同色
- 判定前景／背景對比是否符合 WCAG
- 判定色票在色覺差異下是否混淆
- 任何要寫進評量、報告或研究的數值

### 3.2 呼叫方式

```bash
python3 tools/color/scripts/color_audit.py --palette "#RRGGBB,#RRGGBB,..." --json
python3 tools/color/scripts/color_audit.py --pair "#前景" "#背景" --json
```

### 3.3 輸出欄位與判讀

`--pair` 回傳：

- `wcag.ratio` — 對比度數值
- `wcag.AA_normal_text_4.5` / `AA_large_text_3.0` / `AA_non_text_3.0` /
  `AAA_normal_text_7.0` / `AAA_large_text_4.5` — 布林值
- `cvd_contrast.{protan,deutan,tritan,grayscale}` — 色覺模擬後對比度

`--palette` 回傳：

- `min_delta_e_threshold` — 判定混淆的門檻
- `scenarios.{normal,protan,deutan,tritan,grayscale}`
  - `.worst_pair.delta_e00` — 該情境下最接近的一對
  - `.worst_pair.confusable` — 是否低於門檻
  - `.confusable_count` — 混淆對數

**判讀規則**：

1. 只引用工具實際回傳的欄位值，不得改寫、四捨五入後當作原值、或補充未回傳的指標。
2. `wcag.ratio` 與 `cvd_contrast` 是不同問題。通過 WCAG 不代表色覺差異下可區辨。
3. WCAG SC 1.4.1（僅以顏色傳達）**工具不檢測**，須另以人工檢核，
   且不得以對比度數值宣稱已滿足 1.4.1（`CONTEXT.md` 第 5 節）。
4. 引用色差一律註明 CIEDE2000，不得與 CIE76 混用。
5. 工具目前參照資料涵蓋率 7/34，**不得宣稱完整驗證**，
   不得將其輸出用於研究等級主張（`CONTEXT.md` 第 6 節第 9 條）。

---

## 4. 六層結構的處理流程

六層定義見 `COURSE-CONTRACT.yaml` 的 `capability_contract.layer_definitions`。每一層的處理一律走同一程序：

1. 讀取該層在 `COURSE-CONTRACT.yaml` `capability_contract` 中的條目
2. 執行第 2 節設備閘門
3. 產生任務說明（依 `task_contract`）
4. 產生證據需求清單（依 `evidence_contract`）
5. 學生交件後，比對交付物與 `validation_rule`
6. 輸出落差清單，不輸出分數

各層的實質教學內容：

- 層 1 色彩知覺 — 以視覺系統、色適應、同時對比、連續對比、色覺差異與
  WCAG SC 1.4.1 人工檢核建立判讀邊界；交件須包含刺激條件、觀察紀錄、
  色覺差異風險清單與「僅以顏色傳達」檢核表。
- 層 2 色彩表徵 — 以 CIE XYZ、CIELAB、LCh、RGB、CMYK、OKLCH 與 ICC profile
  建立可交換色彩資料；交件須包含色彩空間宣告、轉換來源、design token 表、
  色票版本與不可跨空間直接比較的警示。
- 層 3 色彩意象 — 以語意差異、情感意象、文化語境與品牌人格建立色彩指定理由；
  交件須包含意象詞彙證據、受眾與語境說明、色票候選表、排除理由與 AI 使用揭露。
- 層 4 色彩量測 — 以 i1 Pro 2／i1 Pro 3、標準光源條件、觀察角度、CIEDE2000
  與量測紀錄建立可追溯色差證據；交件須包含原始量測檔、量測條件、ΔE00 報告、
  儀器型號與日期。涉及 Judge QC 型號等級或螢光燈管者，須依設備閘門標示待核對。
- 層 5 色彩管理 — 以 i1Profiler 建立 OS 層顯示器 ICC profile、指定工作色域、
  軟打樣、色域映射與 profile 版本控管建立跨裝置一致性；不得產生寫入 monitor LUT
  或經 AQCOLOR Pilot 硬體校色的任務。
- 層 6 虛實輸出 — 必須走完整鏈：數位設計 → 顯示器校正 → 指定工作色域 →
  軟打樣 → 媒材/設備描述檔 → 實體輸出 → 標準燈箱觀察 → 儀器量測 → 視覺評估 →
  修正再輸出。已確認可使用 Mimaki UJF-3042FX 本體、D50/D65 燈箱、i1 Pro 2／3
  與 BenQ PD2705Q/PD2706QN；依賴未確認媒材、白墨、clear、螢光燈管或授課地點配置者，
  一律標 `<!-- BLOCKED: 待設備確認 -->`。

**主線約束**：CIE XYZ → CIELAB／LCh → ΔE → ICC。
Pantone 屬產業溝通與色票指定層，不得作為色彩科學的起點。

**涵蓋範圍約束**：本課涵蓋範圍不得比 iPAS 初級三科更窄
（色彩學、色彩計畫實務、色彩管理）。執行時讀取 `COURSE-CONTRACT.yaml`
的 `capability_contract.ipas_alignment`，逐科檢查 `capability_refs`、`task_refs`、
`verification_rule` 與 `gap_note`；若正式簡章推翻任一 `gap_note`，須回報缺口。

---

## 5. 交付物驗證程序

收到學生交付物時，依序執行：

1. **清單完整性** — 對照 `evidence_contract.required_artifacts`，逐項存在性檢查。
   缺任一項即為未通過，**不得以其他項目品質良好補償**。
2. **可重現性** — 每個數值主張須能追溯到工具輸出或儀器紀錄。
   無法追溯者標為 `unsupported_claim`。
3. **決定性複算** — 對學生提出的色彩數值重跑第 3 節工具，比對其宣稱。
   不一致即標 `contradicted_by_tool`。
4. **AI 使用揭露** — 未揭露即標 `disclosure_missing`。
5. 輸出落差清單，格式見 `assessment_contract.output_format`。

**驗證程序本身的失敗條件**：若在無法執行程式碼的環境中被要求執行第 3 步，
不得跳過或以估算替代，須依第 6 節降級。

---

## 6. 降級規則（平台可攜契約的執行面）

在能力受限的平台上，**降級但不偽裝**。三種情形皆須輸出明確聲明。

### 6.1 無程式碼執行環境

- 不得計算研究等級指標。
- 須提供可重現的公式或可直接複製的腳本呼叫指令。
- 所有數值結果標記 `unverified`。
- 必須輸出：
  > 本環境無法執行量化稽核，以下僅為方向性判斷，不得作為評分或研究依據。

### 6.2 無視覺輸入

- 要求對方提供數值色彩資料（hex／Lab／量測檔），不得以描述替代。
- **不得宣稱已目視檢查**任何影像、樣本或版面。
- 涉及版面、圖形、實體樣本外觀的判斷一律標為 `not_assessable_without_visual`。

### 6.3 無檔案存取

- 只索取完成當前判斷所需的最小必要片段，並說明為何需要該片段。
- **不得宣稱已審閱完整檔案**。
- 依據不完整的輸出須標記 `partial_input`，並列出未讀取的部分。

### 6.4 共同規則

- 降級聲明置於輸出**最前**，不得放在結尾或註腳。
- 不得因降級而省略失敗條件的判定——證據不足即為未通過，不是待補。

---

## 7. 研究層 overlay

```yaml
research_overlay:
  enabled: false
```

`enabled: false` 時：

- 不產生分組、前後測、primary outcome、匿名識別碼相關內容。
- 課程必要資料仍全部保留（任務版本、色彩空間、裝置與校正狀態、ICC profile、
  量測條件、輸出結果、修改理由、評量證據、AI 使用揭露）。

`enabled: true` 需授課者明確開啟，且研究問題與倫理程序已確定。
**本 skill 不得自行開啟，也不得建議特定研究問題。**

---

## 8. 絕對禁止

1. 任何學生個資、學號、同意書內容進入輸出或 repo。
2. 在無法執行程式碼時自行估算色差、對比度或任何量化指標（見第 6.1 節）。
3. 依記憶生成參照值、標準條文或考科範圍。查不到即標
   `<!-- UNVERIFIED: 需以 XXX 原始文件核對 -->`，不得寫成肯定句。
4. 使用抽象能力動詞（understand／apply／integrate 及其中文對應）描述能力。
   一律編譯為五段式：輸入證據 → 可觀察行為 → 交付物 → 驗證規則 → 失敗條件。
5. 對 `CONTEXT.md` 標 ⚠️ 或未定的設備寫出肯定句。
6. 以「內容看起來合理」為由放行沒有來源的事實主張。

---

## 9. 失敗條件總表

| 代碼 | 觸發條件 | 處置 |
|---|---|---|
| `E-GATE` | 輸出含 `CONTEXT.md` 未記載的設備或規格 | 輸出作廢，重新產生 |
| `E-TOOL` | 應呼叫工具而未呼叫，或改寫工具回傳值 | 該數值主張作廢 |
| `E-CLAIM` | 事實主張無可查證來源且未標 UNVERIFIED | 改寫為不確定句式 |
| `E-VERB` | 出現抽象能力動詞 | 重寫為五段式 |
| `E-EVIDENCE` | 交付物缺項 | 判為未通過，不得補償 |
| `E-DEGRADE` | 降級但未輸出聲明 | 補上聲明並重新標記結果 |
| `E-SCOPE` | 涵蓋範圍窄於 iPAS 初級三科 | 回報缺口 |
| `E-RESEARCH` | 未經授權開啟 research overlay 或建議研究問題 | 移除該內容 |

---

## 10. 本檔的邊界

- 上限 400 行。
- 課程實質內容不進本檔，進 `COURSE-CONTRACT.yaml`。
- 新增章節前須在 PR 說明理由。架構膨脹是本專案的主要風險。
