"""Test 0077 — PyCSL Annotation Reference 2.3.1 (variation B)"""
""  # pycsl
#@ class invariant self._balance >= 0
class Account:
    def __init__(self):
        self._balance = 0

    #@ requires amount > 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ assigns self._balance
    def deposit(self, amount: int) -> int:
        self._balance = self._balance + amount
        return self._balance

if __name__ == "__main__":
    a = Account()
    assert a.deposit(100) == 100
