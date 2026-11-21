#@ ensures \result == 1
def f(n: int) -> int:
    xs = n * [1]
    return len(xs)
if __name__ == "__main__":
    print(f(3))
