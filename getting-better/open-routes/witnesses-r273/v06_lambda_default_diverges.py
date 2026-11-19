# FALSE (termination): lambda default `spin()` evaluated when the lambda expression is evaluated.
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
    h = lambda x=spin(): x
    return 1

if __name__ == "__main__":
    import signal; signal.alarm(2)
    print(f())
