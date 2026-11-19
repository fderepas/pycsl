r"""Test 9781 -- cap-typed-local-lowering T3 CONTROL (run #7 lvR): a scalar-slot tuple-display
append into the returned `List[Tuple[str, str]]` local type-checks (a `seq pytuple_str_str` of real
records, returned through `materialize_pytuple_str_str`) and the function verifies (expected PASS)."""
# pycsl-expected: PASS
from typing import List, Tuple


#@ assigns \nothing
def pairs(xs: List[str]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for x in xs:
        out.append((x, "a"))
    return out


if __name__ == "__main__":
    print("result", pairs(["p", "q"]))
