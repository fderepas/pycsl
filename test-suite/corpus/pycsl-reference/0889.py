"""Test 0889 — G1: record `.get("field")` lowers to the NATIVE field read (POSITIVE).

09-2223 pure-classifier increment, recognizer G1. A `.get("<key>"[, default])` on a
record-typed receiver (a `TypedDict`/`@dataclass` monomorphized to a native WhyML
record) whose literal key names a declared field lowers to the record FIELD ACCESS
`r.<label>` — NOT the opaque `r_get_N <int-hash>` abstract op that DROPS the read
(a vacuous/unfaithful "proof"). Here the value contract `\result == r.n` proves ONLY
because the read is faithful: with the opaque op, `\result` would be an unconstrained
`r_get_2 …` and the postcondition could not be discharged.

The `.get`'s defensive default (`0`) is dropped: a declared field is always present in
the record model, so the field read is total (sound; faithful for a TypedDict whose key
is declared). If this regresses, the G1 record-`.get`→field-read recognizer broke.
"""
from typing import TypedDict


class Rec(TypedDict):
    n: int
    kind: str


#@ requires True
#@ ensures \result == r.n
#@ assigns \nothing
def read_n(r: Rec) -> int:
    return r.get("n", 0)
