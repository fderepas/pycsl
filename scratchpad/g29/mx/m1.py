r"""Mixin: a provider whose contract is WEAKER than the declared dependency."""
_ = 0  # anchor


#@ mixin
class Needs:
    #@ depends_method val: (self) -> int
    #@     ensures \result >= 0
    #@ ensures \result >= 0
    def use(self) -> int:
        return self.val()


#@ mixin
class Gives:
    #@ provides val
    #@ ensures \result >= -5
    def val(self) -> int:
        return -5


#@ compose_from Needs, Gives
class C:
    def __init__(self) -> None:
        self.k = 0


#@ ensures \result >= 0
def probe() -> int:
    c = C()
    return c.use()


if __name__ == "__main__":
    print("CPython:", probe())
