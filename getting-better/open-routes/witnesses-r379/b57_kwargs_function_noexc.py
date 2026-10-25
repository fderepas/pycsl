#@ assigns \nothing
def h(x: int) -> int:
    return x

#@ no_exception \all
def f() -> int:
    kw = {"y": 5}
    return h(1, **kw)

if __name__ == "__main__":
    print(f())
