# pycsl-expected: FAIL
"""NEGATIVE twin of 0938 — this file MUST NOT prove (marked `pycsl-expected: FAIL`).

It asserts `all(x >= 5 for x in a)` while the precondition only guarantees each element
is >= 0. That is NOT entailed, so the assert cannot be discharged. If it ever proves, the
R2c genexp lowering has collapsed back to the vacuous `all_1` oracle and 0938's green is
worthless.

Non-vacuity here is the EVIL TWIN, not a mutation test: an oracle-erased `all_1
(Array.make 1 0)` body would still let a literal change move the emitted .mlw, so a
mutation test cannot see this failure mode (wall-lessons (l)). Only a real quantified
obligation refutes it."""
from typing import List


#@ requires n >= 0 and \length(a) == n
#@ requires \forall i; 0 <= i and i < n ==> a[i] >= 0
#@ assigns \nothing
def evil_all(a: List[int], n: int) -> int:
    # a[i] >= 0 does NOT entail a[i] >= 5 — this assert must stay unproven.
    #@ assert all(x >= 5 for x in a)
    return 0
