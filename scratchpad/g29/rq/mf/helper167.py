class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ requires d != 0
#@ ensures \result == 1
def fget(d: int) -> int:
    return d // d
