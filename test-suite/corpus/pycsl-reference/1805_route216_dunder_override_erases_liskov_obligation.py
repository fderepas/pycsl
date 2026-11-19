r"""Test 1805 — ROUTE #216, THE EXPLOIT ARM (now REFUSED): a DUNDER override erases the
Liskov obligation.

`Sub.__len__` returns 0 under `#@ ensures \result == 0`; `Base.__len__` promises
`\result >= 5`. That is a substitutability violation, and `--check-behavioral-subtyping`
was asked to check exactly this.

AT THE COMMIT THIS FILE WAS WRITTEN ON, IT REPORTED:

    [+] Verification SUCCESS! All contracts formally proven.

over a module whose entire body was `type sub = {  }` — no methods, no override pair, NO
GOAL. Dunders are not emitted as functions, so the pair is never RECORDED, and
`PYCSL-SUBTYPING-PAIR` (written for this hazard, naming route #97) only fires on a pair
that was recorded and cannot be RESOLVED. CPython ground truth: `Sub().__len__()` is 0.

The decisive twin is 1808: the SAME program with `m` instead of `__len__` builds
`goal sub__m_refines_base`, cannot prove it, and FAILS. One identifier apart.

Now refused with `PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED`. If this file ever reports SUCCESS
again, the obligation is being dropped a second time.
"""
# pycsl-flags: --check-behavioral-subtyping --memory-model hoare
# pycsl-expected: FAIL
_ = 0  # anchor


class Base:
    #@ ensures \result >= 5
    def __len__(self) -> int:
        return 5


class Sub(Base):
    #@ ensures \result == 0
    def __len__(self) -> int:
        return 0
