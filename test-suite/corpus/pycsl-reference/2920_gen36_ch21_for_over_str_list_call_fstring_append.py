r"""Test 2920 — gen #36 ch21 (expected PASS): a `for` over a CALL declared `-> List[str]`
appending f-strings to a `List[str]` local, then returned (the shape of the emitter's own
`preamble._emit_preamble_no_exception_predicates`). At base the call iterable fell to the
opaque `iter_length`/`iter_get : int -> int` (L3-tc: `array string` vs `int`) and the
f-string-grown local stayed `seq int` against the `-> List[str]` return (fail-closed). The
call is now evaluated ONCE into an `array string`, the loop target is a `string`, an f-string
seq element is a `string`, and the TRUE claims prove (CPython agrees, see __main__). `tag`
(no loop, `str` interpolation) already typed at base and is the control for the element
VALUE. Twins: 2921, 2922 (must FAIL).
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \length(\result) == 2
#@ assigns \nothing
def defs() -> List[str]:
    return ["a", "b"]


#@ ensures \length(\result) >= 1
#@ assigns \nothing
def indent_all() -> List[str]:
    out: List[str] = [""]
    #@ loop invariant \length(out) >= 1
    for line in defs():
        out.append(f"  {line}")
    return out


#@ ensures \length(\result) == 2
#@ ensures \result[0] == "" and \result[1] == "<" + s + ">"
#@ assigns \nothing
def tag(s: str) -> List[str]:
    out: List[str] = [""]
    out.append(f"<{s}>")
    return out


if __name__ == "__main__":
    r = indent_all()
    assert len(r) >= 1
    print(r)
    t = tag("x")
    assert len(t) == 2 and t[0] == "" and t[1] == "<" + "x" + ">"
    print(t)
