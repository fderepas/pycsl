"""Test 0706 — named (registry) predicate p(self.field) in a #@ class invariant.

allocator-frame plan §5 / commit 755f89e: a `predicate` declared in the `_AXIOM_FUNCTIONS`
registry (here `field_nonneg`, from the `Pycsl.Reference.FieldPred.` namespace) can be
referenced BARE in a `#@ class invariant` — `field_nonneg(self.x)`. The
`_precompute_axiom_logic_funcs` predicate-recognition (755f89e extended `_names_of` and the
two decl-emitters to accept `predicate FOO` decls) makes it bind to the registry symbol,
NOT an unbound arity-suffixed abstract op; the decl is emitted before the record, and the
DEFINITIONAL intro/elim axioms (`field_nonneg x <-> x >= 0`, ZERO trusted-base growth)
discharge BOTH establishment (the constructor's `self.x = 0`) and maintenance (`bump`).

This is the standalone analogue of the os `uniq` / `inode_bytes_valid` class invariants
whose atom form fixes the allocator body gate (§2a). No `#@ proof` citation is needed —
referencing the predicate in the invariant is what pulls in its decl + axioms.
"""


#@ class invariant field_nonneg(self.x)
class C:
    #@ assigns self.x
    #@ ensures self.x == 0
    def __init__(self) -> None:
        self.x: int = 0

    #@ assigns self.x
    def bump(self) -> None:
        self.x = self.x + 1
