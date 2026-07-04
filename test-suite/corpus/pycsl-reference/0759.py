"""Test 0759 — cleared-hash.md S5/S7: string SET local with native string elements.

A set of strings shares the dict `map` model: `set() ~ map string (option int)` (present ≡ `Some 0`)
with the NATIVE string element as key. `s.add("a")` writes the raw string "a"; `"b" not in s`
reads the raw string "b" — both agree (no `str_hash_op`). So after adding only "a", the DISTINCT
element "b" is provably absent.

UNPROVABLE under the opaque hash: `str_hash_op "b"` could collide with `str_hash_op "a"`, so
membership of "b" could not be excluded. Native `String.(=)` makes the absence provable — and keeps
the write (`.add`) and read (`in`) on the SAME key term (before this fix `.add` hashed while `in`
used the raw string, a type mismatch)."""
_ = 0  # anchor
#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def string_set_absent() -> int:
    s = set()
    s.add("a")
    if "b" not in s:
        return 1
    return 0
