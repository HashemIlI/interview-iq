"""
D88 diagnostic (decisions.md D88): reproduces the two-arm (zero-shot vs
adapter) full Precision-channel NLI matrices for SE-028 and GN-040.

The committed results/pipeline_demo/precision_matrix_two_arms.json was
produced by the ad-hoc Kaggle equivalent of this script on 2026-07-23. This
file is the repo-canonical version per the thin-runner rule (logic lives in
the repo, not in ad-hoc notebook cells).

Claims are FROZEN as hardcoded constants below, copied verbatim from the
"claims" arrays in results/pipeline_demo/SE-028.json and
results/pipeline_demo/GN-040.json -- this script does not call the LLM and
does not re-decompose anything, so the NLI arm is the only variable under
test. Reuses build_pretrained_model_and_tokenizer + load_adapter
(evaluation/gold_eval.py), build_claims_chunks_matrix (nli/engine.py),
load_reference_docs (refdocs/loader.py), and Config -- zero reimplementation.

Usage:
    python scripts/diag_precision_two_arms.py --adapter-path /path/to/iq-checkpoints-nli-v1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_REFERENCE_DOCS_PATH = _REPO_ROOT / "data" / "refdocs" / "reference_docs_250_FINAL_v1.json"
_DEFAULT_OUTPUT_PATH = _REPO_ROOT / "results" / "pipeline_demo" / "precision_matrix_two_arms.json"

sys.path.insert(0, str(_REPO_ROOT / "src"))

from interview_iq.config import Config  # noqa: E402
from interview_iq.evaluation.gold_eval import build_pretrained_model_and_tokenizer, load_adapter  # noqa: E402
from interview_iq.nli.engine import ClaimsChunksMatrix, build_claims_chunks_matrix  # noqa: E402
from interview_iq.refdocs.loader import load_reference_docs  # noqa: E402

# Frozen claims -- copied verbatim from the "claims" arrays in
# results/pipeline_demo/SE-028.json and results/pipeline_demo/GN-040.json.
SE_028_CLAIMS: list[str] = [
    "تكتب التست الأول قبل كتابة الكود نفسه الذي سيحقق التست.",
    "تتابع دورة قصيرة تُسمى دورة التطوير، حيث تكتب التست أولاً.",
    "التست يفشل في البداية لأن الكود لا يزال غير موجود.",
    "تكتب أقل كود ممكن لجعل التست ينجح.",
    "تحسن وتنضف الكود دون تغيير سلوكه.",
    "تكرر الدورة مرة أخرى.",
]

GN_040_CLAIMS: list[str] = [
    "البيت هو أصغر وحدة معلومات في الحاسب.",
    "البيت يأخذ قيمة إما 0 أو 1.",
    "الـ Byte هو مجموعة من 8 بت، وليس 16 بت.",
    "الـ Byte هو الوحدة الأساسية التي تقاس بها حجم البيانات.",
    "الـ Byte هو الوحدة الأساسية التي تقاس بها عنونة الذاكرة.",
]

QUESTIONS: dict[str, list[str]] = {
    "SE-028": SE_028_CLAIMS,
    "GN-040": GN_040_CLAIMS,
}


def _matrix_to_json(matrix: ClaimsChunksMatrix) -> dict[str, Any]:
    return {
        "chunk_ids": list(matrix.chunk_ids),
        "claims": list(matrix.claims),
        "matrix": [[dict(cell) for cell in row] for row in matrix.matrix],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "D88: reproduce the two-arm (zero-shot vs adapter) full Precision-channel "
            "NLI matrices for SE-028 and GN-040, on frozen claims."
        )
    )
    parser.add_argument("--adapter-path", type=Path, required=True)
    parser.add_argument("--reference-docs-path", type=Path, default=_DEFAULT_REFERENCE_DOCS_PATH)
    parser.add_argument("--output-path", type=Path, default=_DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    cfg = Config()
    print(f"[D88] NLI base model: {cfg.nli_model}")
    print(f"[D88] Loading reference docs: {args.reference_docs_path}")
    refdocs = load_reference_docs(args.reference_docs_path)

    print("[D88] Building zero-shot arm model (no adapter)...")
    zero_shot_model, tokenizer = build_pretrained_model_and_tokenizer(cfg.nli_model)
    print("[D88] Building adapter arm base model...")
    adapter_base_model, _ = build_pretrained_model_and_tokenizer(cfg.nli_model)
    adapter_model = load_adapter(adapter_base_model, args.adapter_path)
    print(f"[D88] Loaded adapter: {args.adapter_path}")

    output: dict[str, Any] = {"zero_shot": {}, "adapter": {}}
    arms = (
        ("zero_shot", zero_shot_model),
        ("adapter", adapter_model),
    )
    for arm_name, model in arms:
        for question_id, claims in QUESTIONS.items():
            document = refdocs.get_document(question_id)
            if document is None:
                raise ValueError(f"question_id {question_id!r} not found in {args.reference_docs_path}")
            print(f"[D88] {arm_name} / {question_id}: {len(claims)} claims x {len(document.chunks)} chunks")
            matrix = build_claims_chunks_matrix(model, tokenizer, claims=claims, chunks=list(document.chunks))
            output[arm_name][question_id] = _matrix_to_json(matrix)

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[D88] Output written to: {args.output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
