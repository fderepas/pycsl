#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 0
    return a ** 0
if __name__ == "__main__":
    print(f())
