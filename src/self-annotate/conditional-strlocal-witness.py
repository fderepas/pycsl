"""conditional-strlocal-witness.py — R3 (todict-reflection-plan.md): conditional string local.

In a @mutable_state class a string local first-assigned inside BOTH branches of a
conditional is PRE-DECLARED `ref ""` (the string analogue of the int `ref 0`
pre-decl), so it stays in scope after the branch. This mirrors
`_handle_array_slice_set_stmt`'s `hi` (`if stmt.upper is not None: hi = <str call>
else: hi = f"(Array.length {dst})"`).

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/conditional-strlocal-witness.py
"""
from dataclasses import dataclass
def mutable_state(cls): return cls


def emit(x: int) -> str:
    return "e"


@mutable_state
@dataclass
class Emitter:
    flag: int

    #@ ensures True
    def pick(self, dst: str) -> str:
        if self.flag == 0:
            hi = emit(self.flag)         # str-returning call (recognized)
        else:
            hi = f"(Array.length {dst})" # f-string (recognized)
        return hi + "!"                  # `hi` in scope after the if, string-typed
