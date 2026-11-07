r"""Test 1833 — gen #31 (expected FAIL/REFUSED): route #216's refusal, in its NARROWED form.

Route #219's build emits every dunder but the CONSTRUCTOR HOOKS (`__init__`, `__new__`,
`__post_init__`), so the #216 refusal — "a DUNDER is not emitted as a function, so no
override pair is recorded and NO refinement goal is built" — was narrowed to exactly those.

This file is what keeps that refusal WITNESSED. `Sub` overrides `Base.__new__`; neither is
emitted, so the pair is not recorded and no goal would be built, and the run would otherwise
report `All contracts formally proven` with the substitutability obligation silently absent.
It is refused instead.

Without this file the narrowed refusal would have no witness at all, because 1805/1806 —
the files that used to fire it — now EMIT and fail on the real `goal
sub____len___refines_base` instead. A refusal that loses its last witness when a repair
lands is how a check quietly becomes untested; `bin/check-refusal-witness-coverage.py`
exists to measure exactly that, and this file is what keeps its count honest.
"""
# pycsl-flags: --check-behavioral-subtyping --memory-model hoare
# pycsl-expected: FAIL
_ = 0  # anchor


class Base:
    def __new__(cls):
        return object.__new__(cls)


class Sub(Base):
    def __new__(cls):
        return object.__new__(cls)
