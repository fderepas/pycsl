"""Test 0193 — PyCSL Annotation Reference 2.3.1 (invariant-guarding withdraw)"""
""  # pycsl
#@ class invariant self._balance >= 0
class BankAccount:
    def __init__(self):
        self._balance = 0

    #@ requires amount >= 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ assigns self._balance
    def deposit(self, amount: int) -> int:
        self._balance = self._balance + amount
        return self._balance

    #@ requires amount >= 0
    #@ requires amount <= self._balance
    #@ ensures self._balance == \old(self._balance) - amount
    #@ assigns self._balance
    def withdraw(self, amount: int) -> int:
        self._balance = self._balance - amount
        return self._balance

    #@ ensures \result == self._balance
    #@ assigns \nothing
    def get_balance(self) -> int:
        return self._balance

if __name__ == "__main__":
    acct = BankAccount()
    acct.deposit(100)
    assert acct.get_balance() == 100
    acct.withdraw(40)
    assert acct.get_balance() == 60
