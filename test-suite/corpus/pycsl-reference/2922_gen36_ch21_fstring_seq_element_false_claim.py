r"""Test 2922 — gen #36 ch21 (expected FAIL): FALSE twin of 2920's `tag`. The appended
element is the f-string `f"<{s}>"`, not `s` itself (CPython: `tag("x")[1] == "<x>"`), so
`\result[1] == s` must stay UNPROVED. (This all-`str`-interpolation shape already typed as a
`seq string` at base; the twin pins that the f-string seq element keeps its VALUE — the
`str_concat_op` chain — under the ch21 rule that an f-string element is a `string`.)
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \length(\result) == 2
#@ ensures \result[1] == s
#@ assigns \nothing
def tag(s: str) -> List[str]:
    out: List[str] = [""]
    out.append(f"<{s}>")
    return out


if __name__ == "__main__":
    t = tag("x")
    assert t[1] != "x"
    print(t)
