from collections import Counter

#@ no_exception \all
#@ ensures \result == 1
def g(d: Counter) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(Counter()))
