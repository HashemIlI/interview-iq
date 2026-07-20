from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
import re

import pytest
from transformers import AutoTokenizer

from interview_iq.config import Config
from interview_iq.decomposition.dataset_builder import (
    ASR_TRAIN_FILENAMES,
    TRAIN_FILENAMES,
    _check_variant_claims_match,
    build_gold_validation_set,
    build_kd_dataset,
)
from interview_iq.decomposition.trainer import examples_to_dataset, split_by_question_ids
from interview_iq.decomposition.types import AnnotationRules, KDExample


RESULTS_DIR = Path(__file__).parents[1] / "results"


@pytest.fixture(scope="module")
def examples() -> list[KDExample]:
    rules = AnnotationRules(
        preserve_hedging=True,
        generalise_personal_framing=True,
        no_unverifiable_causal_bridge=True,
        enforce_self_containment=True,
    )
    return build_kd_dataset(RESULTS_DIR, rules)


def test_paired_dataset_contract(examples: list[KDExample]) -> None:
    question_ids = {example.question_id for example in examples}
    example_ids = {example.example_id for example in examples}
    variants = Counter(example.variant for example in examples)

    assert len(examples) == 444
    assert len(question_ids) == 222
    assert len(example_ids) == 444
    assert variants == {"original": 222, "asr_aligned": 222}
    assert "GN-050" not in question_ids

    by_question: dict[str, list[KDExample]] = defaultdict(list)
    for example in examples:
        by_question[example.question_id].append(example)

    assert all(len(records) == 2 for records in by_question.values())
    assert all(
        {record.variant for record in records} == {"original", "asr_aligned"}
        for records in by_question.values()
    )
    assert all(
        {record.example_id for record in records}
        == {f"{question_id}__original", f"{question_id}__asr"}
        for question_id, records in by_question.items()
    )
    print(
        "DATASET_COUNTS "
        f"training_examples={len(examples)} "
        f"unique_question_ids={len(question_ids)} "
        f"unique_example_ids={len(example_ids)} "
        f"original={variants['original']} "
        f"asr_aligned={variants['asr_aligned']} "
        f"questions_with_exactly_two_variants={len(by_question)}"
    )


def test_only_expected_markdown_sources_are_loaded(examples: list[KDExample]) -> None:
    source_files = {example.source_file for example in examples}

    assert source_files == set(TRAIN_FILENAMES) | set(ASR_TRAIN_FILENAMES)
    assert "TERM_MAP_MANUAL.md" not in source_files

    gold = build_gold_validation_set(RESULTS_DIR)
    assert {example.question_id for example in gold}.isdisjoint(
        {example.question_id for example in examples}
    )


def test_all_222_variant_pairs_have_identical_parsed_claims(
    examples: list[KDExample],
) -> None:
    by_question: dict[str, dict[str, KDExample]] = defaultdict(dict)
    for example in examples:
        by_question[example.question_id][example.variant] = example

    differences = [
        question_id
        for question_id, variants in by_question.items()
        if variants["original"].claims != variants["asr_aligned"].claims
    ]

    assert len(by_question) == 222
    assert differences == []
    print(f"CLAIMS_PAIR_COUNTS pairs={len(by_question)} differences={len(differences)}")


def test_claims_guard_raises_with_question_id(examples: list[KDExample]) -> None:
    question_id = examples[0].question_id
    pair = [example for example in examples if example.question_id == question_id]
    asr = next(example for example in pair if example.variant == "asr_aligned")
    mismatched_asr = replace(asr, claims=[*asr.claims, "claim مختلف للاختبار"])

    with pytest.raises(ValueError, match=re.escape(question_id)):
        _check_variant_claims_match(
            [
                next(example for example in pair if example.variant == "original"),
                mismatched_asr,
            ]
        )


def test_question_grouped_split_has_expected_sizes(examples: list[KDExample]) -> None:
    train, validation = split_by_question_ids(examples, val_ratio=0.15, seed=42)
    train_question_ids = {example.question_id for example in train}
    validation_question_ids = {example.question_id for example in validation}

    assert len(train) == 378
    assert len(validation) == 66
    assert len(train_question_ids) == 189
    assert len(validation_question_ids) == 33
    assert train_question_ids.isdisjoint(validation_question_ids)

    placement = defaultdict(set)
    for example in train:
        placement[example.question_id].add("train")
    for example in validation:
        placement[example.question_id].add("validation")
    assert all(len(splits) == 1 for splits in placement.values())
    print(
        "SPLIT_COUNTS "
        f"train_examples={len(train)} "
        f"validation_examples={len(validation)} "
        f"question_id_overlap={len(train_question_ids & validation_question_ids)}"
    )


class _FakeTokenizer:
    def __call__(
        self,
        texts=None,
        *,
        text_target=None,
        truncation: bool,
        max_length: int,
    ):
        values = text_target if text_target is not None else texts
        input_ids = [[min(len(value), max_length)] for value in values]
        return {"input_ids": input_ids, "attention_mask": [[1] for _ in values]}


def test_original_and_asr_variants_reach_train_dataset(examples: list[KDExample]) -> None:
    train, _ = split_by_question_ids(examples, val_ratio=0.15, seed=42)
    train_dataset = examples_to_dataset(
        train,
        tokenizer=_FakeTokenizer(),
        max_source_length=320,
        max_target_length=320,
    )

    assert len(train_dataset) == 378
    assert len(set(train_dataset["example_id"])) == 378
    assert Counter(train_dataset["variant"]) == {
        "original": 189,
        "asr_aligned": 189,
    }
    assert set(train_dataset["source_file"]) == set(TRAIN_FILENAMES) | set(
        ASR_TRAIN_FILENAMES
    )
    print(
        "TRAIN_DATASET_COUNTS "
        f"examples={len(train_dataset)} "
        f"unique_example_ids={len(set(train_dataset['example_id']))} "
        f"original={Counter(train_dataset['variant'])['original']} "
        f"asr_aligned={Counter(train_dataset['variant'])['asr_aligned']}"
    )


def test_real_config_tokenizer_produces_model_inputs_for_both_variants(
    examples: list[KDExample],
) -> None:
    cfg = Config()
    model_name = cfg.decomposition["model"]["selected"]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train, _ = split_by_question_ids(examples, val_ratio=0.15, seed=42)

    train_dataset = examples_to_dataset(
        train,
        tokenizer=tokenizer,
        max_source_length=int(cfg.decomposition["tokenizer"]["max_source_length"]),
        max_target_length=int(cfg.decomposition["tokenizer"]["max_target_length"]),
    )

    required_columns = {"input_ids", "attention_mask", "labels"}
    variants = Counter(train_dataset["variant"])
    assert required_columns <= set(train_dataset.column_names)
    assert variants == {"original": 189, "asr_aligned": 189}
    assert all(train_dataset[column] for column in required_columns)
    print(
        "REAL_TOKENIZER_SMOKE "
        f"model={model_name} examples={len(train_dataset)} "
        f"original={variants['original']} asr_aligned={variants['asr_aligned']} "
        f"columns={','.join(sorted(required_columns))}"
    )
