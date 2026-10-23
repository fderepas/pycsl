r"""Test 1820 — ROUTE #220 WITNESS (expected FAIL): an explicitly-called `__str__` that
writes self state was modelled PURE, by a recognizer that ran BEFORE route #218's repair.

This is route #218's hole in its second spelling, and it was found by an INDEPENDENT
REVIEWER running the oracle on #218's own repair — one grep from the site the repair
touched.

`_handle_call_expr` recognized `x.__str__()` early and returned

    val str_dunder_op () : string

— nullary, contractless, and with no `writes`, which Why3 reads as PURE. Route #218's
body-derived frame lives in `_resolve_dotted_signature`, which this branch RETURNS long
before. So the file below PROVED `\result == 0` while CPython answers **-7**, and the TRUE
twin (`== -7`) FAILED: a false contract proving while the true one is rejected, at the
parent commit and — the reviewer checked — under the emit-dunders spike as well, where the
emitted `let c____str__` exists and the call site ignores it.

LESSON (n3) IN THE DIRECTION NOBODY LOOKS FOR: a check that runs first can retire a REPAIR
as easily as it retires a refusal. #218 was landed, gated and byte-swept the same morning,
and this spelling was outside all of it.

THE REMEDY IS #218's, UNCHANGED: the result stays an opaque string (nothing is claimed about
it) and the receiver's fields stop being provably unchanged, so a FALSE claim becomes an
ABSENT one. Both `\result == 0` and `\result == -7` now FAIL.

SCOPE, RE-COUNTED RATHER THAN INHERITED: the old recognizer's comment asserted "byte-clean
(no corpus driver calls `.__str__()`)". True, and still true — ZERO in pycsl-reference,
ZERO in python-reference, ZERO in `pycsl_lib`. The eight real sites are `super().__str__()`
in the mirror (3) and the live tree (5), which have no record receiver and keep the nullary
op. Control 1821.
"""
# pycsl-expected: FAIL


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    def __str__(self) -> str:
        self.v = 7
        return "x"


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _s: str = c.__str__()
    after: int = c.v
    return before - after
