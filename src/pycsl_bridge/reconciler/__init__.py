"""Reconcile contracts from two IR dumps.

`reconcile_envelopes(rocq_env, lean_env)` returns a `Reconciliation`
mapping each Python qualname to a per-function `Result` with status:

  - RECONCILED   — canonical forms match (ensures/requires multisets)
  - ROCQ_ONLY    — only rocq2pycsl produced contracts for this qualname
  - LEAN_ONLY    — only lean2pycsl produced contracts for this qualname
  - DISAGREEMENT — both produced contracts, canonical forms differ

The bridge CLI uses this to decide what to emit and whether to halt.
"""

from .pipeline import (
    QualnameResult,
    Reconciliation,
    Status,
    reconcile_envelopes,
)
from .diff import format_disagreement

__all__ = [
    "QualnameResult",
    "Reconciliation",
    "Status",
    "reconcile_envelopes",
    "format_disagreement",
]
