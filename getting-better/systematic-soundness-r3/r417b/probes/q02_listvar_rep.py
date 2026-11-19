#@ ensures \result == 2
def f() -> int:
    ys = [1, 2]
    xs = ys * 3
    return len(xs)
if __name__ == "__main__":
    print(f())
