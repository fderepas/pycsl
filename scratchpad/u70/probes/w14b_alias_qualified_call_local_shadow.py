import rt77lib_val as L


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return L.val1()

if __name__ == "__main__":
    print(g())
