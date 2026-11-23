r"""Test 10361 -- run #9 u65, route #619 (expected PASS): over-refusal CONTROL. A genuine (non-vacuous) mutual recursion `ev` / `od`, emitted as one `let rec ... with ...` group: both members are now probed by the non-vacuity gate and neither is vacuous (each `requires n >= 0` is satisfiable), so the true range claims prove.
"""
# pycsl-expected: PASS


#@ requires n >= 0
#@ ensures \result >= 0 and \result <= 1
#@ \variant n
#@ assigns \nothing
def ev(n: int) -> int:
    if n == 0:
        return 1
    return od(n - 1)


#@ requires n >= 0
#@ ensures \result >= 0 and \result <= 1
#@ \variant n
#@ assigns \nothing
def od(n: int) -> int:
    if n == 0:
        return 0
    return ev(n - 1)


if __name__ == "__main__":
    ok = all(ev(k) == 1 - k % 2 and od(k) == k % 2 for k in range(12))
    print("result" if ok else "VIOLATION contract", ev(7), od(7))
