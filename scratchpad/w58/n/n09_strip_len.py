#@ ensures \result == 4
def f() -> int:
    s: str = "  ab  "
    return len(s.strip())
if __name__ == "__main__":
    print(f())
