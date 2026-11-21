#@ ensures \result == True
def f() -> bool:
    b = True
    x = 1
    return f"{b}" == f"{x}"

if __name__ == "__main__":
    assert f() == True, repr(f())
