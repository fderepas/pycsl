class R:
    if True:
        def __eq__(self, o: object) -> bool:
            return True

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
