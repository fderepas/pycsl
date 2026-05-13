# Level 3 feature: two separate #@ class invariant lines on the same class
# Tests stacked invariants: self._balance >= 0 AND self._credit >= 0

class Account:
    def __init__(self):
        self._balance = 0
        self._credit = 0

    def deposit(self, amount):
        self._balance += amount
        return self._balance

    def add_credit(self, amount):
        self._credit += amount
        return self._credit

    def total(self):
        return self._balance + self._credit
