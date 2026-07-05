"""Test 0876 — set-model faithful membership lowering lock (POSITIVE).

Locks the module-level constant string-set membership recognizer. A top-level
`ROCQ_KERNEL_AXIOM_ALLOWLIST = {"propext", ...}` (and the `frozenset({...})` form)
read via `x in NAME` lowers to a FAITHFUL disjunction of string equalities
    (str_eq_op x "propext" || str_eq_op x "Classical.choice" || ...)
— exactly the `name.strip() in ROCQ_KERNEL_AXIOM_ALLOWLIST` shape in
`proof_axiom_allowlist.is_rocq_assumption_allowed`, whose string membership
previously leaked to the opaque int `contains_check` ("string expected int").

Three laws:
  (HIT)   "propext" in ALLOWLIST      == True   — a member returns true.
  (MISS)  "no_such_axiom" in ALLOWLIST == False  — a non-member returns false.
  (NOTIN) "no_such_axiom" not in ...   == True   — `not in` negates faithfully.
All discharge (best-of-N: Z3's native string theory decides the miss/fall-through
disequalities). NO new axiom, NO `\trusted`.
"""
ROCQ_KERNEL_AXIOM_ALLOWLIST = {
    "propext",
    "Classical.choice",
    "Quot.sound",
}

LEAN_KERNEL_AXIOM_ALLOWLIST = frozenset({
    "propext",
    "Classical.choice",
    "Quot.sound",
})


#@ requires name == "propext"
#@ ensures \result == True
def rocq_member_hit(name: str) -> bool:
    """"propext" is in ROCQ_KERNEL_AXIOM_ALLOWLIST — membership is true."""
    return name in ROCQ_KERNEL_AXIOM_ALLOWLIST


#@ requires name == "no_such_axiom"
#@ ensures \result == False
def rocq_member_miss(name: str) -> bool:
    """"no_such_axiom" is absent — membership is false."""
    return name in ROCQ_KERNEL_AXIOM_ALLOWLIST


#@ requires name == "no_such_axiom"
#@ ensures \result == True
def rocq_not_in(name: str) -> bool:
    """`not in` negates faithfully: an absent key is `not in` the set."""
    return name not in ROCQ_KERNEL_AXIOM_ALLOWLIST


#@ requires name == "Quot.sound"
#@ ensures \result == True
def lean_member_hit(name: str) -> bool:
    """The `frozenset({...})` form recognizes identically to the set-display."""
    return name in LEAN_KERNEL_AXIOM_ALLOWLIST


if __name__ == "__main__":
    assert rocq_member_hit("propext") is True
    assert rocq_member_miss("no_such_axiom") is False
    assert rocq_not_in("no_such_axiom") is True
    assert lean_member_hit("Quot.sound") is True
