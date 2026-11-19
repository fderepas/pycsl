#@ ensures \result == 0
def f(x: int = 0.5) -> int:  # type: ignore
    return x % 1

if __name__ == "__main__":
    print(f())
