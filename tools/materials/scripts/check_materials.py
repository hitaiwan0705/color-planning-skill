#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_materials.py — 教材確定性檢核器 v1.0

【存在理由】
教材的錯誤類型是「規格性」的，不是「創造性」的：術語不一致、必備章節缺漏、
抽象能力動詞、設備閘門漏標、數值主張沒有來源、週次與契約不一致、
講義寫的截止日與契約的 weekly_plan 對不起來、把自願問卷寫成必交。
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

# 交件宣告：每份講義必須有一行機器可讀的交件宣告，供本檢核器與契約比對。
# 為什麼要另立一行而不是去讀正文：正文寫「本週收 ASSIGN-03（W10 發放）」時，
# 同一行同時出現「收」與「發放」，靠語序判斷會誤判。宣告行不靠語序。
SUBMISSION_RE = re.compile(
    r"^<!--\s*交件事件:\s*issue=\[(.*?)\]\s*due=\[(.*?)\]\s*-->\s*$")

# 學習問卷是自願、不計分的（授課者裁示 2026-09-06）。
# 「失敗條件」章節若把未填問卷寫成缺交或扣分，就等於把自願問卷變成強迫填答——
# 這正是本 repo 實際發生過的錯誤，由 Codex 抓到。豁免的寫法是把那種處理本身
# 標為違規（「將未填列為缺交 → 違反自願原則」），因此豁免詞只認 違反／不得／自願／不計分。
SURVEY_WORD = "問卷"
SURVEY_PENALTY = ("缺交", "不齊", "扣分")
SURVEY_EXEMPT = ("違反", "不得", "自願", "不計分")

# 個資字樣（第二道防線，主防線在 tools/validation）
PII_PATTERNS = [re.compile(r"\b[A-Z][12]\d{8}\b"), re.compile(r"學號\s*[:：]\s*\S")]


class V:
    def __init__(self, code, path, line, msg):
        self.code, self.path, self.line, self.msg = code, path, line, msg
    def __str__(self):
        return f"{self.path}:{self.line}: [{self.code}] {self.msg}"


def week_dirs(root):
    """回傳 {週次: [目錄, ...]}。

    刻意回傳 list 而非單一路徑：同一週出現兩個目錄是真實會發生的事
    （兩個 agent 同時寫同一週，目錄命名不同）。早期版本用 dict 存單一路徑，
    後寫入的會靜默覆蓋前一個，兩份講義同時存在卻只有一份被檢查。
    2026-09-06 由 Codex 與 Claude 同時寫入 materials/ 時暴露。
    """
    out = {}
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        m = WEEK_DIR_RE.match(name)
        if m and os.path.isdir(os.path.join(root, name)):
            out.setdefault(int(m.group(1)), []).append(os.path.join(root, name))
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


def check_survey_not_graded(path, text):
    """失敗條件章節不得把未填學習問卷寫成缺交或扣分。"""
    v = []
    lines = text.split("\n")
    fenced = fence_mask(lines)
    in_scope = False
    for i, raw in enumerate(lines):
        if raw.startswith("## "):
            in_scope = raw.strip() == "## 失敗條件"
            continue
        if not in_scope or i in fenced:
            continue
        if SURVEY_WORD not in raw:
            continue
        if any(w in raw for w in SURVEY_PENALTY) and not any(w in raw for w in SURVEY_EXEMPT):
            v.append(V("E-MAT-SURVEY", path, i + 1,
                       "失敗條件把未填學習問卷列為缺交或扣分；"
                       "問卷為自願、不計分，綁進成績等於強迫填答"))
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


def parse_contract_submissions(contract_path):
    """抓 weekly_plan 每一週的 issue／due，供講義的交件宣告比對。

    D6 之後交件事件只有四個，而截止日同時寫在契約與 18 份講義裡。
    兩處各自被改，就是這門課最容易發生的不一致——學生看講義，
    檢核器看契約，沒有人比對兩者。這個函式就是那個比對者。
    """
    if not os.path.isfile(contract_path):
        return {}
    text = read(contract_path)
    idx = text.find("weekly_plan:")
    if idx < 0:
        return {}
    out, cur = {}, None
    for raw in text[idx:].split("\n"):
        m = re.match(r"^\s*- week: (\d+)\s*$", raw)
        if m:
            cur = int(m.group(1))
            out[cur] = {"issue": [], "due": []}
            continue
        if cur is None:
            continue
        m2 = re.match(r"^\s+(issue|due): \[(.*)\]\s*$", raw)
        if m2:
            out[cur][m2.group(1)] = [x.strip() for x in m2.group(2).split(",") if x.strip()]
    return out


def check_submission_declaration(path, text, week, contract_sub):
    """講義的交件宣告必須與契約的 weekly_plan 一致。"""
    v = []
    found = None
    for i, raw in enumerate(text.split("\n")):
        m = SUBMISSION_RE.match(raw.strip())
        if m:
            if found is not None:
                v.append(V("E-MAT-SUBMIT", path, i + 1, "同一份講義有兩行交件宣告"))
                return v
            found = ([x.strip() for x in m.group(1).split(",") if x.strip()],
                     [x.strip() for x in m.group(2).split(",") if x.strip()],
                     i + 1)
    if found is None:
        v.append(V("E-MAT-SUBMIT", path, 1,
                   "缺交件宣告行 <!-- 交件事件: issue=[...] due=[...] -->"))
        return v
    issue, due, ln = found
    want = contract_sub.get(week)
    if want is None:
        return v
    for key, got in (("issue", issue), ("due", due)):
        if sorted(got) != sorted(want[key]):
            v.append(V("E-MAT-SUBMIT", path, ln,
                       f"交件宣告的 {key} 為 {got or '[]'}，"
                       f"但契約 week {week} 為 {want[key] or '[]'}"))
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
            v.append(V("E-MAT-ORPHAN", dirs[wk][0], 1,
                       f"materials/ 有 week {wk} 但契約的 weekly_plan 沒有這一週"))
    return v


def audit(root, contract_path):
    dirs = week_dirs(root)
    contract_weeks = parse_contract_weeks(contract_path)
    contract_sub = parse_contract_submissions(contract_path)
    violations = check_week_coverage(root, contract_weeks, dirs)
    for wk, paths in sorted(duplicate_week_dirs(root).items()):
        violations.append(V("E-MAT-DUPLICATE", root, 1,
                            f"week {wk} 有多個教材目錄：{', '.join(paths)}；"
                            f"同一週只能有一份講義，否則學生會拿到兩套說法"))
    files = 0

    for wk in sorted(dirs):
      for d in dirs[wk]:
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
                violations += check_submission_declaration(path, text, wk, contract_sub)
                violations += check_survey_not_graded(path, text)
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
    total_dirs = sum(len(v) for v in dirs.values())
    print(f"週次: {len(dirs)} ｜ 週次目錄: {total_dirs} ｜ Markdown 檔: {files}")

    if violations:
        print(f"\n違規 {len(violations)} 項：")
        for v in violations:
            print(f"  {v}")
        return 1
    print("\n全部通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
