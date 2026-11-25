import rt80_reex


#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    return rt80_reex.f()

if __name__ == "__main__":
    print(g())
