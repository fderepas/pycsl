# Advice probe (route #445): witness 6855 with the subclass calling `super().__init__()`.
class B:
    def __init__(self) -> None:
        self.a = 1


class Q(B):
    def __init__(self) -> None:
        super().__init__()

    def g(self) -> int:
        return self.a


#@ no_exception \all
def f(p: Q) -> int:
    return p.g()
