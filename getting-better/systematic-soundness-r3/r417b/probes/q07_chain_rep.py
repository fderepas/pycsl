#@ ensures \result == 3
def f() -> int:
    xs = [1] * 2 * 3
    return len(xs)
if __name__ == "__main__":
    print(f())
