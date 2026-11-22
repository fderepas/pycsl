r"""Test 10420 -- run #9 u70, review rt77 F1, route #624 (FAIL, PRE-EXISTING). `import qa70` beside a LOCAL
`def val1`: pycsl skipped the dependency's `val1` because the name was taken and lowered `qa70.val1()` to
the local one, so `g() == 2` PROVED at daa36070b. CPython runs qa70.val1 and prints "result 1".
REFUSED: PYCSL-SEM-IMPORT-FUNCTION-NAME-CLASH.
"""
# pycsl-expected: FAIL
import qa70


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return qa70.val1()


if __name__ == "__main__":
    print("result", g())
