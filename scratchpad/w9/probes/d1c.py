"""PROBE: is the DROPPED augmented store `a[i].f += v` exploitable?"""
_ = 0  # anchor

class E:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

class Box:
    #@ requires True
    #@ ensures True
    #@ assigns self.items
    def __init__(self) -> None:
        self.items: list = [E()]

    #@ requires \length(self.items) > 0 and self.items[0].v == 0
    #@ ensures \result == 0
    def bump(self) -> int:
        self.items[0].v = 5
        return self.items[0].v

if __name__ == "__main__":
    print(Box().bump())
