"""Test 0795 — cleared-hash residual-close 1(a): distinct-key non-aliasing on a
CONCATENATION-keyed un-annotated local (κ-inference shrink).

An un-annotated dict local (`d = {}`) keyed by a string CONCATENATION `a + b` is now
inferred string-keyed (κ = string; cleared-hash residual-close 1(a) extends the Module5
`_is_str_key` signal to a `str + str` BinOp). It lowers to `map string (option ν)` with the
native key `str_concat_op a b`, whose emitted contract pins it to Why3's `concat` (with the
length axiom → concat is left-cancellative: `concat a b = concat c b -> a = c`). So a
precondition `a != c` gives `a + b != c + b`, and after `d[a+b] = v1; d[c+b] = v2` the read
`d[a+b]` is still `v1` — writing the `c + b` entry cannot disturb the `a + b` entry.

UNPROVABLE under the retired opaque-hash model: before 1(a), a concat key routed through the
bodyless `str_hash_op` (`str_hash_op (str_concat_op a b)`), so `a != c` did NOT imply
`str_hash_op (str_concat_op a b) != str_hash_op (str_concat_op c b)` (hashing admits a
collision) — the prover had to admit `d[c+b]=v2` might clobber `d[a+b]`. Native concat keys
remove that collision. This is the positive witness that the inference shrink is SOUND and
recovers a distinct-key property the opaque hash could not."""
_ = 0  # anchor
#@ requires a != c
#@ ensures \result == v1
#@ assigns \nothing
def concat_key_non_aliasing(a: str, b: str, c: str, v1: int, v2: int) -> int:
    d = {}
    d[a + b] = v1
    d[c + b] = v2
    return d[a + b]
