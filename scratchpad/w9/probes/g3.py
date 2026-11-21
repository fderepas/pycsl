"""PROBE: GenExp erased to literal 0 — consumed in a GUARD."""
_ = 0  # anchor

#@ requires True
#@ ensures \result == 0
def f() -> int:
    g = (i for i in [1, 2, 3])
    if g:
        return 7
    return 0

if __name__ == "__main__":
    print(f())
