"""Test math.sqrt L5 — negative: caller violates requires x >= 0.

This file exists to document the negative case in the
conventions; the actual `pycsl --proof` rejection happens when
the contract is dispatched to Why3. Marked `# pycsl-flags:
--no-proof` for the corpus run; the soundness claim is
exercised by manual proof-mode invocation.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ ensures \result >= 0
def root_of_anything(x: int) -> int:
    # No `requires x >= 0` here — math.sqrt's precondition
    # cannot be discharged at this call site under full proof.
    return math.sqrt(x)


if __name__ == "__main__":
    pass
