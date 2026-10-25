r"""Test 5309 -- gen #37 route #387 (expected FAIL): `nonlocal get` in a function-local class body before `def get`; FAIL at base, REFUSED after (route #387).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
def mk() -> int:
    get = 0

    class C:
        nonlocal get

        #@ ensures \result == 1
        #@ assigns \nothing
        def get(self) -> int:
            return 1
    return C().get()


if __name__ == "__main__":
    try:
        r = mk()
        print("VIOLATION", r) if r != 1 else print("no violation")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
