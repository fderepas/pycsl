r"""Test 9787 -- cap-typed-local-lowering T2b (run #7 lvR): a `List[str]` local grown only from the
target of `for line in s.splitlines()` is a `seq string`, so `"\n".join(parts)` is the string
`str_join_seq` (was the opaque int `join_1`, a Why3 type error). `\result == "x"` is FALSE in general
and must NOT prove (expected FAIL)."""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == "x"
#@ assigns \nothing
def rejoin(s: str) -> str:
    parts: List[str] = []
    for line in s.splitlines():
        parts.append(line)
    return "\n".join(parts)


if __name__ == "__main__":
    print("result", rejoin("a\nb"))
