"""
D74 LLM-based Claim Decomposition client.

Calls an external LLM (via OpenRouter, OpenAI-compatible API) to perform
answer normalization + claim decomposition, per decisions.md D74. This
REPLACES the archived AraT5 fine-tuning approach (Phase 8, superseded --
see archive/phase8_arat5_superseded/).

The hard constraints (no correction of answer correctness, Latin-script
term preservation, atomicity, self-containment) are enforced by the
system prompt in system_prompt.md -- this module does NOT itself verify
that the model honored them. See scripts/llm_decomposition_sanity_gate.py
(D74 mandatory sanity gate, not yet implemented) for that check. Do not
trust this module's output in any production path until that gate has
been run and passed.

NOT wired into configs/decomposition.yaml or any production pipeline yet.
"""

from __future__ import annotations

import os
import random
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from interview_iq.decomposition.types import DecompositionResult

_MODULE_DIR = Path(__file__).resolve().parent
_SYSTEM_PROMPT_PATH = _MODULE_DIR / "system_prompt.md"
_REPO_ROOT_ENV = _MODULE_DIR.parents[3] / ".env"

load_dotenv(_REPO_ROOT_ENV if _REPO_ROOT_ENV.exists() else None)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
# Verify the current free-tier Qwen model id at https://openrouter.ai/models
# before setting this -- the free lineup rotates and is NOT hardcoded here.
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL")

_MAX_RETRIES = 5
_BASE_BACKOFF_SECONDS = 2.0
_MAX_BACKOFF_SECONDS = 60.0

NO_EXTRACTABLE_CLAIMS_SENTINEL = "NO_EXTRACTABLE_CLAIMS"


class LLMDecompositionError(RuntimeError):
    """Raised when the LLM call fails after all retries, or returns an
    unparseable response. Callers must not silently swallow this -- a
    failed decomposition must not be treated as an empty/valid result."""


def _load_system_prompt() -> str:
    if not _SYSTEM_PROMPT_PATH.exists():
        raise LLMDecompositionError(f"system_prompt.md not found at {_SYSTEM_PROMPT_PATH}")
    return _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def _parse_numbered_claims(raw_output: str) -> list[str]:
    """Parse the model's plain numbered-list output per the OUTPUT FORMAT
    section of system_prompt.md."""
    stripped = raw_output.strip()
    if stripped == NO_EXTRACTABLE_CLAIMS_SENTINEL:
        return []

    claims: list[str] = []
    for line in stripped.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(".", 1)
        if len(parts) == 2 and parts[0].strip().isdigit():
            claim_text = parts[1].strip()
            if claim_text:
                claims.append(claim_text)
        else:
            raise LLMDecompositionError(
                f"Output line does not match 'N. claim' format: {line!r}\n"
                f"Full raw output:\n{raw_output}"
            )
    return claims


def _sleep_before_retry(attempt: int, retry_after: str | None) -> None:
    if retry_after is not None:
        try:
            delay = float(retry_after)
        except ValueError:
            delay = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
    else:
        delay = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
    delay = min(delay, _MAX_BACKOFF_SECONDS)
    delay += random.uniform(0, 1)
    time.sleep(delay)


def _call_openrouter(asr_text: str, system_prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        raise LLMDecompositionError(
            "OPENROUTER_API_KEY is not set. Add it to a .env file at the "
            "repo root (see .env.example)."
        )
    if not OPENROUTER_MODEL:
        raise LLMDecompositionError(
            "OPENROUTER_MODEL is not set. Verify the current free-tier "
            "model id at https://openrouter.ai/models and add it to .env "
            "-- the free lineup rotates, do not assume a stale id works."
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": asr_text},
        ],
        "temperature": 0,
    }

    last_error: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
        except requests.RequestException as exc:
            last_error = exc
            if attempt < _MAX_RETRIES:
                _sleep_before_retry(attempt, retry_after=None)
                continue
            raise LLMDecompositionError(
                f"OpenRouter call failed after {_MAX_RETRIES} attempts (connection error): {exc}"
            ) from exc

        if response.status_code == 200:
            data = response.json()
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError) as exc:
                raise LLMDecompositionError(f"Unexpected response shape from OpenRouter: {data!r}") from exc

        if response.status_code == 429 or response.status_code >= 500:
            retry_after = response.headers.get("Retry-After")
            last_error = LLMDecompositionError(
                f"OpenRouter returned {response.status_code}: {response.text[:500]}"
            )
            if attempt < _MAX_RETRIES:
                _sleep_before_retry(attempt, retry_after=retry_after)
                continue
            raise last_error

        raise LLMDecompositionError(f"OpenRouter returned {response.status_code}: {response.text[:500]}")

    raise LLMDecompositionError(f"OpenRouter call failed after {_MAX_RETRIES} attempts: {last_error}")


def decompose_via_llm(asr_text: str) -> DecompositionResult:
    """
    Convert a raw ASR transcript of a candidate's spoken answer into a
    DecompositionResult, via an external LLM API call.

    Per D74, this function does NOT validate that the LLM honored the
    hard constraints in system_prompt.md. That validation is the job of
    the separate D74 mandatory sanity gate
    (scripts/llm_decomposition_sanity_gate.py, not yet implemented).
    """
    if not asr_text or not asr_text.strip():
        raise LLMDecompositionError("asr_text is empty -- nothing to decompose.")

    system_prompt = _load_system_prompt()
    raw_output = _call_openrouter(asr_text, system_prompt)
    claims = _parse_numbered_claims(raw_output)

    return DecompositionResult(source_text=asr_text, claims=claims)
