#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_contract.py — 契約自身的內部一致性檢核 v1.0

【存在理由】
2026-09-06 的實測：把五個契約違規植入 COURSE-CONTRACT.yaml，
既有的四道 CI 關卡（外洩掃描、CIEDE2000、涵蓋範圍、教材檢核）**一個都沒抓到**：

  1. TASK 的 capability_refs 指向不存在的 CAP
  2. 週次要求 CONTEXT.md 未確認的設備
  3. rubric 權重合計不是 100
  4. 能力條目缺五段式的任一欄
  5. 能力描述使用抽象動詞

這五項正是每次改契約時用臨時腳本手動驗的東西。臨時腳本不持久、不在 CI，
下一個改契約的人不會跑——這是「規則有執行者但執行者不會自己出現」的形態，
和完全沒有執行者一樣危險。

【檢什麼】
C1  能力條目五段式欄位齊全，且 id 與 layer 合法
C2  能力的判準欄位不得使用抽象能力動詞
C3  TASK 的 capability_refs 指向存在的 CAP
C4  週次與任務的 equipment_required 僅含 equipment_gate.confirmed 項
C5  rubric 每組 profile 權重合計 100；學期配分合計等於宣告的 total
C6  週次的 issue／due 指向存在的 ASSIGN
C7  evidence_contract 的 per_task 覆蓋所有 TASK
C8  ASSIGN 條目欄位齊全，且 task_refs 指向存在的 TASK
C9  ASSIGN 的 issue_week／due_week 與 weekly_plan 的 issue／due 雙向一致，
    且每份作業恰好發一次、收一次
C10 交件事件數不超過 assignment_contract.max_submission_events（授課者裁示 D6）
C11 同一 grade_slot 的 ASSIGN 權重合計等於 semester_weighting 中該欄位的分數

【檢不到、也不該假裝檢得到的】
下列規則作用在 skill 的**執行期輸出**或**學生交件**上，不是 repo 檔案，
CI 無法執行，硬做只會給出虛假的安心：
  - assessment_contract「不得輸出分數、等第或總評語」
  - evidence_contract「required_artifacts 缺一即未通過，不得補償」
  - portability_contract「降級但未輸出聲明」
  - tool_contract「量測紀錄缺必填欄位不得引用」
這些要靠 SKILL.md 的執行指令與人工／跨模型審查，不是靠 CI。

【純標準函式庫，零相依】以正則解析固定格式，不引入 pyyaml。

用法: python3 tools/validation/check_contract.py [--contract PATH]
離開碼: 0 = 通過；1 = 違規；2 = 解析不到資料
"""

import argparse
import os
import re
import sys

CONTRACT_DEFAULT = "skill/color-planning/COURSE-CONTRACT.yaml"

CAP_FIELDS = ("layer", "input_evidence", "observable_behavior",
              "deliverable", "validation_rule", "failure_condition")
CAP_JUDGEMENT_FIELDS = ("observable_behavior", "deliverable",
                        "validation_rule", "failure_condition")
ABSTRACT_VERBS = ["理解", "應用", "整合", "熟悉", "掌握",
                  "understand", "apply", "integrate"]
CAP_ID_RE = re.compile(r"^CAP-\d{2}$")
TASK_ID_RE = re.compile(r"^TASK-\d{2}$")
ASSIGN_FIELDS = ("title", "task_refs", "issue_week", "due_week",
                 "grade_slot", "weight", "rubric_profile")


class V:
    def __init__(self, code, line, msg):
        self.code, self.line, self.msg = code, line, msg

    def __str__(self):
        return f"line {self.line}: [{self.code}] {self.msg}"


def _blocks(lines, id_prefix):
    """抓 `- id: PREFIX-nn` 起始的區塊，回傳 [{id,line,indent,fields:{k:(v,line)}}]。

    以 id 前綴全域掃描，不依賴上層 key。早期版本用「遇到縮排較淺的行就停止」
    來界定區塊，結果被清單中間的註解行（`# ── 後半 9 週新增之能力 ──`）截斷，
    CAP-07／08 與 TASK-07／08 全部漏掉。註解不是區塊結束。
    """
    out, cur = [], None
    for i, raw in enumerate(lines, 1):
        m = re.match(r"^(\s*)- id: (%s-\d+)\s*$" % id_prefix, raw)
        if m:
            cur = {"id": m.group(2), "line": i, "indent": len(m.group(1)), "fields": {}}
            out.append(cur)
            continue
        if cur is None:
            continue
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        if indent <= cur["indent"] and not raw.lstrip().startswith("- "):
            cur = None
            continue
        m = re.match(r"^(\s+)([a-z_]+): (.*)$", raw)
        if m and len(m.group(1)) > cur["indent"]:
            cur["fields"].setdefault(m.group(2), (m.group(3).strip(), i))
    return out


def _list_field(val):
    return [x.strip() for x in val.strip("[]").split(",") if x.strip()]


def audit(text):
    lines = text.split("\n")
    v = []

    caps = _blocks(lines, "CAP")
    tasks = _blocks(lines, "TASK")
    if not caps or not tasks:
        return [], [], 0, [V("E-CONTRACT-PARSE", 1,
                             "解析不到 capabilities 或 tasks；契約格式可能已改變")]

    cap_ids = {c["id"] for c in caps}
    task_ids = {t["id"] for t in tasks}

    # C1 / C2
    for c in caps:
        if not CAP_ID_RE.match(c["id"]):
            v.append(V("E-CONTRACT-ID", c["line"], f"{c['id']} 不符 CAP-nn 格式"))
        for f in CAP_FIELDS:
            if f not in c["fields"] or not c["fields"][f][0]:
                v.append(V("E-CONTRACT-FIVE", c["line"],
                           f"{c['id']} 缺五段式欄位 {f!r}；缺任一段該條能力即無效"))
        layer = c["fields"].get("layer", ("", 0))[0]
        if layer and (not layer.isdigit() or not 1 <= int(layer) <= 6):
            v.append(V("E-CONTRACT-LAYER", c["line"],
                       f"{c['id']} 的 layer {layer!r} 不在 1–6"))
        for f in CAP_JUDGEMENT_FIELDS:
            val, ln = c["fields"].get(f, ("", c["line"]))
            for verb in ABSTRACT_VERBS:
                if verb in val:
                    v.append(V("E-CONTRACT-VERB", ln,
                               f"{c['id']} 的 {f} 使用抽象能力動詞 {verb!r}，"
                               f"須改寫為可觀察行為"))

    # C3
    for t in tasks:
        refs = _list_field(t["fields"].get("capability_refs", ("", t["line"]))[0])
        ln = t["fields"].get("capability_refs", ("", t["line"]))[1]
        if not refs:
            v.append(V("E-CONTRACT-REF", t["line"], f"{t['id']} 沒有 capability_refs"))
        for r in refs:
            if r not in cap_ids:
                v.append(V("E-CONTRACT-REF", ln,
                           f"{t['id']} 的 capability_refs 指向不存在的 {r}"))

    # C4 —— 設備閘門
    confirmed = set()
    m = re.search(r"^    confirmed:\n((?:      - .*\n)+)", text, re.M)
    if m:
        for ln in m.group(1).strip().split("\n"):
            # 條目可能帶行內註解：`- display_profiling_via_i1profiler  # ...`
            item = ln.strip().lstrip("- ").split("#")[0].strip()
            if item:
                confirmed.add(item)
    if not confirmed:
        v.append(V("E-CONTRACT-PARSE", 1, "解析不到 equipment_gate.confirmed"))
    else:
        # 任務與週次都用同一個鍵，逐行檢查一次即可；行號足以定位，不需區分二者
        for i, raw in enumerate(lines, 1):
            m2 = re.match(r"^\s+equipment_required: \[(.*)\]\s*$", raw)
            if m2:
                for e in _list_field("[" + m2.group(1) + "]"):
                    if e not in confirmed:
                        v.append(V("E-CONTRACT-EQUIP", i,
                                   f"equipment_required 含 {e}，不在 equipment_gate.confirmed"))

    # C5 —— rubric 權重
    for m in re.finditer(r"^      - id: (R-\w+)\n(?:.*\n)*?(?=^      - id: |^    \w|\Z)",
                         text, re.M):
        pid, block = m.group(1), m.group(0)
        ws = [int(x) for x in re.findall(r"weight: (\d+)", block)]
        if ws and sum(ws) != 100:
            ln = text[:m.start()].count("\n") + 1
            v.append(V("E-CONTRACT-WEIGHT", ln,
                       f"rubric profile {pid} 權重合計 {sum(ws)}，應為 100"))
    # 逐行掃描而非一次比對整段：區塊內夾雜註解行，
    # 早期版本用 `((?:      \S+: \d+\n)+)` 要求下一行就是數字，
    # 被第一行註解擋掉導致整條規則從未生效——由植入測試第 6 項抓到。
    slot_weights, sw_line = {}, None
    start = None
    for i, raw in enumerate(lines):
        if re.match(r"^    semester_weighting:\s*$", raw):
            start = i
            break
    if start is not None:
        sw_line = start + 1
        total = 0
        # 只收「恰好 6 格縮排」的數字鍵；更深的縮排是子區塊（source_map、undecided），
        # 略過而非中止——早期版本一遇到子區塊就 break，等於把規則的作用範圍
        # 綁在鍵的排列順序上。終止條件改為「回到 4 格以內的鍵」。
        for raw in lines[start + 1:]:
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip())
            if indent <= 4:
                break
            m2 = re.match(r"^      (\S+): (\d+)\s*$", raw)
            if m2:
                if m2.group(1) == "total":
                    total = int(m2.group(2))
                else:
                    slot_weights[m2.group(1)] = int(m2.group(2))
        got = sum(slot_weights.values())
        if total and got != total:
            v.append(V("E-CONTRACT-WEIGHT", sw_line,
                       f"學期配分合計 {got}，但宣告 total 為 {total}"))
    else:
        v.append(V("E-CONTRACT-PARSE", 1, "解析不到 semester_weighting"))

    # ── 作業（交件事件）層 ────────────────────────────────────────
    # 2026-09-06 授課者裁示 D6 之後，分數與截止日掛在 ASSIGN 上，TASK 只剩證據規格。
    # 若不同時檢 ASSIGN，C6 會退化成「檢一組沒人用的 id」。
    assigns = _blocks(lines, "ASSIGN")
    assign_ids = {a["id"] for a in assigns}

    # C6 —— 週次的 issue／due 指向存在的 ASSIGN
    # 同時記下週次帳本，供 C9 反向比對
    weekly = {}   # assign_id -> {"issue": [week...], "due": [week...]}
    cur_week = None
    for i, raw in enumerate(lines, 1):
        mw = re.match(r"^    - week: (\d+)\s*$", raw)
        if mw:
            cur_week = int(mw.group(1))
            continue
        m = re.match(r"^      (issue|due): \[(.*)\]\s*$", raw)
        if m:
            for t in _list_field("[" + m.group(2) + "]"):
                if t not in assign_ids:
                    v.append(V("E-CONTRACT-WEEK", i,
                               f"週次 {m.group(1)} 指向不存在的 {t}"))
                elif cur_week is not None:
                    weekly.setdefault(t, {"issue": [], "due": []})[m.group(1)].append(cur_week)

    if not assigns:
        v.append(V("E-CONTRACT-PARSE", 1, "解析不到 assignment_contract.assignments"))
    else:
        # C8 —— ASSIGN 欄位齊全、task_refs 有效
        for a in assigns:
            for f in ASSIGN_FIELDS:
                if f not in a["fields"] or not a["fields"][f][0]:
                    v.append(V("E-CONTRACT-ASSIGN", a["line"],
                               f"{a['id']} 缺欄位 {f!r}"))
            refs_val, refs_ln = a["fields"].get("task_refs", ("", a["line"]))
            for r in _list_field(refs_val):
                if r not in task_ids:
                    v.append(V("E-CONTRACT-ASSIGN", refs_ln,
                               f"{a['id']} 的 task_refs 指向不存在的 {r}"))

        # C9 —— 宣告的週次與 weekly_plan 雙向一致
        for a in assigns:
            book = weekly.get(a["id"], {"issue": [], "due": []})
            for key, field in (("issue", "issue_week"), ("due", "due_week")):
                declared = a["fields"].get(field, ("", a["line"]))[0]
                got = book[key]
                if len(got) != 1:
                    v.append(V("E-CONTRACT-ASSIGN", a["line"],
                               f"{a['id']} 在 weekly_plan 中 {key} {len(got)} 次，應為 1 次"
                               f"（實際週次 {got or '無'}）"))
                elif declared.isdigit() and int(declared) != got[0]:
                    v.append(V("E-CONTRACT-ASSIGN", a["line"],
                               f"{a['id']} 宣告 {field} 為 {declared}，"
                               f"但 weekly_plan 的 {key} 在 week {got[0]}"))

        # C10 —— 交件事件數上限（授課者裁示 D6，上限值讀自契約而非寫死）
        mcap = re.search(r"^  max_submission_events: (\d+)", text, re.M)
        if not mcap:
            v.append(V("E-CONTRACT-PARSE", 1,
                       "解析不到 assignment_contract.max_submission_events"))
        elif len(assigns) > int(mcap.group(1)):
            v.append(V("E-CONTRACT-ASSIGN", 1,
                       f"交件事件 {len(assigns)} 個，超過上限 {mcap.group(1)}"))

        # C11 —— 每個 grade_slot 的作業權重合計等於學期配分
        by_slot = {}
        for a in assigns:
            slot = a["fields"].get("grade_slot", ("", 0))[0]
            w = a["fields"].get("weight", ("", 0))[0]
            if slot and w.isdigit():
                by_slot.setdefault(slot, 0)
                by_slot[slot] += int(w)
        for slot, got in sorted(by_slot.items()):
            want = slot_weights.get(slot)
            if want is None:
                v.append(V("E-CONTRACT-ASSIGN", sw_line or 1,
                           f"作業使用 grade_slot {slot!r}，但 semester_weighting 沒有這一欄"))
            elif got != want:
                v.append(V("E-CONTRACT-ASSIGN", sw_line or 1,
                           f"grade_slot {slot!r} 的作業權重合計 {got}，"
                           f"但 semester_weighting 為 {want}"))

    # C7 —— per_task 覆蓋
    per = set(re.findall(r"^      - task_id: (TASK-\d+)\s*$", text, re.M))
    if per:
        for t in sorted(task_ids - per):
            v.append(V("E-CONTRACT-EVIDENCE", 1,
                       f"{t} 沒有 evidence_contract.per_task 條目"))

    v.sort(key=lambda x: (x.line, x.code))
    return caps, tasks, len(assigns), v


def main(argv=None):
    ap = argparse.ArgumentParser(description="契約內部一致性檢核")
    ap.add_argument("--contract", default=CONTRACT_DEFAULT)
    args = ap.parse_args(argv)

    if not os.path.isfile(args.contract):
        print(f"找不到契約檔: {args.contract}", file=sys.stderr)
        return 2
    with open(args.contract, encoding="utf-8") as f:
        caps, tasks, n_assign, violations = audit(f.read())

    if any(x.code == "E-CONTRACT-PARSE" for x in violations):
        for x in violations:
            print(f"  {x}")
        return 2

    print(f"契約: {args.contract}")
    print(f"能力: {len(caps)} 條｜任務: {len(tasks)} 項｜交件事件: {n_assign} 個")
    if violations:
        print(f"\n違規 {len(violations)} 項：")
        for x in violations:
            print(f"  {x}")
        return 1
    print("\n契約內部一致性：通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
