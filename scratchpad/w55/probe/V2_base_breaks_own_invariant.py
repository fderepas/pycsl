# pycsl-flags: --memory-model hoare


#@ class invariant self.v >= 0
class Base:
    def __init__(self):
        self.v: int = 0

    #@ requires True
    #@ ensures \result >= 0
    #@ assigns \nothing
    def get(self) -> int:
        return self.v

    #@ requires True
    #@ ensures self.v == -5
    #@ assigns self.v
    def break_it(self) -> None:
        self.v = -5
