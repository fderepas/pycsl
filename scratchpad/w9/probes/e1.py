"""PROBE: comparing two DIFFERENT erased tuple literals."""
_ = 0  # anchor
#@ requires True
#@ ensures \result == 7
def f() -> int:
    x = (1, 2)
    if x == (3, 4):
        return 7
    return 0
if __name__ == "__main__":
    print(f())
