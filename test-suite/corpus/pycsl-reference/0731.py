"""Test 0731 — `Literal[1, 2]` parameter annotation (witness).

typing-engagement ty1 (26-0000-typing-spec-2): `Literal[v1, ..., vn]` is
desugared at the front-end normalization seam into a ground `requires` clause
`x = v1 \/ ... \/ x = vn` (L1). The parameter's WhyML type stays the literal's
base type (`int` for `Literal[1, 2]`), so `def f(x: Literal[1, 2]) -> int`
lowers to `let f (x: int) requires { x = 1 \/ x = 2 } = ...`. The contract
`\result == x` discharges under the synthesized precondition (the input is one
of {1, 2}, and the function returns it unchanged).
"""
from typing import Literal

#@ ensures \result == x
#@ assigns \nothing
def echo(x: Literal[1, 2]) -> int:
    return x

if __name__ == "__main__":
    assert echo(1) == 1
    assert echo(2) == 2
    print("PASS")
