class B(ValueError):
    pass
class D(B):
    pass
#@ no_exception \all
def f() -> int:
    e = D(code=1)
    return 1
if __name__ == "__main__":
    print("result", f())
