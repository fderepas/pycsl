r"""Test 5293 -- gen #37 route #386 (expected FAIL): `def max` nested in a PLAIN function; FAIL at base (the lifted def is an unknown int), REFUSED after (route #386).
"""
# pycsl-expected: FAIL
#@ ensures \result >= 3
#@ assigns \nothing
def m(a: int) -> int:
    def max(x: int, y: int) -> int:
        return -100
    return max(3, a)


if __name__ == "__main__":
    r = m(1)
    print("VIOLATION m() =", r) if r < 3 else print("no violation")
