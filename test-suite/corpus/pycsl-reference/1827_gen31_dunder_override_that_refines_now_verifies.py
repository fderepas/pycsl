r"""Test 1827 — gen #31 (expected PASS): a CORRECT dunder override is now CHECKED and PASSES.

This is corpus 1805 with `Sub.__len__` STRENGTHENED instead of weakened (`\result == 7`
refines `\result >= 5`). It is the payoff half of route #216, and before dunders were
emitted it did not exist as a category at all:

  * BEFORE, every dunder override under `--check-behavioral-subtyping` was REFUSED
    (`PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED`), because the pair was never recorded and no
    refinement goal was built. The refusal stopped the LIE — the run would otherwise have
    said "All contracts formally proven" with the substitutability obligation absent — but
    it also meant a correct override could not be CERTIFIED, only declined.
  * NOW the methods are emitted, the pair is recorded, `goal sub____len___refines_base` is
    BUILT, and it DISCHARGES. 1805 (a weakened override) still fails, and it now fails on
    that goal rather than on the refusal — which is the difference between "we refuse to
    look" and "we looked and it does not hold".

The refusal is KEPT for the dunders that are still dropped (`__init__`, `__new__`,
`__post_init__`), where the original hazard is unchanged.

Measured by the independent reviewer of the emit-dunders report (oracle O6), which first
showed that removing the skip ALONE leaves 1805 refused and no goal built — so the report's
claim that "the Liskov obligation becomes CHECKABLE" would have shipped FALSE without
narrowing the refusal in the same increment.
"""
# pycsl-flags: --check-behavioral-subtyping --memory-model hoare
# pycsl-expected: PASS
_ = 0  # anchor


class Base:
    #@ ensures \result >= 5
    def __len__(self) -> int:
        return 5


class Sub(Base):
    #@ ensures \result == 7
    def __len__(self) -> int:
        return 7
