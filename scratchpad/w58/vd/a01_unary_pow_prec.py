#@ ensures \result == -4
#@ assigns \nothing
def f() -> int:
    return -2 ** 2
if __name__ == "__main__":
    print(f())
