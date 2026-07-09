"""
tests/test_config.py — Smoke tests for the Phase 2 Config loader.

All tests run on CPU with no model downloads.
Run with:  pytest tests/test_config.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from interview_iq.config import Config, PRE_CALIBRATION_TAG

# Point tests at the real configs/ directory
CONFIGS_DIR = Path(__file__).parent.parent / "configs"


@pytest.fixture(scope="module")
def cfg() -> Config:
    """Shared Config instance (loads once per module — suppresses duplicate stdout)."""
    return Config(configs_dir=CONFIGS_DIR)


# ── construction ───────────────────────────────────────────────────────────────

def test_config_loads(cfg: Config) -> None:
    """Config must be constructed without raising."""
    assert cfg is not None


def test_repr(cfg: Config) -> None:
    """repr must mention configs_dir."""
    assert "configs_dir" in repr(cfg)


# ── pre-calibration defaults ───────────────────────────────────────────────────

def test_tau_default(cfg: Config) -> None:
    assert cfg.tau == 0.5, "τ pre-calibration default must be 0.5"


def test_tau_e_default(cfg: Config) -> None:
    assert cfg.tau_e == 0.9, "τ_E pre-calibration default must be 0.9"


def test_alpha_default(cfg: Config) -> None:
    assert cfg.alpha == 0.0, "α pre-calibration default must be 0.0"


def test_k_default(cfg: Config) -> None:
    assert cfg.k == 10, "k pre-calibration default must be 10"


# ── types ──────────────────────────────────────────────────────────────────────

def test_tau_is_float(cfg: Config) -> None:
    assert isinstance(cfg.tau, float)


def test_tau_e_is_float(cfg: Config) -> None:
    assert isinstance(cfg.tau_e, float)


def test_alpha_is_float(cfg: Config) -> None:
    assert isinstance(cfg.alpha, float)


def test_k_is_int(cfg: Config) -> None:
    assert isinstance(cfg.k, int)


# ── model names ───────────────────────────────────────────────────────────────

def test_nli_model_non_empty(cfg: Config) -> None:
    assert cfg.nli_model, "nli_model must be a non-empty string"


def test_embedding_model_non_empty(cfg: Config) -> None:
    assert cfg.embedding_model, "embedding_model must be a non-empty string"


def test_asr_model_non_empty(cfg: Config) -> None:
    assert cfg.asr_model, "asr_model must be a non-empty string"


def test_nli_model_is_mdeberta(cfg: Config) -> None:
    assert "mDeBERTa" in cfg.nli_model or "deberta" in cfg.nli_model.lower()


def test_embedding_model_is_bge(cfg: Config) -> None:
    assert "bge" in cfg.embedding_model.lower()


# ── sub-config properties ─────────────────────────────────────────────────────

@pytest.mark.parametrize("attr", [
    "asr", "decomposition", "retrieval", "nli_finetune", "scoring", "calibration"
])
def test_sub_config_is_dict(cfg: Config, attr: str) -> None:
    value = getattr(cfg, attr)
    assert isinstance(value, dict), f"cfg.{attr} must return a dict"


def test_sub_config_not_empty(cfg: Config) -> None:
    for attr in ("asr", "retrieval", "nli_finetune", "scoring", "calibration"):
        assert getattr(cfg, attr), f"cfg.{attr} must not be empty"


# ── YAML structure sanity checks ──────────────────────────────────────────────

def test_scoring_has_thresholds(cfg: Config) -> None:
    assert "thresholds" in cfg.scoring


def test_scoring_has_channels(cfg: Config) -> None:
    assert "channels" in cfg.scoring


def test_scoring_has_decision_rule(cfg: Config) -> None:
    assert cfg.scoring.get("decision_rule") == "v2_entailment_priority"


def test_retrieval_has_top_k(cfg: Config) -> None:
    assert "top_k" in cfg.retrieval


def test_retrieval_k_under_top_k(cfg: Config) -> None:
    assert cfg.retrieval["top_k"]["k"] == 10


def test_nli_finetune_lora_r(cfg: Config) -> None:
    assert cfg.nli_finetune["lora"]["r"] == 16


def test_nli_finetune_lora_alpha(cfg: Config) -> None:
    assert cfg.nli_finetune["lora"]["lora_alpha"] == 32


def test_nli_finetune_target_modules(cfg: Config) -> None:
    mods = cfg.nli_finetune["lora"]["target_modules"]
    assert "query_proj" in mods and "value_proj" in mods


def test_nli_finetune_excluded_question_ids(cfg: Config) -> None:
    """D28 — DS-014 must always be in the excluded list."""
    excluded = cfg.nli_finetune["data"]["excluded_question_ids"]
    assert "DS-014" in excluded


def test_calibration_has_current_defaults(cfg: Config) -> None:
    defaults = cfg.calibration["current_defaults"]
    assert defaults["tau"] == 0.5
    assert defaults["tau_e"] == 0.9
    assert defaults["alpha"] == 0.0
    assert defaults["k"] == 10


# ── PRE-CALIBRATION tag printed on load ───────────────────────────────────────

def test_pre_calibration_tag_in_stdout(capsys: pytest.CaptureFixture) -> None:
    """Every Config instantiation must print the PRE-CALIBRATION tag."""
    Config(configs_dir=CONFIGS_DIR)
    captured = capsys.readouterr()
    assert PRE_CALIBRATION_TAG in captured.out


def test_pre_calibration_all_four_params_in_stdout(capsys: pytest.CaptureFixture) -> None:
    """All four param labels must appear in the stdout announcement."""
    Config(configs_dir=CONFIGS_DIR)
    captured = capsys.readouterr()
    for label_fragment in ("τ", "τ_E", "α", "k"):
        assert label_fragment in captured.out, (
            f"Pre-calibration announcement missing label fragment: {label_fragment!r}"
        )


# ── custom configs_dir override ───────────────────────────────────────────────

def test_configs_dir_override(tmp_path: Path) -> None:
    """Passing a non-existent dir must raise FileNotFoundError (not silently fail)."""
    missing = tmp_path / "nonexistent_configs"
    with pytest.raises((FileNotFoundError, OSError)):
        Config(configs_dir=missing)
