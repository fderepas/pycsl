"""mixed-fstring-witness.py — R3 (todict-reflection-plan.md): mixed str/int f-string.

In a @mutable_state class (the emitter model), a MIXED str/int f-string — e.g. a
gensym `f"__x_{n}"` (an int counter interpolated) — is a STRING: `_handle_fstring_expr`
converts the int segment via `int_to_string`, and the receiving local types as string.
This is the last string-local piece the real emitter handlers need (a gensym like
`_handle_array_slice_set_stmt`'s `src_var`).

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/mixed-fstring-witness.py
"""
from dataclasses import dataclass
def mutable_state(cls): return cls


@mutable_state
@dataclass
class Emitter:
    counter: int

    #@ assigns self.counter
    def gensym(self) -> str:
        n = self.counter + 1
        self.counter = n
        name = f"__pycsl_tmp_{n}"          # MIXED str/int f-string -> string
        return name + "_end"               # string concat proves it is a string
