r"""Test 8437 -- route #528 (control, expected PASS): a parameter index under `requires i == 0 or i == -1` discharges the PyCSL-R528 assertion; CPython returns 2 / 1
"""
# pycsl-expected: PASS
#@ requires i == 0 or i == -1
#@ no_exception \all
#@ ensures \result >= 0
def f(s: str, i: int) -> int:
    return len(s.split(",")[i])


if __name__ == "__main__":
    print("result", f("ab", 0), f("a,b", -1))
