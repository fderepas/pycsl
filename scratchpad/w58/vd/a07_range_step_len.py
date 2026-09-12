#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    n: int = 0
    for i in range(1, 10, 3):
        n = n + 1
    return n
if __name__ == "__main__":
    print(f())
