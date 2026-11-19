class D(SyntaxError):
    pass


#@ no_exception \all
#@ ensures \result == 1
def f(name: str) -> int:
    e = D("m", (name, 1, 2, "t"))
    g = D("only a message")
    return 1


if __name__ == "__main__":
    assert f("x.py") == 1
