"""Test 0414 — UB-7.2: __hash__ without __eq__ uses identity-eq → no goal."""
# pycsl-flags: --no-proof
""  # pycsl
#@ class invariant self._k >= 0
class IdentityEq:
    def __init__(self) -> None:
        self._k: int = 0

    def __hash__(self) -> int:
        return self._k

    #@ requires self._k >= 0
    #@ ensures self._k >= 0
    #@ assigns \nothing
    def get_k(self) -> int:
        return self._k


if __name__ == "__main__":
    pass
