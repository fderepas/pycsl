#@ ensures \result == 5
def f() -> int:
    n: int = 5
    assert n > 0
    return n
if __name__ == "__main__":
    print(f())
