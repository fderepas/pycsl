#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[-100:2])
if __name__ == "__main__":
    print(f())
