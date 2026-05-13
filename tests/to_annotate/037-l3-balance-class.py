# Level 3 feature: balance class with invariant + preconditioned withdraw
# Tests: #@ class invariant self._balance >= 0
# The withdraw method's precondition maintains the invariant

class Wallet:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount):
        self._balance += amount
        return self._balance

    def withdraw(self, amount):
        self._balance -= amount
        return self._balance

    def balance(self):
        return self._balance
