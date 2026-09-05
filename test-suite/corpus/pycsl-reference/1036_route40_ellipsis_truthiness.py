"""Test 1036 — ROUTE #40 negative witness (a): the truthiness of `...`.

FALSE OF THE PROGRAM: `bool(Ellipsis)` is True, so Python returns 7.

Module 5 lowers the `...` literal to `{"type":"Number","value":0,"py_ellipsis":True}`
(`_py_expr_constant`). Relaunch #12 FLAGGED that as "a silent WRONG-VALUE erasure ...
left alone deliberately, because giving `...` a real node type would turn a silent 0
into a hard compile error". IT WAS NEVER PROBED. At the parent commit b5fb0688 the
emission was

    let x = ref 0 in
    x := 0;
    if (!x <> 0) then ... else ...

so `\result == 0` PROVED while Python returns 7. This is #44's rule firing again:
AN ERASURE TO A LITERAL IS ONE `if` AWAY FROM A FALSE PROOF.

The fix is an OPAQUE value (`val function pycsl_ellipsis : int`, no defining axiom),
not a refusal — see 1037-1040 for the four other shapes it closes at the same time,
and note that the model did not merely LOSE the value, it CONFLATED `...` with the
integer 0, which is what made the comparisons decide the wrong way.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = ...
    if x:
        return 7
    return 0
