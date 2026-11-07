r"""H-S capability through a module-global receiver call site."""
# pycsl-flags: --memory-model hoare
#@ happy authn:
#@     targets transfer
#@     precond self.session_authenticated == 1
class Bank:
    def __init__(self) -> None:
        self.session_authenticated: int = 0

    #@ requires True
    def transfer(self, amount: int) -> int:
        return amount


_b = Bank()


#@ ensures \result == 5
def handle(amount: int) -> int:
    return _b.transfer(amount) * 0 + 5


if __name__ == "__main__":
    print("CPython:", handle(5))
