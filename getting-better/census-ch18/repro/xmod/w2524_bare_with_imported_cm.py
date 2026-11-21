from cmlib import Counter


#@ ensures \result == 0
def f() -> int:
    c = Counter()
    with c:
        pass
    return c.n


if __name__ == "__main__":
    print("CPython f() =", f())
