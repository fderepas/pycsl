"""Test 0283 — Negative: undefined variable in ensures (semantic error E2)"""
# pycsl-expected: FAIL

#@ requires x >= 0
#@ ensures \result == x + unknown_var
#@ assigns \nothing
def bad_postcondition(x: int) -> int:
    return x

if __name__ == "__main__":
    print("PASS")
