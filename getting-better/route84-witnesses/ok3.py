#@ requires True
#@ ensures \result == n
#@ assigns \nothing
def identity(n: int) -> int:
    return n

#@ ensures \result == 42
def f() -> int:
    assert identity(42) == 42
    return 42
if __name__ == "__main__":
    print(f())
