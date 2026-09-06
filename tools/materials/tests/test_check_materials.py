#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_check_materials.py — check_materials.py 的驗證套件

【設計原則】只會 PASS 的測試沒有價值。
每一條規則都有負向驗證：植入對應錯誤，確認該規則會抓到且錯誤碼正確。
規則被誤刪或寫壞時，對應測試必須 FAIL。

執行：python3 -m unittest discover -s tools/materials/tests -v
"""

import importlib.util
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_SCRIPT = os.path.join(_REPO, "tools", "materials", "scripts", "check_materials.py")
_spec = importlib.util.spec_from_file_location("check_materials", _SCRIPT)
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)

CONTRACT = """weekly_plan:
  weeks:
    - week: 1
      title: 測試週
      issue: [ASSIGN-01]
      due: []
"""

GOOD_LECTURE = """# W01 測試週｜講義

<!-- 交件事件: issue=[ASSIGN-01] due=[] -->

## 這一週在解什麼問題

一段敘述。這裡可以自由使用理解、應用、整合這些詞，因為不是判準。

## 本週交付

- 交出觀察條件紀錄，含光源、背景與觀察距離三欄
- 交出色票清單，每筆附來源檔名

## 失敗條件

- 缺任一欄位即未通過
- 以口頭描述代替數值紀錄即未通過
"""


class Fixture:
    def __init__(self, lecture=GOOD_LECTURE, contract=CONTRACT, dirname="W01_測試週", extra=None):
        self.root = tempfile.mkdtemp(prefix="mat_")
        self.materials = os.path.join(self.root, "materials")
        wk = os.path.join(self.materials, dirname)
        os.makedirs(wk)
        if lecture is not None:
            with open(os.path.join(wk, "講義.md"), "w", encoding="utf-8") as f:
                f.write(lecture)
        if extra:
            for fn, body in extra.items():
                with open(os.path.join(wk, fn), "w", encoding="utf-8") as f:
                    f.write(body)
        self.contract = os.path.join(self.root, "CONTRACT.yaml")
        with open(self.contract, "w", encoding="utf-8") as f:
            f.write(contract)

    def codes(self):
        _dirs, _files, vs = cm.audit(self.materials, self.contract)
        return [v.code for v in vs]

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def codes(**kw):
    fx = Fixture(**kw)
    try:
        return fx.codes()
    finally:
        fx.cleanup()


class TestPositive(unittest.TestCase):
    """合法輸入不得被誤判，否則負向測試沒有意義。"""

    def test_good_week_passes(self):
        self.assertEqual(codes(), [])

    def test_abstract_verbs_allowed_outside_criteria_sections(self):
        """敘述性內文用『理解／應用／整合』不算違規 —— 只有判準章節禁止。"""
        self.assertNotIn("E-MAT-VERB", codes())

    def test_real_materials_pass(self):
        root = os.path.join(_REPO, "materials")
        contract = os.path.join(_REPO, "skill", "color-planning", "COURSE-CONTRACT.yaml")
        if not os.path.isdir(root) or not os.listdir(root):
            self.skipTest("materials/ 尚未建立")
        _d, _f, vs = cm.audit(root, contract)
        self.assertEqual([str(v) for v in vs], [])


class TestNegativeSections(unittest.TestCase):
    def test_missing_required_section_fails(self):
        bad = GOOD_LECTURE.replace("## 失敗條件", "## 其他")
        self.assertIn("E-MAT-SECTION", codes(lecture=bad))

    def test_missing_lecture_file_fails(self):
        self.assertIn("E-MAT-MISSING", codes(lecture=None))


class TestNegativeVerbs(unittest.TestCase):
    def test_abstract_verb_in_deliverable_section_fails(self):
        bad = GOOD_LECTURE.replace("- 交出觀察條件紀錄，含光源、背景與觀察距離三欄",
                                   "- 學生能整合觀察條件與量測資料")
        self.assertIn("E-MAT-VERB", codes(lecture=bad))

    def test_abstract_verb_in_failure_section_fails(self):
        bad = GOOD_LECTURE.replace("- 缺任一欄位即未通過", "- 未掌握色差概念即未通過")
        self.assertIn("E-MAT-VERB", codes(lecture=bad))

    def test_every_listed_verb_is_detected(self):
        """逐字驗證：清單漏掉任何一個詞，本測試就 FAIL。"""
        for verb in cm.ABSTRACT_VERBS:
            with self.subTest(verb=verb):
                bad = GOOD_LECTURE.replace("- 缺任一欄位即未通過", f"- 未{verb}即未通過")
                self.assertIn("E-MAT-VERB", codes(lecture=bad), f"漏掉 {verb!r}")


class TestNegativeGates(unittest.TestCase):
    def test_mimaki_without_gate_fails(self):
        bad = GOOD_LECTURE + "\n用 Mimaki 輸出一張樣本。\n"
        self.assertIn("E-MAT-GATE", codes(lecture=bad))

    def test_mimaki_with_gate_passes(self):
        ok = GOOD_LECTURE + "\n用 Mimaki 輸出，上限 300 × 420 mm、厚度 50 mm。\n"
        self.assertNotIn("E-MAT-GATE", codes(lecture=ok))

    def test_tl84_without_blocked_fails(self):
        bad = GOOD_LECTURE + "\n在 TL84 下觀察同色異譜。\n"
        self.assertIn("E-MAT-GATE", codes(lecture=bad))

    def test_white_ink_without_blocked_fails(self):
        bad = GOOD_LECTURE + "\n先上一層白墨再印。\n"
        self.assertIn("E-MAT-GATE", codes(lecture=bad))


class TestNegativeNumericClaims(unittest.TestCase):
    def test_delta_e_without_source_fails(self):
        bad = GOOD_LECTURE + "\n這一對的 ΔE00 = 3.2，屬於可接受範圍。\n"
        self.assertIn("E-MAT-CLAIM", codes(lecture=bad))

    def test_delta_e_with_source_passes(self):
        ok = GOOD_LECTURE + "\n這一對的 ΔE00 = 3.2（來源：color_audit.py 輸出）。\n"
        self.assertNotIn("E-MAT-CLAIM", codes(lecture=ok))

    def test_delta_e_inside_code_fence_is_ignored(self):
        ok = GOOD_LECTURE + "\n```\nΔE00 = 3.2\n```\n"
        self.assertNotIn("E-MAT-CLAIM", codes(lecture=ok))


class TestNegativePII(unittest.TestCase):
    """個資夾具在原始碼裡一律拆開組裝。

    整串寫死會讓 tools/validation/check_no_student_data.py 命中本檔——
    負向測試需要那個形狀的字串，但 repo 的外洩防線不該為了測試而放寬。
    由 Codex 於 2026-09-06 的同步中指出。"""

    def test_id_number_fails(self):
        fake_id = "A" + "1234567" + "89"
        bad = GOOD_LECTURE + f"\n範例：{fake_id}\n"
        self.assertIn("E-MAT-PII", codes(lecture=bad))

    def test_student_number_fails(self):
        label = "學" + "號"
        bad = GOOD_LECTURE + f"\n{label}：{'4105' + '4001'}\n"
        self.assertIn("E-MAT-PII", codes(lecture=bad))


class TestNegativeDuplicateWeek(unittest.TestCase):
    """同一週兩個目錄必須被抓出來，而且兩份都要被內容檢查。

    真實事故：2026-09-06 Codex 與 Claude 同時寫 materials/，W08–W18 多週各產生
    兩個目錄。錯誤碼 E-MAT-DUPLICATE 由 Codex 定義，週次目錄改存 list 由 Claude 修
    ——只報「有重複」而不檢查內容，等於換一種漏法。"""

    def test_two_directories_for_one_week_fails(self):
        fx = Fixture()
        try:
            second = os.path.join(fx.materials, "W01_另一個名字")
            os.makedirs(second)
            with open(os.path.join(second, "講義.md"), "w", encoding="utf-8") as f:
                f.write(GOOD_LECTURE)
            self.assertIn("E-MAT-DUPLICATE", fx.codes())
        finally:
            fx.cleanup()

    def test_both_directories_are_still_checked(self):
        """重複不得讓其中一份逃過內容檢查。"""
        fx = Fixture()
        try:
            second = os.path.join(fx.materials, "W01_另一個名字")
            os.makedirs(second)
            with open(os.path.join(second, "講義.md"), "w", encoding="utf-8") as f:
                f.write(GOOD_LECTURE.replace("## 失敗條件", "## 其他"))
            found = fx.codes()
            self.assertIn("E-MAT-DUPLICATE", found)
            self.assertIn("E-MAT-SECTION", found)
        finally:
            fx.cleanup()


class TestNegativeSubmissionDeclaration(unittest.TestCase):
    """交件宣告必須與契約的 weekly_plan 一致。

    這條規則存在的理由：截止日同時寫在契約與 18 份講義裡。
    兩處各自被改，學生看講義、檢核器看契約，沒有人比對兩者。
    """

    def test_missing_declaration_fails(self):
        bad = GOOD_LECTURE.replace("<!-- 交件事件: issue=[ASSIGN-01] due=[] -->\n", "")
        self.assertIn("E-MAT-SUBMIT", codes(lecture=bad))

    def test_declaration_disagreeing_with_contract_fails(self):
        bad = GOOD_LECTURE.replace("issue=[ASSIGN-01]", "issue=[ASSIGN-02]")
        self.assertIn("E-MAT-SUBMIT", codes(lecture=bad))

    def test_declaring_a_due_the_contract_does_not_have_fails(self):
        bad = GOOD_LECTURE.replace("due=[]", "due=[ASSIGN-01]")
        self.assertIn("E-MAT-SUBMIT", codes(lecture=bad))

    def test_contract_side_change_alone_fails(self):
        """反向：只改契約不改講義，也必須抓到——不一致沒有方向之分。"""
        bad_contract = CONTRACT.replace("issue: [ASSIGN-01]", "issue: [ASSIGN-03]")
        self.assertIn("E-MAT-SUBMIT", codes(contract=bad_contract))

    def test_two_declarations_fail(self):
        bad = GOOD_LECTURE.replace(
            "<!-- 交件事件: issue=[ASSIGN-01] due=[] -->",
            "<!-- 交件事件: issue=[ASSIGN-01] due=[] -->\n"
            "<!-- 交件事件: issue=[ASSIGN-01] due=[] -->")
        self.assertIn("E-MAT-SUBMIT", codes(lecture=bad))

    def test_order_within_the_list_does_not_matter(self):
        contract = CONTRACT.replace("issue: [ASSIGN-01]", "issue: [ASSIGN-01, ASSIGN-02]")
        good = GOOD_LECTURE.replace("issue=[ASSIGN-01]", "issue=[ASSIGN-02, ASSIGN-01]")
        self.assertNotIn("E-MAT-SUBMIT", codes(lecture=good, contract=contract))


class TestNegativeWeekCoverage(unittest.TestCase):
    def test_contract_week_without_directory_fails(self):
        c = CONTRACT + "    - week: 2\n      title: 第二週\n"
        self.assertIn("E-MAT-MISSING", codes(contract=c))

    def test_directory_without_contract_week_fails(self):
        self.assertIn("E-MAT-ORPHAN", codes(dirname="W99_不存在的週"))

    def test_duplicate_week_directories_fail(self):
        fx = Fixture()
        try:
            duplicate = os.path.join(fx.materials, "W01_另一份教材")
            os.makedirs(duplicate)
            with open(os.path.join(duplicate, "講義.md"), "w", encoding="utf-8") as f:
                f.write(GOOD_LECTURE)
            self.assertIn("E-MAT-DUPLICATE", fx.codes())
        finally:
            fx.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
