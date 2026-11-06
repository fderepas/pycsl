r"""Test 9146 -- lvD3 control (expected PASS, as under C2): the visit_MatchStar shape with
`is not None` -- every read of `name` is an `is (not) None` operand or a part of a two-or-more-part f-string,
so C2 still lowers `name = "?"` to its hash and the result is `str_concat_op "<" (..)`, never empty.
"""
# pycsl-expected: PASS
from __future__ import annotations


#@ ensures \result != ""
#@ assigns \nothing
def f(x) -> str:
    name = x
    if name is not None:
        return f"[{name}]"
    name = "?"
    return f"<{name}>"


if __name__ == "__main__":
    r = f(None)
    print("VIOLATION contract" if r == "" else "result", r)
