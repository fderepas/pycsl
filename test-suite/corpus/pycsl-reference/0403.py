"""Test 0403 — UB-7.5 baseline: class without `__del__` is unchanged."""
""  # pycsl
#@ class invariant self._n >= 0
class NoFinalizer:
    def __init__(self) -> None:
        self._n: int = 0

    #@ requires self._n >= 0
    #@ ensures self._n == \old(self._n) + 1
    #@ assigns self._n
    def inc(self) -> None:
        self._n = self._n + 1


if __name__ == "__main__":
    obj = NoFinalizer()
    obj.inc()
    assert obj._n == 1
