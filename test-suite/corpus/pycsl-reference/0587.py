"""Test 0587 — `\result[N]` constrains a tuple-returning `val` stub (1009.md R3).

A trusted/abstract helper emitted as a body-less `val` returns a tuple `(int, int)`. Its
`#@ ensures \result[0] >= 0` must lower to a per-component destructure
`ensures { (let (_r0_, _) = result in _r0_) >= 0 }` (NOT the abstract `subscript_get`, which
would be both wrong and unbound), and the constraint must reach a caller that tuple-unpacks
the result. This is the pattern `_unpack_direntry` + `_dir_lookup` rely on to preserve
`0 <= inode_num` after `found := inode_num`. Verified: the val stub emits `: (int, int)`
(arity inferred from the body return), `\result[0]` destructures, and `use` discharges
`\result >= 0` through the unpack.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ \trusted
#@ requires \valid(data, 32)
#@ ensures \result[0] >= 0
#@ assigns \nothing
def unpack_pair(data: list) -> tuple:
    return (data[0], data[1])


#@ requires \valid(d, 32)
#@ ensures \result >= 0
#@ assigns \nothing
def use(d: list) -> int:
    a, b = unpack_pair(d)
    return a
