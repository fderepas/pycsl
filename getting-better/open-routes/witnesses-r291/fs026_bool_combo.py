#@ ensures \result == True
def f1() -> bool:
    b = True
    x = 1
    return "{}".format(b) == "{}".format(x)

#@ ensures \result == True
def f2() -> bool:
    b = True
    x = 1
    return format(b) == format(x)

#@ ensures \result == True
def f3() -> bool:
    b = False
    x = 0
    return f"v={b}" == f"v={x}"

#@ ensures \result == True
def f4(x: int) -> bool:
    b = x == 1
    return f"{b}" == f"{1 if b else 0}"

if __name__ == "__main__":
    print(f1(), f2(), f3(), f4(1))
    assert (f1(), f2(), f3(), f4(1)) == (True, True, True, True)
