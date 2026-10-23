#@ ensures \result == 512
#@ assigns \nothing
def f() -> int:
    return 2 ** 3 ** 2
if __name__ == "__main__":
    print(f())
