from types import SimpleNamespace

#@ no_exception \all
#@ ensures \result == 1
def g(d: SimpleNamespace) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(SimpleNamespace()))
