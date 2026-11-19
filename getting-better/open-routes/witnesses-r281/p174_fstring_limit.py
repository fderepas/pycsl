#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = f"v={x}"
    return 1

if __name__ == "__main__":
    f(10**5000)
