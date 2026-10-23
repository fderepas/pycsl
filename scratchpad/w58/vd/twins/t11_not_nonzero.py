#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = 5
    return not a
if __name__ == "__main__":
    print(f())
