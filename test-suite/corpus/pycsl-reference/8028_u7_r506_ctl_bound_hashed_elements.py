r"""Test 8028 -- route #506 (control, expected PASS): the honest shapes of 5044 (now refused: a subscript inside a set display is never evaluated by the lowering) with the advice followed -- the tuple component and the guarded dict value are bound by plain statements first, then hashed (`{w}`, `{fv}`), so each subscript carries its own obligation under `#@ no_exception \all`; CPython g((1, 2), {0: F(1)}) returns 2
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class F:
    x: int


#@ no_exception \all
#@ ensures \result == t[1]
def g(t: Tuple[int, int], m: Dict[int, F]) -> int:
    w = t[1]
    u = {w}
    if 0 in m:
        fv = m[0]
        v = {fv}
    return w


if __name__ == "__main__":
    print("result", g((1, 2), {0: F(1)}))
