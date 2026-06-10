"""Test 0695 — `#@ \\diverges` rejected on a provably-terminating (straight-line) body."""
# pycsl-flags: --no-proof
# pycsl-expected: FAIL
_ = 0  # anchor

# `#@ \diverges` is the escape from Why3's termination VC: it asserts the body MAY fail to
# terminate. Why3 then enforces the dual obligation — the body must in fact be able to
# diverge — and rejects a provably-terminating body with "this expression does not diverge".
# PyCSL catches this at semantic time (Module4._validate_diverges, refactor.md Phase D2):
# a straight-line body with no critical section / no loop / no call-or-recursion cannot
# diverge, so `#@ \diverges` is unjustified and is a hard error (rather than emitting WhyML
# that silently fails to type-check — the dishonest SUCCESS the honest gate forbids).
#@ \diverges
#@ ensures \result == 0
def straight_line() -> int:
    x = 1
    y = x + 1
    return y - y


if __name__ == "__main__":
    print("PASS")
