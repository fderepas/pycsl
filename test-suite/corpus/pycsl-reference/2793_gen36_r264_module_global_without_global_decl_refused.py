r"""Test 2793 — route #264 (expected FAIL, refused): module global `n = 5`, and `f` does
`n += 1` WITHOUT `global n`. The augmented assignment makes `n` local to all of `f`, so the
module binding is never consulted and the read raises `UnboundLocalError`. `\result == 1`
(the hoisted default 0, plus one) PROVED at 283d1033.
"""
# pycsl-expected: FAIL
n = 5

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    n += 1
    return n

if __name__ == "__main__":
    try:
        print(f())
    except UnboundLocalError as exc:
        print("UnboundLocalError:", exc)
