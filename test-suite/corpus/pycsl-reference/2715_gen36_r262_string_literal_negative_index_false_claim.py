r"""Test 2715 — route #262 (expected FAIL): the string arm never had even the literal
rewrite — `s[-1] == ""` PROVED over a length-2 string at b35d9c5e. CPython: "ab"[-1] == "b".
"""
# pycsl-expected: FAIL


#@ requires len(s) == 2
#@ ensures s[-1] == ""
#@ assigns \nothing
def f(s: str) -> int:
    return 0


if __name__ == "__main__":
    assert f("ab") == 0 and "ab"[-1] == "b"
