"""
tests/test_chunk_cap.py — Phase 6 retrieval-cap smoke tests.

Verifies the n_chunks <= k short-circuit path (no embedder ever
constructed) and the n_chunks > k ranking path (with a fake, fully-offline
embedder — never BgeM3Embedder, so no FlagEmbedding import or model
download is ever triggered).

Run with:  pytest tests/test_chunk_cap.py -v
"""

from __future__ import annotations

from interview_iq.refdocs.loader import Chunk
from interview_iq.retrieval.chunk_cap import ChunkCapResult, select_top_k_chunks


class _ExplodingEmbedder:
    """If select_top_k_chunks ever calls .encode() on the n_chunks<=k path,
    this makes the test fail loudly instead of silently doing extra work."""

    def encode(self, texts):  # noqa: ANN001 - test double
        raise AssertionError("encode() must not be called when n_chunks <= k")


class _FakeEmbedder:
    """Deterministic 1-D 'embedding': encodes each text as [len(text)], so
    similarity ranking is fully predictable without any real model."""

    def encode(self, texts):  # noqa: ANN001 - test double
        return [[float(len(t))] for t in texts]


def _chunks(n: int) -> list[Chunk]:
    return [Chunk(chunk_id=f"C{i:02d}", text="x" * (i + 1)) for i in range(n)]


def test_n_chunks_le_k_short_circuits_without_embedder() -> None:
    chunks = _chunks(5)
    result = select_top_k_chunks("claim", chunks, k=10, embedder=_ExplodingEmbedder())
    assert isinstance(result, ChunkCapResult)
    assert result.capped is False
    assert [c.chunk_id for c in result.chunks] == [c.chunk_id for c in chunks]


def test_n_chunks_equal_to_k_short_circuits_too() -> None:
    chunks = _chunks(10)
    result = select_top_k_chunks("claim", chunks, k=10, embedder=_ExplodingEmbedder())
    assert result.capped is False
    assert len(result.chunks) == 10


def test_n_chunks_gt_k_ranks_and_truncates() -> None:
    # Mechanical contract: exactly k chunks returned, all drawn from the
    # original set, no duplicates, capped=True. (See the test below for a
    # case where the fake embedder's geometry lets similarity ranking
    # itself be asserted.)
    chunks = _chunks(12)  # matches the real corpus's observed max (D42)
    result = select_top_k_chunks("claim", chunks, k=10, embedder=_FakeEmbedder())
    assert result.capped is True
    assert len(result.chunks) == 10
    original_ids = {c.chunk_id for c in chunks}
    assert {c.chunk_id for c in result.chunks} <= original_ids
    assert len({c.chunk_id for c in result.chunks}) == 10  # no duplicates


def test_n_chunks_gt_k_prefers_closer_cosine_similarity() -> None:
    # 2-D fake embedder lets cosine similarity actually discriminate: claim
    # points along +x; chunks at increasing angles away from +x should rank
    # in that order.
    class _AngledEmbedder:
        def encode(self, texts):  # noqa: ANN001
            vectors = {
                "claim": [1.0, 0.0],
                "same-direction": [2.0, 0.0],
                "slightly-off": [1.0, 0.3],
                "orthogonal": [0.0, 1.0],
                "opposite": [-1.0, 0.0],
            }
            return [vectors[t] for t in texts]

    chunks = [
        Chunk(chunk_id="OPPOSITE", text="opposite"),
        Chunk(chunk_id="ORTHOGONAL", text="orthogonal"),
        Chunk(chunk_id="SLIGHT", text="slightly-off"),
        Chunk(chunk_id="SAME", text="same-direction"),
    ]
    # k=2, but n_chunks(4) > k so ranking must run (force via extra padding chunks).
    padded = chunks + [Chunk(chunk_id=f"PAD{i}", text="orthogonal") for i in range(3)]
    result = select_top_k_chunks("claim", padded, k=2, embedder=_AngledEmbedder())
    assert result.capped is True
    top_ids = [c.chunk_id for c in result.chunks]
    assert top_ids[0] == "SAME"
    assert top_ids[1] == "SLIGHT"
