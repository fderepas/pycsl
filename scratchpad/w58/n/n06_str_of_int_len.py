#@ ensures \result == 1
def f() -> int:
    n: int = 100
    return len(str(n))
if __name__ == "__main__":
    print(f())
