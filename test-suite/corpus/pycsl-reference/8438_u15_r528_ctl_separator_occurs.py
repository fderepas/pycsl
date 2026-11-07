r"""Test 8438 -- route #528 (control, expected PASS): `s.split(",")[1]` / `s.split(",", 1)[-2]` after `if "," not in s: return 0` -- the separator occurs, so there are at least two pieces and the PyCSL-R528 assertion is discharged by the `str_contains_op` law; CPython returns 0 / 2
"""
# pycsl-expected: PASS


#@ no_exception \all
#@ ensures \result >= 0
def f(s: str) -> int:
    if "," not in s:
        return 0
    a = s.split(",")[1]
    b = s.split(",", 1)[-2]
    return len(a) + len(b)


if __name__ == "__main__":
    print("result", f("ab"), f("a,b"))
