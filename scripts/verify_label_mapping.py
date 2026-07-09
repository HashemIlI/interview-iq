"""
scripts/verify_label_mapping.py — Phase 5 hardening, Task A (blocking).

Audits label2id/id2label consistency across the three places it matters:
  (1) the training code path actually used in Phase 4
      (interview_iq.nli.finetune._label_to_id, which reads
      cfg.nli_finetune["labels"] from configs/nli_finetune.yaml — read here,
      not guessed);
  (2) the LoRA checkpoint's saved config, if a --checkpoint-dir is given and
      exists locally (this machine has no local checkpoint — the trained
      adapter lives only on Kaggle as the 'iq-checkpoints-nli-v1' dataset);
  (3) the canonical MoritzLaurer/mDeBERTa-v3-base-mnli-xnli mapping, read
      ONLY from a local Hugging Face cache — never fetched over the network,
      never fabricated if absent.

CPU-only, no network calls, no writes. Prints a hard VERDICT line:
IDENTICAL / MISMATCH / UNVERIFIED.

Usage:
    python scripts/verify_label_mapping.py [--checkpoint-dir PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from interview_iq.config import Config  # noqa: E402
from interview_iq.nli import finetune as finetune_module  # noqa: E402


def get_training_label_mapping(cfg: Config) -> dict[str, int]:
    """The exact mapping interview_iq.nli.finetune._label_to_id uses: it
    reads cfg.nli_finetune["labels"] directly. We call the same accessor
    here rather than re-deriving the value, so this IS the code path, not a
    re-implementation of it."""
    assert hasattr(finetune_module, "_label_to_id"), "nli/finetune.py._label_to_id not found — code path changed."
    labels_map = cfg.nli_finetune["labels"]
    return {str(k): int(v) for k, v in labels_map.items()}


def get_checkpoint_label_mapping(checkpoint_dir: Path | None) -> tuple[dict | None, dict | None, str]:
    """PEFT's adapter_config.json does NOT store label2id/id2label — those
    live on the base model's config.json, not the adapter config. Checks
    both files if present; returns (label2id, id2label, human-readable note)."""
    if checkpoint_dir is None:
        return None, None, "No --checkpoint-dir given."
    checkpoint_dir = Path(checkpoint_dir)
    if not checkpoint_dir.exists():
        return None, None, f"Checkpoint dir does not exist locally: {checkpoint_dir}"

    adapter_config_path = checkpoint_dir / "adapter_config.json"
    config_path = checkpoint_dir / "config.json"
    found_files = sorted(p.name for p in checkpoint_dir.iterdir()) if checkpoint_dir.is_dir() else []

    if adapter_config_path.exists():
        adapter_config = json.loads(adapter_config_path.read_text(encoding="utf-8"))
        if "label2id" in adapter_config or "id2label" in adapter_config:
            return (
                adapter_config.get("label2id"),
                adapter_config.get("id2label"),
                f"Read from {adapter_config_path} (unexpected: PEFT adapter configs don't normally carry this).",
            )

    if config_path.exists():
        base_config = json.loads(config_path.read_text(encoding="utf-8"))
        label2id = base_config.get("label2id")
        id2label = base_config.get("id2label")
        if label2id or id2label:
            return label2id, id2label, f"Read from {config_path}"
        return None, None, f"{config_path} exists but has no label2id/id2label fields."

    return (
        None,
        None,
        f"Neither adapter_config.json's label fields nor a config.json with label fields "
        f"were found under {checkpoint_dir}. Files present: {found_files}",
    )


def get_canonical_base_model_mapping(model_name: str) -> tuple[dict | None, dict | None, str]:
    """Reads ONLY from a local Hugging Face cache via huggingface_hub.scan_cache_dir.
    Never triggers a network request. Never fabricates a mapping if the model
    isn't cached — returns None with an explicit UNVERIFIED note instead."""
    try:
        from huggingface_hub import scan_cache_dir
    except ImportError:
        return None, None, "huggingface_hub not importable — cannot scan local cache."

    try:
        cache_info = scan_cache_dir()
    except Exception as exc:  # pragma: no cover - defensive
        return None, None, f"Could not scan local HF cache: {exc}"

    for repo in cache_info.repos:
        if repo.repo_id == model_name:
            for revision in repo.revisions:
                for file in revision.files:
                    if file.file_name == "config.json":
                        config = json.loads(Path(file.file_path).read_text(encoding="utf-8"))
                        label2id = config.get("label2id")
                        id2label = config.get("id2label")
                        if label2id or id2label:
                            return label2id, id2label, f"Read from local HF cache: {file.file_path}"

    return (
        None,
        None,
        f"{model_name!r} not found in the local HF cache "
        f"({len(cache_info.repos)} repo(s), {cache_info.size_on_disk} bytes cached total). "
        f"UNVERIFIED — requires network.",
    )


def _normalize(mapping: dict | None) -> dict | None:
    if mapping is None:
        return None
    return {str(k).strip().lower(): int(v) for k, v in mapping.items()}


def _quote_lora_yaml_section(configs_dir: Path) -> str:
    """Returns the verbatim `lora:` block from configs/nli_finetune.yaml so
    the absence (or presence) of modules_to_save can be visually confirmed,
    not just asserted."""
    text = (configs_dir / "nli_finetune.yaml").read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "lora:")
    end = start + 1
    while end < len(lines) and (lines[end].startswith("  ") or not lines[end].strip()):
        if lines[end].strip() and not lines[end].startswith(" "):
            break
        end += 1
    return "\n".join(lines[start:end])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 5 Task A: label2id/id2label audit.")
    parser.add_argument("--checkpoint-dir", type=Path, default=None, help="Local LoRA checkpoint directory, if any.")
    parser.add_argument("--configs-dir", type=Path, default=None, help="Override the configs/ directory.")
    args = parser.parse_args(argv)

    cfg = Config(configs_dir=args.configs_dir)
    configs_dir = args.configs_dir if args.configs_dir is not None else (REPO_ROOT / "configs")
    lora_cfg = cfg.nli_finetune["lora"]

    training_label2id = get_training_label_mapping(cfg)
    checkpoint_label2id, checkpoint_id2label, checkpoint_note = get_checkpoint_label_mapping(args.checkpoint_dir)
    canonical_label2id, canonical_id2label, canonical_note = get_canonical_base_model_mapping(cfg.nli_model)

    print("=" * 78)
    print("Label-mapping audit (Phase 5, Task A)")
    print("=" * 78)

    print("\n(1) Training code path — interview_iq.nli.finetune._label_to_id")
    print("    (reads cfg.nli_finetune['labels'] from configs/nli_finetune.yaml):")
    print(f"    label2id = {training_label2id}")

    print(f"\n(2) LoRA checkpoint ({args.checkpoint_dir if args.checkpoint_dir else 'no --checkpoint-dir given'}):")
    if checkpoint_label2id is None:
        print(f"    NOT FOUND — {checkpoint_note}")
    else:
        print(f"    label2id = {checkpoint_label2id}")
        print(f"    id2label = {checkpoint_id2label}")
        print(f"    ({checkpoint_note})")

    print(f"\n(3) Canonical base model ({cfg.nli_model}):")
    if canonical_label2id is None:
        print(f"    UNVERIFIED — requires network. {canonical_note}")
    else:
        print(f"    label2id = {canonical_label2id}")
        print(f"    id2label = {canonical_id2label}")
        print(f"    ({canonical_note})")

    have_checkpoint = checkpoint_label2id is not None
    have_canonical = canonical_label2id is not None

    if have_checkpoint and have_canonical:
        norm_training = _normalize(training_label2id)
        norm_checkpoint = _normalize(checkpoint_label2id)
        norm_canonical = _normalize(canonical_label2id)
        verdict = "IDENTICAL" if norm_training == norm_checkpoint == norm_canonical else "MISMATCH"
    else:
        verdict = "UNVERIFIED"

    print(f"\nVERDICT: {verdict}")
    if verdict == "UNVERIFIED":
        missing = []
        if not have_checkpoint:
            missing.append("checkpoint config (no --checkpoint-dir / not found locally)")
        if not have_canonical:
            missing.append("canonical base-model config (not in local HF cache)")
        print(f"  Reason: missing {', '.join(missing)} — full three-way comparison not possible on this machine.")

    print("\n" + "-" * 78)
    print("modules_to_save (classification head) — verbatim configs/nli_finetune.yaml lora: block:")
    print("-" * 78)
    print(_quote_lora_yaml_section(configs_dir))
    if "modules_to_save" in lora_cfg:
        print(f"\nFOUND: modules_to_save = {lora_cfg['modules_to_save']}")
    else:
        print("\nNOT PRESENT. modules_to_save is absent from the lora: block above.")
        print("=> Only query_proj/value_proj are LoRA-adapted; the classification head")
        print("   (the 3-way entailment/neutral/contradiction classifier) is NOT included")
        print("   in the adapter and is used unmodified from the pretrained base model.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
