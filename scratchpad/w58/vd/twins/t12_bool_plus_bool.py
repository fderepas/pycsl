#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: bool = True
    b: bool = True
    return a + b
if __name__ == "__main__":
    print(f())
