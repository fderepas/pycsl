"""Test 0401 — UB-7.5: class with `__del__` is rejected by Module 3."""
# pycsl-expected: FAIL
""  # pycsl
#@ class invariant self._n >= 0
class WithFinalizer:
    def __init__(self) -> None:
        self._n: int = 0

    def __del__(self) -> None:
        # finalizer — UB-7.5 rejects this
        self._n = 0


if __name__ == "__main__":
    pass
