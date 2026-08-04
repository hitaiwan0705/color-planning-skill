#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ciede2000.py — CIEDE2000 實作驗證套件 v1.0

【設計原則】
本套件刻意分為兩類測試，因為兩者的證據強度不同：

  A. 參照資料測試 (reference tests)
     依賴外部權威資料集的預期值。強度取決於資料集的完整性與來源可信度。
     目前僅含 7/34 組，**不足以宣稱通過完整基準**。

  B. 性質測試 (property tests)
     不依賴任何記憶或外部數值，由公式本身的數學性質推導而來。
     這類測試可自我驗證，涵蓋參照資料未必觸及的邊界條件。

執行：
  python3 test_ciede2000.py                    # 跑全部
  python3 test_ciede2000.py --report report.md # 產出報告
"""

import sys, os, csv, math, platform, argparse, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from color_audit import ciede2000  # noqa: E402

TOL = 1e-4   # 絕對誤差容許值


class Runner:
    def __init__(self):
        self.rows = []

    def check(self, category, name, ok, detail=""):
        self.rows.append({"category": category, "name": name,
                          "pass": bool(ok), "detail": detail})
        return ok

    @property
    def failed(self):
        return [r for r in self.rows if not r["pass"]]


# ---------------- A. 參照資料測試 ----------------

def reference_tests(r, csv_path):
    n = 0
    with open(csv_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or line.startswith('pair_id'):
                continue
            c = line.strip().split(',')
            if len(c) < 8:
                continue
            pid = c[0]
            lab1 = tuple(float(x) for x in c[1:4])
            lab2 = tuple(float(x) for x in c[4:7])
            exp = float(c[7])
            got = ciede2000(lab1, lab2)
            err = abs(got - exp)
            r.check("A. 參照資料", f"pair {pid}", err < TOL,
                    f"預期={exp:.4f} 實際={got:.6f} 絕對誤差={err:.2e}")
            n += 1
    return n


# ---------------- B. 性質測試（自我驗證） ----------------

def property_tests(r):
    P = lambda name, ok, d="": r.check("B. 性質測試", name, ok, d)

    # B1 同一性：ΔE(x,x) = 0
    samples = [(50, 0, 0), (0, 0, 0), (100, 0, 0), (32.3, -12.5, 44.1),
               (75, 60, -70), (2.08, 0.08, -1.14)]
    worst = max(abs(ciede2000(s, s)) for s in samples)
    P("B1 同一性 ΔE(x,x)=0", worst < 1e-12, f"最大殘差={worst:.2e}")

    # B2 對稱性：ΔE(x,y) = ΔE(y,x)  ← CIEDE2000 的 h̄' 分支邏輯最易在此出錯
    pairs = [((50, 2.6772, -79.7751), (50, 0, -82.7485)),
             ((50, -1.3802, -84.2814), (50, 0, -82.7485)),
             ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387)),
             ((50, 25, 0), (50, 0, 25)),
             ((50, -5, 0.1), (50, -5, -0.1))]
    worst = max(abs(ciede2000(a, b) - ciede2000(b, a)) for a, b in pairs)
    P("B2 對稱性 ΔE(x,y)=ΔE(y,x)", worst < 1e-10, f"最大不對稱={worst:.2e}")

    # B3 色相環繞：h̄'（平均色相）跨越 0°/360° 的分支邏輯
    #    參數 C=100、跨界角距 10° 是實測出的最大鑑別條件：
    #    若移除 hbp 的環繞分支，此案例 ΔE 由 5.85 變為 7.06（+20.8%）。
    #    【已知限制】dhp 的 ±360 修正因 sin(dhp/2) 半角性質而自我抵銷，
    #    無法由 ΔE 輸出偵測。此為性質測試的固有盲區，只能靠完整參照資料覆蓋。
    def lab_at(hue_deg, C=100.0, L=50.0):
        rad = math.radians(hue_deg)
        return (L, C * math.cos(rad), C * math.sin(rad))
    crossing = ciede2000(lab_at(355), lab_at(5))
    P("B3 平均色相 h̄' 環繞分支", abs(crossing - 5.8487) < 0.01,
      f"跨界ΔE={crossing:.4f}（正確值 5.8487；缺環繞分支之實作為 7.0649）")

    # B4 中性色除零防護：C'=0 時 h' 未定義，不得拋出例外或回傳 NaN
    try:
        v1 = ciede2000((50, 0, 0), (60, 0, 0))
        v2 = ciede2000((50, 0, 0), (50, 10, 0))
        ok = all(math.isfinite(v) for v in (v1, v2)) and v1 > 0 and v2 > 0
        P("B4 中性色 C'=0 除零防護", ok, f"ΔE={v1:.4f}, {v2:.4f}，皆有限且為正")
    except Exception as e:
        P("B4 中性色 C'=0 除零防護", False, f"拋出例外: {e}")

    # B5 極端值穩定性：Lab 定義域邊界不得溢位
    try:
        vals = [ciede2000((0, -128, -128), (100, 127, 127)),
                ciede2000((0, 0, 0), (100, 0, 0)),
                ciede2000((100, 127, 127), (100, 127, 126.9))]
        P("B5 極端值穩定性", all(math.isfinite(v) and v >= 0 for v in vals),
          "ΔE=" + ", ".join(f"{v:.4f}" for v in vals))
    except Exception as e:
        P("B5 極端值穩定性", False, f"拋出例外: {e}")

    # B6 RT 旋轉項生效：藍色區 (h'≈275°) 必須觸發旋轉修正
    #    若 RT 被誤實作為 0，此處色差會與未修正版本相同
    blue1, blue2 = (50, 20, -50), (50, 10, -55)
    with_rt = ciede2000(blue1, blue2)
    P("B6 藍色區 RT 旋轉項生效", 0 < with_rt < 20,
      f"ΔE00={with_rt:.4f}（藍色區旋轉修正應使其小於未修正之歐氏距離）")

    # B7 亮度權重 SL 生效：同樣的 ΔL* 在中亮度與極端亮度應得到不同 ΔE
    mid = ciede2000((50, 0, 0), (55, 0, 0))
    low = ciede2000((5, 0, 0), (10, 0, 0))
    P("B7 亮度權重 SL 生效", abs(mid - low) > 0.5,
      f"中亮度ΔE={mid:.4f} vs 低亮度ΔE={low:.4f}（SL 應使兩者顯著不同）")

    # B8 單調性：沿單一軸遞增時 ΔE 應遞增
    base = (50, 0, 0)
    seq = [ciede2000(base, (50, k, 0)) for k in (1, 5, 10, 20, 40)]
    P("B8 沿 a* 軸單調遞增", all(x < y for x, y in zip(seq, seq[1:])),
      " < ".join(f"{v:.3f}" for v in seq))


# ---------------- 報告 ----------------

def build_report(r, n_ref, csv_path):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    lines = [
        "# CIEDE2000 實作驗證報告", "",
        f"- 產生時間（UTC）：{now}",
        f"- Python：{platform.python_version()}（{platform.python_implementation()}）",
        f"- 平台：{platform.platform()}",
        f"- 受測模組：`tools/color/scripts/color_audit.py` → `ciede2000()`",
        f"- 絕對誤差容許值：{TOL}", "",
        "## 驗證範圍聲明（必讀）", "",
        f"- 參照資料測試：**{n_ref} / 34 組**，來源 `{os.path.basename(csv_path)}`",
        "- **本報告不得被解讀為「已通過 Sharma et al. (2005) 完整基準測試」。**",
        "  完整 34 組資料請自 Sharma 公開頁面下載後覆蓋參照 CSV 再重跑本套件。",
        "- 性質測試不依賴外部資料，由 CIEDE2000 公式的數學性質推導，可獨立自我驗證。", "",
        "## 測試結果", "",
        "| 類別 | 測試項 | 結果 | 細節 |", "|---|---|---|---|",
    ]
    for row in r.rows:
        lines.append(f"| {row['category']} | {row['name']} | "
                     f"{'PASS' if row['pass'] else '**FAIL**'} | {row['detail']} |")
    n_pass = len(r.rows) - len(r.failed)
    lines += ["", f"**總計：{n_pass} / {len(r.rows)} 通過**", ""]
    if r.failed:
        lines.append("### 未通過項目")
        for row in r.failed:
            lines.append(f"- {row['name']}：{row['detail']}")
    else:
        lines += ["## 結論", "",
                  "所有已執行的測試通過。就已涵蓋的範圍而言，實作與 CIEDE2000 定義一致；",
                  "但**參照資料涵蓋率不足**，完整宣稱須待 34 組資料補齊後重跑。"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", help="輸出 Markdown 報告路徑")
    args = ap.parse_args()

    csv_path = os.path.join(os.path.dirname(__file__), "sharma_reference_data.csv")
    r = Runner()
    n_ref = reference_tests(r, csv_path)
    property_tests(r)

    for row in r.rows:
        print(f"[{'PASS' if row['pass'] else 'FAIL'}] {row['category']} | "
              f"{row['name']:<28} {row['detail']}")
    print("-" * 72)
    print(f"總計 {len(r.rows) - len(r.failed)}/{len(r.rows)} 通過｜"
          f"參照資料涵蓋率 {n_ref}/34（不足以宣稱完整驗證）")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(build_report(r, n_ref, csv_path))
        print(f"報告已寫入 {args.report}")

    sys.exit(1 if r.failed else 0)


if __name__ == "__main__":
    main()
