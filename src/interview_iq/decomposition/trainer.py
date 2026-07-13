"""
decomposition/trainer.py — Decomposition model trainer (interface only).

⛔ Phase 8 — Gate G2 is closed (decisions.md D51/D52) but Q6 (AraT5 vs
mT5-base) is still OPEN. No tokenizer or model checkpoint may be loaded
here until Q6 is resolved — doing so would hardcode the very decision
this module must not make.
"""

from __future__ import annotations

from pathlib import Path

from interview_iq.decomposition.types import KDExample


def train_decomposition_model(
    examples: list[KDExample],
    output_dir: Path,
) -> None:
    """Train the claim-decomposition model on the KD corpus.

    Not implemented: blocked on Q6 (see module docstring).
    """
    raise NotImplementedError(
        "decomposition.trainer.train_decomposition_model: blocked on Q6 "
        "(AraT5 vs mT5-base — decisions.md) — Phase 8 skeleton only, no "
        "model-dependent logic implemented yet."
    )
