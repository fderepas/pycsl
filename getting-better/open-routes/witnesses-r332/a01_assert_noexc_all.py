#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception \all
def g() -> int:
    x = 1
    assert x == 2
    return 7

if __name__ == "__main__":
    print(g())
