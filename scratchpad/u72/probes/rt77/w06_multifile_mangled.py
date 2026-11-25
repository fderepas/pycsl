from rt77lib_cls import C


#@ ensures \result == 2
#@ assigns \nothing
def c__m(x: int) -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    o = C()
    return o.m(0)

if __name__ == "__main__":
    print(g())
