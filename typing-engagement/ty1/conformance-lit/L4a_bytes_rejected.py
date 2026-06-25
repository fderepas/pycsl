"""Static gate L4a (negative) — `bytes` literals REJECTED (L4a / PEP 586).

Spec clause L4a (literal-twoplane-spec.md §1.4): `bytes` literals
(`b"..."`) are NOT permitted as `Literal` arguments. PEP 586 (S2)
restricts `Literal` to int/str/bool/None literals. A `Literal[b"x"]`
form is a static error, raised at the front-end normalization seam
before any WhyML is emitted.

Expected (from spec): FAIL (PIPELINE ERROR — `bytes` not supported).
"""

# pycsl-expected: FAIL
from typing import Literal


#@ assigns \nothing
def f(x: Literal[b"x"]) -> int:
    return 0


if __name__ == "__main__":
    print("PASS")
