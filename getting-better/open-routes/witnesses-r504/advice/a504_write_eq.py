# route #504 advice 'Write `==` if you mean equality': witness b60104 with `is` -> `==`.
class K:
    def __init__(self, n: int) -> None:
        self.a = n + 1000
        self.b = n + 1000


#@ ensures \result == True
def f(n: int) -> bool:
    k = K(n)
    return k.a == k.b
