"""Test math.gcd L5 — negative: caller violates requires integers >= 0."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import math  # noqa: F401


#@ ensures \result >= 0
def gcd_of_anything(n: int) -> int:
    # No `requires n >= 0` — math.gcd's precondition cannot be
    # discharged here under full proof.
    return math.gcd(n)


if __name__ == "__main__":
    pass
