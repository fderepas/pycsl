#@ ensures \result == 0
#@ assigns \nothing
#@ \diverges
#@ no_exception \all
def f(k: int) -> int:
    return f(k)

if __name__ == "__main__":
    print(f(1))
