"""
decomposition/dataset_builder.py — KD dataset builder (interface only).

⛔ Phase 8 — Gate G2 is closed (decisions.md D51/D52) but Q6 (AraT5 vs
mT5-base) is still OPEN. Building the corpus involves tokenization, which
is model-dependent — the real builder cannot be written until Q6 closes
and `configs/decomposition.yaml`'s `model.selected` placeholder
("TBD_pending_Q6") is replaced with a concrete decision.
"""

from __future__ import annotations

from pathlib import Path

from interview_iq.decomposition.types import AnnotationRules, KDExample


def build_kd_dataset(
    corpus_path: Path,
    annotation_rules: AnnotationRules,
) -> list[KDExample]:
    """Build the Knowledge-Distillation training corpus from the
    human-reviewed decomposition exercises
    (results/o9_decomposition_exercises.md), enforcing the four locked
    annotation rules.

    Not implemented: blocked on Q6 (see module docstring).
    """
    raise NotImplementedError(
        "decomposition.dataset_builder.build_kd_dataset: blocked on Q6 "
        "(AraT5 vs mT5-base — decisions.md) — Phase 8 skeleton only, no "
        "model-dependent logic implemented yet."
    )
