# u72 helper (route #630, review rt80 R3b): a class whose method body calls the library's own `helper`.


#@ ensures \result == 1
#@ assigns \nothing
def helper() -> int:
    return 1


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return helper()
