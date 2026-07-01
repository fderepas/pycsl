"""emit-ir-local-witness.py — typed-ir-for-b-ceiling.md §19 (emit_ir local).

A local bound to an emit_ir value (`node = stmt.value`, an ExprIR field) is pre-declared
`ref (IrOther "")` — the emit_ir counterpart of the string `ref ""` pre-decl — so its
`:=` typechecks and it flows to an ExprIR-typed sibling. This is what
`_handle_critical_section_stmt`'s `assume_inv = stmt.assume_invariant` needs.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/emit-ir-local-witness.py
"""
from dataclasses import dataclass
def mutable_state(cls): return cls


@dataclass
class Stmt:
    value: "ExprIR"


@mutable_state
@dataclass
class Emitter:
    tag: int

    #@ \trusted reviewer: x
    #@ ensures True
    def sink(self, ir: "ExprIR") -> int:
        return 0

    #@ ensures True
    def handle(self, stmt: Stmt, flag: int) -> int:
        node = stmt.value          # emit_ir local (ref (IrOther ""))
        if flag == 0:
            node = stmt.value      # reassign — still emit_ir
        return self.sink(node)     # emit_ir local -> ExprIR sibling
