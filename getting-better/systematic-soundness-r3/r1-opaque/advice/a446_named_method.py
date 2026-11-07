# Advice probe (route #446): `a @ b` of a file class rewritten as a call of a NAMED method `a.matmul(b)`.
class V:
    def __init__(self) -> None:
        self.w = 2


class M:
    def __init__(self) -> None:
        self.v = 1

    def matmul(self, o: V) -> int:
        return self.v + o.w


#@ no_exception \all
def f(a: M, b: V) -> int:
    return a.matmul(b)
