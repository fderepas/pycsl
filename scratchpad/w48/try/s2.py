class C:
    #@ requires True
    #@ ensures self.__v == 3
    #@ assigns self.__v
    def __init__(self) -> None:
        self.__v = 3

    #@ requires True
    #@ ensures \result == self.__v
    #@ assigns \nothing
    def get(self) -> int:
        return self.__v

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    if c.get() == 3:
        return 0
    return 1
