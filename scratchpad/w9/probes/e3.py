"""PROBE: an erased tuple RETURNED and compared by the caller."""
_ = 0  # anchor
#@ requires True
#@ ensures True
def mk() -> tuple:
    return (1, 2)

#@ requires True
#@ ensures \result == 7
def f() -> int:
    a = mk()
    b = mk()
    if a == b:
        return 7
    return 0
if __name__ == "__main__":
    print(f())
