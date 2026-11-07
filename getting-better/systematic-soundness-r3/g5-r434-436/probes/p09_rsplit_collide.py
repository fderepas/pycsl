class C:
    def rsplit(self, a: str, n: int) -> int:
        return n


#@ no_exception \all
def f(s: str, n: int) -> int:
    return len(s.rsplit(" ", n))
