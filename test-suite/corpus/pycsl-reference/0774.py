"""Test 0774 — cleared-hash.md S4/S7: literal↔variable key consistency on a record dict FIELD.

Under `map string`, a string LITERAL key and a variable holding the SAME string are the identical
Why3 string term, so writing `self.d["k"] = v` and reading `self.d[key]` (with `key == "k"`) yields
the same entry. The store and the subscript read use the raw native string key — no `str_hash_op`.

UNPROVABLE under the retired opaque model: the write path used the emit-time constant hash of the
LITERAL ("k") while a variable-key read used the abstract runtime `str_hash_op key`; the two ints
were never related, so a literal-key write and a variable-key read could not be connected."""
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Store:
    d: Dict[str, int] = None

    #@ requires key == "k"
    #@ ensures \result == v
    #@ assigns self.d
    #@ no_exception KeyError
    def literal_var_field(self, key: str, v: int) -> int:
        self.d["k"] = v
        return self.d[key]


if __name__ == "__main__":
    s = Store()
    s.d = {}
    assert s.literal_var_field("k", 7) == 7
