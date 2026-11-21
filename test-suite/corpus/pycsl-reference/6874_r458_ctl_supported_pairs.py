r"""Test 6874 -- route #458 (expected PASS): CONTROL -- operator class triples CPython supports: `str + str`, `int + bool`. Not refused by PYCSL-R458-OPERAND-CLASSES.
"""
# pycsl-expected: PASS


#@ no_exception \all
#@ ensures \result == len(s) + len(t) + n + 1
def f(s: str, t: str, n: int) -> int:
    u = s + t
    return len(u) + n + True


if __name__ == "__main__":
    print("result", f("a", "bc", 2))
