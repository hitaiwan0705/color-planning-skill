#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_scope_floor.py — 涵蓋範圍下限的確定性檢核 v1.0

【存在理由】
`COURSE-CONTRACT.yaml` 的 global_rules.scope_floor 規定：
「涵蓋範圍不得窄於 iPAS 初級三科」。

這條規則寫在契約裡，但在 2026-09-06 之前**沒有任何工具在執行它**。
當時是靠授課者提供官方簡章 PDF、人工逐條比對 42 條評鑑細目，才發現 14 條
未涵蓋或整項排在考後。下一次沒有人提供 PDF，就不會有人發現。

有規則而沒有執行者，等於沒有規則。本檔補上那個執行者。

【檢什麼】
R1  每條評鑑細目的 covered_in 不得為空
R2  沒有任何細目的 status 為 not_covered 或 post_exam
R3  status 必須屬於契約允許的字彙
R4  severity 為 blocking 的缺口必須有 status（不得懸而未決卻無標記）
R5  verdict 必須與資料一致——這條抓的是「改了資料忘了改判定」與
    「改了判定卻沒改資料」兩種相反的失誤
R6  gaps[].items 引用的細目必須存在於 official_syllabus

【純標準函式庫，零相依】contract 為 YAML，但本檔以正則解析固定格式，
不引入 pyyaml——CI 的 python 環境沒有安裝任何第三方套件。

用法:
  python3 tools/validation/check_scope_floor.py
  python3 tools/validation/check_scope_floor.py --contract <path>

離開碼: 0 = 通過；1 = 違規；2 = 找不到契約或解析不到資料
"""

import argparse
import os
import re
import sys

CONTRACT_DEFAULT = "skill/color-planning/COURSE-CONTRACT.yaml"

# 例：          L11101_認識色彩: {covered_in: [W02 客座①], status: guest_only}
ITEM_RE = re.compile(
    r"^\s*(?P<code>L\d{5})_(?P<name>[^:]+): \{covered_in: \[(?P<cov>[^\]]*)\], status: (?P<status>\w+)\}\s*$"
)
# verdict 的值含連字號（E-SCOPE_TRIGGERED），字元類必須包含 "-"。
# 早期版本寫成 [A-Z_]+，解析不到觸發狀態的判定 —— 由 R5 的反向測試抓到。
VERDICT_RE = re.compile(r"^\s{6}verdict: (?P<verdict>[A-Z_-]+)\s*$")
GAP_ID_RE = re.compile(r"^\s*- id: (?P<gid>GAP-\d+)\s*$")
GAP_FIELD_RE = re.compile(r"^\s+(?P<key>status|severity|items): (?P<val>.+?)\s*$")

ALLOWED_STATUS = {
    "covered",           # 已排入且有實作或完整講授
    "covered_concept",   # 概念層已排入
    "partial",           # 部分涵蓋
    "partial_post_exam", # 部分涵蓋且部分排在考後
    "guest_only",        # 僅由客座承擔
    "self_study",        # 交付自習清單
    "not_covered",       # 完全未涵蓋 —— 違反 scope_floor
    "post_exam",         # 整項排在考後 —— 違反考前涵蓋
}
VIOLATING_STATUS = {"not_covered", "post_exam"}

VERDICT_TRIGGERED = "E-SCOPE_TRIGGERED"


class V:
    def __init__(self, code, line, msg):
        self.code, self.line, self.msg = code, line, msg

    def __str__(self):
        return f"line {self.line}: [{self.code}] {self.msg}"


def parse(text):
    """回傳 (items, verdict, verdict_line, gaps)。"""
    items, gaps = [], []
    verdict, verdict_line = None, 0
    cur = None

    for i, raw in enumerate(text.split("\n"), 1):
        m = ITEM_RE.match(raw)
        if m:
            cov = [c.strip() for c in m.group("cov").split(",") if c.strip()]
            items.append({
                "code": m.group("code"),
                "name": m.group("name"),
                "covered_in": cov,
                "status": m.group("status"),
                "line": i,
            })
            continue

        m = VERDICT_RE.match(raw)
        if m and verdict is None:
            verdict, verdict_line = m.group("verdict"), i
            continue

        m = GAP_ID_RE.match(raw)
        if m:
            cur = {"id": m.group("gid"), "line": i, "status": None,
                   "severity": None, "items": []}
            gaps.append(cur)
            continue

        if cur is not None:
            m = GAP_FIELD_RE.match(raw)
            if m:
                key, val = m.group("key"), m.group("val")
                if key == "items":
                    cur["items"] = [x.strip() for x in
                                    val.strip("[]").split(",") if x.strip()]
                else:
                    cur[key] = val
            elif raw.strip() and not raw.startswith(" " * 10):
                cur = None

    return items, verdict, verdict_line, gaps


def audit(text):
    items, verdict, verdict_line, gaps = parse(text)
    v = []

    if not items:
        return items, verdict, gaps, [V("E-SCOPE-PARSE", 1,
                                        "解析不到任何評鑑細目；official_syllabus 的格式可能已改變")]

    known = {it["code"] for it in items}

    for it in items:
        # R3 —— 先驗 status，不合法時後續判斷沒有意義
        if it["status"] not in ALLOWED_STATUS:
            v.append(V("E-SCOPE-STATUS", it["line"],
                       f"{it['code']} 的 status {it['status']!r} 不在契約允許的字彙中"))
            continue
        # R1
        if not it["covered_in"]:
            v.append(V("E-SCOPE-EMPTY", it["line"],
                       f"{it['code']} 的 covered_in 為空，無法查核它在哪一週被涵蓋"))
        # R2
        if it["status"] in VIOLATING_STATUS:
            v.append(V("E-SCOPE-FLOOR", it["line"],
                       f"{it['code']}（{it['name']}）status={it['status']}，"
                       f"違反 global_rules.scope_floor"))

    # R4 / R6
    for g in gaps:
        if g["severity"] == "blocking" and not g["status"]:
            v.append(V("E-SCOPE-GAP", g["line"],
                       f"{g['id']} 的 severity 為 blocking 但沒有 status，"
                       f"無法判斷它是已補救還是仍懸而未決"))
        for code in g["items"]:
            if code not in known:
                v.append(V("E-SCOPE-XREF", g["line"],
                           f"{g['id']} 引用的 {code} 不存在於 official_syllabus"))

    # R5 —— 判定與資料必須一致，兩個方向都要抓
    breaches = [it for it in items if it["status"] in VIOLATING_STATUS]
    if breaches and verdict != VERDICT_TRIGGERED:
        v.append(V("E-SCOPE-VERDICT", verdict_line or 1,
                   f"有 {len(breaches)} 條細目違反 scope_floor，"
                   f"但 verdict 是 {verdict!r} 而非 {VERDICT_TRIGGERED}"))
    if not breaches and verdict == VERDICT_TRIGGERED:
        v.append(V("E-SCOPE-VERDICT", verdict_line or 1,
                   f"沒有任何細目違反 scope_floor，但 verdict 仍是 {VERDICT_TRIGGERED}；"
                   f"判定未隨資料更新"))

    v.sort(key=lambda x: (x.line, x.code))
    return items, verdict, gaps, v


def main(argv=None):
    ap = argparse.ArgumentParser(description="涵蓋範圍下限檢核")
    ap.add_argument("--contract", default=CONTRACT_DEFAULT)
    args = ap.parse_args(argv)

    if not os.path.isfile(args.contract):
        print(f"找不到契約檔: {args.contract}", file=sys.stderr)
        return 2

    with open(args.contract, encoding="utf-8") as f:
        text = f.read()

    items, verdict, gaps, violations = audit(text)

    if any(x.code == "E-SCOPE-PARSE" for x in violations):
        for x in violations:
            print(f"  {x}")
        return 2

    counts = {}
    for it in items:
        counts[it["status"]] = counts.get(it["status"], 0) + 1

    print(f"契約: {args.contract}")
    print(f"評鑑細目: {len(items)} 條｜缺口: {len(gaps)} 項｜判定: {verdict}")
    for s in sorted(counts):
        mark = "  ← 違反 scope_floor" if s in VIOLATING_STATUS else ""
        print(f"  {s}: {counts[s]}{mark}")

    if violations:
        print(f"\n違規 {len(violations)} 項：")
        for x in violations:
            print(f"  {x}")
        return 1

    print("\n涵蓋範圍下限：通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
