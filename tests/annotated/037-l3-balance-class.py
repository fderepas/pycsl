# Level 3 feature: balance class with invariant + preconditioned withdraw
# Tests: #@ class invariant self._balance >= 0
# The withdraw method's precondition maintains the invariant

#@ class invariant self._balance >= 0
class Wallet:
    def __init__(self):
        self._balance = 0
#@ requires amount >= 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ ensures \result == self._balance
    #@ assigns self._balance
    def deposit(self, amount: int) -> int:
        self._balance += amount
        return self._balance
        return self._balance
#@ requires amount >= 0
    #@ requires amount <= self._balance
    #@ ensures self._balance == \old(self._balance) - amount
    #@ ensures \result == self._balance
    #@ assigns self._balance
    def withdraw(self, amount: int) -> int:
        self._balance -= amount
        return self._balance
        return self._balance
#@ requires 1 == 1
    #@ ensures \result == self._balance
    #@ assigns \nothing
    def balance(self) -> int:
        return self._balance
        return self._balance
