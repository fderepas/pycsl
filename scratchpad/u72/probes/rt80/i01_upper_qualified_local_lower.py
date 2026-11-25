import rt80_upper


#@ ensures \result == 2
#@ assigns \nothing
def val1() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt80_upper.Val1()

if __name__ == "__main__":
    print(g())
