import rt80_cond


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_cond.f()

if __name__ == "__main__":
    print(g())
