#@ ensures \result == 1
def f() -> int:
    x: int = 1
    del x
    return x
if __name__ == "__main__":
    print(f())
