# FALSE (termination): diverging call in a default argument of a nested def / evaluated at def time.
#@ \diverges
#@ ensures \result == 1
#@ assigns \nothing
def spin() -> int:
    while True:
        pass
    return 1

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    def inner(x: int = spin()) -> int:
        return 1
    return 1

if __name__ == "__main__":
    import signal; signal.alarm(2)
    print(f())
