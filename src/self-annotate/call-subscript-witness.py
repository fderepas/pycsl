"""call-subscript-witness.py — typed-ir-for-b-ceiling.md B-C5 (Call/Subscript reflection).

Reflection over Call/Subscript emit_ir nodes:
  val_ir.get("func")            -> func_of   (string)
  len(val_ir.get("args"))       -> nargs_of  (int, Call arity)
  val_ir.get("args")[0]         -> arg0_of   (emit_ir, Call's first arg)
  val_ir.get("value")/.get("index") -> svalue_of/sindex_of (emit_ir sub-nodes)
what _handle_tuple_unpack_stmt / _handle_expr_stmt reflect on.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/call-subscript-witness.py
"""
from dataclasses import dataclass
def mutable_state(cls): return cls


@dataclass
class Stmt:
    value: "ExprIR"


@mutable_state
@dataclass
class E:
    tag: int

    #@ \trusted reviewer: x
    #@ ensures True
    def sink(self, ir: "ExprIR") -> int:
        return 0

    #@ ensures True
    def h(self, stmt: Stmt) -> int:
        val_ir = stmt.value.to_dict()
        if val_ir.get("type") == "Call":
            func_name = val_ir.get("func", "")     # func_of (string)
            nargs = len(val_ir.get("args", []))    # nargs_of (int)
            first = self.sink(val_ir.get("args", [])[0])   # arg0_of (emit_ir)
            if func_name == "append":
                return nargs + first
        if val_ir.get("type") == "Subscript":
            inner = self.sink(val_ir.get("value", {}))   # svalue_of (emit_ir)
            idx = self.sink(val_ir.get("index", {}))     # sindex_of (emit_ir)
            return inner + idx
        return 0
