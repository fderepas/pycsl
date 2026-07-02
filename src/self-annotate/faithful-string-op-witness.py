"""faithful-string-op-witness.py — faithful-string-op.md (P1+P2 acceptance).

The emitter idiom that stalled `_handle_expr_stmt` — building a WhyML identifier from a
Python func name — now type-checks: `func.rsplit(".",1)[0]` (str_split_elem_op, string) is
`.replace(".","_")`'d (str_replace_op, string), so `arr_name : string` flows to a sibling.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/faithful-string-op-witness.py
"""
from dataclasses import dataclass
def mutable_state(cls): return cls


@mutable_state
@dataclass
class Emitter:
    tag: int

    #@ \trusted reviewer: x
    #@ ensures True
    def sink(self, name: str) -> int:
        return 0

    #@ ensures True
    def build(self, func: str) -> int:
        arr_name = func.rsplit(".", 1)[0].replace(".", "_")   # str_split_elem_op + str_replace_op
        title = "-".join([func, arr_name])                    # str_concat_op (literal join)
        return self.sink(arr_name) + len(title)
