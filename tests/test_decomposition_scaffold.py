"""
tests/test_decomposition_scaffold.py — Phase 8 skeleton smoke tests.

Confirms the decomposition/ interface stubs import cleanly and raise
NotImplementedError (not a crash) when called — no model, tokenizer, or
checkpoint is ever touched here. Q6 (AraT5 vs mT5-base) is still OPEN;
these stubs must stay model-agnostic until it closes.

Run with:  pytest tests/test_decomposition_scaffold.py -v
"""

from __future__ import annotations

import pytest

from interview_iq.decomposition.dataset_builder import build_kd_dataset
from interview_iq.decomposition.inference import decompose
from interview_iq.decomposition.trainer import train_decomposition_model
from interview_iq.decomposition.types import AnnotationRules, KDExample


def test_build_kd_dataset_not_implemented(tmp_path):
    rules = AnnotationRules(
        preserve_hedging=True,
        generalise_personal_framing=True,
        no_unverifiable_causal_bridge=True,
        enforce_self_containment=True,
    )
    with pytest.raises(NotImplementedError):
        build_kd_dataset(tmp_path, rules)


def test_train_decomposition_model_not_implemented(tmp_path):
    example = KDExample(question_id="DA-001", source_text="...", claims=["..."])
    with pytest.raises(NotImplementedError):
        train_decomposition_model([example], tmp_path)


def test_decompose_not_implemented():
    with pytest.raises(NotImplementedError):
        decompose("...")
