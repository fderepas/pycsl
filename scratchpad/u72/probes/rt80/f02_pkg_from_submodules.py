from rt80pkg import a, b


#@ ensures \result == 2 or \result == 4
#@ assigns \nothing
def g() -> int:
    return a.f() + b.f()

if __name__ == "__main__":
    print(g())
