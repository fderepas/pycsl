from rt77lib_val import val1


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return val1()

if __name__ == "__main__":
    print(g())
