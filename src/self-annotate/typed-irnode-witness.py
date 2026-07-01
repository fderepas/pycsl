"""typed-irnode-witness.py — typed-ir-for-b-ceiling.md B-C1+B-C2.

An inline IR-node construction `{"type": "Var", "name": target}` lowers to the typed
`irnode` sum constructor `(IrVar target)` (B-C1), and an `ExprIR`-annotated sibling
param lowers to the `irnode` type (B-C2) — so the constructed node and a real ExprIR
field UNIFY at a sibling that takes both. This is the Ceiling-B pattern that blocked
`_handle_augassign_stmt` (todict-reflection-plan.md §14).

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/typed-irnode-witness.py
"""
from dataclasses import dataclass
from typing import Dict, Any
def mutable_state(cls): return cls

@dataclass
class ExprIR:
    kind: str

@mutable_state
@dataclass
class Emitter:
    tag: int
    #@ \trusted reviewer: x
    #@ ensures True
    def sink(self, ir: ExprIR) -> int:
        return 0
    #@ ensures True
    def build(self, target: str) -> int:
        return self.sink({"type": "Var", "name": target})
