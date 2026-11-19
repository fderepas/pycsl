r"""Test 5298 -- gen #37 route #386 (expected FAIL): function-local `class abs`, `abs(a).v`; FAIL at base, REFUSED after (builtin rebound by a nested class, route #386).
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def m(a: int) -> int:
    class abs:
        def __init__(self, v: int) -> None:
            self.v: int = -1
    return 0 if abs(a).v < 0 else 1


if __name__ == "__main__":
    r = m(-5)
    print("VIOLATION m() =", r) if r != 1 else print("no violation")
