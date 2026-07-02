"""seq-reassign-witness.py — seq-model-pivot.md SQ1-SQ4.

A REASSIGNED list local is an immutable `seq` (freely reassignable), not a mutable `array`
(a `ref (array _)` reassignment is an illegal Why3 region alias). `ys = stmt.body` snapshots
the `List[str]` array field to a seq; `ys = ys[:-1]` is a `seq_sub` sub-sequence; `ys[-1]` is
`Seq.get`. Mirrors critical_section's `body_stmts = stmt.body; body_stmts = body_stmts[:-1]`.
@mutable_state-only.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/seq-reassign-witness.py
"""
from dataclasses import dataclass
from typing import List
def mutable_state(cls): return cls
def whyml_ident(s: str) -> str:
    #@ ensures True
    return s


@dataclass
class Stmt:
    body: List[str]


@mutable_state
@dataclass
class Emitter:
    _n: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def drop_last(self, stmt: Stmt) -> str:
        ys = stmt.body             # array-string field read -> snapshot to seq (reassigned below)
        ys = ys[:-1]               # seq_sub (pure value, freely reassignable — no region alias)
        if ys:                     # seq truthiness
            return whyml_ident(ys[-1])   # Seq.get -> string
        return ""
