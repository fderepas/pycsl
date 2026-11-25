import rt77lib_val


class C:
    def __init__(self) -> None:
        self.v = 0


#@ ensures \result == 2
#@ assigns \nothing
def rt77lib_val__val1() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return rt77lib_val.val1()

if __name__ == "__main__":
    print(g())
