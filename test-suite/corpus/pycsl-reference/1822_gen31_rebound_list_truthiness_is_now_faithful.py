r"""Test 1822 — gen #31: the TRUE twin of witness 1804 now PROVES.

1804 is the tripwire the previous generation left behind:

    a: list = []
    if n > 0: a = [1, 2]
    if a: return 1
    return 2                       # CPython f(0) -> 2

`_emit_array_local_reassign` lowers the rebinding as "reset the counter, then append each
element" — it WRITES `a_len` — but the `let <tgt>_len = ref 0 in` declaration was emitted
only for `.append` targets, so `a_len` was UNBOUND and L3-tc refused the module. Behind
that accident sat route #31's archetype: truthiness lowered to `Array.length a <> 0` over an
`Array.make 1024 0` shadow, i.e. ALWAYS TRUE. 1804's own docstring says what it is for —
"the day someone declares the counter, this file starts PROVING".

Gen #31 declared the counter AND routed BOTH length answers through it (truthiness and
`len`), so the model is faithful rather than merely blocked. This file is the payoff: with
`n == 0` the list is empty, CPython returns 2, and PyCSL now proves it.

THE OTHER HALF WAS NOT OPTIONAL AND WAS PROVED NECESSARY BY A FALSE CLAIM. With the counter
declared and truthiness fixed but `len` left alone, `a: list = [7,8,9]; if n > 0: a = [1,2];
return len(a)` PROVED `\result == 3` (CPython 2) because `len` fell through to
`Array.length a` — the length of the array the FIRST literal allocated. 1823/1824 pin both
directions.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires n == 0
#@ ensures \result == 2
def f(n: int) -> int:
    a: list = []
    if n > 0:
        a = [1, 2]
    if a:
        return 1
    return 2
