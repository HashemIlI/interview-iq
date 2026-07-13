"""
decomposition/ — Claim Decomposition (Knowledge Distillation) module.

⛔ Phase 8 — Gate G2 is closed (decisions.md D51/D52) but Q6 (AraT5 vs
mT5-base) is still OPEN — see decisions.md and PROJECT_EXECUTION_PLAN.md
§Phase 8. This package currently ships interface stubs only:

  - types.py            data containers (model-agnostic)
  - dataset_builder.py  KD corpus builder — raises NotImplementedError
  - trainer.py          model trainer — raises NotImplementedError
  - inference.py        decomposition inference — raises NotImplementedError

No function in this package may load a tokenizer, checkpoint, or model
name until Q6 is resolved and `configs/decomposition.yaml`'s
`model.selected` placeholder ("TBD_pending_Q6") is replaced with a
concrete decision.
"""

from __future__ import annotations
