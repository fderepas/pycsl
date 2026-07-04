"""Test 0756 — cleared-hash.md S7: absent-key membership under native string keys.

After inserting only the string literals "a" and "b" into an un-annotated local dict, the key "c"
is provably absent (`"c" not in d`). With `map string (option ν)` the three literals are distinct
Why3 string terms, so `Map.get d "c" = None`.

UNPROVABLE under the opaque hash: `str_hash_op "c"` could collide with `str_hash_op "a"`, so the
prover cannot exclude `"c"` reading back a value. Native `String.(=)` makes the absence provable."""
_ = 0  # anchor
#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def absent_key_local() -> int:
    d = {}
    d["a"] = 1
    d["b"] = 2
    if "c" not in d:
        return 1
    return 0
