#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_check_file_budgets.py — check_file_budgets.py 的驗證套件

【設計原則】只會 PASS 的測試沒有價值。
每條規則都有負向驗證：植入對應違規，確認抓得到且錯誤碼正確。

本檔特別驗「剛好等於上限」與「超過一行」兩個邊界。上限檢核最容易寫成
差一錯誤（>= 寫成 >），而差一錯誤在正向測試裡永遠看不出來。

執行：python3 -m unittest discover -s tools/validation/tests -v
"""

import importlib.util
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_SCRIPT = os.path.join(_REPO, "tools", "validation", "check_file_budgets.py")
_spec = importlib.util.spec_from_file_location("check_file_budgets", _SCRIPT)
fb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fb)

LIMIT = fb.BUDGETS["CONTEXT.md"][0]


def make(n_lines, declared=LIMIT):
    """造一份剛好 n_lines 行、內文宣告 declared 行上限的 CONTEXT.md。"""
    head = ["# CONTEXT.md", f"上限 {declared} 行。超過就是有東西該搬去別處。"]
    body = [f"- 第 {i} 條已定案事實" for i in range(len(head) + 1, n_lines + 1)]
    return "\n".join((head + body)[:n_lines]) + "\n"


def codes(text):
    root = tempfile.mkdtemp(prefix="budget_")
    try:
        with open(os.path.join(root, "CONTEXT.md"), "w", encoding="utf-8") as f:
            f.write(text)
        return [v.code for v in fb.audit(root)]
    finally:
        shutil.rmtree(root, ignore_errors=True)


class TestPositive(unittest.TestCase):
    def test_exactly_at_the_limit_passes(self):
        """剛好等於上限不是違規——差一錯誤會讓這條 FAIL。"""
        self.assertEqual(codes(make(LIMIT)), [])

    def test_well_under_the_limit_passes(self):
        self.assertEqual(codes(make(20)), [])

    def test_real_context_passes(self):
        p = os.path.join(_REPO, "CONTEXT.md")
        if not os.path.isfile(p):
            self.skipTest("CONTEXT.md 不存在")
        self.assertEqual([str(v) for v in fb.audit(_REPO)], [])


class TestNegativeB1(unittest.TestCase):
    """B1 行數上限"""

    def test_one_line_over_fails(self):
        """超過一行就要抓到。實際發生的每一次都只超過 1–3 行。"""
        self.assertIn("E-BUDGET-LINES", codes(make(LIMIT + 1)))

    def test_far_over_fails(self):
        self.assertIn("E-BUDGET-LINES", codes(make(LIMIT + 40)))


class TestNegativeB2(unittest.TestCase):
    """B2 檔案自己宣告的上限必須與檢核器一致"""

    def test_declared_limit_mismatch_fails(self):
        """把檔案裡的數字改大來「通過」，是這條規則最可能被規避的方式。"""
        self.assertIn("E-BUDGET-DECLARE", codes(make(20, declared=LIMIT + 50)))

    def test_missing_declaration_is_a_parse_error(self):
        bad = make(20).replace(f"上限 {LIMIT} 行。", "")
        self.assertIn("E-BUDGET-PARSE", codes(bad))

    def test_missing_file_is_a_parse_error(self):
        root = tempfile.mkdtemp(prefix="budget_")
        try:
            self.assertIn("E-BUDGET-PARSE", [v.code for v in fb.audit(root)])
        finally:
            shutil.rmtree(root, ignore_errors=True)


class TestLineCounting(unittest.TestCase):
    """行數必須與 wc -l 一致，否則邊界判定會偏一行。"""

    def test_counting_matches_wc_l(self):
        self.assertEqual(fb.count_lines(""), 0)
        self.assertEqual(fb.count_lines("a\n"), 1)
        self.assertEqual(fb.count_lines("a\nb\n"), 2)
        self.assertEqual(fb.count_lines("a\nb"), 2)   # 結尾無換行仍計入


if __name__ == "__main__":
    unittest.main(verbosity=2)
