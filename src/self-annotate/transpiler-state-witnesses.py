"""transpiler-state-witnesses.py — A3 Slice-0 (a3-plan.md), unblocked by M.7.

A `@mutable_state @dataclass` transpiler-state class proves CHECKED `assigns`
frames for its mutating methods — the exact witness a3-plan.md §9 FALSIFIED under
value-semantics (`assigns \nothing` passed on a mutating body). With mutable-self
M.2-M.4 + M.7 (`self.<setfield>.add(x)` as a real field write) it is now green.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/transpiler-state-witnesses.py
"""
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class TranspilerState:
    dict_locals: Set[str]     # a set-of-name field (like _dict_locals / _array_locals)
    havoc_counter: int        # a counter field (like _havoc_counter)

    # set-field mutation: `.add` lowers to a real `self.dict_locals <- …` write,
    # framed by a CHECKED `writes { self.dict_locals }`. A `\nothing` here FAILS.
    #@ assigns self.dict_locals
    def mark_dict(self, name: str) -> None:
        self.dict_locals.add(name)

    # counter mutation: `+= 1` is a real field write, framed by `writes { self.havoc_counter }`.
    #@ assigns self.havoc_counter
    def next_havoc(self) -> None:
        self.havoc_counter = self.havoc_counter + 1


# --- NON-VACUITY (expected FAIL, kept OUT of this pass-file) ---
#   #@ assigns \nothing
#   def mark_dict(self, name): self.dict_locals.add(name)   # lies — writes dict_locals
#   => Why3 rejects ("unlisted write effect"). The a3-plan.md §9 hole is CLOSED:
#      a state-mutating emitter method can now state a PROVEN assigns frame.
