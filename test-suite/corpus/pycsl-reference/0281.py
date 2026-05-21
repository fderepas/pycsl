"""Test 0281 — Negative: \\result in requires (semantic error E1)"""
# pycsl-expected: FAIL

#@ requires \result >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def bad_precondition(x: int) -> int:
    return x

if __name__ == "__main__":
    print("PASS")
