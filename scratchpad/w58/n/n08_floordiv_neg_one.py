#@ ensures \result == 5
def f() -> int:
    a: int = -5
    b: int = -1
    return a // b
if __name__ == "__main__":
    print(f())
