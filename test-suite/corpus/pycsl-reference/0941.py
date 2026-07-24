"""Test 0941 — r1-setop I2: string SET-UNION `<field> | {x}` writes the RAW native string key.

r1-setop-impl.md I2 (self-tcb-reduction). A `Set[str]` record FIELD is `map string
(option int)` (present ≡ `Some 0`) with the NATIVE string element as key (cleared-hash
S4). The SET-UNION `self.s | {"b"}` must add the element with the SAME raw native string
key its `.add`/membership uses — `map_update_some self.s "b" 0` — NOT the retired opaque
`str_hash_op "b"` (an `int`), which cannot index a `map string` field (a WhyML type error).
I2 threads the field's κ=string into the union's key so write and read agree.

After clearing to the empty set, adding "a", then UNIONING in {"b"}, both "a" and "b" are
provably present in the union, and the DISTINCT element "c" is provably absent. Under the
retired `str_hash_op` the union either ill-typed (int key into a `map string` field) or —
in an int-keyed model — `str_hash_op "c"` could collide with `str_hash_op "a"`/`"b"`, so
"c"'s absence could not be excluded. Native `String.(=)` makes both the presence and the
absence provable, on ONE consistent raw string key across `.add`, `|`, and `in`.
"""
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
    def string_set_union(self) -> int:
        self.s = set()
        self.s.add("a")
        t = self.s | {"b"}
        if "a" in t and "b" in t and "c" not in t:
            return 1
        return 0


if __name__ == "__main__":
    obj = Seen()
    assert obj.string_set_union() == 1
