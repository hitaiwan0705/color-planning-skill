#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_check_contract.py — check_contract.py 的驗證套件

【設計原則】只會 PASS 的測試沒有價值。
每條規則都有負向驗證：植入對應違規，確認抓得到且錯誤碼正確。

本檔的夾具刻意在區塊中夾雜**註解行**。理由：check_contract.py 的兩個 parser bug
都是被註解觸發的——一個讓 CAP-07／08 整批漏掉，一個讓學期配分規則從未生效。
註解是這份契約的常態，測試夾具就必須長成那樣。

執行：python3 -m unittest discover -s tools/validation/tests -v
"""

import importlib.util
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_SCRIPT = os.path.join(_REPO, "tools", "validation", "check_contract.py")
_spec = importlib.util.spec_from_file_location("check_contract", _SCRIPT)
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)

GOOD = """capability_contract:
  capabilities:
    # ── 前半週次的能力 ──
    - id: CAP-01
      layer: 1
      input_evidence: 指定色票、觀察條件紀錄
      observable_behavior: 標出色適應可能改變判讀的位置
      deliverable: 色彩知覺風險表
      validation_rule: 每一筆風險須連到截圖座標
      failure_condition: 缺任一交付物即未通過
    # ── 後半週次新增之能力 ──
    - id: CAP-02
      layer: 4
      input_evidence: i1 Pro 量測檔
      observable_behavior: 在指定光源下量測樣本
      deliverable: ΔE00 報告
      validation_rule: 數值須追溯至量測檔
      failure_condition: 缺原始量測檔即未通過

task_contract:
  equipment_gate:
    confirmed:
      - i1_pro_2
      - light_booth_d50_d65  # D50 與 D65 皆具備
    unverified:
      - judge_qc_fluorescent_lamp
  tasks:
    - id: TASK-01
      capability_refs: [CAP-01]
      equipment_required: []
    # ── 後半新增之任務 ──
    - id: TASK-02
      capability_refs: [CAP-02]
      equipment_required: [i1_pro_2, light_booth_d50_d65]

assignment_contract:
  # ── 交件事件層：分數與截止日掛在 ASSIGN，不掛在 TASK ──
  max_submission_events: 2
  assignments:
    - id: ASSIGN-01
      title: 色彩知覺風險盤點
      task_refs: [TASK-01]
      issue_week: 1
      due_week: 2
      grade_slot: 平時
      weight: 40
      rubric_profile: R-A
    # ── 期末 ──
    - id: ASSIGN-02
      title: 量測與驗證
      task_refs: [TASK-02]
      issue_week: 2
      due_week: 3
      grade_slot: 期末
      weight: 60
      rubric_profile: R-A

weekly_plan:
  weeks:
    - week: 1
      issue: [ASSIGN-01]
      due: []
      equipment_required: []
    - week: 2
      issue: [ASSIGN-02]
      due: [ASSIGN-01]
      equipment_required: [light_booth_d50_d65]
    - week: 3
      issue: []
      due: [ASSIGN-02]
      equipment_required: []

assessment_contract:
  rubric_dimensions:
    profiles:
      - id: R-A
        applies_to: [TASK-01]
        dimensions:
          - {name: 可追溯性, weight: 50}
          - {name: 規格符合度, weight: 50}
    semester_weighting:
      # 授課者裁定的成績欄位配分
      平時: 40
      期末: 60
      total: 100
      source_map:
        # 子區塊不得中止掃描，也不得被誤收為配分
        平時: ASSIGN-01
        期末: ASSIGN-02

evidence_contract:
  required_artifacts:
    per_task:
      - task_id: TASK-01
        artifacts: [風險表]
      - task_id: TASK-02
        artifacts: [量測檔]
"""


def codes(text):
    *_, vs = cc.audit(text)
    return [v.code for v in vs]


class TestPositive(unittest.TestCase):
    def test_good_contract_passes(self):
        self.assertEqual(codes(GOOD), [])

    def test_comments_do_not_truncate_blocks(self):
        """註解行不得截斷區塊——兩個 parser bug 都由此而來。"""
        caps, tasks, _n, _vs = cc.audit(GOOD)
        self.assertEqual([c["id"] for c in caps], ["CAP-01", "CAP-02"])
        self.assertEqual([t["id"] for t in tasks], ["TASK-01", "TASK-02"])

    def test_real_contract_passes(self):
        p = os.path.join(_REPO, "skill", "color-planning", "COURSE-CONTRACT.yaml")
        if not os.path.isfile(p):
            self.skipTest("契約檔不存在")
        with open(p, encoding="utf-8") as f:
            caps, tasks, n, vs = cc.audit(f.read())
        self.assertGreaterEqual(len(caps), 8)
        self.assertGreaterEqual(len(tasks), 8)
        self.assertGreaterEqual(n, 1)
        self.assertEqual([str(x) for x in vs], [])


class TestNegativeC1(unittest.TestCase):
    """C1 五段式欄位與 id／layer"""

    def test_missing_deliverable_fails(self):
        bad = GOOD.replace("      deliverable: 色彩知覺風險表\n", "")
        self.assertIn("E-CONTRACT-FIVE", codes(bad))

    def test_every_required_field_is_checked(self):
        """逐欄驗證：清單漏掉任何一欄，本測試就 FAIL。"""
        for f in cc.CAP_FIELDS:
            with self.subTest(field=f):
                bad = GOOD
                for line in GOOD.split("\n"):
                    if line.strip().startswith(f + ": "):
                        bad = GOOD.replace(line + "\n", "", 1)
                        break
                self.assertNotEqual(bad, GOOD, f"夾具裡找不到 {f!r} 欄位")
                self.assertIn("E-CONTRACT-FIVE", codes(bad), f"漏掉 {f!r}")

    def test_layer_out_of_range_fails(self):
        bad = GOOD.replace("      layer: 1", "      layer: 9")
        self.assertIn("E-CONTRACT-LAYER", codes(bad))


class TestNegativeC2(unittest.TestCase):
    """C2 判準欄位不得用抽象能力動詞"""

    def test_abstract_verb_fails(self):
        bad = GOOD.replace("observable_behavior: 標出色適應可能改變判讀的位置",
                           "observable_behavior: 學生能整合觀察與量測")
        self.assertIn("E-CONTRACT-VERB", codes(bad))

    def test_every_listed_verb_is_detected(self):
        for verb in cc.ABSTRACT_VERBS:
            with self.subTest(verb=verb):
                bad = GOOD.replace("deliverable: 色彩知覺風險表",
                                   f"deliverable: 能{verb}的成果")
                self.assertIn("E-CONTRACT-VERB", codes(bad), f"漏掉 {verb!r}")

    def test_verb_outside_judgement_fields_is_allowed(self):
        """input_evidence 不是判準欄位，出現這些詞不算違規。"""
        ok = GOOD.replace("input_evidence: 指定色票、觀察條件紀錄",
                          "input_evidence: 學生整合後的色票清單")
        self.assertNotIn("E-CONTRACT-VERB", codes(ok))


class TestNegativeC3(unittest.TestCase):
    def test_dangling_capability_ref_fails(self):
        bad = GOOD.replace("capability_refs: [CAP-01]", "capability_refs: [CAP-99]")
        self.assertIn("E-CONTRACT-REF", codes(bad))


class TestNegativeC4(unittest.TestCase):
    """C4 設備閘門"""

    def test_unconfirmed_equipment_in_task_fails(self):
        bad = GOOD.replace("equipment_required: [i1_pro_2, light_booth_d50_d65]",
                           "equipment_required: [i1_pro_2, judge_qc_fluorescent_lamp]")
        self.assertIn("E-CONTRACT-EQUIP", codes(bad))

    def test_unconfirmed_equipment_in_week_fails(self):
        bad = GOOD.replace("      equipment_required: [light_booth_d50_d65]",
                           "      equipment_required: [judge_qc_fluorescent_lamp]")
        self.assertIn("E-CONTRACT-EQUIP", codes(bad))

    def test_inline_comment_in_confirmed_list_is_parsed(self):
        """confirmed 條目帶行內註解時仍須被認得，否則整批合法設備被誤報。"""
        self.assertNotIn("E-CONTRACT-EQUIP", codes(GOOD))


class TestNegativeC5(unittest.TestCase):
    """C5 權重"""

    def test_profile_weights_not_100_fails(self):
        bad = GOOD.replace("{name: 規格符合度, weight: 50}",
                           "{name: 規格符合度, weight: 40}")
        self.assertIn("E-CONTRACT-WEIGHT", codes(bad))

    def test_semester_weighting_mismatch_fails(self):
        """區塊第一行是註解時仍須生效——早期版本在此完全失效。"""
        bad = GOOD.replace("      平時: 40", "      平時: 50")
        self.assertIn("E-CONTRACT-WEIGHT", codes(bad))

    def test_nested_block_does_not_stop_the_scan(self):
        """source_map 這類子區塊只能被略過，不能中止掃描。

        若掃描在子區塊處中止，total 之後若還有配分鍵就永遠讀不到；
        本測試把 total 移到最後，確認前面的鍵仍被收齊。
        """
        moved = GOOD.replace("      total: 100\n", "")
        moved = moved.replace("        期末: ASSIGN-02\n",
                              "        期末: ASSIGN-02\n      total: 100\n")
        self.assertNotIn("E-CONTRACT-WEIGHT", codes(moved))
        bad = moved.replace("      平時: 40", "      平時: 50")
        self.assertIn("E-CONTRACT-WEIGHT", codes(bad))


class TestNegativeC6(unittest.TestCase):
    """C6 週次的 issue／due 指向存在的 ASSIGN"""

    def test_week_due_dangling_assignment_fails(self):
        bad = GOOD.replace("      due: [ASSIGN-01]", "      due: [ASSIGN-99]")
        self.assertIn("E-CONTRACT-WEEK", codes(bad))

    def test_week_pointing_at_a_task_now_fails(self):
        """D6 之後週次不得再直接指向 TASK——TASK 只剩證據規格，沒有截止日。"""
        bad = GOOD.replace("      due: [ASSIGN-01]", "      due: [TASK-01]")
        self.assertIn("E-CONTRACT-WEEK", codes(bad))


class TestNegativeC8(unittest.TestCase):
    """C8 ASSIGN 欄位齊全、task_refs 有效"""

    def test_every_required_field_is_checked(self):
        for f in cc.ASSIGN_FIELDS:
            with self.subTest(field=f):
                bad, hit = GOOD, False
                for line in GOOD.split("\n"):
                    if line.strip().startswith(f + ": "):
                        bad = GOOD.replace(line + "\n", "", 1)
                        hit = True
                        break
                self.assertTrue(hit, f"夾具裡找不到 {f!r} 欄位")
                self.assertIn("E-CONTRACT-ASSIGN", codes(bad), f"漏掉 {f!r}")

    def test_dangling_task_ref_fails(self):
        bad = GOOD.replace("      task_refs: [TASK-01]", "      task_refs: [TASK-99]")
        self.assertIn("E-CONTRACT-ASSIGN", codes(bad))

    def test_comment_between_assignments_does_not_truncate(self):
        """夾具在兩份作業之間放了註解行；若被截斷，ASSIGN-02 會整條消失。"""
        _caps, _tasks, n, _vs = cc.audit(GOOD)
        self.assertEqual(n, 2)


class TestNegativeC9(unittest.TestCase):
    """C9 宣告週次與 weekly_plan 雙向一致"""

    def test_declared_week_mismatch_fails(self):
        bad = GOOD.replace("      issue_week: 1", "      issue_week: 2")
        self.assertIn("E-CONTRACT-ASSIGN", codes(bad))

    def test_assignment_never_issued_fails(self):
        """只宣告不排週次，等於學生永遠拿不到題目。"""
        bad = GOOD.replace("      issue: [ASSIGN-01]", "      issue: []")
        self.assertIn("E-CONTRACT-ASSIGN", codes(bad))

    def test_assignment_collected_twice_fails(self):
        bad = GOOD.replace("      due: [ASSIGN-02]", "      due: [ASSIGN-02, ASSIGN-01]")
        self.assertIn("E-CONTRACT-ASSIGN", codes(bad))


class TestNegativeC10(unittest.TestCase):
    """C10 交件事件數上限（授課者裁示 D6）"""

    def test_exceeding_the_cap_fails(self):
        bad = GOOD.replace("  max_submission_events: 2", "  max_submission_events: 1")
        self.assertIn("E-CONTRACT-ASSIGN", codes(bad))

    def test_cap_is_read_from_the_contract_not_hardcoded(self):
        """上限是授課者的裁示，改契約就該改行為；寫死在程式裡會讓裁示失效。"""
        ok = GOOD.replace("  max_submission_events: 2", "  max_submission_events: 9")
        self.assertNotIn("E-CONTRACT-ASSIGN", codes(ok))

    def test_missing_cap_is_a_parse_error(self):
        bad = GOOD.replace("  max_submission_events: 2\n", "")
        self.assertIn("E-CONTRACT-PARSE", codes(bad))


class TestNegativeC11(unittest.TestCase):
    """C11 作業權重合計等於學期配分"""

    def test_slot_weight_mismatch_fails(self):
        bad = GOOD.replace("      weight: 40", "      weight: 30")
        self.assertIn("E-CONTRACT-ASSIGN", codes(bad))

    def test_unknown_grade_slot_fails(self):
        bad = GOOD.replace("      grade_slot: 平時", "      grade_slot: 期中")
        self.assertIn("E-CONTRACT-ASSIGN", codes(bad))


class TestNegativeC7(unittest.TestCase):
    def test_task_without_per_task_evidence_fails(self):
        bad = GOOD.replace("      - task_id: TASK-02\n        artifacts: [量測檔]\n", "")
        self.assertIn("E-CONTRACT-EVIDENCE", codes(bad))


class TestNegativeParse(unittest.TestCase):
    def test_unparseable_reports_error_not_success(self):
        self.assertIn("E-CONTRACT-PARSE", codes("capability_contract: {}\n"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
