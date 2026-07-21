"""
decomposition_llm/ — Claim Decomposition via external LLM API (D74 pivot).

decisions.md D74 replaces the AraT5-base fine-tuning approach (archived under
archive/phase8_arat5_superseded/) with an external LLM API call for this
module only. Zero-LLM-at-runtime remains in force for the rest of the
pipeline (NLI, BGE-M3, ASR) — see D74 scope.

Status: scaffold only.
  - system_prompt.md   the D74-supplied system prompt (real content, not a
                        placeholder)
  - client.py          empty function signature — no API call implemented
                        yet

Not wired into configs/decomposition.yaml or any production path yet. The
mandatory D74 sanity gate (verifying the LLM preserves candidate errors
rather than correcting them) has not been implemented or run.
"""

from __future__ import annotations

from interview_iq.decomposition_llm.client import LLMDecompositionError, decompose_via_llm

__all__ = ["decompose_via_llm", "LLMDecompositionError"]
