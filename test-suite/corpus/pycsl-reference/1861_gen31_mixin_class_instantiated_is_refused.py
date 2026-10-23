r"""Test 1861 — gen #31 WITNESS: a `#@ mixin` class CONSTRUCTED directly is refused.

The second documented consequence of §2.7 row 1 — "Marks the class as a composable mixin
(**not instantiated directly**)" — and the half that `1857` deliberately did not reach for.
Measured before the repair: a `#@ mixin` class with a real `__init__`, instantiated and
called from a free function, VERIFIED — and so did the identical file with the marker
deleted, so the two were indistinguishable.

WHY IT MATTERS, stated as the reading it protects: a mixin's methods are verified against
the COMPOSER's record (the flatten-and-re-verify discipline, S2b / finding w66), so a
direct construction produces an object whose own methods were never proved over it, and
its `__init__` and class invariant are written to be read as part of a composer.

Refused at `_run_pipeline` with `PYCSL-SEM-MIXIN-INSTANTIATED`, beside the compose-side
half whose marked-name set it reuses. ONLY the callee position counts: a mixin name in an
ARGUMENT (`isinstance(x, MixinCls)`) or in an annotation is not a construction.

CENSUS BEFORE LANDING, by AST rather than by grep: 20 sources declare `#@ mixin`, 19
marked classes between them, and ZERO constructor calls of any of them anywhere in the
corpus, `src/`, the mirror or `pycsl_lib`.

Control: 1862, the identical file with the marker removed, which verifies — so the refusal
is about the MARKER and not about constructing a class.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ mixin
class CoreEmit:
    def __init__(self) -> None:
        self.program_ir: int = 0

    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0


#@ ensures \result >= 0
#@ assigns \nothing
def go() -> int:
    c: CoreEmit = CoreEmit()
    return c.emit(3)
