#@ \trusted
#@ ensures \result == 2
def outer() -> int:
    #@ ensures \result == 2
    def f() -> int:
        return 2
    return f()


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    print(g())
