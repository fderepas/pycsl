#@ ensures \result == 3
def f() -> int:
    s: str = "abc"
    return len(s.replace("b", ""))
if __name__ == "__main__":
    print(f())
