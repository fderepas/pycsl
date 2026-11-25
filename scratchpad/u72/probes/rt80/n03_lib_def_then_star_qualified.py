import rt80_late_star


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_late_star.f()

if __name__ == "__main__":
    print(g())
