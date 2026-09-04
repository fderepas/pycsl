"""PROBE: is a set comprehension's ELT dropped?"""
_ = 0  # anchor
#@ requires \length(a) >= 1 and a[0] == 1
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    s = {x + 7 for x in a}
    if 8 in s:
        return 7
    return 0
if __name__ == "__main__":
    print(f([1]))
