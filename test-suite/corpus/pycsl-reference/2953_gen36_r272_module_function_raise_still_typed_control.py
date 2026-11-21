r"""Test 2953 — gen #36 r272 (expected FAIL): control: the MODULE-function form was never the hole — `chk(k)` is applied
concretely and Why3's effect typing refuses the unlisted ValueError at 5fe6cbdd and after (the
new rule does not fire on it). CPython raises ValueError for `m(1)`.
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
def chk(k: int) -> int:
    if k > 0:
        raise ValueError("bad")
    return 0


#@ ensures \result == 7
#@ no_exception \all
def m(k: int) -> int:
    chk(k)
    return 7


if __name__ == "__main__":
    try:
        m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
