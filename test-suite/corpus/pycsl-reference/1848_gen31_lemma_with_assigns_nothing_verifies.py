r"""Test 1848 — gen #31 CONTROL for 1847 (expected PASS): the clause is all that was missing.

Byte-identical to 1847 except for the one line `#@ assigns \nothing`. It verifies, so the
refusal in 1847 is about the ABSENT CLAUSE and not about the lemma, its `requires`, its
`ensures` or its body — the same control discipline 1841 and 1843 pay for.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ lemma
#@ requires a >= 0 and b >= 0
#@ ensures a + b >= 0
#@ assigns \nothing
def sum_nonneg(a: int, b: int) -> None:
    pass
