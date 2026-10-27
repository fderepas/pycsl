#@ ensures \result == 1
def f(n: int) -> int:
    s = {*range(n)}
    return len(s)
if __name__ == "__main__":
    print(f(3))
