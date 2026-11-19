

#@ no_exception \all
#@ ensures \result == 1
def g(d: dict) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g({}))
