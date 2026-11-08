class D(KeyError):
    pass
#@ no_exception \all
def f() -> int:
    try:
        raise D(k=1)
    except D:
        return 1
    return 2
if __name__ == "__main__":
    print("result", f())
