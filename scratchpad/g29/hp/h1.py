r"""H-S capability through a RECEIVER-VAR call site (documented follow-up in annotations.md row 8)."""
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


#@ ensures \result == 5
def handle(amount: int) -> int:
    b = Bank()
    return b.transfer(amount) * 0 + 5


if __name__ == "__main__":
    print("CPython:", handle(5))
