"""Test 0775 — cleared-hash.md S4/S7: string SET FIELD with native string elements.

A `Set[str]` record FIELD shares the dict `map` model: `set[str] ~ map string (option int)`
(present ≡ `Some 0`) with the NATIVE string element as key. `self.s.add("a")` writes the raw string
"a"; `"b" not in self.s` reads the raw string "b" — both agree (no `str_hash_op`). After clearing
to the empty set and adding only "a", the DISTINCT element "b" is provably absent.

UNPROVABLE under the retired opaque hash: `str_hash_op "b"` could collide with `str_hash_op "a"`, so
membership of "b" could not be excluded. Native `String.(=)` makes the absence provable — and keeps
the write (`.add`) and read (`in`) on the SAME raw string key (a mismatch is a WhyML type error)."""
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Seen:
    s: Set[str] = None

    #@ requires True
    #@ ensures \result == 1
    #@ assigns self.s
    def string_set_field(self) -> int:
        self.s = set()
        self.s.add("a")
        if "b" not in self.s:
            return 1
        return 0


if __name__ == "__main__":
    obj = Seen()
    assert obj.string_set_field() == 1
