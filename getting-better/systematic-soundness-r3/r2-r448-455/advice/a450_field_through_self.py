# advice probe (route #450): witness 6964 reading the field through `self` -- must VERIFY
class B:
    def __init__(self) -> None:
        self.v = 1


class Q(B):
    def g(self) -> int:
        return self.v


#@ no_exception \all
def f(p: Q) -> int:
    return p.g()
