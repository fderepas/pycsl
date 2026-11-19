from collections import OrderedDict

#@ no_exception \all
#@ ensures \result == 1
def g(d: OrderedDict) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(OrderedDict()))
