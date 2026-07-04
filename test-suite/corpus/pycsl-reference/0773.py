"""Test 0773 — cleared-hash.md S4/S7: absent-key on a record dict FIELD.

With the field lowered to `map string (option int)` (native, injective string keys), an entry that
was never inserted is provably ABSENT. After clearing `self.d` to the empty map and inserting only
"a" and "b", the DISTINCT key "c" is provably `not in self.d`.

UNPROVABLE under the retired opaque hash: `str_hash_op "c"` could collide with `str_hash_op "a"`
(or "b"), so membership of "c" could not be excluded. Native `String.(=)` makes the absence
provable — membership reads the same raw string key the store wrote."""
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Store:
    d: Dict[str, int] = None

    #@ requires True
    #@ ensures \result == 1
    #@ assigns self.d
    def absent_key_field(self) -> int:
        self.d = {}
        self.d["a"] = 1
        self.d["b"] = 2
        if "c" not in self.d:
            return 1
        return 0


if __name__ == "__main__":
    s = Store()
    assert s.absent_key_field() == 1
