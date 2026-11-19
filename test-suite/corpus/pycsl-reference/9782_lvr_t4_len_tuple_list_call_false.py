r"""Test 9782 -- cap-typed-local-lowering T4 (run #7 lvR): `len(f(..))` of a call returning the
`array pytuple_str_str` of a scalar-slot `-> List[Tuple[str, str]]` function is the ARRAY length (was
the opaque `iter_length : int -> int`, a Why3 type error). `\result == 5` is FALSE (it is `len(xs)`),
so it must NOT prove (expected FAIL)."""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ assigns \nothing
def pairs(xs: List[str]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for x in xs:
        out.append((x, "a"))
    return out


#@ ensures \result == 5
#@ assigns \nothing
def count(xs: List[str]) -> int:
    return len(pairs(xs))


if __name__ == "__main__":
    print("result", count(["p"]))
