"""Test 0656 — L2 arg-materialize (os-bodyvc-spec): a seq-promoted local passed to bytes() materializes.

`parts = []; parts += [1, 2]` makes `parts` seq-promoted; `bytes(parts)` needs `array int` but `parts`
is `seq int`. Previously this was a Why3 `@rho` type error (the real `_pack_inode`'s `return bytes(parts)`
only worked inlined). The call-arg coercion now bridges seq→array via `materialize` (length+element
preserving), so `len(bytes(parts)) == 2` proves. (Reuses the return-arr materialize bridge, now at a
call-arg boundary rather than only return boundaries.)
"""


#@ requires True
#@ assigns \nothing
#@ ensures \result == 2
def f() -> int:
    parts = []
    parts += [1, 2]
    data = bytes(parts)
    return len(data)
