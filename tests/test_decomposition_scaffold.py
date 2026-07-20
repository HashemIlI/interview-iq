"""
tests/test_decomposition_scaffold.py — remaining inference scaffold smoke test.

Confirms the remaining inference interface stub raises NotImplementedError.
Dataset and trainer behavior is covered by test_decomposition_dataset.py.

Run with:  pytest tests/test_decomposition_scaffold.py -v
"""

from __future__ import annotations

import pytest

from interview_iq.decomposition.inference import decompose


def test_decompose_not_implemented():
    with pytest.raises(NotImplementedError):
        decompose("...")
