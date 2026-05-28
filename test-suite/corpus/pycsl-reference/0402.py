"""Test 0402 — UB-7.5: `__del__` with `#@ allow_finalizer` is accepted."""
""  # pycsl
#@ class invariant self._n >= 0
#@ allow_finalizer
class WithFinalizer:
    def __init__(self) -> None:
        self._n: int = 0

    def __del__(self) -> None:
        # explicit acknowledgment via allow_finalizer
        self._n = 0


if __name__ == "__main__":
    pass
