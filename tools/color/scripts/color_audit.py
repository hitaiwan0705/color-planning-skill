#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
color_audit.py — 色彩規劃決定性稽核引擎 v1.0
Deterministic Color Audit Engine

【存在理由】
LLM 無法「看見」顏色。#C41E3A 對模型而言只是 token，
任何「這兩色對比夠不夠」「色盲看得出來嗎」的判斷若由模型憑語感生成，
都是不可複製、不可審查、不可寫進論文的偽數據。
本腳本把所有量化判斷收斂為可重跑的決定性運算。

【純標準函式庫，零相依】學生電腦、教室電腦、離線環境均可執行。

用法:
  python3 color_audit.py --palette "#0072B2,#D55E00,#009E73,#CC79A7"
  python3 color_audit.py --pair "#767676" "#FFFFFF"
  python3 color_audit.py --palette "..." --json > audit.json

參考依據:
  WCAG 2.2 SC 1.4.3 / 1.4.11 — https://www.w3.org/TR/WCAG22/
  Machado, Oliveira & Fernandes (2009) IEEE TVCG 15(6):1291-1298
  Sharma, Wu & Dalal (2005) Color Res Appl 30(1):21-30 (CIEDE2000 實作註記)
"""

import math
import json
import argparse
import itertools

# ---------- 色彩空間轉換 ----------

def hex_to_rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"非法色碼: {h}")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#' + ''.join(f'{max(0, min(255, round(c * 255))):02X}' for c in rgb)


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def rgb_to_xyz(rgb):
    r, g, b = (srgb_to_linear(c) for c in rgb)
    return (
        0.4124564 * r + 0.3575761 * g + 0.1804375 * b,
        0.2126729 * r + 0.7151522 * g + 0.0721750 * b,
        0.0193339 * r + 0.1191920 * g + 0.9503041 * b,
    )


def xyz_to_lab(xyz, white=(0.95047, 1.00000, 1.08883)):
    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29
    fx, fy, fz = (f(v / w) for v, w in zip(xyz, white))
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def hex_to_lab(h):
    return xyz_to_lab(rgb_to_xyz(hex_to_rgb(h)))


# ---------- WCAG 2.2 對比度 ----------

def relative_luminance(rgb):
    r, g, b = (srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1, hex2):
    l1 = relative_luminance(hex_to_rgb(hex1))
    l2 = relative_luminance(hex_to_rgb(hex2))
    lo, hi = sorted((l1, l2))
    return (hi + 0.05) / (lo + 0.05)


def wcag_verdict(ratio):
    """回傳各情境是否通過 WCAG 2.2 Level AA / AAA"""
    return {
        "ratio": round(ratio, 3),
        "AA_normal_text_4.5": ratio >= 4.5,
        "AA_large_text_3.0": ratio >= 3.0,
        "AA_non_text_3.0": ratio >= 3.0,   # SC 1.4.11 UI 元件與圖形物件
        "AAA_normal_text_7.0": ratio >= 7.0,
        "AAA_large_text_4.5": ratio >= 4.5,
    }


# ---------- CIEDE2000 色差 ----------

def ciede2000(lab1, lab2, kL=1.0, kC=1.0, kH=1.0):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    Cbar = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cbar ** 7 / (Cbar ** 7 + 25 ** 7))) if Cbar > 0 else 0.5
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0.0

    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    else:
        dh = h2p - h1p
        dhp = dh - 360 if dh > 180 else (dh + 360 if dh < -180 else dh)
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))

    Lbp = (L1 + L2) / 2
    Cbp = (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    else:
        s = h1p + h2p
        if abs(h1p - h2p) > 180:
            hbp = (s + 360) / 2 if s < 360 else (s - 360) / 2
        else:
            hbp = s / 2

    T = (1 - 0.17 * math.cos(math.radians(hbp - 30))
         + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6))
         - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dTheta = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    RC = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) if Cbp > 0 else 0.0
    SL = 1 + (0.015 * (Lbp - 50) ** 2) / math.sqrt(20 + (Lbp - 50) ** 2)
    SC = 1 + 0.045 * Cbp
    SH = 1 + 0.015 * Cbp * T
    RT = -math.sin(math.radians(2 * dTheta)) * RC

    return math.sqrt(
        (dLp / (kL * SL)) ** 2 + (dCp / (kC * SC)) ** 2 + (dHp / (kH * SH)) ** 2
        + RT * (dCp / (kC * SC)) * (dHp / (kH * SH))
    )


# ---------- 色覺類型模擬 (Machado et al. 2009) ----------

CVD_MATRICES = {
    "protan": [[0.152286, 1.052583, -0.204868],
               [0.114503, 0.786281, 0.099216],
               [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968],
               [0.280085, 0.672501, 0.047413],
               [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.076749, -0.178779],
               [-0.078411, 0.930809, 0.147602],
               [0.004733, 0.691367, 0.303900]],
}

CVD_LABEL = {
    "protan": "紅色盲 / 第一型 (L錐體異常)",
    "deutan": "綠色盲 / 第二型 (M錐體異常)",
    "tritan": "藍黃色盲 / 第三型 (S錐體異常)",
}


def simulate_cvd(hex_color, kind):
    """在線性 RGB 空間套用 Machado 矩陣（severity = 1.0）"""
    m = CVD_MATRICES[kind]
    lin = [srgb_to_linear(c) for c in hex_to_rgb(hex_color)]
    out = [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]
    return rgb_to_hex([linear_to_srgb(c) for c in out])


def simulate_grayscale(hex_color):
    """單色列印 / 影印情境：以相對亮度轉灰階"""
    y = relative_luminance(hex_to_rgb(hex_color))
    v = linear_to_srgb(y)
    return rgb_to_hex((v, v, v))


# ---------- 主稽核流程 ----------

# 可辨識門檻：ΔE00 判讀慣例（供教學用，非國際標準硬性規定）
DE_THRESHOLDS = {"identical": 1.0, "risky": 3.0, "safe": 10.0}


def audit_palette(palette, min_de=10.0):
    """對整組色票做兩兩色差 × 四種色覺情境的稽核"""
    scenarios = ["normal", "protan", "deutan", "tritan", "grayscale"]
    report = {"palette": palette, "min_delta_e_threshold": min_de, "scenarios": {}}
    worst_overall = None

    for sc in scenarios:
        if sc == "normal":
            mapped = {c: c for c in palette}
        elif sc == "grayscale":
            mapped = {c: simulate_grayscale(c) for c in palette}
        else:
            mapped = {c: simulate_cvd(c, sc) for c in palette}

        pairs = []
        for c1, c2 in itertools.combinations(palette, 2):
            de = ciede2000(hex_to_lab(mapped[c1]), hex_to_lab(mapped[c2]))
            pairs.append({
                "pair": [c1, c2],
                "seen_as": [mapped[c1], mapped[c2]],
                "delta_e00": round(de, 2),
                "confusable": de < min_de,
            })
        pairs.sort(key=lambda p: p["delta_e00"])
        worst = pairs[0] if pairs else None
        report["scenarios"][sc] = {
            "label": CVD_LABEL.get(sc, {"normal": "常態三色視", "grayscale": "灰階/單色輸出"}.get(sc, sc)),
            "worst_pair": worst,
            "confusable_count": sum(1 for p in pairs if p["confusable"]),
            "pairs": pairs,
        }
        if worst and (worst_overall is None or worst["delta_e00"] < worst_overall["delta_e00"]):
            worst_overall = dict(worst, scenario=sc)

    report["verdict"] = {
        "worst_case": worst_overall,
        "pass": all(v["confusable_count"] == 0 for v in report["scenarios"].values()),
    }
    return report


def audit_pair(fg, bg):
    r = contrast_ratio(fg, bg)
    out = {"foreground": fg, "background": bg, "wcag": wcag_verdict(r), "cvd_contrast": {}}
    for kind in CVD_MATRICES:
        out["cvd_contrast"][kind] = round(
            contrast_ratio(simulate_cvd(fg, kind), simulate_cvd(bg, kind)), 3)
    out["cvd_contrast"]["grayscale"] = round(
        contrast_ratio(simulate_grayscale(fg), simulate_grayscale(bg)), 3)
    return out


def pretty(report):
    lines = []
    if "wcag" in report:
        w = report["wcag"]
        lines.append(f"前景 {report['foreground']} / 背景 {report['background']}")
        lines.append(f"  對比度 = {w['ratio']}:1")
        lines.append(f"  AA 內文(4.5:1)      {'PASS' if w['AA_normal_text_4.5'] else 'FAIL'}")
        lines.append(f"  AA 大字(3:1)        {'PASS' if w['AA_large_text_3.0'] else 'FAIL'}")
        lines.append(f"  AA 非文字元件(3:1)  {'PASS' if w['AA_non_text_3.0'] else 'FAIL'}")
        lines.append(f"  AAA 內文(7:1)       {'PASS' if w['AAA_normal_text_7.0'] else 'FAIL'}")
        lines.append("  色覺模擬後對比度: " + ", ".join(
            f"{k}={v}" for k, v in report["cvd_contrast"].items()))
        return "\n".join(lines)

    lines.append(f"色票組 ({len(report['palette'])} 色)：" + "  ".join(report["palette"]))
    lines.append(f"可辨識門檻 ΔE00 ≥ {report['min_delta_e_threshold']}")
    lines.append("-" * 64)
    for sc, d in report["scenarios"].items():
        w = d["worst_pair"]
        flag = "OK  " if d["confusable_count"] == 0 else "WARN"
        lines.append(f"[{flag}] {d['label']:<26} 最小ΔE00={w['delta_e00']:>6}  "
                     f"({w['pair'][0]}↔{w['pair'][1]})  混淆對數={d['confusable_count']}")
    lines.append("-" * 64)
    v = report["verdict"]
    lines.append("整體判定：" + ("通過" if v["pass"] else "未通過"))
    if v["worst_case"]:
        wc = v["worst_case"]
        lines.append(f"最脆弱情境：{wc['scenario']} — {wc['pair'][0]} 與 {wc['pair'][1]} "
                     f"在該情境下看起來是 {wc['seen_as'][0]} 與 {wc['seen_as'][1]}，ΔE00={wc['delta_e00']}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="色彩規劃決定性稽核引擎")
    ap.add_argument("--palette", help="逗號分隔色碼，例如 #0072B2,#D55E00")
    ap.add_argument("--pair", nargs=2, metavar=("FG", "BG"), help="前景色 背景色")
    ap.add_argument("--min-de", type=float, default=10.0, help="可辨識門檻 ΔE00 (預設10)")
    ap.add_argument("--json", action="store_true", help="輸出 JSON")
    args = ap.parse_args()

    if args.pair:
        rep = audit_pair(*args.pair)
    elif args.palette:
        rep = audit_palette([c.strip() for c in args.palette.split(",") if c.strip()],
                            min_de=args.min_de)
    else:
        ap.error("需指定 --palette 或 --pair")

    print(json.dumps(rep, ensure_ascii=False, indent=2) if args.json else pretty(rep))


if __name__ == "__main__":
    main()
