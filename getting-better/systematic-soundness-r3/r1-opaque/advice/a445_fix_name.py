# Advice probe (route #445): witness 6853 with the attribute name fixed (`self.cout` -> `self.count`).
class P:
    def __init__(self) -> None:
        self.count = 1

    def g(self) -> int:
        return self.count


#@ no_exception \all
def f(p: P) -> int:
    return p.g()
