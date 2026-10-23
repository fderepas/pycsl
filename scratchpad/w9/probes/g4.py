"""PROBE: a SLICE erased to literal 0 — consumed in a GUARD."""
_ = 0  # anchor

#@ requires \length(a) >= 4
#@ ensures \result == 0
def f(a: list) -> int:
    s = a[1:3]
    if s:
        return 7
    return 0

if __name__ == "__main__":
    print(f([1, 2, 3, 4]))
