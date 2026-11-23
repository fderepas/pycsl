import rt80_redef


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_redef.f()

if __name__ == "__main__":
    print(g())
