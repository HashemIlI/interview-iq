"""
scripts/select_o9_sample.py — O9 stratified sample draw (D50).

Draws the 21 remaining questions for the O9 annotation-guide pilot sample,
completing the 25-question stratified set pre-registered in decisions.md D50
(5 questions per track: DA/DS/CS/SE/GN). Four questions were already
completed manually before D50 was registered (DA-001, DA-002, DS-010,
DS-011) and are excluded from the random draw pool -- they count toward
the 25 but are not re-selected.

Randomness: uses the standard-library `random` module, not numpy. This is
a one-off selection over small lists (<= 47 items per track pool) with no
numeric/array work involved, so numpy would be an unjustified dependency
for what random.sample() already does. Python's random module uses the
Mersenne Twister seeded deterministically from an integer (D50: seed=
20260711) -- identical inputs and CPython version reproduce the same draw
every time.

Run once, per D50's pre-registered method (no difficulty criterion, no
manual curation):
    python scripts/select_o9_sample.py
"""

from __future__ import annotations

import datetime
import json
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

QUESTIONS_PATH = REPO_ROOT / "data" / "questions" / "questions_250.json"
OUTPUT_PATH = REPO_ROOT / "results" / "o9_sample_selection.json"

SEED = 20260711

ALREADY_COMPLETED = ["DA-001", "DA-002", "DS-010", "DS-011"]

DRAW_COUNTS = {
    "DA": 3,
    "DS": 3,
    "CS": 5,
    "SE": 5,
    "GN": 5,
}


def _track_of(question_id: str) -> str:
    return question_id.split("-")[0]


def main() -> int:
    with QUESTIONS_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    all_ids = [q["question_id"] for q in data["questions"]]

    already_completed_set = set(ALREADY_COMPLETED)
    missing = already_completed_set - set(all_ids)
    if missing:
        raise RuntimeError(f"Already-completed question IDs not found in {QUESTIONS_PATH}: {sorted(missing)}")

    pool_by_track: dict[str, list[str]] = {track: [] for track in DRAW_COUNTS}
    for qid in all_ids:
        track = _track_of(qid)
        if qid in already_completed_set:
            continue
        if track in pool_by_track:
            pool_by_track[track].append(qid)

    for track, count in DRAW_COUNTS.items():
        available = len(pool_by_track[track])
        if available < count:
            raise RuntimeError(
                f"Track {track}: need {count} questions but only {available} available in the draw "
                f"pool (after excluding already-completed IDs)."
            )

    random.seed(SEED)

    drawn_by_track: dict[str, list[str]] = {}
    for track, count in DRAW_COUNTS.items():
        drawn_by_track[track] = sorted(random.sample(pool_by_track[track], count))

    final_sample_by_track: dict[str, list[str]] = {}
    for track in DRAW_COUNTS:
        completed_in_track = sorted(qid for qid in already_completed_set if _track_of(qid) == track)
        final_sample_by_track[track] = completed_in_track + drawn_by_track[track]

    all_selected = [qid for track in DRAW_COUNTS for qid in final_sample_by_track[track]]

    print("[select_o9_sample] O9 stratified sample (D50) -- 25 questions total\n")
    for track in DRAW_COUNTS:
        print(f"  {track} ({len(final_sample_by_track[track])}):")
        for qid in final_sample_by_track[track]:
            tag = " (already completed)" if qid in already_completed_set else ""
            print(f"    {qid}{tag}")
    print(f"\n  TOTAL: {len(all_selected)}")

    result = {
        "metadata": {
            "decision_ref": "D50",
            "seed": SEED,
            "rng_library": "random (Python standard library)",
            "execution_date": datetime.date.today().isoformat(),
            "already_completed": ALREADY_COMPLETED,
            "draw_counts": DRAW_COUNTS,
            "total_sample_size": len(all_selected),
        },
        "sample_by_track": final_sample_by_track,
        "sample_all": all_selected,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"\n[select_o9_sample] Wrote: {OUTPUT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
