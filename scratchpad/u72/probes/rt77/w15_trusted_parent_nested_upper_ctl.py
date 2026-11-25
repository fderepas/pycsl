#@ \trusted
#@ ensures \result == 2
def outer() -> int:
    def F() -> int:
        return 2
    return F()


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    print(g(), outer())
