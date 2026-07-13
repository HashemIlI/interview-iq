"""
decomposition/types.py — Data structures for the Claim Decomposition module.

⛔ Phase 8 — Gate G2 is closed (decisions.md D51/D52) but Q6 (AraT5 vs
mT5-base) is still OPEN. These are plain, model-agnostic data containers
only — no field here may assume a specific tokenizer, checkpoint, or
model architecture until Q6 is resolved.
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
