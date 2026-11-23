import rt80_rebind


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_rebind.f()

if __name__ == "__main__":
    print(g())
