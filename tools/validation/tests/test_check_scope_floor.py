#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_check_scope_floor.py — check_scope_floor.py 的驗證套件

【設計原則】只會 PASS 的測試沒有價值。
每條規則都有負向驗證：植入對應錯誤，確認該規則抓得到且錯誤碼正確。

R5（判定與資料一致）特別做**雙向**驗證：
資料壞了判定沒改、判定改了資料沒壞，兩種相反的失誤都要抓到。
只驗一個方向，等於只擋住一半。

執行：python3 -m unittest discover -s tools/validation/tests -v
"""

import importlib.util
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_SCRIPT = os.path.join(_REPO, "tools", "validation", "check_scope_floor.py")
_spec = importlib.util.spec_from_file_location("check_scope_floor", _SCRIPT)
sf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sf)

# 最小可用的契約片段。縮排與真實契約一致，否則正則對不上。
GOOD = """capability_contract:
  ipas_alignment:
    official_syllabus:
      L11_色彩學:
        L111_色彩學基礎知識:
          L11101_認識色彩: {covered_in: [W02 客座①], status: guest_only}
          L11102_色彩視覺原理: {covered_in: [W02 客座①, W14], status: partial}
        L114_配色的基本法則:
          L11401_色調與配色: {covered_in: [W04], status: covered}
    coverage_gap_analysis:
      verdict: REMEDIED_PENDING_RATIFICATION
      gaps:
        - id: GAP-01
          status: remedied_draft
          severity: blocking
          items: [L11401]
          finding: 配色法則未排入
"""


def codes(text):
    _items, _verdict, _gaps, vs = sf.audit(text)
    return [v.code for v in vs]


class TestPositive(unittest.TestCase):
    """合法輸入不得被誤判，否則負向測試沒有意義。"""

    def test_good_contract_passes(self):
        self.assertEqual(codes(GOOD), [])

    def test_parses_all_items(self):
        items, verdict, gaps, _ = sf.audit(GOOD)
        self.assertEqual(len(items), 3)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(verdict, "REMEDIED_PENDING_RATIFICATION")
        self.assertEqual(items[0]["covered_in"], ["W02 客座①"])

    def test_real_contract_passes(self):
        p = os.path.join(_REPO, "skill", "color-planning", "COURSE-CONTRACT.yaml")
        if not os.path.isfile(p):
            self.skipTest("契約檔不存在")
        with open(p, encoding="utf-8") as f:
            items, _v, _g, vs = sf.audit(f.read())
        self.assertGreaterEqual(len(items), 40, "應解析到 40 條以上細目")
        self.assertEqual([str(x) for x in vs], [])


class TestNegativeR1(unittest.TestCase):
    """R1 covered_in 不得為空"""

    def test_empty_covered_in_fails(self):
        bad = GOOD.replace("{covered_in: [W04], status: covered}",
                           "{covered_in: [], status: covered}")
        self.assertIn("E-SCOPE-EMPTY", codes(bad))


class TestNegativeR2(unittest.TestCase):
    """R2 not_covered / post_exam 即違反 scope_floor"""

    def test_not_covered_fails(self):
        bad = GOOD.replace("{covered_in: [W04], status: covered}",
                           "{covered_in: [], status: not_covered}") \
                  .replace("verdict: REMEDIED_PENDING_RATIFICATION",
                           "verdict: E-SCOPE_TRIGGERED")
        self.assertIn("E-SCOPE-FLOOR", codes(bad))

    def test_post_exam_fails(self):
        bad = GOOD.replace("{covered_in: [W04], status: covered}",
                           "{covered_in: [W14], status: post_exam}") \
                  .replace("verdict: REMEDIED_PENDING_RATIFICATION",
                           "verdict: E-SCOPE_TRIGGERED")
        self.assertIn("E-SCOPE-FLOOR", codes(bad))

    def test_every_violating_status_is_detected(self):
        """逐字驗證：清單漏掉任何一個違規狀態，本測試就 FAIL。"""
        for status in sf.VIOLATING_STATUS:
            with self.subTest(status=status):
                bad = GOOD.replace("{covered_in: [W04], status: covered}",
                                   "{covered_in: [W04], status: %s}" % status) \
                          .replace("verdict: REMEDIED_PENDING_RATIFICATION",
                                   "verdict: E-SCOPE_TRIGGERED")
                self.assertIn("E-SCOPE-FLOOR", codes(bad), f"漏掉 {status!r}")


class TestNegativeR3(unittest.TestCase):
    """R3 status 字彙"""

    def test_unknown_status_fails(self):
        bad = GOOD.replace("status: covered}", "status: 應該沒問題吧}")
        self.assertIn("E-SCOPE-STATUS", codes(bad))


class TestNegativeR4(unittest.TestCase):
    """R4 blocking 缺口必須有 status"""

    def test_blocking_gap_without_status_fails(self):
        bad = GOOD.replace("          status: remedied_draft\n", "")
        self.assertIn("E-SCOPE-GAP", codes(bad))

    def test_non_blocking_gap_without_status_passes(self):
        ok = GOOD.replace("          status: remedied_draft\n", "") \
                 .replace("severity: blocking", "severity: minor")
        self.assertNotIn("E-SCOPE-GAP", codes(ok))


class TestNegativeR5(unittest.TestCase):
    """R5 判定與資料一致 —— 兩個方向都要抓。

    只驗一個方向等於只擋住一半：實務上「改了資料忘了改判定」與
    「改了判定卻沒改資料」都發生過。"""

    def test_data_breached_but_verdict_clean_fails(self):
        bad = GOOD.replace("{covered_in: [W04], status: covered}",
                           "{covered_in: [W04], status: post_exam}")
        found = codes(bad)
        self.assertIn("E-SCOPE-VERDICT", found)
        self.assertIn("E-SCOPE-FLOOR", found)

    def test_verdict_triggered_but_data_clean_fails(self):
        bad = GOOD.replace("verdict: REMEDIED_PENDING_RATIFICATION",
                           "verdict: E-SCOPE_TRIGGERED")
        self.assertIn("E-SCOPE-VERDICT", codes(bad))


class TestNegativeR6(unittest.TestCase):
    """R6 缺口引用的細目必須存在"""

    def test_dangling_item_reference_fails(self):
        bad = GOOD.replace("items: [L11401]", "items: [L11401, L99999]")
        self.assertIn("E-SCOPE-XREF", codes(bad))


class TestNegativeParse(unittest.TestCase):
    """格式改變導致解析不到資料時，必須明講，不得靜靜地回報通過。"""

    def test_no_items_reports_parse_error_not_success(self):
        found = codes("capability_contract:\n  ipas_alignment: {}\n")
        self.assertIn("E-SCOPE-PARSE", found)


if __name__ == "__main__":
    unittest.main(verbosity=2)
