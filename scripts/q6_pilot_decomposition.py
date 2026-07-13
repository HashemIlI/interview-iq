"""
scripts/q6_pilot_decomposition.py — Q6 pilot diagnostic runner (decisions.md D53).

Standalone diagnostic measurement tool for the Q6 decision (AraT5 vs
mT5-base). Deliberately independent of the locked
src/interview_iq/decomposition/ package (D52) — that package's stubs
still raise NotImplementedError and are untouched by this script.

Scope, per D53:
  - zero-shot generation only, for BOTH candidate models — no fine-tuning,
    no LoRA.
  - ONE prompt template (PROMPT_TEMPLATE below), used verbatim for both
    models — no per-model wording differences.
  - raw model output saved as-is — no automated scoring, no preference
    logic, no filtering. Evaluation is manual (Ahmed), against the five
    directional criteria in D53.

Intended execution environment: Kaggle T4 (thin runner — git clone +
pip install + `python scripts/q6_pilot_decomposition.py`, no local
logic). Do NOT run `main()` locally: it downloads and loads both
candidate HuggingFace checkpoints. The `--extract-only` mode below is
the only mode safe to run locally/in CI (no network, no model weights).

VRAM / size note (estimated from published model cards — NOT measured on
Kaggle; verify with `nvidia-smi` / actual load before assuming success):
  - UBC-NLP/AraT5-base: ~220M params (T5-base-sized) ≈ 0.9 GB fp32
    weights. Zero-shot generation over 5 short prompts should need only
    a few GB of VRAM total (weights + activations) — comfortable on a
    T4 (16 GB).
  - google/mt5-base: ~580M params (T5-base architecture but a much
    larger ~250k-token multilingual SentencePiece vocab drives most of
    the extra size) ≈ 2.3 GB fp32 weights. Still expected to fit on a
    T4 for zero-shot generation, but the larger embedding matrix and
    vocab make this a firmer assumption than for AraT5-base — if it
    fails, load in fp16 (`torch_dtype=torch.float16`) before concluding
    the pilot can't run.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXERCISES_PATH = REPO_ROOT / "results" / "o9_decomposition_exercises.md"
OUTPUT_DIR = REPO_ROOT / "results" / "q6_pilot"

# D53: named, purposive sample (not random) — the five hardest / most
# error-dense questions in the O9 set.
PILOT_QUESTION_IDS: tuple[str, ...] = ("DA-029", "DS-030", "CS-039", "SE-013", "GN-004")

# Candidate models, in the order specified by D53 (AraT5-base first, then
# mt5-base). Names must match configs/decomposition.yaml candidate_a/candidate_b
# exactly. This hardcoded pair is permitted ONLY in this standalone
# diagnostic script (D53's explicit architectural exception) — it remains
# forbidden inside src/interview_iq/decomposition/ (D52).
CANDIDATES: dict[str, str] = {
    "arat5": "UBC-NLP/AraT5-base",
    "mt5": "google/mt5-base",
}

# Single prompt template — used verbatim for both models, no per-model variants.
PROMPT_TEMPLATE = (
    "فكّك الإجابة العامية التالية إلى claims ذرّية بالفصحى المبسّطة، مع إبقاء "
    "المصطلحات التقنية بحروف لاتينية، ومع الحفاظ على التردد والأخطاء كما "
    "وردت دون تصحيح أو حذف:\n\n{raw_answer}"
)

# Format verified directly against results/o9_decomposition_exercises.md
# (not guessed): a level-3 heading "### <ID>...", then a "**إجابة...:**"
# label line (label text varies, e.g. plain "إجابة:" or "إجابة (لهجة
# مصرية):"), then the answer paragraph, terminated by the next blank line.
_HEADING_RE = re.compile(r"^### (?P<id>[A-Z]{2,3}-\d{3})\b")
_ANSWER_LABEL_RE = re.compile(r"^\*\*إجابة[^*]*:\*\*\s*$")


@dataclass(frozen=True)
class PilotQuestion:
    question_id: str
    raw_answer: str


def extract_answers(
    markdown_path: Path = EXERCISES_PATH,
    question_ids: tuple[str, ...] = PILOT_QUESTION_IDS,
) -> list[PilotQuestion]:
    """Parse results/o9_decomposition_exercises.md and pull out the raw
    candidate-answer paragraph for each requested question ID, in the
    order given by `question_ids`.

    Only the raw answer paragraph is extracted — the human reference
    claims and review notes that follow it are deliberately not read or
    passed anywhere in this script (per D53: no reference-claim leakage
    into the model input).
    """
    text = markdown_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    wanted = set(question_ids)
    found: dict[str, str] = {}

    i = 0
    while i < len(lines):
        heading_match = _HEADING_RE.match(lines[i])
        if heading_match and heading_match.group("id") in wanted:
            qid = heading_match.group("id")
            j = i + 1
            while j < len(lines) and not _ANSWER_LABEL_RE.match(lines[j]):
                j += 1
            if j >= len(lines):
                raise ValueError(f"{qid}: no '**إجابة...:**' label found after heading")
            k = j + 1
            answer_lines: list[str] = []
            while k < len(lines) and lines[k].strip() != "":
                answer_lines.append(lines[k])
                k += 1
            if not answer_lines:
                raise ValueError(f"{qid}: empty answer paragraph")
            found[qid] = "\n".join(answer_lines).strip()
            i = k
        else:
            i += 1

    missing = wanted - found.keys()
    if missing:
        raise ValueError(
            f"extract_answers: missing question IDs in {markdown_path}: {sorted(missing)}"
        )

    return [PilotQuestion(question_id=qid, raw_answer=found[qid]) for qid in question_ids]


def build_prompt(raw_answer: str) -> str:
    return PROMPT_TEMPLATE.format(raw_answer=raw_answer)


def run_pilot(model_name: str, generate_fn) -> list[dict]:
    """Run the zero-shot pilot for one model over the five pilot
    questions. `generate_fn(prompt: str) -> str` is injected by the
    caller — this function contains no model-loading or generation logic
    of its own, only the loop, prompt construction, and raw-output
    capture."""
    questions = extract_answers()
    results = []
    for q in questions:
        prompt = build_prompt(q.raw_answer)
        raw_output = generate_fn(prompt)
        results.append(
            {
                "question_id": q.question_id,
                "raw_answer": q.raw_answer,
                "model_output": raw_output,
                "model_name": model_name,
                "timestamp": None,  # filled in by main() at actual run time
            }
        )
    return results


def _save_results(results: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"saved {len(results)} outputs -> {output_path}")


def main() -> None:  # pragma: no cover - Kaggle-only, downloads real model weights
    """Kaggle T4 entry point: for each candidate model (AraT5-base then
    mt5-base), load it zero-shot (no fine-tuning), generate over the 5
    pilot questions, and write results/q6_pilot/{arat5,mt5}_outputs.json.

    Not exercised by the local test suite — it requires network access
    and ~1-3 GB+ of HuggingFace model downloads. See the module docstring
    for the `--extract-only` mode used for local testing instead.
    """
    import datetime

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    for key, model_name in CANDIDATES.items():
        print(f"[{key}] loading {model_name} (zero-shot, no fine-tuning)...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.eval()

        def generate_fn(prompt: str, _tokenizer=tokenizer, _model=model) -> str:
            inputs = _tokenizer(prompt, return_tensors="pt", truncation=True)
            output_ids = _model.generate(
                **inputs,
                max_new_tokens=256,
                min_new_tokens=5,
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
            )
            return _tokenizer.decode(output_ids[0], skip_special_tokens=True)

        results = run_pilot(model_name=model_name, generate_fn=generate_fn)
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        for r in results:
            r["timestamp"] = timestamp

        output_path = OUTPUT_DIR / f"{key}_outputs.json"
        _save_results(results, output_path)


def _extract_only(output_path: Path) -> None:
    """Debug/test mode: run extract_answers() only, no model involved at
    all. Safe to run locally and in CI."""
    questions = extract_answers()
    payload = [{"question_id": q.question_id, "raw_answer": q.raw_answer} for q in questions]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"extracted {len(payload)} answers -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extract-only",
        metavar="OUTPUT_JSON",
        type=Path,
        default=None,
        help="Only run extract_answers() and write the raw answers to OUTPUT_JSON. "
        "No model is loaded. Safe for local/CI use.",
    )
    args = parser.parse_args()

    if args.extract_only is not None:
        _extract_only(args.extract_only)
    else:
        main()
