import rt77lib_val


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt77lib_val.val1()

if __name__ == "__main__":
    print(g())
