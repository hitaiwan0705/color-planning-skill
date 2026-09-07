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
  meta:
    session_minutes: 120
    self_study_weeks: [17, 18]
  weeks:
    - week: 1
      title: 測試週
      issue: [ASSIGN-01]
      due: []
"""

GOOD_LECTURE = """# W01 測試週｜講義

<!-- 交件事件: issue=[ASSIGN-01] due=[] -->
<!-- 課堂時間: 120 分鐘 -->

## 這一週在解什麼問題

一段敘述。這裡可以自由使用理解、應用、整合這些詞，因為不是判準。

## 本週學習目標

- 標出訊息、媒介與觀看條件

## 知識群與關鍵詞

- 色彩傳播：訊息、媒介、閱聽人

## 課堂活動與時間配置

- 20 分鐘觀察、30 分鐘比較、40 分鐘修正

## 學習證據與評量角色

- 觀察表供形成性回饋，不另計分

## 學習工作量

- 課內 90 分鐘；課外 30 分鐘整理

## 本週交付

- 交出觀察條件紀錄，含光源、背景與觀察距離三欄
- 交出色票清單，每筆附來源檔名

## 失敗條件

- 缺任一欄位即未通過
- 以口頭描述代替數值紀錄即未通過

## 本週重點整理

1. 色彩判斷必須帶觀看條件。
2. 數值須可追溯。
3. 訊息功能須有可觀察判準。

## 下週銜接

下週用同一份觀察表進行跨媒介比較。
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

    def test_every_required_section_is_checked(self):
        for section in cm.REQUIRED_SECTIONS:
            with self.subTest(section=section):
                bad = GOOD_LECTURE.replace(section, "## 被移除的章節", 1)
                self.assertIn("E-MAT-SECTION", codes(lecture=bad))


class TestNegativeStudentFacingInternals(unittest.TestCase):
    def test_every_internal_marker_is_rejected(self):
        for marker in cm.FORBIDDEN_STUDENT_MARKERS:
            with self.subTest(marker=marker):
                bad = GOOD_LECTURE + f"\n教師備註：{marker}\n"
                self.assertIn("E-MAT-INTERNAL", codes(lecture=bad))


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


class TestNegativeSurveyNotGraded(unittest.TestCase):
    """學習問卷自願、不計分——失敗條件不得把未填寫成缺交或扣分。

    這條規則來自一個真的犯過的錯：本 repo 一度在 W18 寫「學習問卷未填 →
    交付物不齊」。把自願問卷綁進成績就是強迫填答，而問卷日後若轉作研究資料，
    這種綁定在倫理上站不住。豁免的寫法是把那種處理本身標為違規。
    """

    def test_survey_as_missing_deliverable_fails(self):
        bad = GOOD_LECTURE.replace("- 缺任一欄位即未通過",
                                   "- 學習問卷未填 → 交付物不齊")
        self.assertIn("E-MAT-SURVEY", codes(lecture=bad))

    def test_survey_as_deduction_fails(self):
        bad = GOOD_LECTURE.replace("- 缺任一欄位即未通過",
                                   "- 未填學習問卷者扣分")
        self.assertIn("E-MAT-SURVEY", codes(lecture=bad))

    def test_inverted_form_is_allowed(self):
        """把「列為缺交」本身標為違規，是正確寫法，不得誤判。"""
        ok = GOOD_LECTURE.replace("- 缺任一欄位即未通過",
                                  "- 將學習問卷未填列為缺交或扣分 → 違反自願、不計分原則")
        self.assertNotIn("E-MAT-SURVEY", codes(lecture=ok))

    def test_survey_mentioned_outside_failure_section_is_allowed(self):
        """只有判準章節受限；內文說明問卷怎麼交不算違規。"""
        ok = GOOD_LECTURE.replace("- 交出色票清單，每筆附來源檔名",
                                  "- 交出色票清單；學習問卷另行自願填答")
        self.assertNotIn("E-MAT-SURVEY", codes(lecture=ok))


class TestNegativeToolLimits(unittest.TestCase):
    """引用決定性工具的講義必須寫出它的限制。

    這條規則來自一次真實的退化：把內部品管數字「7/34」列入學生端禁用字串後，
    18 份講義的工具限制聲明**一起消失了**——禁一個數字，順手把那句誠實話也刪了。
    契約與 SKILL.md 仍寫著「不得宣稱完整驗證」，但學生看的是講義。
    """

    def test_tool_without_limit_statement_fails(self):
        bad = GOOD_LECTURE.replace("- 交出色票清單，每筆附來源檔名",
                                   "- 交出 color_audit.py 的 JSON 輸出檔")
        self.assertIn("E-MAT-TOOLLIMIT", codes(lecture=bad))

    def test_limit_statement_without_the_internal_ratio_passes(self):
        """限制可以不帶內部品管數字——兩條規則不得互相逼死。"""
        ok = GOOD_LECTURE.replace(
            "- 交出色票清單，每筆附來源檔名",
            "- 交出 color_audit.py 的 JSON 輸出檔\n"
            "- 註明：color_audit.py 尚未通過完整參照驗證，不得寫成「已完整驗證」")
        got = codes(lecture=ok)
        self.assertNotIn("E-MAT-TOOLLIMIT", got)
        self.assertNotIn("E-MAT-INTERNAL", got)

    def test_lecture_without_the_tool_is_unaffected(self):
        self.assertNotIn("E-MAT-TOOLLIMIT", codes())


class TestNegativeSessionMinutes(unittest.TestCase):
    """授課時數宣告必須與契約的 session_minutes 一致（V3：2 學分＝每週 2 小時）。

    這條規則的由來：人工核對 16 個授課週時，同一件事有四種寫法
    （純列分鐘、「本週共 120 分鐘：」、「完成 120 分鐘活動：」、表格時間區間），
    要寫四種剖析才驗得出來。結果全部正確——但「驗得出來」不能靠每次都有人手寫剖析器。
    """

    def test_wrong_minutes_fails(self):
        bad = GOOD_LECTURE.replace("課堂時間: 120 分鐘", "課堂時間: 150 分鐘")
        self.assertIn("E-MAT-SESSION", codes(lecture=bad))

    def test_missing_declaration_fails(self):
        bad = GOOD_LECTURE.replace("<!-- 課堂時間: 120 分鐘 -->\n", "")
        self.assertIn("E-MAT-SESSION", codes(lecture=bad))

    def test_contract_side_change_alone_fails(self):
        """只改契約不改講義也要抓到——不一致沒有方向之分。"""
        bad = CONTRACT.replace("session_minutes: 120", "session_minutes: 100")
        self.assertIn("E-MAT-SESSION", codes(contract=bad))

    def test_value_comes_from_the_contract_not_hardcoded(self):
        """時數是授課者的裁示；寫死在程式裡等於讓裁示失效。"""
        contract = CONTRACT.replace("session_minutes: 120", "session_minutes: 90")
        ok = GOOD_LECTURE.replace("課堂時間: 120 分鐘", "課堂時間: 90 分鐘")
        self.assertNotIn("E-MAT-SESSION", codes(lecture=ok, contract=contract))

    def test_self_study_week_must_declare_zero(self):
        """夾具是 week 1；把它列為自主學習週，120 分鐘就該轉紅。"""
        contract = CONTRACT.replace("self_study_weeks: [17, 18]", "self_study_weeks: [1]")
        self.assertIn("E-MAT-SESSION", codes(contract=contract))

    def test_two_declarations_fail(self):
        bad = GOOD_LECTURE.replace("<!-- 課堂時間: 120 分鐘 -->",
                                   "<!-- 課堂時間: 120 分鐘 -->\n<!-- 課堂時間: 120 分鐘 -->")
        self.assertIn("E-MAT-SESSION", codes(lecture=bad))

    def test_missing_contract_key_is_a_parse_error(self):
        bad = CONTRACT.replace("    session_minutes: 120\n", "")
        self.assertIn("E-MAT-PARSE", codes(contract=bad))


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
