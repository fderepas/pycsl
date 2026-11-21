r"""Test 5686 -- gen #37 CONTROL route #393 (the advice followed) (expected PASS): `D(SyntaxError)` constructed `(msg, (filename, lineno, offset, text))` and `(msg)` under `no_exception`; PROVED (CPython 1).
"""
# pycsl-expected: PASS
class D(SyntaxError):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(name: str) -> int:
    e = D("m", (name, 1, 2, "t"))
    g = D("only a message")
    return 1


if __name__ == "__main__":
    assert f("x.py") == 1
