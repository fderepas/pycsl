"""set-model POSITIVE driver.

A module-level constant string-set literal (`ROCQ_KERNEL_AXIOM_ALLOWLIST = {...}`,
and the `frozenset({...})` form) read via `x in NAME` membership lowers to a faithful
disjunction of string equalities. A member returns true (hit); a non-member returns
false (miss); `not in` negates faithfully. All discharge.
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
    """The `frozenset({...})` form recognizes identically."""
    return name in LEAN_KERNEL_AXIOM_ALLOWLIST


if __name__ == "__main__":
    assert rocq_member_hit("propext") is True
    assert rocq_member_miss("no_such_axiom") is False
    assert rocq_not_in("no_such_axiom") is True
    assert lean_member_hit("Quot.sound") is True
