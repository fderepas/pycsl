#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


def f() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    print(g())
