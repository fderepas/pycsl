r"""G29 M1 — a module constant REBOUND through `global` inside a function; is it still folded?"""
_ = 0  # anchor
LIM = -1


#@ assigns \nothing
def setlim() -> None:
    global LIM
    LIM = 5


#@ ensures \result == -1
def g() -> int:
    setlim()
    return LIM


if __name__ == "__main__":
    print("CPython:", g())
