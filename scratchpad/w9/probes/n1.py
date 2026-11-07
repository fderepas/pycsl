"""PROBE: is a SLICE's LOWER bound dropped?"""
_ = 0  # anchor
#@ requires \length(a) >= 4 and a[0] == 0 and a[1] == 7
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    b = a[1:3]
    return b[0]
if __name__ == "__main__":
    print(f([0, 7, 0, 0]))
