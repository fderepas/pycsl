"""range(n) used as a loop iterable. The stub contract treats the
result as iterable of integers in [0, n).
"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def sum_via_range(n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        total = total + 1
        i = i + 1
    return total


if __name__ == "__main__":
    assert sum_via_range(5) == 5
