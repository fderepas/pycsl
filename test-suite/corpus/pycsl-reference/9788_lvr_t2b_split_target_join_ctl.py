r"""Test 9788 -- cap-typed-local-lowering T2b CONTROL (run #7 lvR): the join of the split-target
`seq string` type-checks as the string `str_join_seq` and the function verifies (expected PASS)."""
# pycsl-expected: PASS
from typing import List


#@ assigns \nothing
def rejoin(s: str) -> str:
    parts: List[str] = []
    for line in s.splitlines():
        parts.append(line)
    return "\n".join(parts)


if __name__ == "__main__":
    print("result", rejoin("a\nb"))
