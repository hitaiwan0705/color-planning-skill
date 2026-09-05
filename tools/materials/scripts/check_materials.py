#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_materials.py — 教材確定性檢核器 v1.0

【存在理由】
教材的錯誤類型是「規格性」的，不是「創造性」的：術語不一致、必備章節缺漏、
抽象能力動詞、設備閘門漏標、數值主張沒有來源、週次與契約不一致。
規格性錯誤用確定性檢核抓，比用第二個 LLM 抓更準、更便宜、且可重現。
異質模型複審應限縮在觀點與論證層次（MATERIALS-PLAN.md 1.0b）。

【純標準函式庫，零相依】

用法:
  python3 tools/materials/scripts/check_materials.py
  python3 tools/materials/scripts/check_materials.py --root materials --contract skill/color-planning/COURSE-CONTRACT.yaml

離開碼: 0 = 全部通過；1 = 有違規
"""

import argparse
import os
import re
import sys

# ---------- 契約常數 ----------

WEEK_DIR_RE = re.compile(r"^W(\d{2})_")

# 講義必備章節（缺一即該週未完成）
REQUIRED_SECTIONS = ["## 這一週在解什麼問題", "## 本週交付", "## 失敗條件"]

# 能力描述不得使用的抽象動詞（CLAUDE.md 能力軸處理原則）
ABSTRACT_VERBS = ["理解", "應用", "整合", "熟悉", "掌握",
                  "understand", "apply", "integrate"]

# 出現這些設備字樣時，同一份檔案必須帶對應的閘門標記
EQUIPMENT_GATES = {
    "Mimaki": ["BLOCKED", "300", "50 mm"],
    "白墨": ["BLOCKED"],
    "clear": ["BLOCKED"],
    "TL84": ["BLOCKED"],
    "硬體校色": ["software calibration", "不得"],
}

# 數值主張：出現 ΔE 數值時必須有來源字樣
DELTA_E_NUM_RE = re.compile(r"ΔE(?:00|\*ab|\*)?\s*[=＝]\s*\d")
SOURCE_MARKERS = ["color_audit.py", "i1_pro", "i1 Pro", "量測檔", "工具輸出"]

# 個資字樣（第二道防線，主防線在 tools/validation）
PII_PATTERNS = [re.compile(r"\b[A-Z][12]\d{8}\b"), re.compile(r"學號\s*[:：]\s*\S")]


class V:
    def __init__(self, code, path, line, msg):
        self.code, self.path, self.line, self.msg = code, path, line, msg
    def __str__(self):
        return f"{self.path}:{self.line}: [{self.code}] {self.msg}"


def week_dirs(root):
    out = {}
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        m = WEEK_DIR_RE.match(name)
        if m and os.path.isdir(os.path.join(root, name)):
            out[int(m.group(1))] = os.path.join(root, name)
    return out


def duplicate_week_dirs(root):
    """Return week numbers mapped to all colliding directory paths."""
    found = {}
    if not os.path.isdir(root):
        return {}
    for name in sorted(os.listdir(root)):
        m = WEEK_DIR_RE.match(name)
        path = os.path.join(root, name)
        if m and os.path.isdir(path):
            found.setdefault(int(m.group(1)), []).append(path)
    return {wk: paths for wk, paths in found.items() if len(paths) > 1}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def fence_mask(lines):
    inside, open_f = set(), False
    for i, raw in enumerate(lines):
        if raw.lstrip().startswith("```"):
            open_f = not open_f
            inside.add(i)
        elif open_f:
            inside.add(i)
    return inside


# ---------- 規則 ----------

def check_required_sections(path, text):
    v = []
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            v.append(V("E-MAT-SECTION", path, 1, f"講義缺必備章節 {sec!r}"))
    return v


def check_abstract_verbs(path, text):
    """抽象能力動詞只在『本週交付』與『失敗條件』兩節內禁止 —— 那裡是判準。
    敘述性內文可以用這些詞。"""
    v = []
    lines = text.split("\n")
    fenced = fence_mask(lines)
    in_scope = False
    for i, raw in enumerate(lines):
        if raw.startswith("## "):
            in_scope = raw.strip() in ("## 本週交付", "## 失敗條件")
            continue
        if not in_scope or i in fenced:
            continue
        for verb in ABSTRACT_VERBS:
            if verb in raw:
                v.append(V("E-MAT-VERB", path, i + 1,
                           f"判準章節出現抽象能力動詞 {verb!r}，須改寫為可觀察行為"))
    return v


def check_equipment_gates(path, text):
    v = []
    for kw, needles in EQUIPMENT_GATES.items():
        if kw in text and not any(n in text for n in needles):
            v.append(V("E-MAT-GATE", path, 1,
                       f"提到 {kw!r} 但整份檔案沒有任何閘門標記（需其一：{needles}）"))
    return v


def check_numeric_claims(path, text):
    v = []
    lines = text.split("\n")
    fenced = fence_mask(lines)
    for i, raw in enumerate(lines):
        if i in fenced:
            continue
        if DELTA_E_NUM_RE.search(raw) and not any(m in text for m in SOURCE_MARKERS):
            v.append(V("E-MAT-CLAIM", path, i + 1,
                       "出現 ΔE 數值但整份檔案未指出來源（工具輸出或儀器量測檔）"))
    return v


def check_pii(path, text):
    v = []
    for i, raw in enumerate(text.split("\n")):
        for pat in PII_PATTERNS:
            if pat.search(raw):
                v.append(V("E-MAT-PII", path, i + 1, "疑似個資字樣"))
    return v


def parse_contract_weeks(contract_path):
    """不引入 yaml 相依：只抓 weekly_plan 底下的 `- week: N` 與其 title。"""
    if not os.path.isfile(contract_path):
        return {}
    text = read(contract_path)
    idx = text.find("weekly_plan:")
    if idx < 0:
        return {}
    seg = text[idx:]
    out = {}
    cur = None
    for raw in seg.split("\n"):
        m = re.match(r"^\s*- week: (\d+)\s*$", raw)
        if m:
            cur = int(m.group(1))
            continue
        if cur is not None:
            m2 = re.match(r"^\s*title: (.+?)\s*$", raw)
            if m2:
                out[cur] = m2.group(1)
                cur = None
    return out


def check_week_coverage(root, contract_weeks, dirs):
    v = []
    for wk in sorted(contract_weeks):
        if wk not in dirs:
            v.append(V("E-MAT-MISSING", root, 1,
                       f"契約有 week {wk}（{contract_weeks[wk]}）但 materials/ 沒有對應目錄"))
    for wk in sorted(dirs):
        if wk not in contract_weeks:
            v.append(V("E-MAT-ORPHAN", dirs[wk], 1,
                       f"materials/ 有 week {wk} 但契約的 weekly_plan 沒有這一週"))
    return v


def audit(root, contract_path):
    dirs = week_dirs(root)
    contract_weeks = parse_contract_weeks(contract_path)
    violations = check_week_coverage(root, contract_weeks, dirs)
    for wk, paths in sorted(duplicate_week_dirs(root).items()):
        violations.append(V("E-MAT-DUPLICATE", root, 1,
                            f"week {wk} 有多個教材目錄：{', '.join(paths)}"))
    files = 0

    for wk in sorted(dirs):
        d = dirs[wk]
        lecture = os.path.join(d, "講義.md")
        if not os.path.isfile(lecture):
            violations.append(V("E-MAT-MISSING", d, 1, f"week {wk} 缺 講義.md"))
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(d, fn)
            text = read(path)
            files += 1
            if fn == "講義.md":
                violations += check_required_sections(path, text)
                violations += check_abstract_verbs(path, text)
            violations += check_equipment_gates(path, text)
            violations += check_numeric_claims(path, text)
            violations += check_pii(path, text)

    violations.sort(key=lambda x: (x.path, x.line, x.code))
    return dirs, files, violations


def main(argv=None):
    ap = argparse.ArgumentParser(description="教材確定性檢核器")
    ap.add_argument("--root", default="materials")
    ap.add_argument("--contract", default="skill/color-planning/COURSE-CONTRACT.yaml")
    args = ap.parse_args(argv)

    dirs, files, violations = audit(args.root, args.contract)
    print(f"教材目錄: {args.root}")
    print(f"週次目錄: {len(dirs)} ｜ Markdown 檔: {files}")

    if violations:
        print(f"\n違規 {len(violations)} 項：")
        for v in violations:
            print(f"  {v}")
        return 1
    print("\n全部通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
