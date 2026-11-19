import mylib


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return mylib.inc(1)


if __name__ == "__main__":
    r = f()
    print("result", r, "OK" if r == 2 else "VIOLATION ensures")
