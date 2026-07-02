"""list-comp-witness.py — list-comprehension-lowering.md L1/L2/L6.

A list comprehension over a `List[str]` binds an `array string` (`list_comp_string`, a
length-lawed opaque array); `len(...)` is `Array.length`, `xs[i]` is a string element, and
`", ".join(xs)` is a `string` (`str_join_arr`). @mutable_state-only; the corpus keeps the
opaque int `list_comp`/`join_1`.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/list-comp-witness.py
"""
from dataclasses import dataclass
from typing import List
def mutable_state(cls): return cls
def whyml_ident(s: str) -> str:
    #@ ensures True
    return s


@mutable_state
@dataclass
class Emitter:
    _n: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def build(self, targets: List[str]) -> str:
        safe = [whyml_ident(t) for t in targets]   # comprehension -> array string
        n = len(safe)                              # len -> Array.length
        pattern = ", ".join(safe)                  # join over array string -> str_join_arr
        if n > 0:
            return safe[0] + pattern               # index -> string; + -> str_concat_op
        return pattern
