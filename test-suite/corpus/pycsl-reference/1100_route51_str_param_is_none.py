"""Test 1100 — ROUTE #51 shape (c): a `str`-annotated PARAMETER tested `is None`.

FALSE OF THE PROGRAM: Python takes the `is None` branch and `o.probe(None)` returns 0.

THE CHEAPEST REPRODUCTION IN THE WHOLE `is None` CLASS, and the one that needs least from
the attacker: no annotation lie, no field store, no call, no branch join — one parameter
and one `is None`. A Python type hint is not enforced, so a caller simply passes `None`.

Route #50 gave the string `is None` fall-through two BINDING-justified answers (decided
under a live `None` record, opaque under `AMBIG`) and left a third — the always-present
`false` — justified by nothing but the operand's TYPE. A parameter reaches that third
answer with no binding at all: the function cannot bind what it does not have. At the
parent commit `27cf17b1` `\result == 7` PROVED.

Fixed by requiring a BINDING: the always-present answer is now made only about a name the
function actually binds, and a parameter gets the opaque `pycsl_none_str` instead — which
is exactly what the `int` and `bool` spellings of this same file already do (they reach
route #44's opaque `pycsl_none` and fail closed at the parent too).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self, s: str) -> int:
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.probe(None) == 0
