r"""Test 1862 — gen #31 CONTROL for 1861 (expected PASS): without the marker it verifies.

Byte-identical to 1861 except that `class CoreEmit:` carries no `#@ mixin`. It verifies,
so the refusal in 1861 is about the MARKER — the class declared itself composable and is
then used on its own — and not about constructing a class, about `#@ shared_state`, or
about `#@ provides`.

Read together with 1857/1858 this pins both halves of §2.7 row 1 in both directions: a
`#@ compose_from` name must carry the marker, a marked class must not be constructed, and
neither rule fires on the shape it is not about.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


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
