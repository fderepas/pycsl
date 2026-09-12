#@ ensures \result == 99
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[1:100])
if __name__ == "__main__":
    print(f())
