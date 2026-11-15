r"""Test 9783 -- cap-typed-local-lowering T4 CONTROL (run #7 lvR): `len(f(..))` of a
`-> List[Tuple[str, str]]` call is an ARRAY length, hence non-negative (expected PASS)."""
# pycsl-expected: PASS
from typing import List, Tuple


#@ assigns \nothing
def pairs(xs: List[str]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for x in xs:
        out.append((x, "a"))
    return out


#@ ensures \result >= 0
#@ assigns \nothing
def count(xs: List[str]) -> int:
    return len(pairs(xs))


if __name__ == "__main__":
    print("result", count(["p"]))
