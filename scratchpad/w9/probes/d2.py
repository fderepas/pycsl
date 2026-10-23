"""PROBE: is `obj.f += v` on a LOCAL record dropped?"""
_ = 0  # anchor

class E:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

#@ requires True
#@ ensures \result == 0
def f() -> int:
    e = E()
    e.v += 5
    return e.v

if __name__ == "__main__":
    print(f())
