"""Test 1076 — ROUTE #48 negative witness (a): a seeded `Counter` DROPS its seed, and the
empty map's missing-key default is then DECIDED on.

FALSE OF THE PROGRAM: `Counter([1, 1, 2])[1]` is 2 in Python, so `f()` returns 0.

`_call_named_builtins` lowered the whole dict-family to `(const (None: option int))` and the
comment justified it as "a seeded iterable is modelled as empty (a sound under-approximation:
content that depends on the seed fails to prove, never proves falsely)". That is the one
claim the coercion could not make: `(const None)` is not an UNKNOWN map, it is the EMPTY
one, and the model's missing-key default is the integer `0`. So the seed was not merely
lost — every read of a seeded key became the decidable `0`. At the parent commit 57777b56
`\\result == 7` PROVED.

FOUND BY READING THE EMITTER'S OWN SOUNDNESS CLAIMS AND PROBING EACH, a method the window
recorded because it worked on the first corpus-reachable claim it reached.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import Counter


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = Counter([1, 1, 2])
    if c[1] == 0:
        return 7
    return 0
