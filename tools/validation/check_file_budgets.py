#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_file_budgets.py — 檔案長度上限的執行者 v1.0

【存在理由】
CONTEXT.md 第一段自己寫著「上限 150 行。超過就是有東西該搬去別處」，
但沒有任何東西在數。2026-09-06 這一輪，它被超過三次，三次都是人工發現的：
補一段裁示 +3、Codex 補設備原則 +2、我補問卷與授權分離 +1。
每一次都靠當下有人想起來去數，而不是靠 CI。

這正是 CLAUDE.md 那條規則的形態：規則寫了，沒人執行，於是它慢慢失效。
上限的意義不在數字，在於它強迫「這件事該不該進 CONTEXT.md」被問出來——
沒有執行者，這個問題就不會被問。

【檢什麼】
B1  受管制檔案的行數不得超過其上限
B2  上限值必須寫在該檔案自己的文字裡，且與本檔宣告的一致
    —— 避免上限被改在程式裡而檔案自己還宣稱另一個數字

【純標準函式庫，零相依】

用法: python3 tools/validation/check_file_budgets.py
離開碼: 0 = 通過；1 = 超過上限；2 = 解析不到宣告
"""

import argparse
import os
import re
import sys

# path -> (上限行數, 用來在檔案內文找出同一個數字的正則)
BUDGETS = {
    "CONTEXT.md": (150, re.compile(r"上限\s*(\d+)\s*行")),
}


class V:
    def __init__(self, code, path, msg):
        self.code, self.path, self.msg = code, path, msg

    def __str__(self):
        return f"{self.path}: [{self.code}] {self.msg}"


def count_lines(text):
    """以「換行數」計，與 wc -l 一致；結尾無換行的最後一行仍計入。"""
    if text == "":
        return 0
    n = text.count("\n")
    return n if text.endswith("\n") else n + 1


def audit(root="."):
    v = []
    for rel, (limit, declared_re) in sorted(BUDGETS.items()):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            v.append(V("E-BUDGET-PARSE", rel, "受管制檔案不存在"))
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        n = count_lines(text)

        # B2 —— 檔案自己宣告的上限必須與本檔一致
        m = declared_re.search(text)
        if not m:
            v.append(V("E-BUDGET-PARSE", rel,
                       f"檔案內文找不到上限宣告（預期形如「上限 {limit} 行」）"))
        elif int(m.group(1)) != limit:
            v.append(V("E-BUDGET-DECLARE", rel,
                       f"檔案內文宣告上限 {m.group(1)} 行，但本檢核器設為 {limit} 行；"
                       f"兩處必須同時改"))

        # B1 —— 行數上限
        if n > limit:
            v.append(V("E-BUDGET-LINES", rel,
                       f"{n} 行，超過上限 {limit} 行 {n - limit} 行。"
                       f"上限不是排版問題——超過表示有東西該搬去契約或別處"))
    return v


def main(argv=None):
    ap = argparse.ArgumentParser(description="檔案長度上限檢核")
    ap.add_argument("--root", default=".")
    args = ap.parse_args(argv)

    violations = audit(args.root)
    for rel, (limit, _re) in sorted(BUDGETS.items()):
        path = os.path.join(args.root, rel)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                print(f"{rel}: {count_lines(f.read())} / {limit} 行")

    if any(x.code == "E-BUDGET-PARSE" for x in violations):
        for x in violations:
            print(f"  {x}")
        return 2
    if violations:
        print(f"\n違規 {len(violations)} 項：")
        for x in violations:
            print(f"  {x}")
        return 1
    print("\n檔案長度上限：通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
