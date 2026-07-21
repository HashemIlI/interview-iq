# Decomposition Corpus v2 Pilot

A 100-case synthetic Dataset Engineering pilot. Every record is `DRAFT_UNREVIEWED`; nothing is human-reviewed or training-approved. `answer_asr_simulated` is paired text-only simulation, never a real or aligned transcript.

Run `python scripts/generate_decomposition_pilot_v2.py --provider local`. `--provider gemini` requires `GEMINI_API_KEY`. Raw pass responses support safe resume. Claims are authoritative JSON lists; no rendered target or automatic split is created.
