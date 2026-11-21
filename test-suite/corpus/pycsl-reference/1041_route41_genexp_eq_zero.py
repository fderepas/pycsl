"""Test 1041 — ROUTE #41 negative witness (a): an erased local COMPARED to 0.

FALSE OF THE PROGRAM: a generator object is not equal to 0, so Python returns 0.

Routes #25/#26/#27 established that a local bound to a generator expression, a
non-empty set literal or a non-empty tuple literal is emitted as the LITERAL `0`, and
refused its TRUTHINESS in `_to_bool`. THE REFUSAL WAS PLACED WHERE THE DEFECT WAS
VISIBLE — the guard — AND NOT WHERE THE ERASURE IS, so every OTHER consumer of the same
local stayed exploitable. At the parent commit c37f0059 this proved `\result == 7`
with the emission `x := 0; if (!x = 0) then 7 else 0`.

Same window, same lesson as route #39: a fix that enumerates the dangerous CONSUMERS is
an under-approximation; the value itself has to stop being a decidable literal. The
read of such a name now lowers to a per-name opaque `val function pycsl_erased_<x>`,
which closes 1041-1045 at one stroke. PER-NAME matters: one shared constant would let
the model prove `x == y` for two distinct erased locals, trading one unsoundness for
another.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = (i for i in [1, 2, 3])
    if x == 0:
        return 7
    return 0
