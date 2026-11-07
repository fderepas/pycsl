# pycsl-flags: --memory-model hoare


class Base:
    def __init__(self):
        self.v: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def get(self) -> int:
        return self.v


class Sub(Base):
    #@ requires True
    #@ ensures self.v == -5
    #@ assigns self.v
    def break_it(self) -> None:
        self.v = -5
