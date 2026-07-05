"""CAL good — the 1024-backing must NOT leak into len(): ==1024 UNPROVABLE."""
_ = 0
#@ ensures \result == 1024
def f() -> int:
    a = [10, 20, 30]
    return len(a)
