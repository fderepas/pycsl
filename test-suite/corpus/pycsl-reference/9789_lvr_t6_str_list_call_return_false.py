r"""Test 9789 -- cap-typed-local-lowering T6 (run #7 lvR): a `-> List[str]` function that returns
the `-> List[str]` result of another call bridges it with `snapshot_str` (was the int `snapshot`, a
Why3 type error outside `@mutable_state`). `len(\result) == 7` is FALSE (it is `len(xs)`) and must NOT
prove (expected FAIL)."""
# pycsl-expected: FAIL
from typing import List


#@ assigns \nothing
def strip_all(xs: List[str]) -> List[str]:
    out: List[str] = []
    for x in xs:
        out.append(x.strip())
    return out


#@ ensures len(\result) == 7
#@ assigns \nothing
def norm(xs: List[str], fold: bool) -> List[str]:
    if fold:
        return []
    return strip_all(xs)


if __name__ == "__main__":
    print("result", norm([" a "], False))
