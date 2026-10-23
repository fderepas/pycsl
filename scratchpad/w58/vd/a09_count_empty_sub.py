#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    s: str = "abc"
    return s.count("")
if __name__ == "__main__":
    print(f())
