#@ ensures \result == -6
#@ assigns \nothing
def f() -> int:
    s: str = "ab"
    return len(s * -3)
if __name__ == "__main__":
    print(f())
