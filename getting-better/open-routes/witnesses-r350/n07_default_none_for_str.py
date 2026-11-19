#@ no_exception \all
#@ ensures \result >= 0
def f(s: str = None) -> int:  # type: ignore
    return len(s)

if __name__ == "__main__":
    print(f())
