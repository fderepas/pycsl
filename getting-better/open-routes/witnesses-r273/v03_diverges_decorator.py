# FALSE (termination): diverging decorator applied at module level.
#@ \diverges
#@ ensures \result == 1
#@ assigns \nothing
def spin(fn: object) -> int:
    while True:
        pass
    return 1

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    @spin
    def inner() -> int:
        return 1
    return 1

if __name__ == "__main__":
    import signal; signal.alarm(2)
    print(f())
