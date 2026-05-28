"""Test 0332 — PyCSL Annotation Reference 2.1.11 — Proof attribution (rocq + lean dual)."""
_ = 0  # anchor
#@ requires 1 == 1
#@ ensures \result == x * 2
#@ ensures \result % 2 == 0
#@ assigns \nothing
def double_dual_attribution(x: int) -> int:
    """Dual rocq+lean attribution above a real contract.

    Verifies that proof attributions do not interfere with VC generation:
    both ensures clauses must still discharge."""
    return x * 2

if __name__ == "__main__":
    assert double_dual_attribution(3) == 6
    assert double_dual_attribution(0) == 0
