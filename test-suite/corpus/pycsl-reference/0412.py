"""Test 0412 — UB-7.2 under strict mode: hash/eq consistency goal must
be discharged. Without an external proof citation Why3 reports it as
unproven and verification fails.
"""
# pycsl-flags: --strict-hash-eq-consistency
# pycsl-expected: FAIL
""  # pycsl
#@ class invariant self._key >= 0
class HashableKey:
    def __init__(self) -> None:
        self._key: int = 0

    def __hash__(self) -> int:
        return self._key

    def __eq__(self, other: object) -> bool:
        return self._key == other._key


if __name__ == "__main__":
    pass
