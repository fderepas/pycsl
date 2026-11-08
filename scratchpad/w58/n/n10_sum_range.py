#@ ensures \result == 0
def f() -> int:
    t: int = 0
    for i in range(4):
        t = t + i
    return t
if __name__ == "__main__":
    print(f())
