#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_no_student_data.py — 學生資料與機密外洩防線

【存在理由】
本 repo 會被 Claude Code、Codex 與 GitHub Actions 讀取，
一旦學生個資或雜湊鹽值進入版本控制，即使事後刪除，git history 仍保留。
本檢查在 CI 中執行，任一項命中即讓 PR 無法合併。

用法：
  python3 tools/validation/check_no_student_data.py           # 檢查已追蹤檔案
  python3 tools/validation/check_no_student_data.py --staged  # pre-commit 用
"""

import re
import sys
import subprocess
import argparse

# 允許存在的路徑（範本、schema 定義、說明文件本身）
# 全式錨定：規則文件位於 repo 根目錄，路徑無前導斜線；
# 且錨定可避免 MY-CONTEXT.md 這類檔名藉由後綴比對繞過檢查。
ALLOWLIST_PATH = re.compile(
    r'^(?:tools/validation/check_no_student_data\.py'
    r'|.*\.example\.(?:json|csv|ya?ml)'
    r'|(?:.*/)?(?:README|CONTEXT|CLAUDE|AGENTS|PROMPTS)\.md)$'
)

PATTERNS = [
    # 個資
    (r'\b[A-Z][12]\d{8}\b',              "疑似身分證字號"),
    (r'\b[A-Za-z]\d{7,9}\b(?=.*學號)',    "疑似學號"),
    (r'\b09\d{2}-?\d{3}-?\d{3}\b',        "疑似手機號碼"),
    (r'[\w.+-]+@(?!example\.|test\.)[\w-]+\.(?:edu|com|org|net)\.?\w*',
                                          "疑似真實 email"),
    # 機密
    (r'sk-[A-Za-z0-9_-]{20,}',            "疑似 OpenAI API key"),
    (r'sk-ant-[A-Za-z0-9_-]{20,}',        "疑似 Anthropic API key"),
    (r'gh[pousr]_[A-Za-z0-9]{30,}',       "疑似 GitHub token"),
    (r'(?i)(salt|鹽值)\s*[:=]\s*["\'][^"\']{8,}',
                                          "疑似雜湊鹽值明文"),
    # 研究資料
    (r'"student_hash"\s*:\s*"sha256:[0-9a-f]{64}"',
                                          "含真實 student_hash 的研究資料"),
    (r'(?i)(知情同意書|informed[_ ]consent).*(簽署|signed).*\b\d{4}-\d{2}-\d{2}',
                                          "疑似已簽署之同意書內容"),
]

BLOCKED_EXT = ('.xlsx', '.xls', '.sav', '.dta', '.db', '.sqlite', '.pdf')


def tracked_files(staged: bool):
    cmd = (["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
           if staged else ["git", "ls-files"])
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    return [f for f in out.splitlines() if f.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", action="store_true")
    args = ap.parse_args()

    findings = []
    for path in tracked_files(args.staged):
        if ALLOWLIST_PATH.search(path):
            continue

        if path.lower().endswith(BLOCKED_EXT):
            findings.append((path, 0, f"禁止的檔案類型（{path.rsplit('.',1)[-1]}）"
                                      "：資料檔不得進入 repo"))
            continue

        try:
            with open(path, encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue

        for i, line in enumerate(lines, 1):
            for pat, label in PATTERNS:
                if re.search(pat, line):
                    findings.append((path, i, label))

    if findings:
        print("=" * 68)
        print("學生資料／機密外洩檢查：未通過")
        print("=" * 68)
        for path, ln, label in findings:
            loc = f"{path}:{ln}" if ln else path
            print(f"  [BLOCK] {loc}\n          {label}")
        print("=" * 68)
        print("處理方式：")
        print("  1. 移除該內容，改用 *.example.json 範本（欄位保留、值改為假資料）")
        print("  2. 真實資料放在 repo 之外的加密位置，路徑寫進 CONTEXT.md 但值不進 repo")
        print("  3. 若已 commit 並 push，僅刪除檔案不夠——git history 仍保留，需重寫歷史")
        return 1

    print("學生資料／機密外洩檢查：通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
