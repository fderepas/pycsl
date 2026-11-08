"""PROBE: an ANNOTATED subscript store `a[0]: int = 5`."""
_ = 0  # anchor

#@ requires \length(a) > 0 and a[0] == 0
#@ ensures \result == 0
#@ assigns a[0..0]
def f(a: list) -> int:
    a[0]: int = 7
    return a[0]

if __name__ == "__main__":
    print(f([0]))
