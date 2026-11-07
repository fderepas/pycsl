#@ ensures \result == 0
def f() -> int:
    x = ...
    return x + 0

if __name__ == "__main__":
    print(f())
