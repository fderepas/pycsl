g: int = 0

#@ assigns g
#@ ensures g == 5
def setter() -> None:
    global g
    g = 5

#@ ensures \result == 0
def reader() -> int:
    setter()
    return g
