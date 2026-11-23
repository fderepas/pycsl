#@ ensures \result == 1
#@ assigns \nothing
def constant(x: int) -> int:
    return 1


#@ ensures \result == 2
#@ assigns \nothing
def py_constant(x: int) -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return constant(0)

if __name__ == "__main__":
    print(g())
