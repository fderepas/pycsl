"""Test 0772 — cleared-hash.md S4/S7: distinct-key non-aliasing on a record dict FIELD.

A `@mutable_state @dataclass` record with a `Dict[str, int]` FIELD now lowers that field to
`map string (option int)` with native, injective `String.(=)` keys — NOT `map int` + the opaque
`str_hash_op` (cleared-hash.md S4). So two DISTINCT keys (`k1 != k2`) are provably non-aliasing on
`self.d`: after `self.d[k1] = v1; self.d[k2] = v2`, the read `self.d[k1]` is still `v1` (writing
`k2` cannot disturb the `k1` entry). The write (store) and read (subscript) use the SAME raw string
key term — a mismatch would be a WhyML type error.

UNPROVABLE under the retired opaque-hash field model: `str_hash_op` is a bodyless `val`, so
`k1 != k2` does NOT imply `str_hash_op k1 != str_hash_op k2` — the prover must admit a collision
under which `self.d[k2]=v2` clobbers `self.d[k1]`."""
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Store:
    d: Dict[str, int] = None

    #@ requires k1 != k2
    #@ ensures \result == v1
    #@ assigns self.d
    #@ no_exception KeyError
    def distinct_keys_field(self, k1: str, k2: str, v1: int, v2: int) -> int:
        self.d[k1] = v1
        self.d[k2] = v2
        return self.d[k1]


if __name__ == "__main__":
    s = Store()
    s.d = {}
    assert s.distinct_keys_field("a", "b", 1, 2) == 1
