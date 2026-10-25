NOHASH = None

class R:
    __hash__ = NOHASH

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
