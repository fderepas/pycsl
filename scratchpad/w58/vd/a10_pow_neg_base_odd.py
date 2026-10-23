#@ ensures \result == -8
#@ assigns \nothing
def f() -> int:
    a: int = -2
    return a ** 3
if __name__ == "__main__":
    print(f())
