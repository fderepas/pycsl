r"""Test 1846 — gen #31: two `#@ verify_module` groups that call EACH OTHER (expected PASS).

The case the old interleaved emission order could not express at all. `Amod.a_top` calls
`Bmod.b_leaf` and `Bmod.b_top` calls `Amod.a_leaf`, so each provider module needs the
other's proven interface — and Why3 requires a module to be defined earlier in the file
than any use of it, which no single interleaved ordering can give both.

Emitting ALL `<G>Sig` modules first and THEN all providers makes the question disappear
rather than answering it: a `<G>Sig` is bodyless `val`s over `Shared` and can never
depend on a provider, so the Sig layer is acyclic BY CONSTRUCTION and the `use` edges run
provider -> Sig only. Mutual recursion between groups then costs nothing.

This file is the reason the repair is a REORDERING and not a topological sort of the
groups: a sort would have to fail on this input, and there is nothing here to fail on.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ verify_module Amod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def a_leaf(self) -> int:
        return 3

    #@ verify_module Amod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def a_top(self) -> int:
        return self.b_leaf()

    #@ verify_module Bmod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def b_leaf(self) -> int:
        return 5

    #@ verify_module Bmod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def b_top(self) -> int:
        return self.a_leaf()
