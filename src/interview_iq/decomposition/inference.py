"""
decomposition/inference.py — Decomposition inference (interface only).

⛔ Phase 8 — Gate G2 is closed (decisions.md D51/D52) but Q6 (AraT5 vs
mT5-base) is still OPEN. No tokenizer or model checkpoint may be loaded
here until Q6 is resolved.
"""

from __future__ import annotations

from interview_iq.decomposition.types import DecompositionResult


def decompose(source_text: str) -> DecompositionResult:
    """Decompose a source answer into atomic, self-contained claims,
    enforcing the four locked annotation rules.

    Not implemented: blocked on Q6 (see module docstring).
    """
    raise NotImplementedError(
        "decomposition.inference.decompose: blocked on Q6 "
        "(AraT5 vs mT5-base — decisions.md) — Phase 8 skeleton only, no "
        "model-dependent logic implemented yet."
    )
