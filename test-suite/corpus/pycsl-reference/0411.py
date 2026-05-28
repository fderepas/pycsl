"""Test 0411 — UB-7.2: class with both __hash__ and __eq__ — axiom mode.

In default (non-strict) mode, the consistency relationship is emitted
as an axiom; the user is on the hook to keep them consistent. The
file verifies cleanly. Switching to `--strict-hash-eq-consistency`
turns the axiom into a goal that must be discharged externally.
"""
# pycsl-flags: --no-proof
""  # pycsl
#@ class invariant self._key >= 0
class HashableKey:
    def __init__(self) -> None:
        self._key: int = 0

    def __hash__(self) -> int:
        return self._key

    def __eq__(self, other: object) -> bool:
        return self._key == other._key

    #@ requires self._key >= 0
    #@ ensures self._key >= 0
    #@ assigns \nothing
    def get_key(self) -> int:
        return self._key


if __name__ == "__main__":
    pass
