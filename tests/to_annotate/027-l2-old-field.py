# Level 2 feature: OldField in ensures contract
# Tests \old(self._balance) → (old self._balance) in WhyML spec

class Ledger:
    def __init__(self):
        self._balance = 0

    def deposit(self, n):
        self._balance += n
        return self._balance

    def withdraw(self, n):
        if n <= self._balance:
            self._balance -= n
        return self._balance
