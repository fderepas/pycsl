#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 5
    b: int = 3
    c: int = 1
    return a > b > c
if __name__ == "__main__":
    print(f())
