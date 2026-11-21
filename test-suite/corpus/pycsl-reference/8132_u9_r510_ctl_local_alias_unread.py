r"""Test 8132 -- route #510 (control, expected PASS): a function-local `type V = list[int]` used only to annotate a local, and `assert V is not None` (a TypeAliasType is never None: exact in CPython); CPython f() returns 3
"""
# pycsl-expected: PASS


#@ ensures \result == 3
def f() -> int:
    type V = list[int]
    assert V is not None
    x: int = 3
    return x


if __name__ == "__main__":
    print("result", f())
