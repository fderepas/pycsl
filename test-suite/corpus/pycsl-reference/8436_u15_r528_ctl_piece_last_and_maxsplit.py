r"""Test 8436 -- route #528 (control, expected PASS): `s.split(",")[-1]` and `s.split(":", 1)[0]` keep their lowering; CPython returns 4 / 4
"""
# pycsl-expected: PASS
#@ no_exception \all
#@ ensures \result >= 0
def f(s: str) -> int:
    return len(s.split(",")[-1]) + len(s.split(":", 1)[0])


if __name__ == "__main__":
    print("result", f("ab"), f("a,b"))
