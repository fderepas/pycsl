# route #343: the W-typed self.me() result returned through -> int? (route #252 flow)
class P:
    def me(self) -> "P":
        return self

#@ no_exception \all
def h(n: int) -> int:
    return n + 1

class Q:
    def me(self) -> "Q":
        return self

    #@ no_exception \all
    def m(self) -> int:
        return h(self.me())

if __name__ == "__main__":
    Q().m()
