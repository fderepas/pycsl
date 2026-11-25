import rt80_tryd


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_tryd.f()

if __name__ == "__main__":
    print(g())
