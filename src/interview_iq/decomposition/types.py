"""
decomposition/types.py — Data structures for the Claim Decomposition module.

⛔ Phase 8 — Gate G2 is closed (decisions.md D51/D52) and Q6 (AraT5 vs
mT5-base) is now resolved: AraT5-base was selected on
linguistic-specialization grounds (decisions.md D54). These remain
plain, model-agnostic data containers — no field here assumes a specific
tokenizer, checkpoint, or model architecture; that belongs to the actual
Phase 8 implementation, not this scaffold.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnnotationRules:
    """The four locked KD annotation rules (configs/decomposition.yaml
    `annotation_rules`; see D50 annotation guide)."""

    preserve_hedging: bool
    generalise_personal_framing: bool
    no_unverifiable_causal_bridge: bool
    enforce_self_containment: bool


@dataclass(frozen=True)
class KDExample:
    """One source-text → decomposed-claims training pair for the KD corpus."""

    question_id: str
    source_text: str
    claims: list[str]


@dataclass(frozen=True)
class DecompositionResult:
    """Output of a single decomposition call."""

    source_text: str
    claims: list[str]
