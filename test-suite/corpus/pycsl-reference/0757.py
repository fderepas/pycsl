"""Test 0757 — cleared-hash.md S7: literal <-> variable key consistency.

A dict written with the string LITERAL "k" and read back with a str-typed VARIABLE `key` bound to
"k" reads the same entry: `d["k"] = v; ...; key == "k" -> d[key] == v`. With native string keys the
literal "k" and the variable `key` are the SAME Why3 string term (`key = "k"`), so the read hits the
write.

UNPROVABLE under the opaque hash: the literal write used the compile-time constant `stable_hash("k")`
while the variable read used the runtime `str_hash_op key` — two UNRELATED ints, never connected even
when `key == "k"`. Native string keys unify them."""
_ = 0  # anchor
#@ requires key == "k"
#@ ensures \result == v
#@ assigns \nothing
#@ no_exception KeyError
def literal_var_key(key: str, v: int) -> int:
    d = {}
    d["k"] = v
    return d[key]
