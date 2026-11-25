import rt77lib_val


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt77lib_val.val1()

if __name__ == "__main__":
    print(g())
