r"""Test 2271 — route #242 (expected FAIL): the `type(x) == bool` spelling of 2270. The body reads
the opaque program `val` `py_type_1`, frozen per argument inside a `let function`, so `h(True) ==
h(1)` (both `h 1`) PROVED `\result == 1` at f0fc0201; CPython `m()` = 0. Now a plain `let`: unproved.
"""
# pycsl-expected: FAIL


#@ assigns \nothing
def h(x: int) -> int:
    if type(x) == bool:
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    if h(True) == h(1):
        return 1
    return 0
