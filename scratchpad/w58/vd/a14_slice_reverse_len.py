#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[::-1])
if __name__ == "__main__":
    print(f())
