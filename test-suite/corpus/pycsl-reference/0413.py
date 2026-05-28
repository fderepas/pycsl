"""Test 0413 — UB-7.2: __eq__ without __hash__ → class is unhashable.

Module 6 emits a documentation comment only — no goal/axiom is
emitted. The file still verifies; the comment lives in the WhyML
preamble for human review.
"""
# pycsl-flags: --no-proof
""  # pycsl
#@ class invariant self._n >= 0
class UnhashableThing:
    def __init__(self) -> None:
        self._n: int = 0

    def __eq__(self, other: object) -> bool:
        return self._n == other._n

    #@ requires self._n >= 0
    #@ ensures self._n >= 0
    #@ assigns \nothing
    def get(self) -> int:
        return self._n


if __name__ == "__main__":
    pass
