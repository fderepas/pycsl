"""Test 0195 — PyCSL Annotation Reference 4.4 (recursive pure function in contract)"""
""  # pycsl
#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
#@ \variant n
def sum_to(n: int) -> int:
    if n == 0:
        return 0
    return n + sum_to(n - 1)

#@ requires n >= 0
#@ ensures \result == sum_to(n) * 2
#@ assigns \nothing
def double_sum(n: int) -> int:
    return sum_to(n) + sum_to(n)

if __name__ == "__main__":
    assert sum_to(5) == 15
    assert double_sum(5) == 30
