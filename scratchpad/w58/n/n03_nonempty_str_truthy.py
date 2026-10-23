#@ ensures \result == 0
def f() -> int:
    s: str = "0"
    return 1 if s else 0
if __name__ == "__main__":
    print(f())
