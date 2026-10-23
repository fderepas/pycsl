def gen():
    yield 1
    yield 2


#@ ensures \result == 0
def probe() -> int:
    s = 0
    for x in gen():
        s = s + x
    return s
