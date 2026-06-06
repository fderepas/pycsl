# Level 3 feature: two separate #@ class invariant lines on the same class
# Tests stacked invariants: self._balance >= 0 AND self._credit >= 0

#@ class invariant self._balance >= 0
#@ class invariant self._credit >= 0
class Account:
    def __init__(self):
        self._balance = 0
        self._credit = 0
#@ requires amount >= 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ ensures \result == self._balance
    #@ assigns self._balance
    def deposit(self, amount: int) -> int:
        self._balance += amount
        return self._balance
        return self._balance
#@ requires amount >= 0
    #@ ensures self._credit == \old(self._credit) + amount
    #@ ensures \result == self._credit
    #@ assigns self._credit
    def add_credit(self, amount: int) -> int:
        self._credit += amount
        return self._credit
        return self._credit
#@ requires 1 == 1
    #@ ensures \result == self._balance + self._credit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def total(self) -> int:
        return self._balance + self._credit
        return self._balance + self._credit
