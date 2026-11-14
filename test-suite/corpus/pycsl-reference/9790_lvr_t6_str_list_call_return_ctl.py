r"""Test 9790 -- cap-typed-local-lowering T6 CONTROL (run #7 lvR): the `snapshot_str`-bridged
`-> List[str]` call result has a non-negative length (expected PASS)."""
# pycsl-expected: PASS
from typing import List


#@ assigns \nothing
def strip_all(xs: List[str]) -> List[str]:
    out: List[str] = []
    for x in xs:
        out.append(x.strip())
    return out


#@ ensures len(\result) >= 0
#@ assigns \nothing
def norm(xs: List[str], fold: bool) -> List[str]:
    if fold:
        return []
    return strip_all(xs)


if __name__ == "__main__":
    print("result", norm([" a "], False))
