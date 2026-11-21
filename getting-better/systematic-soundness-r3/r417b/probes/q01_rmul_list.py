#@ ensures \result == 3
def f() -> int:
    xs = 3 * [1, 2]
    return len(xs)
if __name__ == "__main__":
    print(f())
