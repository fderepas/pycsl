r"""Test 4389 -- gen #37 route #332 (expected PASS): CONTROL: a TRUE `assert x == 2, "msg"` under `no_exception \all` PROVES (the obligation is discharged).
"""
# pycsl-expected: PASS
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g() -> int:
    x = 2
    assert x == 2, "msg"
    return 7

if __name__ == "__main__":
    print(g())
