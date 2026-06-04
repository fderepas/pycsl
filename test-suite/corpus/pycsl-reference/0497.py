"""Test 0497 — class: non-trivial __new__ is rejected (base_op.md Tier A, UB-7.6).

Allocation interposition — a caching singleton here — cannot be soundly modelled: construction
`C(...)` is a fresh record literal, so a `__new__` that returns a cached / other / conditionally
chosen instance is rejected at weave time (UB-7.6), not faked. Expected-FAIL = the pipeline
raises the UB-7.6 semantic error rather than emitting an unsound proof."""
# pycsl-expected: FAIL
_ = 0  # anchor
class Singleton:
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __init__(self):
        self.x = 1


#@ ensures \result == 1
def use() -> int:
    s = Singleton()
    return s.x
