# advice probe (route #450): witness 6963 calling the base method with its parameters -- must VERIFY
class B:
    def h(self) -> int:
        return 1


class Q(B):
    def g(self) -> int:
        return super().h()


#@ no_exception \all
def f(p: Q) -> int:
    return p.g()
