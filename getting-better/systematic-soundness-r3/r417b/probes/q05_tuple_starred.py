#@ ensures \result == 1
def f(n: int) -> int:
    t = (*range(n),)
    return len(t)
if __name__ == "__main__":
    print(f(3))
