"""
tests/test_q6_pilot_extraction.py — scripts/q6_pilot_decomposition.py extraction test.

Exercises ONLY the markdown-parsing / extraction path (`--extract-only`
CLI mode), invoked as a subprocess exactly like it is really run — no
model, no network, no HuggingFace download. Confirms extract_answers()
pulls the correct raw candidate-answer text for the five D53 pilot
question IDs out of the real results/o9_decomposition_exercises.md file.

Run with:  pytest tests/test_q6_pilot_extraction.py -v
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "scripts" / "q6_pilot_decomposition.py"

EXPECTED_QUESTION_IDS = ["DA-029", "DS-030", "CS-039", "SE-013", "GN-004"]

# Short, exact substrings copied from results/o9_decomposition_exercises.md's
# answer paragraphs for each pilot question — used to confirm the extracted
# text is the real answer, not a wrong section (e.g. the Claims list).
EXPECTED_SUBSTRINGS = {
    "DA-029": "الـ p-value بصراحة دي حاجة دايمًا بتلخبطني",
    "DS-030": "XGBoostده أنا استخدمته في مشروع",
    "CS-039": "الـ Sandbox من الاسم، صندوق الرمل بتاع الأطفال",
    "SE-013": "SQL يعني جداول",
    "GN-004": "الـ CPU هي المخ بتاع الجهاز",
}


def test_extract_only_pulls_correct_raw_answers(tmp_path: Path) -> None:
    output_path = tmp_path / "extracted.json"

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--extract-only", str(output_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert output_path.exists()

    with output_path.open(encoding="utf-8") as fh:
        extracted = json.load(fh)

    assert [item["question_id"] for item in extracted] == EXPECTED_QUESTION_IDS

    by_id = {item["question_id"]: item["raw_answer"] for item in extracted}
    for qid, substring in EXPECTED_SUBSTRINGS.items():
        assert substring in by_id[qid], f"{qid}: expected substring not found in extracted answer"

    # Reference claims / review notes must never leak into the extracted answer.
    for qid, answer in by_id.items():
        assert "الـ Claims" not in answer, f"{qid}: Claims section leaked into raw_answer"
        assert "⚠️" not in answer, f"{qid}: review annotation marker leaked into raw_answer"
