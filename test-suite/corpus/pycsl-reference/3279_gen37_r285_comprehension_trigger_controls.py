r"""Test 3279 — route #285 controls (PASS): comprehensions whose expressions match no
`exception_model.TRIGGER_EXPR_SHAPES` row stay accepted under `no_exception \all` (`[x + 1 ...]`,
`sum(x for ...)`, `[x for ... if x > 0]`); a trigger shape whose exception is NOT in the claim
is not refused (`[str(x) ...]` / `[chr(x) ...]` / `[1 << x ...]` under `no_exception KeyError`); and a
function without `no_exception` is untouched.
"""
# pycsl-expected: PASS

from typing import List


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(xs: List[int]) -> int:
    a = [x + 1 for x in xs]
    c = sum(x for x in xs)
    d = [x for x in xs if x > 0]
    return 1


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception KeyError
def g(xs: List[int]) -> int:
    a = [str(x) for x in xs]
    b = [chr(x) for x in xs]
    c = [1 << x for x in xs]
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def h(xs: List[int]) -> int:
    a = [str(x) for x in xs]
    return 1


if __name__ == "__main__":
    assert f([1, 2, 3]) == 1
    assert g([65, 66]) == 1 and h([1]) == 1
    try:
        g([-1])
    except ValueError:
        print("g raises ValueError, outside its KeyError claim")
