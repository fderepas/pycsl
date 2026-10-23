#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return 7 // 2 // 2
if __name__ == "__main__":
    print(f())
