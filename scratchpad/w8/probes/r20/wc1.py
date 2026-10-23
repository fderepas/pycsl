class CM:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def __enter__(self) -> int:
        return 7

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __exit__(self, a: int, b: int, c: int) -> None:
        pass

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    v: int = 0
    with CM() as v:
        return v
