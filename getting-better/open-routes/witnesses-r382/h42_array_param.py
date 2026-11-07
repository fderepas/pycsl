import array

#@ no_exception \all
#@ ensures \result == 1
def g(d: array.array) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(array.array('i')))
