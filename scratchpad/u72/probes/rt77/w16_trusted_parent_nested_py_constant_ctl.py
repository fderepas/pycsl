#@ \trusted
#@ ensures \result == 2
def outer() -> int:
    def constant() -> int:
        return 2
    return constant()


#@ ensures \result == 1
#@ assigns \nothing
def py_constant() -> int:
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return py_constant()

if __name__ == "__main__":
    print(g(), outer())
