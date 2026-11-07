r"""Test 1803 — WITNESS: a bodyless `val` that declares BOTH `assigns \nothing` AND a
write target is refused (PYCSL-CONTRADICTORY-ASSIGNS).

The refusal's own message explains why neither clause may silently win: every `#@ assigns`
of a function is flattened into ONE frame, and preferring `\nothing` emits a `val` with no
`writes`, which Why3 reads as PURE — letting a caller prove the target UNCHANGED across a
stub contracted to write it. That is routes #96, #98, #101 and #103.

Its source comment says the guard is "NEGATIVE-TESTED by feeding it the mixed spelling
directly", and it is — by a developer, by hand, once. `bin/check-refusal-witness-coverage.py`
listed it as having no witness in the corpus, which is the difference between "it was
tested" and "it is tested". This file is the standing one.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires n >= 0
#@ assigns \nothing
#@ assigns g.v
#@ \trusted
def stub(n: int) -> None:
    g.v = n
