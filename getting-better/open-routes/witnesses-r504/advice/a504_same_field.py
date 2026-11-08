# route #504 advice 'compare identity ... between two reads of the same field': = control 7992.
class K:
    def __init__(self, n: int) -> None:
        self.a = n + 1000
        self.b = n + 1000


#@ ensures \result == True
def f(n: int) -> bool:
    k = K(n)
    return k.a is k.a
